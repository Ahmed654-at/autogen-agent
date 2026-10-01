"""Offline smoke tests: no model calls, no API key needed."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from autogen_ext.models.replay import ReplayChatCompletionClient

from agents.assistant import build_assistant
from models.model_client import OPEN_MODEL_INFO
from tools.basic_tools import calculator, get_current_time


def test_calculator_basic_math():
    assert calculator("2345 * 67") == "157115"
    assert calculator("2345 × 67") == "157115"
    assert calculator("(3 + 4) ** 2") == "49"
    assert calculator("-10 / 4") == "-2.5"


def test_calculator_rejects_unsafe_input():
    assert calculator("__import__('os').system('dir')").startswith("Error")
    assert calculator("1 / 0").startswith("Error")


def test_get_current_time_returns_text():
    assert len(get_current_time()) >= 19


def test_agent_builds_with_tools():
    client = ReplayChatCompletionClient(["ok"], model_info=OPEN_MODEL_INFO)
    agent = build_assistant(client)
    assert agent.name == "assistant"
    tool_names = {tool.name for tool in agent._tools}
    assert tool_names == {"get_current_time", "calculator"}
