"""Aplicación FastAPI de agenteval."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import service
from .config import settings
from .db import SessionLocal
from .routers import agents, runs, suites
from .seed import maybe_seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        # Cierra runs que quedaron 'running' si la API se reinició a mitad.
        failed = service.fail_orphaned_runs(db)
        if failed:
            print(f"[agenteval] {failed} run(s) huérfano(s) marcados como fallidos")
        maybe_seed(db)
    except Exception as exc:  # noqa: BLE001 - el arranque nunca debe tumbar la API
        print(f"[agenteval] arranque parcial: {exc}")
    finally:
        db.close()
    yield


app = FastAPI(
    title="agenteval API",
    version="0.1.0",
    description="Lanza evaluaciones de agentes LLM y consulta sus resultados.",
    lifespan=lifespan,
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
