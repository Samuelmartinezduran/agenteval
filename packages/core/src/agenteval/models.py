"""Modelos de dominio de agenteval.

Estos modelos pydantic son la fuente de verdad para la configuración de una
evaluación y para sus resultados. La librería core, la CLI y la API REST
comparten exactamente estas estructuras.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

# ---------------------------------------------------------------------------
# Configuración del agente a evaluar (contrato HTTP OpenAI-compatible).
# ---------------------------------------------------------------------------


class AgentConfig(BaseModel):
    """Cómo contactar con el agente bajo evaluación.

    agenteval envía un POST con ``{"messages": [...], "tools": [...]}`` y espera
    una respuesta estilo OpenAI (``choices[0].message`` con ``content`` y/o
    ``tool_calls``).
    """

    url: str
    method: str = "POST"
    headers: dict[str, str] = Field(default_factory=dict)
    timeout: float = 30.0


# ---------------------------------------------------------------------------
# Definición de casos de prueba.
# ---------------------------------------------------------------------------


class ToolDefinition(BaseModel):
    """Definición de una tool que se ofrece al agente para un caso."""

    name: str
    description: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)


class ExpectedBehavior(BaseModel):
    """Comportamiento esperado en cuanto a tool calling.

    - ``tool=None`` significa que el agente NO debería invocar ninguna tool.
    - ``params`` se compara contra los argumentos de la tool invocada.
    """

    tool: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class TestCase(BaseModel):
    __test__ = False  # no es una clase de test de pytest

    name: str
    input: str
    tools: list[ToolDefinition] = Field(default_factory=list)
    expected: ExpectedBehavior = Field(default_factory=ExpectedBehavior)
    quality_rubric: str | None = None
    safety_focus: str | None = None


class TestSuite(BaseModel):
    __test__ = False  # no es una clase de test de pytest

    suite: str
    description: str = ""
    agent: AgentConfig
    cases: list[TestCase]

    @model_validator(mode="after")
    def _non_empty(self) -> TestSuite:
        if not self.cases:
            raise ValueError("La suite no contiene casos de prueba.")
        return self


# ---------------------------------------------------------------------------
# Respuesta normalizada del agente.
# ---------------------------------------------------------------------------


class ToolCall(BaseModel):
    """Una tool call normalizada a partir de la respuesta del agente."""

    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Respuesta del agente normalizada desde el formato OpenAI."""

    content: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Resultados de evaluación.
# ---------------------------------------------------------------------------


class CaseResult(BaseModel):
    """Resultado de evaluar un único caso (puntuaciones 0-100)."""

    case_name: str
    tool_accuracy: float
    response_quality: float
    safety: float
    score: float  # total ponderado 0-100
    reasoning: str = ""  # razonamiento del juez LLM
    agent_content: str = ""
    agent_tool_calls: list[ToolCall] = Field(default_factory=list)
    error: str | None = None  # poblado si el caso falló al ejecutarse


class RunResult(BaseModel):
    """Resultado agregado de ejecutar una suite completa."""

    suite: str
    results: list[CaseResult]

    @property
    def avg_tool_accuracy(self) -> float:
        return _avg(r.tool_accuracy for r in self.results)

    @property
    def avg_response_quality(self) -> float:
        return _avg(r.response_quality for r in self.results)

    @property
    def avg_safety(self) -> float:
        return _avg(r.safety for r in self.results)

    @property
    def avg_score(self) -> float:
        return _avg(r.score for r in self.results)


def _avg(values) -> float:
    values = list(values)
    return round(sum(values) / len(values), 2) if values else 0.0
