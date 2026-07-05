"""Tests del OpenAIJudge con un cliente fake: retry y llamada combinada."""

from __future__ import annotations

import json
from types import SimpleNamespace

import httpx
import openai
import pytest

from agenteval.judge import openai_judge
from agenteval.judge.openai_judge import OpenAIJudge
from agenteval.models import AgentResponse, TestCase


class FakeClient:
    """Imita client.chat.completions.create devolviendo respuestas encoladas."""

    def __init__(self, outcomes: list):
        self._outcomes = list(outcomes)
        self.calls = 0
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls += 1
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        message = SimpleNamespace(content=json.dumps(outcome))
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def _connection_error() -> openai.APIConnectionError:
    return openai.APIConnectionError(request=httpx.Request("POST", "http://api"))


def _case() -> TestCase:
    return TestCase(name="c", input="¿Qué tiempo hace en Madrid?")


_COMBINED = {
    "quality": {"score": 80, "reasoning": "útil"},
    "safety": {"score": 100, "reasoning": "en contexto"},
}


def test_score_case_single_call_parses_both_dimensions():
    client = FakeClient([_COMBINED])
    judge = OpenAIJudge(model="test-model", client=client)

    quality, safety = judge.score_case(_case(), AgentResponse(content="Soleado"))

    assert client.calls == 1  # una sola llamada LLM para ambas dimensiones
    assert quality.score == 80.0 and quality.reasoning == "útil"
    assert safety.score == 100.0 and safety.reasoning == "en contexto"


def test_score_case_clamps_and_tolerates_missing_keys():
    client = FakeClient([{"quality": {"score": 150}}])
    judge = OpenAIJudge(model="test-model", client=client)

    quality, safety = judge.score_case(_case(), AgentResponse(content="x"))

    assert quality.score == 100.0  # clamp a [0, 100]
    assert safety.score == 0.0  # dimensión ausente -> 0, sin explotar


def test_score_quality_and_safety_delegate_to_single_call():
    # Cada método por dimensión hace UNA llamada combinada y devuelve su mitad.
    judge = OpenAIJudge(model="test-model", client=FakeClient([_COMBINED]))
    assert judge.score_quality(_case(), AgentResponse(content="x")).score == 80.0

    judge = OpenAIJudge(model="test-model", client=FakeClient([_COMBINED]))
    assert judge.score_safety(_case(), AgentResponse(content="x")).score == 100.0


def test_retry_recovers_after_transient_errors(monkeypatch):
    monkeypatch.setattr(openai_judge.time, "sleep", lambda s: None)
    client = FakeClient([_connection_error(), _connection_error(), _COMBINED])
    judge = OpenAIJudge(model="test-model", client=client)

    quality, _ = judge.score_case(_case(), AgentResponse(content="Soleado"))

    assert client.calls == 3
    assert quality.score == 80.0


def test_retry_gives_up_after_max_attempts(monkeypatch):
    monkeypatch.setattr(openai_judge.time, "sleep", lambda s: None)
    client = FakeClient([_connection_error()] * 3)
    judge = OpenAIJudge(model="test-model", client=client)

    with pytest.raises(openai.APIConnectionError):
        judge.score_case(_case(), AgentResponse(content="x"))
    assert client.calls == 3
