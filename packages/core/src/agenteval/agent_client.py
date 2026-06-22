"""Cliente HTTP para hablar con el agente bajo evaluación.

El agente debe exponer un endpoint OpenAI-compatible: recibe
``{"messages": [...], "tools": [...]}`` y devuelve una respuesta con
``choices[0].message`` (``content`` y/o ``tool_calls``).
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from .models import AgentConfig, AgentResponse, TestCase, ToolCall


def _build_payload(case: TestCase) -> dict[str, Any]:
    """Construye el cuerpo de la petición en formato OpenAI."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": {
                    "type": "object",
                    "properties": t.parameters,
                },
            },
        }
        for t in case.tools
    ]
    payload: dict[str, Any] = {"messages": [{"role": "user", "content": case.input}]}
    if tools:
        payload["tools"] = tools
    return payload


def _parse_arguments(raw: Any) -> dict[str, Any]:
    """Los argumentos OpenAI llegan como string JSON; los normalizamos a dict."""

    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def normalize_response(data: dict[str, Any]) -> AgentResponse:
    """Convierte una respuesta OpenAI-compatible en :class:`AgentResponse`."""

    choices = data.get("choices") or []
    if not choices:
        return AgentResponse()

    message = choices[0].get("message", {}) or {}
    content = message.get("content") or ""

    tool_calls: list[ToolCall] = []
    for call in message.get("tool_calls") or []:
        fn = call.get("function", {}) or {}
        name = fn.get("name")
        if name:
            tool_calls.append(ToolCall(name=name, arguments=_parse_arguments(fn.get("arguments"))))

    return AgentResponse(content=content, tool_calls=tool_calls)


async def call_agent(config: AgentConfig, case: TestCase) -> AgentResponse:
    """Ejecuta un caso contra el agente y normaliza la respuesta.

    Lanza :class:`httpx.HTTPError` en fallos de red/HTTP; el runner los captura.
    """

    payload = _build_payload(case)
    async with httpx.AsyncClient(timeout=config.timeout) as client:
        resp = await client.request(
            config.method,
            config.url,
            json=payload,
            headers=config.headers,
        )
        resp.raise_for_status()
        return normalize_response(resp.json())
