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


def test_contains_matcher():
    expected = ExpectedBehavior(tool="get_weather", params={"city": {"contains": "madrid"}})
    assert score_tool_accuracy(expected, [_call("get_weather", city="Madrid, España")]) == 100.0
    assert score_tool_accuracy(expected, [_call("get_weather", city="Paris")]) == 50.0


def test_regex_matcher():
    expected = ExpectedBehavior(tool="get_weather", params={"city": {"regex": r"^mad\w+$"}})
    assert score_tool_accuracy(expected, [_call("get_weather", city="Madrid")]) == 100.0
    assert score_tool_accuracy(expected, [_call("get_weather", city="Valladolid")]) == 50.0


def test_invalid_regex_does_not_crash_the_run():
    # Una regex mal formada en la suite no debe propagar re.error: se trata como
    # "no coincide" (params incorrectos), no como un fallo del run.
    expected = ExpectedBehavior(tool="get_weather", params={"city": {"regex": "["}})
    assert score_tool_accuracy(expected, [_call("get_weather", city="Madrid")]) == 50.0


def test_plain_dict_value_still_uses_exact_equality():
    # Un dict esperado que no es un matcher reservado se compara por igualdad.
    expected = ExpectedBehavior(tool="t", params={"filters": {"country": "ES"}})
    assert score_tool_accuracy(expected, [_call("t", filters={"country": "ES"})]) == 100.0
    assert score_tool_accuracy(expected, [_call("t", filters={"country": "FR"})]) == 50.0
