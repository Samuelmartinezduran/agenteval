.PHONY: setup sync test lint run-mock run-cli api fix-pth

# Los targets que ejecutan código no dependen del editable install: le pasan
# PYTHONPATH explícito (igual que los tests con pythonpath de pytest). Esto
# esquiva el bug uv+CPython de macOS: uv marca los .pth editables como ocultos
# (y los re-oculta en CADA `uv run`, incluso con --no-sync), y CPython los
# ignora. fix-pth los desmarca como best-effort para otros usos del venv.
PYPATH := $(CURDIR)/packages/core/src:$(CURDIR)/packages/api/src

sync:
	uv sync --all-packages --all-extras
	$(MAKE) fix-pth

fix-pth:
	-find .venv -name '*.pth' -exec chflags nohidden {} + 2>/dev/null || true

setup: sync

# Ejecuta los tests de ambos paquetes (no dependen del editable: usan pythonpath).
test:
	cd packages/core && uv run --no-sync pytest -q
	cd packages/api && uv run --no-sync pytest -q

lint:
	uv run --no-sync ruff check packages

# Arranca el agente de juguete en :9000.
run-mock:
	uv run --no-sync python -m examples.mock_agent.server

# Evalúa la suite de ejemplo con el juez heurístico (sin clave de API).
run-cli:
	cd packages/core && PYTHONPATH=$(PYPATH) uv run --no-sync python -m agenteval.cli run ../../examples/suites/weather-agent.yaml --judge heuristic

# Arranca la API en :8000.
api:
	cd packages/api && PYTHONPATH=$(PYPATH) uv run --no-sync python -m uvicorn agenteval_api.main:app --reload
