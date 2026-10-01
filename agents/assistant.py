"""Build the AssistantAgent with its tools and system prompt."""

from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

from config.settings import PROJECT_ROOT
from tools.basic_tools import calculator, get_current_time

SYSTEM_PROMPT_PATH = PROJECT_ROOT / "prompts" / "assistant_system.md"


def build_assistant(model_client: ChatCompletionClient) -> AssistantAgent:
    """Create the assistant agent that can use the basic tools."""
    return AssistantAgent(
        name="assistant",
        model_client=model_client,
        tools=[get_current_time, calculator],
        system_message=SYSTEM_PROMPT_PATH.read_text(encoding="utf-8"),
        reflect_on_tool_use=True,
    )
