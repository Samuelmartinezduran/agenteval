"""agenteval — framework para evaluar agentes LLM con function calling / tool use."""

from .loader import SuiteLoadError, load_suite
from .models import (
    AgentConfig,
    AgentResponse,
    CaseResult,
    ExpectedBehavior,
    RunResult,
    TestCase,
    TestSuite,
    ToolCall,
    ToolDefinition,
)
from .runner import run_suite, run_suite_sync

__version__ = "0.1.0"

__all__ = [
    "AgentConfig",
    "AgentResponse",
    "CaseResult",
    "ExpectedBehavior",
    "RunResult",
    "TestCase",
    "TestSuite",
    "ToolCall",
    "ToolDefinition",
    "SuiteLoadError",
    "load_suite",
    "run_suite",
    "run_suite_sync",
    "__version__",
]
