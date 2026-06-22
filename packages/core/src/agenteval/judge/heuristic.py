"""Juez heurístico sin LLM, para demos y CI sin clave de API.

No sustituye a un juez LLM real: solo aplica reglas simples y deterministas.
Útil para probar agenteval rápidamente o para CI que solo quiere fijarse en la
dimensión determinista (tool accuracy) sin coste ni dependencias externas.
"""

from __future__ import annotations

from ..models import AgentResponse, TestCase
from .base import Judge, QualityVerdict, SafetyVerdict


class HeuristicJudge(Judge):
    def score_quality(self, case: TestCase, response: AgentResponse) -> QualityVerdict:
        if response.tool_calls or response.content.strip():
            return QualityVerdict(score=100.0, reasoning="Respuesta presente (heurístico).")
        return QualityVerdict(score=0.0, reasoning="Respuesta vacía (heurístico).")

    def score_safety(self, case: TestCase, response: AgentResponse) -> SafetyVerdict:
        # Sin LLM no podemos juzgar safety de verdad: devolvemos un valor neutro.
        return SafetyVerdict(score=100.0, reasoning="Safety no evaluada sin LLM (heurístico).")
