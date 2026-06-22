.PHONY: setup sync test lint run-mock run-cli api fix-pth

# Sincroniza el workspace. En macOS, uv marca los .pth editables como ocultos y
# las versiones recientes de CPython los ignoran; los desmarcamos para que
# `uv run` funcione. En Linux/Docker es un no-op.
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
	cd packages/core && uv run --no-sync agenteval run ../../examples/suites/weather-agent.yaml --judge heuristic

# Arranca la API en :8000.
api:
	cd packages/api && uv run --no-sync uvicorn agenteval_api.main:app --reload
