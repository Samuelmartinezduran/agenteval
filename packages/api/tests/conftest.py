"""Fixtures de test de la API: DB SQLite efímera, TestClient y mock agent real."""

from __future__ import annotations

import os
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

# Configurar la DB ANTES de importar la app (settings se lee al importar).
_DB = Path(__file__).parent / "_test.db"
os.environ["AGENTEVAL_DATABASE_URL"] = f"sqlite:///{_DB}"
os.environ["AGENTEVAL_JUDGE"] = "heuristic"

# Hacer importable examples/mock_agent desde la raíz del repo.
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from examples.mock_agent.server import Handler  # noqa: E402

from agenteval_api.db import Base, engine  # noqa: E402
from agenteval_api.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def _fresh_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_agent_url():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
