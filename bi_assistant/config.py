"""Runtime settings, read from environment variables (or a local .env file)."""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional
    pass

PROVIDERS = {
    "anthropic": {"label": "Claude", "keys": ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"),
                  "model_env": "BI_ASSISTANT_MODEL", "default_model": "claude-opus-5-5"},
    "openai": {"label": "GPT", "keys": ("OPENAI_API_KEY",),
               "model_env": "OPENAI_MODEL", "default_model": "gpt-5.5"},
}

EFFORT = os.getenv("BI_ASSISTANT_EFFORT", "high")
MAX_TOKENS = int(os.getenv("BI_ASSISTANT_MAX_TOKENS", "16000"))

# Language for explanations shown to users (code stays as-is).
OUTPUT_LANGUAGE = os.getenv("BI_ASSISTANT_OUTPUT_LANGUAGE", "Korean")

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


def has_key(provider: str) -> bool:
    return any(os.getenv(k) for k in PROVIDERS[provider]["keys"])


def available_providers() -> list[str]:
    return [p for p in PROVIDERS if has_key(p)]


def model_for(provider: str) -> str:
    info = PROVIDERS[provider]
    return os.getenv(info["model_env"], info["default_model"])


def _default_provider() -> str | None:
    wanted = os.getenv("BI_ASSISTANT_PROVIDER", "").lower()
    if wanted in PROVIDERS and has_key(wanted):
        return wanted
    available = available_providers()
    return available[0] if available else None


# Active provider; the web UI may switch it when both keys are set.
PROVIDER = _default_provider()


def has_api_key() -> bool:
    return PROVIDER is not None
