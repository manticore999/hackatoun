"""Manager's rejection reason (free text or quick chips) -> modifiers from the fixed catalogue.

Classify fact (road cut, duration) vs preference (priority, less driving). Ask ONE clarifying question if ambiguous.
Output must be strict JSON matching dispatch.engine.modifiers.CATALOGUE.
"""
from __future__ import annotations

from dispatch.engine.modifiers import Modifier


def reason_to_modifiers(reason: str, context: dict, cfg) -> list[Modifier] | str:
    """Return modifiers, or a clarifying question (str) when the reason is ambiguous."""
    raise NotImplementedError("LLM workstream")
