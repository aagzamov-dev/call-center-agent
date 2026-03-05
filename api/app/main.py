"""FastAPI application entry point — mounts all routers, creates tables on startup."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.engine import engine
from app.db.models import Base

from app.routers import (
    alerts,
    incidents,
    timeline,
    agent,
    human,
    tickets,
    messages,
    email,
    chat,
    voice,
    kb,
    topology,
    tools,
    demo,
    ws,
)


# Ensure storage directories exist before StaticFiles mount
Path("storage").mkdir(exist_ok=True)
Path("storage/audio").mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Incident AI Agent API",
    description="Demo callcenter/incident management system with AI-powered investigation agent",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for generated audio
app.mount("/static/audio", StaticFiles(directory="storage/audio"), name="audio")

# Mount all routers
app.include_router(alerts.router)
app.include_router(incidents.router)
app.include_router(timeline.router)
app.include_router(agent.router)
app.include_router(human.router)
app.include_router(tickets.router)
app.include_router(messages.router)
app.include_router(email.router)
app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(kb.router)
app.include_router(topology.router)
app.include_router(tools.router)
app.include_router(demo.router)
app.include_router(ws.router)


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "service": "Incident AI Agent API"}


@app.get("/health", tags=["health"])
async def health():
    return {"status": "healthy"}
