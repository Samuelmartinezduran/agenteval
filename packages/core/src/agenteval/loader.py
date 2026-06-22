"""Carga y validación de suites de prueba desde YAML."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from .models import TestSuite


class SuiteLoadError(Exception):
    """Error legible al cargar/validar una suite YAML."""


def load_suite(path: str | Path) -> TestSuite:
    """Carga un fichero YAML y lo valida contra :class:`TestSuite`.

    Lanza :class:`SuiteLoadError` con un mensaje claro si el YAML es inválido o
    no cumple el esquema, para dar buen feedback en CLI y CI.
    """

    path = Path(path)
    if not path.exists():
        raise SuiteLoadError(f"No se encontró el fichero de suite: {path}")

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SuiteLoadError(f"YAML inválido en {path}:\n{exc}") from exc

    if not isinstance(raw, dict):
        raise SuiteLoadError(f"La suite {path} debe ser un mapping YAML en la raíz.")

    try:
        return TestSuite.model_validate(raw)
    except ValidationError as exc:
        raise SuiteLoadError(f"La suite {path} no cumple el esquema:\n{exc}") from exc
