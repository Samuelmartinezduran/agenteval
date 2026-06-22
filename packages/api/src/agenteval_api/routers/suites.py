"""Endpoints para gestionar suites de prueba."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db

router = APIRouter(prefix="/suites", tags=["suites"])


@router.post("", response_model=schemas.SuiteOut, status_code=201)
def create_suite(payload: schemas.SuiteCreate, db: Session = Depends(get_db)):
    definition = payload.definition
    suite = models.Suite(
        name=definition.suite,
        description=definition.description,
        definition=definition.model_dump(),
    )
    db.add(suite)
    db.commit()
    db.refresh(suite)
    return suite


@router.get("", response_model=list[schemas.SuiteOut])
def list_suites(db: Session = Depends(get_db)):
    return db.scalars(select(models.Suite).order_by(models.Suite.id.desc())).all()


@router.get("/{suite_id}", response_model=schemas.SuiteOut)
def get_suite(suite_id: int, db: Session = Depends(get_db)):
    suite = db.get(models.Suite, suite_id)
    if not suite:
        raise HTTPException(404, "Suite no encontrada")
    return suite
