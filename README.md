# agenteval

**Framework open source para evaluar agentes LLM con function calling / tool use.**

agenteval es **agnóstico**: funciona con cualquier agente que exponga un endpoint
HTTP compatible con OpenAI. Defines tus casos de prueba en YAML, los ejecutas
contra tu agente y obtienes una **puntuación por dimensión** (0-100) por cada caso,
desde la línea de comandos o desde un dashboard visual.

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
uv run agenteval run ../../examples/suites/weather-agent.yaml
```

## Stack completo (API + dashboard) con Docker

```bash
cp .env.example .env      # ajusta OPENAI_API_KEY si quieres el juez real
docker compose up --build
```

- API (FastAPI): http://localhost:8000 · docs en `/docs`
- Dashboard (React): http://localhost:5173

Crea una suite (`POST /suites`), lánzala (`POST /runs`) y explora los resultados
por dimensión en el dashboard.

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
