"""Curated domain knowledge loaded from the YAML files in this folder."""

from functools import cache

import yaml

from ..config import KNOWLEDGE_DIR


@cache
def load(name: str):
    with open(KNOWLEDGE_DIR / f"{name}.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def as_text(name: str) -> str:
    """Raw YAML text, for inclusion in prompts."""
    return (KNOWLEDGE_DIR / f"{name}.yaml").read_text(encoding="utf-8")
