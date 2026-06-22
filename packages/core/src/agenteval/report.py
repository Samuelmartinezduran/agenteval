"""Renderizado de resultados: tabla rich para humanos y dict JSON para CI/API."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.table import Table

from .models import RunResult


def _color(score: float) -> str:
    if score >= 80:
        return "green"
    if score >= 50:
        return "yellow"
    return "red"


def render_table(run: RunResult, console: Console | None = None) -> None:
    """Imprime una tabla con la puntuación por caso y por dimensión."""

    console = console or Console()
    table = Table(title=f"agenteval · {run.suite}")
    table.add_column("Caso", style="bold")
    table.add_column("Tool acc.", justify="right")
    table.add_column("Quality", justify="right")
    table.add_column("Safety", justify="right")
    table.add_column("Score", justify="right")

    for r in run.results:
        name = r.case_name if not r.error else f"{r.case_name} [red](error)[/red]"
        table.add_row(
            name,
            f"{r.tool_accuracy:.0f}",
            f"{r.response_quality:.0f}",
            f"{r.safety:.0f}",
            f"[{_color(r.score)}]{r.score:.1f}[/{_color(r.score)}]",
        )

    table.add_section()
    table.add_row(
        "[bold]PROMEDIO[/bold]",
        f"{run.avg_tool_accuracy:.0f}",
        f"{run.avg_response_quality:.0f}",
        f"{run.avg_safety:.0f}",
        f"[{_color(run.avg_score)}]{run.avg_score:.1f}[/{_color(run.avg_score)}]",
    )
    console.print(table)

    errors = [r for r in run.results if r.error]
    if errors:
        console.print("\n[red]Errores:[/red]")
        for r in errors:
            console.print(f"  • {r.case_name}: {r.error}")


def to_dict(run: RunResult) -> dict[str, Any]:
    """Serializa un :class:`RunResult` a dict (para --json y para la API)."""

    return {
        "suite": run.suite,
        "summary": {
            "tool_accuracy": run.avg_tool_accuracy,
            "response_quality": run.avg_response_quality,
            "safety": run.avg_safety,
            "score": run.avg_score,
        },
        "results": [r.model_dump() for r in run.results],
    }
