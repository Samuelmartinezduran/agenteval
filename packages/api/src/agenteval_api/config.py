"""Configuración de la API (variables de entorno)."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGENTEVAL_", env_file=".env", extra="ignore")

    # SQLite por defecto para arrancar sin infra; Postgres en producción/Docker.
    database_url: str = "sqlite:///./agenteval.db"

    # Juez por defecto de la API: 'heuristic' (sin coste) u 'openai'.
    judge: str = "heuristic"

    # Orígenes permitidos para el dashboard (CORS).
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
