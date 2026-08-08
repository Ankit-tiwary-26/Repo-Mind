import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.agents import orchestrator
from app import db

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatRequest(BaseModel):
    project_id: str
    question: str


@router.post("")
def ask(req: ChatRequest):
    project = db.get_project(req.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found. Ingest it first.")
    local_path = project.get("local_path")
    try:
        result = orchestrator.handle(req.project_id, req.question, local_path=local_path)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    # Save to history
    db.save_chat(req.project_id, req.question, result["answer"], result["agent"])
    return result


@router.post("/stream")
async def ask_stream(req: ChatRequest):
    project = db.get_project(req.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found. Ingest it first.")
    local_path = project.get("local_path")

    async def event_generator():
        try:
            full_answer = ""
            for agent_name, chunk in orchestrator.handle_stream(req.project_id, req.question, local_path=local_path):
                full_answer += chunk
                yield {
                    "event": "chunk",
                    "data": json.dumps({"agent": agent_name, "chunk": chunk}),
                }
            # Save complete answer to history
            db.save_chat(req.project_id, req.question, full_answer, agent_name)
            yield {
                "event": "done",
                "data": json.dumps({"agent": agent_name, "answer": full_answer}),
            }
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }

    return EventSourceResponse(event_generator())


@router.get("/{project_id}/history")
def get_history(project_id: str, limit: int = 50):
    if not db.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return db.get_chat_history(project_id, limit=limit)
