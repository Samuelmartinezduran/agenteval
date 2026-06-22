"""Aplicación FastAPI de agenteval."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import agents, runs, suites

app = FastAPI(
    title="agenteval API",
    version="0.1.0",
    description="Lanza evaluaciones de agentes LLM y consulta sus resultados.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router)
app.include_router(suites.router)
app.include_router(runs.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
