"""Fixtures compartidas: un juez stub determinista para no llamar a OpenAI."""

from __future__ import annotations

import pytest

from agenteval.judge.base import Judge, QualityVerdict, SafetyVerdict
from agenteval.models import AgentResponse, TestCase


class StubJudge(Judge):
    """Juez determinista: puntúa quality según si hay contenido y safety fijo a 100.

    Permite testear runner/scoring sin depender de una API externa.
    """

    def score_quality(self, case: TestCase, response: AgentResponse) -> QualityVerdict:
        score = 90.0 if (response.content or response.tool_calls) else 0.0
        return QualityVerdict(score=score, reasoning="stub quality")

    def score_safety(self, case: TestCase, response: AgentResponse) -> SafetyVerdict:
        return SafetyVerdict(score=100.0, reasoning="stub safety")


@pytest.fixture
def stub_judge() -> StubJudge:
    return StubJudge()
