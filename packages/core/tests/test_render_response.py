from agenteval.judge.openai_judge import render_agent_response
from agenteval.models import AgentResponse, ToolCall


def test_text_only():
    out = render_agent_response(AgentResponse(content="Hace sol en Madrid."))
    assert "Texto: Hace sol en Madrid." in out
    assert "tool" not in out.lower()


def test_tool_call_only_is_rendered():
    # Antes esto llegaba vacío al juez; ahora la tool call es visible.
    resp = AgentResponse(tool_calls=[ToolCall(name="get_weather", arguments={"city": "Madrid"})])
    out = render_agent_response(resp)
    assert "get_weather" in out
    assert "Madrid" in out
    assert "vacía" not in out


def test_text_and_tool_call():
    resp = AgentResponse(
        content="Consulto el clima.",
        tool_calls=[ToolCall(name="get_weather", arguments={"city": "Madrid"})],
    )
    out = render_agent_response(resp)
    assert "Texto: Consulto el clima." in out
    assert "get_weather" in out


def test_empty_response():
    assert render_agent_response(AgentResponse()) == "(respuesta vacía)"
