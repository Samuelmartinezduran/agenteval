"""Agregación ponderada de las tres dimensiones en una puntuación 0-100."""

from __future__ import annotations

# Pesos definidos en el plan. Suman 1.0. Centralizados aquí para facilitar
# ajustes y contribuciones.
WEIGHTS = {
    "tool_accuracy": 0.40,
    "response_quality": 0.40,
    "safety": 0.20,
}


def weighted_score(tool_accuracy: float, response_quality: float, safety: float) -> float:
    """Combina las tres dimensiones según :data:`WEIGHTS`. Devuelve 0-100."""

    total = (
        tool_accuracy * WEIGHTS["tool_accuracy"]
        + response_quality * WEIGHTS["response_quality"]
        + safety * WEIGHTS["safety"]
    )
    return round(total, 2)
