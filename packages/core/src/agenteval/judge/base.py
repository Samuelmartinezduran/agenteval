"""Interfaz abstracta de juez LLM.

El juez puntúa las dimensiones no deterministas (response quality y safety).
Es pluggable: implementar un nuevo proveedor es subclasear :class:`Judge` sin
tocar el runner. La implementación por defecto es ``OpenAIJudge``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from ..models import AgentResponse, TestCase


class QualityVerdict(BaseModel):
    score: float = Field(ge=0, le=100)
    reasoning: str = ""


class SafetyVerdict(BaseModel):
    score: float = Field(ge=0, le=100)
    reasoning: str = ""


class Judge(ABC):
    """Contrato de un juez LLM."""

    @abstractmethod
    def score_quality(self, case: TestCase, response: AgentResponse) -> QualityVerdict:
        """Puntúa lo buena que es la respuesta del agente (0-100)."""

    @abstractmethod
    def score_safety(self, case: TestCase, response: AgentResponse) -> SafetyVerdict:
        """Puntúa si el agente se mantuvo en contexto y evitó salidas dañinas (0-100)."""

    def score_case(
        self, case: TestCase, response: AgentResponse
    ) -> tuple[QualityVerdict, SafetyVerdict]:
        """Puntúa ambas dimensiones de un caso.

        Las implementaciones pueden sobrescribirlo para resolver las dos
        dimensiones en una sola llamada al proveedor (más barato/rápido).
        """

        return self.score_quality(case, response), self.score_safety(case, response)
