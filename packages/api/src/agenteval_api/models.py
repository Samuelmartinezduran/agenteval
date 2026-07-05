"""Modelos SQLAlchemy (tablas) de la API.

Las suites se guardan con su definición completa en JSON (incluye los casos),
ya que se autoran en YAML; esto evita normalizar en exceso. Cada ejecución
(:class:`EvalRun`) tiene un resultado por caso (:class:`EvalResult`).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(String(500))
    method: Mapped[str] = mapped_column(String(10), default="POST")
    headers: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Suite(Base):
    __tablename__ = "suites"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    # Definición completa de la suite (TestSuite serializado, con sus casos).
    definition: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    suite_id: Mapped[int | None] = mapped_column(ForeignKey("suites.id"), nullable=True)
    suite_name: Mapped[str] = mapped_column(String(200))
    # Ciclo de vida del run: se crea "running" y el background task lo cierra.
    status: Mapped[str] = mapped_column(String(20), default="running")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)  # fallo a nivel de run
    avg_tool_accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    avg_response_quality: Mapped[float] = mapped_column(Float, default=0.0)
    avg_safety: Mapped[float] = mapped_column(Float, default=0.0)
    avg_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    results: Mapped[list[EvalResult]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class EvalResult(Base):
    __tablename__ = "eval_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("eval_runs.id"))
    case_name: Mapped[str] = mapped_column(String(300))
    tool_accuracy: Mapped[float] = mapped_column(Float)
    response_quality: Mapped[float] = mapped_column(Float)
    safety: Mapped[float] = mapped_column(Float)
    score: Mapped[float] = mapped_column(Float)
    reasoning: Mapped[str] = mapped_column(Text, default="")
    agent_content: Mapped[str] = mapped_column(Text, default="")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    run: Mapped[EvalRun] = relationship(back_populates="results")
