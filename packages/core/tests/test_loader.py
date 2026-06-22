import pytest

from agenteval.loader import SuiteLoadError, load_suite


def _write(tmp_path, content):
    p = tmp_path / "suite.yaml"
    p.write_text(content, encoding="utf-8")
    return p


def test_loads_valid_suite(tmp_path):
    suite = load_suite(
        _write(
            tmp_path,
            """
suite: demo
agent:
  url: http://localhost:9000
cases:
  - name: caso 1
    input: hola
    expected:
      tool: null
""",
        )
    )
    assert suite.suite == "demo"
    assert len(suite.cases) == 1


def test_missing_file():
    with pytest.raises(SuiteLoadError):
        load_suite("/no/existe.yaml")


def test_invalid_schema_missing_agent(tmp_path):
    with pytest.raises(SuiteLoadError):
        load_suite(_write(tmp_path, "suite: x\ncases: []\n"))


def test_empty_cases_rejected(tmp_path):
    with pytest.raises(SuiteLoadError):
        load_suite(
            _write(
                tmp_path,
                "suite: x\nagent:\n  url: http://h\ncases: []\n",
            )
        )
