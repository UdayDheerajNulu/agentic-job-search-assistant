"""Swappable LLM provider. Returns None when no key/SDK is configured so callers
fall back to deterministic heuristics. Supports OpenAI, Anthropic, and Gemini."""
from . import config


def llm_available():
    return config.PROVIDER in {"openai", "anthropic", "gemini"} and bool(config.get_key())


def chat(system, user, json_mode=False):
    """Return the model's text, or None if not configured / on error."""
    if not llm_available():
        return None
    try:
        if config.PROVIDER == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=config.get_key())
            kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
            r = client.chat.completions.create(
                model=config.LLM_MODEL or "gpt-4o-mini",
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": user}],
                **kwargs,
            )
            return r.choices[0].message.content
        if config.PROVIDER == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=config.get_key())
            r = client.messages.create(
                model=config.LLM_MODEL or "claude-3-5-sonnet-latest",
                max_tokens=1500, system=system,
                messages=[{"role": "user", "content": user}],
            )
            return r.content[0].text
        if config.PROVIDER == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=config.get_key())
            model = genai.GenerativeModel(config.LLM_MODEL or "gemini-1.5-pro")
            r = model.generate_content(system + "\n\n" + user)
            return r.text
    except Exception:
        return None
    return None
