"""Load settings from the project's .env file."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


def get_setting(name: str, default: str = "") -> str:
    """Return a setting from the environment (stripped), or the default."""
    return os.getenv(name, default).strip()


def require_setting(name: str) -> str:
    """Return a setting, or raise a clear error if it is missing or empty."""
    value = get_setting(name)
    if not value:
        raise ValueError(f"{name} is not set. Add it to the .env file in {PROJECT_ROOT}.")
    return value
