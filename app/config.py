from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    chroma_path: str = "./chroma_data"
    repos_path: str = "./repos"
    chunk_size_lines: int = 120
    chunk_overlap_lines: int = 20
    max_file_size_bytes: int = 500_000
    database_url: str = "sqlite:///repomind.db"

    class Config:
        env_file = ".env"


settings = Settings()

IGNORE_DIRS = {
    "node_modules", ".git", "venv", ".venv", "env", "__pycache__",
    "build", "dist", ".next", "target", "vendor", ".idea", ".vscode",
    "coverage", ".pytest_cache", "site-packages", ".mypy_cache", "out",
}

LANGUAGE_BY_EXT = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".java": "Java",
    ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP",
    ".c": "C", ".h": "C", ".cpp": "C++", ".hpp": "C++",
    ".cs": "C#", ".kt": "Kotlin", ".swift": "Swift",
    ".sql": "SQL", ".sh": "Shell", ".yml": "YAML", ".yaml": "YAML",
    ".json": "JSON", ".md": "Markdown", ".dockerfile": "Docker",
}
