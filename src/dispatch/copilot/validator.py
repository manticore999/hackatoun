"""Guardrail between the LLM and the engine: IDs exist, values in range, safety rules untouchable."""
from __future__ import annotations

from dispatch.engine.modifiers import Modifier
from dispatch.engine.types import State


class InvalidModifier(ValueError):
    pass


def validate(raw: dict, state: State) -> Modifier:
    """Parse one JSON modifier from the LLM into a catalogue dataclass, or raise InvalidModifier."""
    raise NotImplementedError("LLM / modifiers workstream")
