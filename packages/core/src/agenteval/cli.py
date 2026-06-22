"""CLI de agenteval (Typer).

Comandos:
    agenteval run <suite.yaml>       Ejecuta una suite y muestra una tabla.
    agenteval validate <suite.yaml>  Valida el YAML sin ejecutar nada.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import typer
from rich.console import Console

from .loader import SuiteLoadError, load_suite
from .report import render_table, to_dict
from .runner import run_suite_sync

app = typer.Typer(help="Evalúa agentes LLM con function calling / tool use.", no_args_is_help=True)
console = Console()
err_console = Console(stderr=True)


def _load_judge(kind: str):
    """Carga el juez indicado. 'openai' (default) o 'heuristic' (sin LLM)."""

    if kind == "heuristic":
        from .judge.heuristic import HeuristicJudge

        return HeuristicJudge()

    from .judge.openai_judge import OpenAIJudge

    return OpenAIJudge()


@app.command()
def run(
    suite_path: Path = typer.Argument(..., help="Ruta al fichero YAML de la suite."),
    json_output: bool = typer.Option(False, "--json", help="Imprime los resultados como JSON."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Guarda el JSON en fichero."),
    fail_under: float | None = typer.Option(
        None, "--fail-under", help="Sale con código 1 si el score medio es menor (útil en CI)."
    ),
    judge_kind: str = typer.Option(
        os.environ.get("AGENTEVAL_JUDGE", "openai"),
        "--judge",
        help="Juez a usar: 'openai' (GPT-4o-mini) o 'heuristic' (sin LLM, para demos/CI).",
    ),
):
    """Ejecuta una suite contra su agente y puntúa cada caso."""

    try:
        suite = load_suite(suite_path)
    except SuiteLoadError as exc:
        err_console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=2) from exc

    try:
        judge = _load_judge(judge_kind)
    except Exception as exc:  # noqa: BLE001 - feedback claro al usuario
        err_console.print(f"[red]No se pudo inicializar el juez LLM: {exc}[/red]")
        err_console.print("[yellow]¿Has definido OPENAI_API_KEY?[/yellow]")
        raise typer.Exit(code=2) from exc

    result = run_suite_sync(suite, judge)
    data = to_dict(result)

    if output:
        output.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        console.print(f"[green]Resultados guardados en {output}[/green]")

    if json_output:
        console.print_json(data=data)
    else:
        render_table(result)

    if fail_under is not None and result.avg_score < fail_under:
        err_console.print(
            f"[red]Score medio {result.avg_score:.1f} < umbral {fail_under:.1f}[/red]"
        )
        raise typer.Exit(code=1)


@app.command()
def validate(suite_path: Path = typer.Argument(..., help="Ruta al fichero YAML de la suite.")):
    """Valida una suite YAML sin ejecutarla."""

    try:
        suite = load_suite(suite_path)
    except SuiteLoadError as exc:
        err_console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=2) from exc

    console.print(
        f"[green]✓[/green] Suite '[bold]{suite.suite}[/bold]' válida "
        f"({len(suite.cases)} caso(s))."
    )


if __name__ == "__main__":
    app()
