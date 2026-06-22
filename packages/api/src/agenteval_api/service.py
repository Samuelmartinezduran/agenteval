"""Lógica de negocio: ejecutar una suite reutilizando el runner del core.

La API no reimplementa scoring: invoca ``agenteval.run_suite_sync`` y persiste
el resultado. Es la única fuente de verdad de evaluación.
"""

from __future__ import annotations

from agenteval import TestSuite, run_suite_sync
from agenteval.judge.base import Judge
from sqlalchemy.orm import Session

from . import models
from .config import settings


def _load_judge() -> Judge:
    if settings.judge == "openai":
        from agenteval.judge.openai_judge import OpenAIJudge

        return OpenAIJudge()
    from agenteval.judge.heuristic import HeuristicJudge

    return HeuristicJudge()


def execute_run(db: Session, suite_row: models.Suite) -> models.EvalRun:
    """Ejecuta la suite contra su agente y persiste run + resultados."""

    suite = TestSuite.model_validate(suite_row.definition)
    result = run_suite_sync(suite, _load_judge())

    run = models.EvalRun(
        suite_id=suite_row.id,
        suite_name=result.suite,
        avg_tool_accuracy=result.avg_tool_accuracy,
        avg_response_quality=result.avg_response_quality,
        avg_safety=result.avg_safety,
        avg_score=result.avg_score,
        results=[
            models.EvalResult(
                case_name=r.case_name,
                tool_accuracy=r.tool_accuracy,
                response_quality=r.response_quality,
                safety=r.safety,
                score=r.score,
                reasoning=r.reasoning,
                agent_content=r.agent_content,
                error=r.error,
            )
            for r in result.results
        ],
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run
