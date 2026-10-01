"""Runtime settings, read from environment variables (or a local .env file)."""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional
    pass

MODEL = os.getenv("BI_ASSISTANT_MODEL", "claude-opus-5-5")
EFFORT = os.getenv("BI_ASSISTANT_EFFORT", "high")
MAX_TOKENS = int(os.getenv("BI_ASSISTANT_MAX_TOKENS", "16000"))

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


def has_api_key() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN"))

# Language for explanations shown to users (code stays as-is).
OUTPUT_LANGUAGE = os.getenv("BI_ASSISTANT_OUTPUT_LANGUAGE", "Korean")
