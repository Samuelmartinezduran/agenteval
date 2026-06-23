"""Orquestador de una evaluación.

Es la única fuente de verdad del proceso de evaluación: la CLI y la API REST
lo invocan en lugar de reimplementar la lógica de scoring.
"""

from __future__ import annotations

import asyncio

import httpx

from .agent_client import call_agent
from .judge.base import Judge
from .models import AgentResponse, CaseResult, RunResult, TestCase, TestSuite
from .scoring.aggregate import weighted_score
from .scoring.tool_accuracy import score_tool_accuracy


async def _run_case(suite: TestSuite, case: TestCase, judge: Judge) -> CaseResult:
    try:
        response = await call_agent(suite.agent, case)
    except (httpx.HTTPError, ValueError) as exc:
        return CaseResult(
            case_name=case.name,
            tool_accuracy=0.0,
            response_quality=0.0,
            safety=0.0,
            score=0.0,
            error=f"Fallo al contactar con el agente: {exc}",
        )

    tool_accuracy = score_tool_accuracy(case.expected, response.tool_calls)

    # El juez LLM es síncrono; lo ejecutamos en un hilo para no bloquear el loop.
    # Si falla (rate limit, key inválida, red), marcamos el caso como error en
    # lugar de tumbar todo el run y perder el resto de resultados.
    try:
        quality, safety = await asyncio.gather(
            asyncio.to_thread(judge.score_quality, case, response),
            asyncio.to_thread(judge.score_safety, case, response),
        )
    except Exception as exc:
        return CaseResult(
            case_name=case.name,
            tool_accuracy=tool_accuracy,
            response_quality=0.0,
            safety=0.0,
            score=weighted_score(tool_accuracy, 0.0, 0.0),
            agent_content=response.content,
            agent_tool_calls=response.tool_calls,
            error=f"Fallo del juez: {exc}",
        )

    reasoning = _merge_reasoning(quality.reasoning, safety.reasoning)
    return CaseResult(
        case_name=case.name,
        tool_accuracy=tool_accuracy,
        response_quality=quality.score,
        safety=safety.score,
        score=weighted_score(tool_accuracy, quality.score, safety.score),
        reasoning=reasoning,
        agent_content=response.content,
        agent_tool_calls=response.tool_calls,
    )


def _merge_reasoning(quality: str, safety: str) -> str:
    parts = []
    if quality:
        parts.append(f"Quality: {quality}")
    if safety:
        parts.append(f"Safety: {safety}")
    return " | ".join(parts)


async def run_suite(suite: TestSuite, judge: Judge) -> RunResult:
    """Ejecuta todos los casos de la suite (concurrentemente) y agrega resultados."""

    results = await asyncio.gather(*(_run_case(suite, case, judge) for case in suite.cases))
    return RunResult(suite=suite.suite, results=list(results))


def run_suite_sync(suite: TestSuite, judge: Judge) -> RunResult:
    """Wrapper síncrono de :func:`run_suite` para CLI/API."""

    return asyncio.run(run_suite(suite, judge))


__all__ = ["run_suite", "run_suite_sync", "AgentResponse"]
