"""Entry point: python main.py starts a chat session with the agent."""

import asyncio
import sys

from workflows.single_agent import chat


def main() -> int:
    # Windows consoles default to a legacy code page; UTF-8 keeps symbols like × readable.
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")

    print("Chat with the assistant. It remembers this session. Type 'exit' or 'quit' to stop.")
    try:
        asyncio.run(chat())
    except KeyboardInterrupt:
        print("\nStopped.")
        return 130
    except Exception as error:
        print(f"\nError: {type(error).__name__}: {error}", file=sys.stderr)
        print("Check MODEL_PROVIDER and the matching settings in .env.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
