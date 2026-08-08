import ast
import logging
from pathlib import Path
from app.config import IGNORE_DIRS, LANGUAGE_BY_EXT

logger = logging.getLogger(__name__)


def build_import_graph(local_path: str) -> dict:
    """Walk Python files and extract import relationships.
    Returns {file_path: [imported_module, ...]}."""
    graph = {}
    root = Path(local_path)
    for py_file in root.rglob("*.py"):
        # Skip ignored directories
        parts = py_file.relative_to(root).parts
        if any(p in IGNORE_DIRS or p.startswith(".") for p in parts):
            continue
        try:
            source = py_file.read_text(errors="ignore")
            tree = ast.parse(source)
        except (SyntaxError, OSError):
            continue

        rel = str(py_file.relative_to(root))
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.append(module)
        graph[rel] = imports
    return graph


def build_call_graph(local_path: str) -> dict:
    """Walk Python files and extract function call relationships.
    Returns {file_path: {function_name: [called_functions]}}."""
    graph = {}
    root = Path(local_path)
    for py_file in root.rglob("*.py"):
        parts = py_file.relative_to(root).parts
        if any(p in IGNORE_DIRS or p.startswith(".") for p in parts):
            continue
        try:
            source = py_file.read_text(errors="ignore")
            tree = ast.parse(source)
        except (SyntaxError, OSError):
            continue

        rel = str(py_file.relative_to(root))
        file_calls = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                calls = []
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            calls.append(child.func.id)
                        elif isinstance(child.func, ast.Attribute):
                            calls.append(child.func.attr)
                file_calls[node.name] = calls
        if file_calls:
            graph[rel] = file_calls
    return graph


def get_project_graph_summary(local_path: str) -> str:
    """Build a text summary of the project's import and call graphs for the architecture agent."""
    import_graph = build_import_graph(local_path)
    call_graph = build_call_graph(local_path)

    lines = []
    if import_graph:
        lines.append("IMPORT GRAPH:")
        for file, imports in sorted(import_graph.items()):
            if imports:
                lines.append(f"  {file} imports: {', '.join(imports[:15])}")

    if call_graph:
        lines.append("\nCALL GRAPH:")
        for file, funcs in sorted(call_graph.items()):
            for func_name, calls in funcs.items():
                if calls:
                    lines.append(f"  {file}::{func_name}() calls: {', '.join(calls[:10])}")

    return "\n".join(lines) if lines else "No Python code graph available."
