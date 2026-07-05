"""Lógica de negocio: ejecutar una suite reutilizando el runner del core.

La API no reimplementa scoring: invoca ``agenteval.run_suite_sync`` y persiste
el resultado. Es la única fuente de verdad de evaluación.

Los runs se ejecutan en background: ``create_run`` inserta la fila en estado
"running" y ``execute_run_background`` (lanzado como BackgroundTask) la
completa con su propia sesión de BD.
"""

from __future__ import annotations

from datetime import datetime, timezone

from agenteval import TestSuite, run_suite_sync
from agenteval.judge.base import Judge
from sqlalchemy.orm import Session

from . import models, schemas
from .config import settings
from .db import SessionLocal


def _load_judge() -> Judge:
    if settings.judge == "openai":
        from agenteval.judge.openai_judge import OpenAIJudge

        return OpenAIJudge()
    from agenteval.judge.heuristic import HeuristicJudge

    return HeuristicJudge()


def create_run(db: Session, suite_row: models.Suite) -> models.EvalRun:
    """Inserta un run en estado "running"; el background task lo completará."""

    run = models.EvalRun(
        suite_id=suite_row.id,
        suite_name=suite_row.name,
        status="running",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def execute_run_background(run_id: int, definition: dict) -> None:
    """Ejecuta la suite y cierra el run. Corre fuera de la request, con su propia sesión."""

    db = SessionLocal()
    try:
        run = db.get(models.EvalRun, run_id)
        if run is None:
            return
        try:
            suite = TestSuite.model_validate(definition)
            result = run_suite_sync(suite, _load_judge(), concurrency=settings.concurrency)
        except Exception as exc:  # noqa: BLE001 - el fallo se persiste, no se propaga
            run.status = "failed"
            run.error = str(exc)
        else:
            run.status = "completed"
            run.suite_name = result.suite
            run.avg_tool_accuracy = result.avg_tool_accuracy
            run.avg_response_quality = result.avg_response_quality
            run.avg_safety = result.avg_safety
            run.avg_score = result.avg_score
            run.results = [
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
            ]
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()


def compare_runs(run_a: models.EvalRun, run_b: models.EvalRun) -> schemas.RunComparison:
    """Diff por caso entre dos runs (matching por case_name)."""

    def _scores(r: models.EvalResult) -> schemas.CaseScores:
        return schemas.CaseScores(
            tool_accuracy=r.tool_accuracy,
            response_quality=r.response_quality,
            safety=r.safety,
            score=r.score,
        )

    by_name_b = {r.case_name: r for r in run_b.results}
    cases: list[schemas.CaseComparison] = []
    for res_a in run_a.results:
        res_b = by_name_b.pop(res_a.case_name, None)
        cases.append(
            schemas.CaseComparison(
                case_name=res_a.case_name,
                a=_scores(res_a),
                b=_scores(res_b) if res_b else None,
                delta_score=round(res_b.score - res_a.score, 2) if res_b else None,
            )
        )
    for res_b in by_name_b.values():
        cases.append(
            schemas.CaseComparison(case_name=res_b.case_name, a=None, b=_scores(res_b), delta_score=None)
        )

    return schemas.RunComparison(
        run_a=schemas.EvalRunOut.model_validate(run_a),
        run_b=schemas.EvalRunOut.model_validate(run_b),
        cases=cases,
    )
