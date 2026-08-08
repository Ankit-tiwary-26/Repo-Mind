import ast
import logging
from app.config import settings

logger = logging.getLogger(__name__)


def _chunk_python_ast(source: str, rel_path: str) -> list[dict] | None:
    """Try to chunk Python files by function/class boundaries using the ast module.
    Returns None if parsing fails (caller should fall back to line-window)."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None

    lines = source.splitlines(keepends=True)
    chunks = []
    # Collect top-level and nested class/function definitions
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno - 1  # 0-indexed
            end = node.end_lineno if node.end_lineno else start + 1
            text = "".join(lines[start:end]).strip()
            if not text:
                continue
            chunks.append({
                "text": text,
                "metadata": {
                    "path": rel_path,
                    "language": "Python",
                    "start_line": start + 1,
                    "end_line": end,
                    "symbol": getattr(node, "name", ""),
                    "symbol_type": type(node).__name__,
                },
            })

    # Also grab module-level code (imports, constants, etc.) that isn't inside any def/class
    if lines:
        top_level_ranges = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = node.lineno - 1
                end = node.end_lineno if node.end_lineno else start + 1
                top_level_ranges.append((start, end))
        # Collect lines not covered by any top-level def/class
        module_lines = []
        module_start = None
        for i, line in enumerate(lines):
            in_range = any(s <= i < e for s, e in top_level_ranges)
            if not in_range:
                if module_start is None:
                    module_start = i
            else:
                if module_start is not None and module_lines:
                    text = "".join(lines[module_start:i]).strip()
                    if text:
                        chunks.insert(0, {
                            "text": text,
                            "metadata": {
                                "path": rel_path,
                                "language": "Python",
                                "start_line": module_start + 1,
                                "end_line": i,
                                "symbol": "<module>",
                                "symbol_type": "Module",
                            },
                        })
                    module_lines = []
                    module_start = None
            if not in_range:
                module_lines.append(line)
        # Flush remaining module-level code
        if module_start is not None and module_lines:
            text = "".join(module_lines).strip()
            if text:
                chunks.insert(0, {
                    "text": text,
                    "metadata": {
                        "path": rel_path,
                        "language": "Python",
                        "start_line": module_start + 1,
                        "end_line": len(lines),
                        "symbol": "<module>",
                        "symbol_type": "Module",
                    },
                })

    return chunks if chunks else None


def _chunk_line_window(lines: list[str], rel_path: str, language: str) -> list[dict]:
    """Fallback: fixed-size line-window chunking with overlap."""
    chunks = []
    size = settings.chunk_size_lines
    overlap = settings.chunk_overlap_lines
    step = max(size - overlap, 1)

    for start in range(0, len(lines), step):
        end = min(start + size, len(lines))
        text = "".join(lines[start:end]).strip()
        if not text:
            continue
        chunks.append({
            "text": text,
            "metadata": {
                "path": rel_path,
                "language": language,
                "start_line": start + 1,
                "end_line": end,
            },
        })
        if end == len(lines):
            break
    return chunks


def chunk_file(abs_path: str, rel_path: str, language: str) -> list[dict]:
    """Chunk a source file. Uses AST-based chunking for Python, line-window for everything else."""
    try:
        with open(abs_path, "r", errors="ignore") as f:
            source = f.read()
    except OSError:
        return []

    if not source.strip():
        return []

    # Try AST chunking for Python
    if language == "Python":
        ast_chunks = _chunk_python_ast(source, rel_path)
        if ast_chunks:
            return ast_chunks

    # Fallback to line-window
    lines = source.splitlines(keepends=True)
    return _chunk_line_window(lines, rel_path, language)
