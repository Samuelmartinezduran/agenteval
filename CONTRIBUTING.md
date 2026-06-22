# Contribuir a agenteval

¡Gracias por tu interés! agenteval busca ser fácil de leer y de extender.

## Requisitos

- [uv](https://docs.astral.sh/uv/) y Python 3.10+
- Node.js 20+ (solo para el dashboard)

## Puesta en marcha

```bash
make setup     # uv sync de todo el workspace
make test      # tests de core + api
make lint      # ruff
```

> En macOS, `make setup` aplica un workaround para el bug uv + CPython de los
> `.pth` ocultos. Los tests usan `pythonpath` y no dependen del editable install.

## Estructura

| Carpeta            | Qué es                                                     |
| ------------------ | ---------------------------------------------------------- |
| `packages/core`    | Librería `agenteval` + CLI. Toda la lógica de evaluación.  |
| `packages/api`     | API REST (FastAPI). Reutiliza el runner del core.          |
| `frontend`         | Dashboard React + Vite + Tailwind.                         |
| `examples`         | Agente de juguete y suite de ejemplo.                      |

## Cómo extender

- **Añadir un juez (otro proveedor LLM):** subclasea `Judge` en
  [packages/core/src/agenteval/judge/base.py](packages/core/src/agenteval/judge/base.py)
  e impleméntalo. No hace falta tocar el runner.
- **Cambiar pesos o reglas de scoring:** están centralizados en
  [scoring/aggregate.py](packages/core/src/agenteval/scoring/aggregate.py) y
  [scoring/tool_accuracy.py](packages/core/src/agenteval/scoring/tool_accuracy.py).

## Pautas

- Añade tests para todo cambio de comportamiento (`packages/*/tests`).
- Mantén `make lint` y `make test` en verde; CI los ejecuta en cada PR.
- Cambios pequeños y enfocados; un PR, un objetivo.

## Migraciones de base de datos

Tras cambiar los modelos de [packages/api](packages/api/src/agenteval_api/models.py):

```bash
cd packages/api
uv run alembic revision --autogenerate -m "descripción"
uv run alembic upgrade head
```
