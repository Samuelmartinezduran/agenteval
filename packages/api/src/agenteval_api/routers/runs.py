"""Endpoints para lanzar y consultar ejecuciones de evaluación."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .. import models, schemas, service
from ..db import get_db

router = APIRouter(prefix="/runs", tags=["runs"])


# La suite se ejecuta en un BackgroundTask (función síncrona -> threadpool, así
# el asyncio.run interno del runner no choca con el event loop). La respuesta
# vuelve de inmediato con el run en estado "running"; el cliente hace polling.
@router.post("", response_model=schemas.EvalRunDetail, status_code=201)
def create_run(
    payload: schemas.RunCreate, background: BackgroundTasks, db: Session = Depends(get_db)
):
    suite = db.get(models.Suite, payload.suite_id)
    if not suite:
        raise HTTPException(404, "Suite no encontrada")
    run = service.create_run(db, suite)
    background.add_task(service.execute_run_background, run.id, suite.definition)
    return run


@router.get("", response_model=list[schemas.EvalRunOut])
def list_runs(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return db.scalars(
        select(models.EvalRun).order_by(models.EvalRun.id.desc()).limit(limit).offset(offset)
    ).all()


def _get_run_with_results(db: Session, run_id: int) -> models.EvalRun:
    run = db.scalars(
        select(models.EvalRun)
        .where(models.EvalRun.id == run_id)
        .options(selectinload(models.EvalRun.results))
    ).first()
    if not run:
        raise HTTPException(404, f"Run {run_id} no encontrado")
    return run


@router.get("/{run_id}", response_model=schemas.EvalRunDetail)
def get_run(run_id: int, db: Session = Depends(get_db)):
    return _get_run_with_results(db, run_id)


@router.get("/{run_id}/compare/{other_id}", response_model=schemas.RunComparison)
def compare_runs(run_id: int, other_id: int, db: Session = Depends(get_db)):
    run_a = _get_run_with_results(db, run_id)
    run_b = _get_run_with_results(db, other_id)
    return service.compare_runs(run_a, run_b)
