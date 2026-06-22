from agenteval.models import ExpectedBehavior, ToolCall
from agenteval.scoring.tool_accuracy import score_tool_accuracy


def _call(name, **args):
    return ToolCall(name=name, arguments=args)


def test_correct_tool_and_params():
    expected = ExpectedBehavior(tool="get_weather", params={"city": "Madrid"})
    assert score_tool_accuracy(expected, [_call("get_weather", city="Madrid")]) == 100.0


def test_params_match_is_case_insensitive():
    expected = ExpectedBehavior(tool="get_weather", params={"city": "Madrid"})
    assert score_tool_accuracy(expected, [_call("get_weather", city=" madrid ")]) == 100.0


def test_correct_tool_wrong_params():
    expected = ExpectedBehavior(tool="get_weather", params={"city": "Madrid"})
    assert score_tool_accuracy(expected, [_call("get_weather", city="Paris")]) == 50.0


def test_wrong_tool():
    expected = ExpectedBehavior(tool="get_weather", params={"city": "Madrid"})
    assert score_tool_accuracy(expected, [_call("send_email", to="x")]) == 0.0


def test_no_tool_expected_and_none_called():
    expected = ExpectedBehavior(tool=None)
    assert score_tool_accuracy(expected, []) == 100.0


def test_no_tool_expected_but_one_called():
    expected = ExpectedBehavior(tool=None)
    assert score_tool_accuracy(expected, [_call("get_weather", city="Madrid")]) == 0.0


def test_expected_tool_but_none_called():
    expected = ExpectedBehavior(tool="get_weather", params={"city": "Madrid"})
    assert score_tool_accuracy(expected, []) == 0.0
