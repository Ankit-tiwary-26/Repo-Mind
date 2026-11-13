from starlette.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import repo, chat
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="RepoMind AI",
    description="AI assistant that understands your entire codebase",
    version="0.2.0",
    lifespan=lifespan,
)

app = CORSMiddleware(
    app=app,
    allow_origins=[
        "https://repo-mind-rho.vercel.app",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(repo.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}

