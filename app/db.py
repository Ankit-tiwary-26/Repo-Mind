import sqlite3
import json
from app.config import settings

def _get_db_path():
    path = getattr(settings, "database_url", "sqlite:///repomind.db")
    if path.startswith("sqlite:///"):
        path = path.replace("sqlite:///", "")
    return path

def init_db():
    conn = sqlite3.connect(_get_db_path())
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY,
            repo_url TEXT,
            local_path TEXT,
            files_indexed INT,
            chunk_count INT,
            meta_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT,
            question TEXT,
            answer TEXT,
            agent TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_project(project_id: str, repo_url: str, local_path: str, files_indexed: int, chunk_count: int, meta: dict = None):
    conn = sqlite3.connect(_get_db_path())
    cursor = conn.cursor()
    meta_json = json.dumps(meta) if meta else "{}"
    cursor.execute("""
        INSERT OR REPLACE INTO projects (project_id, repo_url, local_path, files_indexed, chunk_count, meta_json)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (project_id, repo_url, local_path, files_indexed, chunk_count, meta_json))
    conn.commit()
    conn.close()

def get_project(project_id: str) -> dict | None:
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    meta_json = d.pop("meta_json", None)
    d["meta"] = json.loads(meta_json) if meta_json else None
    return d

def list_projects() -> list[dict]:
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        d = dict(row)
        meta_json = d.pop("meta_json", None)
        d["meta"] = json.loads(meta_json) if meta_json else None
        results.append(d)
    return results

def delete_project(project_id: str):
    conn = sqlite3.connect(_get_db_path())
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
    cursor.execute("DELETE FROM chat_history WHERE project_id = ?", (project_id,))
    conn.commit()
    conn.close()

def project_exists(project_id: str) -> bool:
    conn = sqlite3.connect(_get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM projects WHERE project_id = ?", (project_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def save_chat(project_id: str, question: str, answer: str, agent: str):
    conn = sqlite3.connect(_get_db_path())
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_history (project_id, question, answer, agent)
        VALUES (?, ?, ?, ?)
    """, (project_id, question, answer, agent))
    conn.commit()
    conn.close()

def get_chat_history(project_id: str, limit: int = 50) -> list[dict]:
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM chat_history 
        WHERE project_id = ? 
        ORDER BY created_at ASC 
        LIMIT ?
    """, (project_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]