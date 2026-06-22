"""Endpoints para lanzar y consultar ejecuciones de evaluación."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .. import models, schemas, service
from ..db import get_db

router = APIRouter(prefix="/runs", tags=["runs"])


# Endpoint síncrono: FastAPI lo ejecuta en un threadpool, así el runner del core
# (que usa asyncio.run internamente) corre sin chocar con el event loop.
@router.post("", response_model=schemas.EvalRunDetail, status_code=201)
def create_run(payload: schemas.RunCreate, db: Session = Depends(get_db)):
    suite = db.get(models.Suite, payload.suite_id)
    if not suite:
        raise HTTPException(404, "Suite no encontrada")
    return service.execute_run(db, suite)


@router.get("", response_model=list[schemas.EvalRunOut])
def list_runs(db: Session = Depends(get_db)):
    return db.scalars(select(models.EvalRun).order_by(models.EvalRun.id.desc())).all()


@router.get("/{run_id}", response_model=schemas.EvalRunDetail)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.scalars(
        select(models.EvalRun)
        .where(models.EvalRun.id == run_id)
        .options(selectinload(models.EvalRun.results))
    ).first()
    if not run:
        raise HTTPException(404, "Run no encontrado")
    return run
