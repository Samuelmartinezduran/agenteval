# agenteval

[![CI](https://github.com/Samuelmartinezduran/agenteval/actions/workflows/ci.yml/badge.svg)](https://github.com/Samuelmartinezduran/agenteval/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Framework open source para evaluar agentes LLM con function calling / tool use.**

agenteval es **agnóstico**: funciona con cualquier agente que exponga un endpoint
HTTP compatible con OpenAI. Defines tus casos de prueba en YAML, los ejecutas
contra tu agente y obtienes una **puntuación por dimensión** (0-100) por cada caso,
desde la línea de comandos o desde un dashboard visual.

![Dashboard de agenteval](docs/dashboard.png)

> Detalle de una ejecución, con score por dimensión y el razonamiento del juez:
>
> ![Detalle de una ejecución](docs/run-detail.png)

```
┌──────────┐   POST {messages, tools}   ┌──────────────┐
│ agenteval │ ─────────────────────────▶ │   tu agente   │
│  runner   │ ◀───────────────────────── │  (HTTP/JSON)  │
└────┬─────┘   choices[].message          └──────────────┘
     │
     ▼  Tool accuracy · Response quality · Safety  →  Score 0-100
```

## Dimensiones de puntuación

Cada caso se puntúa de 0 a 100 combinando tres dimensiones:

| Dimensión          | Peso | Cómo se evalúa                                            |
| ------------------ | ---- | -------------------------------------------------------- |
| **Tool accuracy**  | 40%  | Determinista: ¿llamó a la tool correcta con los params correctos? |
| **Response quality**| 40% | Juez LLM (GPT-4o-mini por defecto, pluggable)            |
| **Safety**         | 20%  | Juez LLM: ¿se mantuvo en contexto y evitó salidas dañinas? |

## Quickstart (CLI, sin clave de API)

Requiere [uv](https://docs.astral.sh/uv/) y Python 3.10+.

```bash
make setup            # crea el entorno (uv sync)

# En una terminal: arranca el agente de juguete de ejemplo
make run-mock

# En otra: evalúa la suite de ejemplo con el juez heurístico (sin LLM)
make run-cli
```

Verás una tabla con la puntuación por dimensión de cada caso. Para usar el juez
LLM real, define `OPENAI_API_KEY` y quita `--judge heuristic`:

```bash
export OPENAI_API_KEY=sk-...
cd packages/core
# PYTHONPATH evita el bug de los .pth ocultos de uv en macOS (ver nota abajo).
PYTHONPATH=src uv run --no-sync python -m agenteval.cli run ../../examples/suites/weather-agent.yaml
```

Opciones útiles de `agenteval run`:

- `--concurrency N` — máximo de casos evaluados en paralelo (default 5, evita rate limits).
- `--output resultados.json` — guarda el run en JSON.
- `--baseline resultados.json` — compara contra un run previo y muestra el delta por caso
  (ideal para detectar regresiones en CI junto con `--fail-under`).
- `--fail-under 80` — sale con código 1 si el score medio no llega al umbral.

## Stack completo (API + dashboard) con Docker — un comando

```bash
docker compose up --build
```

Esto levanta todo y **deja el dashboard listo para usar**: incluye un agente de
juguete y precarga la suite de ejemplo automáticamente.

- Dashboard (React): http://localhost:5173 → pulsa **▶ weather-agent** y verás los scores
- API (FastAPI): http://localhost:8000 · docs en `/docs`

Los runs se ejecutan **en background**: `POST /runs` responde al instante con el run en
estado `running` y el dashboard hace polling hasta que pasa a `completed` (o `failed`).
Desde el detalle de un run puedes **compararlo** con otro run de la misma suite
(`GET /runs/{id}/compare/{other_id}`) para ver el delta de score por caso.

Por defecto usa el juez heurístico (sin coste). Para el juez real, crea un `.env`
con `OPENAI_API_KEY=...` y `AGENTEVAL_JUDGE=openai` antes de levantar el stack.

## El contrato del agente (OpenAI-compatible)

agenteval envía a tu agente un `POST` con:

```json
{ "messages": [{ "role": "user", "content": "..." }], "tools": [ ... ] }
```

y espera una respuesta estilo OpenAI:

```json
{ "choices": [ { "message": { "content": "...", "tool_calls": [ ... ] } } ] }
```

Cualquier agente que cumpla este contrato es evaluable sin adaptadores. Hay un
agente de ejemplo en [examples/mock_agent](examples/mock_agent/server.py).

## Formato de los casos de prueba (YAML)

```yaml
suite: weather-agent
description: Evalúa un agente de clima con function calling.
agent:
  url: http://localhost:9000
cases:
  - name: consulta de clima válida
    input: "¿Qué tiempo hace en Madrid?"
    tools:
      - name: get_weather
        parameters:
          city: { type: string }
    expected:
      tool: get_weather          # tool: null = no debería llamar a ninguna tool
      params: { city: Madrid }
    quality_rubric: "Debe consultar el clima de Madrid."
```

Los `params` esperados se comparan por igualdad (case-insensitive) o con matchers:

```yaml
expected:
  tool: get_weather
  params:
    city: { contains: madrid }   # el valor real debe contener el texto
    date: { regex: '^\d{4}-\d{2}-\d{2}$' }  # o casar con la regex
```

Valida una suite sin ejecutarla con `agenteval validate <suite.yaml>`.

## Arquitectura

Monorepo (workspace de uv):

- [packages/core](packages/core) — librería `agenteval` + CLI. Lógica de evaluación
  pura, sin base de datos. El **runner** es la única fuente de verdad del scoring.
- [packages/api](packages/api) — API REST (FastAPI + SQLAlchemy + Alembic) que
  reutiliza el runner del core y persiste los resultados.
- [frontend](frontend) — dashboard React + Vite + Tailwind.
- [examples](examples) — agente de juguete y suite de ejemplo.

El **juez** es una interfaz abstracta ([judge/base.py](packages/core/src/agenteval/judge/base.py));
añadir un proveedor nuevo es escribir una subclase. Incluye `OpenAIJudge`
(por defecto) y `HeuristicJudge` (sin LLM, para demos/CI).

## Desarrollo

```bash
make test     # tests de core + api
make lint     # ruff
```

> **Nota (macOS):** uv marca los `.pth` de los editable installs como ocultos y
> las versiones recientes de CPython los ignoran, lo que rompería `uv run`.
> `make sync` lo corrige automáticamente (en Linux es un no-op). Los tests no
> dependen del editable: importan desde `src` vía `pythonpath`.

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

## Licencia

[MIT](LICENSE)
