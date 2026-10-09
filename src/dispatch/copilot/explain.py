"""Turn engine ExplanationFacts into French text for the crisis manager.

Rule: every number in the generated text must appear in the facts; otherwise reject and regenerate.
"""
from __future__ import annotations

from dispatch.engine.types import ExplanationFacts


def explain_recommendation(facts: ExplanationFacts, cfg) -> str:
    raise NotImplementedError("LLM workstream")


def check_numbers_grounded(text: str, facts: ExplanationFacts) -> bool:
    """True if every number stated in `text` exists in `facts`."""
    raise NotImplementedError("LLM workstream")
