"""Esquemas pydantic de entrada/salida de la API."""

from __future__ import annotations

from datetime import datetime

from agenteval.models import TestSuite
from pydantic import BaseModel, ConfigDict


# --- Agent ---------------------------------------------------------------


class AgentCreate(BaseModel):
    name: str
    url: str
    method: str = "POST"
    headers: dict[str, str] = {}


class AgentOut(AgentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# --- Suite ---------------------------------------------------------------


class SuiteCreate(BaseModel):
    # Definición completa de la suite (mismo esquema que el YAML del core).
    definition: TestSuite


class SuiteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    definition: dict
    created_at: datetime


# --- Runs ----------------------------------------------------------------


class RunCreate(BaseModel):
    """Lanza una ejecución a partir de una suite ya guardada."""

    suite_id: int


class EvalResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_name: str
    tool_accuracy: float
    response_quality: float
    safety: float
    score: float
    reasoning: str
    agent_content: str
    error: str | None


class EvalRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    suite_id: int | None
    suite_name: str
    avg_tool_accuracy: float
    avg_response_quality: float
    avg_safety: float
    avg_score: float
    created_at: datetime


class EvalRunDetail(EvalRunOut):
    results: list[EvalResultOut]
