import os
import shutil
import zipfile
import uuid
from pathlib import Path
from git import Repo

from app.config import settings, IGNORE_DIRS, LANGUAGE_BY_EXT


def new_project_id() -> str:
    return uuid.uuid4().hex[:12]


def clone_repo(git_url: str, token: str | None = None) -> tuple[str, str]:
    """Clone a public or private (token) repo. Returns (project_id, local_path)."""
    project_id = new_project_id()
    dest = Path(settings.repos_path) / project_id
    dest.mkdir(parents=True, exist_ok=True)

    clone_url = git_url
    if token:
        # inject token for private repo auth, e.g. https://TOKEN@github.com/org/repo.git
        if git_url.startswith("https://"):
            clone_url = git_url.replace("https://", f"https://{token}@")

    Repo.clone_from(clone_url, dest, depth=1)
    return project_id, str(dest)


def ingest_zip(zip_path: str) -> tuple[str, str]:
    project_id = new_project_id()
    dest = Path(settings.repos_path) / project_id
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest)
    return project_id, str(dest)


def walk_project(local_path: str) -> list[dict]:
    """Walk the project, skipping ignored dirs, return file metadata."""
    files_meta = []
    for root, dirs, files in os.walk(local_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
        for fname in files:
            fpath = Path(root) / fname
            try:
                size = fpath.stat().st_size
            except OSError:
                continue
            if size == 0 or size > settings.max_file_size_bytes:
                continue
            ext = fpath.suffix.lower()
            language = LANGUAGE_BY_EXT.get(ext)
            if language is None:
                continue  # skip binary/unknown files for now
            files_meta.append({
                "path": str(fpath.relative_to(local_path)),
                "abs_path": str(fpath),
                "language": language,
                "size": size,
            })
    return files_meta


def detect_frameworks(local_path: str) -> list[str]:
    markers = {
        "package.json": "Node.js",
        "requirements.txt": "Python",
        "pyproject.toml": "Python (Poetry/PEP517)",
        "pom.xml": "Java (Maven)",
        "build.gradle": "Java/Kotlin (Gradle)",
        "go.mod": "Go Modules",
        "Cargo.toml": "Rust (Cargo)",
        "Dockerfile": "Docker",
        "docker-compose.yml": "Docker Compose",
        "next.config.js": "Next.js",
        "manage.py": "Django",
    }
    found = []
    root = Path(local_path)
    for fname, label in markers.items():
        if (root / fname).exists() or any(root.glob(f"**/{fname}")):
            found.append(label)
    return found


def project_summary(local_path: str) -> dict:
    files = walk_project(local_path)
    lang_counts: dict[str, int] = {}
    for f in files:
        lang_counts[f["language"]] = lang_counts.get(f["language"], 0) + 1
    return {
        "total_files": len(files),
        "languages": sorted(lang_counts.items(), key=lambda x: -x[1]),
        "frameworks": detect_frameworks(local_path),
    }
