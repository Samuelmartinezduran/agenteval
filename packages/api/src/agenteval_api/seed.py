"""Seed opcional de una suite de ejemplo al arrancar.

Pensado para que `docker compose up` deje el dashboard listo: si está
configurado ``AGENTEVAL_SEED_SUITE`` y la BD no tiene suites, carga esa suite
(reutilizando el loader del core) y la inserta.
"""

from __future__ import annotations

from agenteval import load_suite
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .config import settings


def maybe_seed(db: Session) -> None:
    if not settings.seed_suite:
        return
    if db.scalar(select(models.Suite.id).limit(1)) is not None:
        return  # ya hay datos; no duplicar

    suite = load_suite(settings.seed_suite)
    if settings.seed_agent_url:
        suite.agent.url = settings.seed_agent_url

    db.add(
        models.Suite(
            name=suite.suite,
            description=suite.description,
            definition=suite.model_dump(),
        )
    )
    db.commit()
