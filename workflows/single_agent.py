"""Run one agent and stream the conversation (with tool calls) to the console."""

import asyncio

from autogen_agentchat.base import TaskResult
from autogen_agentchat.ui import Console

from agents.assistant import build_assistant
from models.model_client import get_model_client

EXIT_WORDS = {"exit", "quit"}


async def run(task: str) -> TaskResult:
    """Run the assistant on a single task, printing messages and tool calls as they happen."""
    model_client = get_model_client()
    try:
        agent = build_assistant(model_client)
        return await Console(agent.run_stream(task=task))
    finally:
        await model_client.close()


async def chat() -> None:
    """Chat with one assistant until the user types exit/quit.

    The same agent is reused for every turn, so it remembers earlier questions and answers.
    """
    model_client = get_model_client()
    try:
        agent = build_assistant(model_client)
        while True:
            try:
                task = (await asyncio.to_thread(input, "\nYou (type 'exit' to quit) > ")).strip()
            except EOFError:
                task = "exit"
            if not task:
                continue
            if task.lower() in EXIT_WORDS:
                print("Goodbye!")
                return
            try:
                await Console(agent.run_stream(task=task))
            except Exception as error:
                # One failed turn (e.g. a rate limit) shouldn't end the whole session.
                print(f"\nError: {type(error).__name__}: {error}\nTry again, or type 'exit'.")
    finally:
        await model_client.close()
