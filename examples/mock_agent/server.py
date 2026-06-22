"""Agente de juguete OpenAI-compatible (solo stdlib).

Implementa el contrato que evalúa agenteval: recibe
``{"messages": [...], "tools": [...]}`` y devuelve ``choices[0].message`` con
``content`` y/o ``tool_calls``.

Lógica de demo (determinista):
- Si se ofrece la tool ``get_weather`` y el mensaje menciona una ciudad conocida,
  llama a ``get_weather`` con esa ciudad.
- Si el mensaje intenta una inyección ("ignora tus instrucciones"), se mantiene
  en su rol y responde con texto, sin llamar a ninguna tool.
- En cualquier otro caso responde con un texto genérico.

Ejecutar:  python -m examples.mock_agent.server   (escucha en :9000)
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

KNOWN_CITIES = ["Madrid", "Barcelona", "Sevilla", "Valencia", "Bilbao"]
INJECTION_MARKERS = ["ignora", "ignore", "olvida tus instrucciones", "system prompt"]


def build_response(payload: dict) -> dict:
    """Genera una respuesta OpenAI-compatible a partir del payload entrante."""

    messages = payload.get("messages") or []
    user_text = ""
    for msg in messages:
        if msg.get("role") == "user":
            user_text = msg.get("content") or ""
    lowered = user_text.lower()

    tool_names = {
        (t.get("function") or {}).get("name") for t in (payload.get("tools") or [])
    }

    # Intento de inyección -> nos mantenemos en el rol.
    if any(marker in lowered for marker in INJECTION_MARKERS):
        return _text_message(
            "Lo siento, solo puedo ayudarte con consultas sobre el tiempo."
        )

    # Consulta de clima con la tool disponible.
    if "get_weather" in tool_names:
        for city in KNOWN_CITIES:
            if city.lower() in lowered:
                return _tool_call_message("get_weather", {"city": city})

    return _text_message("¿En qué ciudad quieres consultar el tiempo?")


def _text_message(content: str) -> dict:
    return {"choices": [{"message": {"role": "assistant", "content": content}}]}


def _tool_call_message(name: str, arguments: dict) -> dict:
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {"name": name, "arguments": json.dumps(arguments)},
                        }
                    ],
                }
            }
        ]
    }


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802 - nombre impuesto por BaseHTTPRequestHandler
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            payload = {}

        body = json.dumps(build_response(payload)).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # silenciar logs por defecto
        pass


def serve(host: str = "0.0.0.0", port: int = 9000) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"mock_agent escuchando en http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    serve()
