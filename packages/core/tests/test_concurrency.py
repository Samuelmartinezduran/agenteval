"""El runner nunca ejecuta más casos en paralelo que el límite de concurrencia."""

from __future__ import annotations

import asyncio

import pytest

from agenteval import runner
from agenteval.models import AgentConfig, AgentResponse, ExpectedBehavior, TestCase, TestSuite


def _suite(n_cases: int) -> TestSuite:
    return TestSuite(
        suite="concurrencia",
        agent=AgentConfig(url="http://unused"),
        cases=[
            TestCase(name=f"caso {i}", input="hola", expected=ExpectedBehavior(tool=None))
            for i in range(n_cases)
        ],
    )


@pytest.mark.parametrize("limit", [1, 3])
def test_concurrency_never_exceeds_limit(monkeypatch, stub_judge, limit):
    current = 0
    peak = 0

    async def fake_call_agent(agent, case):
        nonlocal current, peak
        current += 1
        peak = max(peak, current)
        await asyncio.sleep(0.01)  # da margen a que otros casos entren si pudieran
        current -= 1
        return AgentResponse(content="ok")

    monkeypatch.setattr(runner, "call_agent", fake_call_agent)

    result = runner.run_suite_sync(_suite(10), stub_judge, concurrency=limit)

    assert len(result.results) == 10
    assert peak <= limit
