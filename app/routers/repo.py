import shutil
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.services import ingest, chunker, vectorstore
from app import db

router = APIRouter(prefix="/api/v1/repo", tags=["repo"])


class CloneRequest(BaseModel):
    git_url: str
    github_token: str | None = None


def _ingest_and_index(project_id: str, local_path: str, repo_url: str = "") -> dict:
    files = ingest.walk_project(local_path)
    all_chunks = []
    for f in files:
        all_chunks.extend(chunker.chunk_file(f["abs_path"], f["path"], f["language"]))
    vectorstore.add_chunks(project_id, all_chunks)
    summary = ingest.project_summary(local_path)

    # Persist to SQLite
    db.save_project(
        project_id=project_id,
        repo_url=repo_url,
        local_path=local_path,
        files_indexed=len(files),
        chunk_count=len(all_chunks),
        meta=summary,
    )

    return {
        "project_id": project_id,
        "files_indexed": len(files),
        "chunks_indexed": len(all_chunks),
        "summary": summary,
    }


@router.post("/clone")
def clone(req: CloneRequest):
    local_path = None
    try:
        project_id, local_path = ingest.clone_repo(req.git_url, req.github_token)
        return _ingest_and_index(project_id, local_path, repo_url=req.git_url)
    except Exception as e:
        if local_path:
            shutil.rmtree(local_path, ignore_errors=True)
        raise HTTPException(
            status_code=400,
            detail=f"Repository ingest failed: {e}",
        ) from e


@router.post("/upload-zip")
async def upload_zip(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    project_id, local_path = ingest.ingest_zip(tmp_path)
    return _ingest_and_index(project_id, local_path, repo_url=file.filename or "uploaded.zip")


@router.get("/list")
def list_projects():
    return db.list_projects()


@router.get("/{project_id}/summary")
def get_summary(project_id: str):
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}")
def delete_project(project_id: str):
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # Clean up local files
    local_path = project.get("local_path")
    if local_path:
        p = Path(local_path)
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
    # Clean up vector store
    try:
        vectorstore.delete_collection(project_id)
    except Exception:
        pass
    # Clean up database
    db.delete_project(project_id)
    return {"status": "deleted", "project_id": project_id}
