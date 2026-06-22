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

    # Seed opcional al arrancar: ruta a una suite YAML a cargar si la BD está
    # vacía (para que `docker compose up` deje el dashboard listo para usar).
    seed_suite: str | None = None
    # Sobrescribe el agent.url de la suite seedeada (p. ej. el servicio del mock).
    seed_agent_url: str | None = None


settings = Settings()
