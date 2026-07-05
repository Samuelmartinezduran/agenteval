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


def render_baseline_diff(
    run: RunResult, baseline: dict[str, Any], console: Console | None = None
) -> None:
    """Compara el run actual contra un JSON previo (formato de :func:`to_dict`)."""

    console = console or Console()
    base_scores = {r["case_name"]: r["score"] for r in baseline.get("results", [])}
    base_avg = baseline.get("summary", {}).get("score", 0.0)

    def _delta(value: float) -> str:
        color = "green" if value > 0 else "red" if value < 0 else "dim"
        return f"[{color}]{value:+.1f}[/{color}]"

    table = Table(title=f"agenteval · {run.suite} vs baseline")
    table.add_column("Caso", style="bold")
    table.add_column("Baseline", justify="right")
    table.add_column("Actual", justify="right")
    table.add_column("Δ", justify="right")

    for r in run.results:
        if r.case_name in base_scores:
            base = base_scores.pop(r.case_name)
            table.add_row(r.case_name, f"{base:.1f}", f"{r.score:.1f}", _delta(r.score - base))
        else:
            table.add_row(r.case_name, "[dim]—[/dim]", f"{r.score:.1f}", "[dim]nuevo[/dim]")
    for name, base in base_scores.items():
        table.add_row(name, f"{base:.1f}", "[dim]—[/dim]", "[dim]eliminado[/dim]")

    table.add_section()
    table.add_row(
        "[bold]PROMEDIO[/bold]",
        f"{base_avg:.1f}",
        f"{run.avg_score:.1f}",
        _delta(run.avg_score - base_avg),
    )
    console.print(table)


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
