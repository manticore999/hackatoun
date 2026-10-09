"""Thin wrapper around the Claude API. Needs the `llm` extra and ANTHROPIC_API_KEY (see .env.example)."""
from __future__ import annotations


def get_client():
    import anthropic  # imported lazily so the rest of the project runs without the llm extra

    return anthropic.Anthropic()


def complete(system: str, messages: list[dict], cfg, tools: list[dict] | None = None):
    """One Messages API call with the configured model and effort.

    Server-side refusal fallback is enabled: if the main model declines, the API re-runs the
    request on the fallback model within the same call.
    """
    kwargs = {"tools": tools} if tools else {}
    response = get_client().beta.messages.create(
        model=cfg.llm.model,
        max_tokens=cfg.llm.max_tokens,
        system=system,
        messages=messages,
        output_config={"effort": cfg.llm.effort},
        betas=["server-side-fallback-2026-06-01"],
        fallbacks=[{"model": "claude-opus-4-8"}],
        **kwargs,
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"LLM refused: {response.stop_details}")
    return response
