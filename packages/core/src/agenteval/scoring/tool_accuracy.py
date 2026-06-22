"""Puntuación determinista de tool accuracy (0-100).

Reglas (documentadas para que sean fáciles de ajustar/contribuir):

- Se espera tool y el agente la llama con los params esperados -> 100
- Se espera tool y el agente la llama pero con params incorrectos/incompletos -> 50
- Se espera tool y el agente llama a otra / a ninguna -> 0
- NO se espera ninguna tool (expected.tool is None):
    - el agente no llamó a ninguna -> 100
    - el agente llamó a alguna -> 0

El matching de params comprueba que cada key esperada esté presente y su valor
coincida tras normalizar (comparación case-insensitive y trim para strings).
"""

from __future__ import annotations

from typing import Any

from ..models import ExpectedBehavior, ToolCall

CORRECT_TOOL_WRONG_PARAMS = 50.0


def _normalize(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().lower()
    return value


def _params_match(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    for key, exp_value in expected.items():
        if key not in actual:
            return False
        if _normalize(actual[key]) != _normalize(exp_value):
            return False
    return True


def score_tool_accuracy(expected: ExpectedBehavior, tool_calls: list[ToolCall]) -> float:
    # Caso "no debería llamar a ninguna tool".
    if expected.tool is None:
        return 100.0 if not tool_calls else 0.0

    matching = [c for c in tool_calls if c.name == expected.tool]
    if not matching:
        return 0.0

    if any(_params_match(expected.params, c.arguments) for c in matching):
        return 100.0
    return CORRECT_TOOL_WRONG_PARAMS
