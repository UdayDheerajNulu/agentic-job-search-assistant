"""Environment-driven config. Defaults to a no-key 'heuristic' mode that runs anywhere."""
import os

PROVIDER = os.getenv("LLM_PROVIDER", "none").lower()  # none | openai | anthropic | gemini
LLM_MODEL = os.getenv("LLM_MODEL", "")


def get_key():
    return {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "gemini": os.getenv("GEMINI_API_KEY"),
    }.get(PROVIDER)
