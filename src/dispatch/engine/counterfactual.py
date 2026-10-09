"""What-if: re-solve with extra modifiers and price the difference. Powers override cost and LLM what-ifs. Brief §7."""
from __future__ import annotations

from dispatch.engine.modifiers import Modifier
from dispatch.engine.types import Plan, State


def counterfactual(state: State, forced: list[Modifier], cfg) -> tuple[Plan, float]:
    """Return (new plan, Δscore vs the current best plan). Δ = 0 when forcing what was already recommended."""
    raise NotImplementedError("RO workstream: see docs/RO_ENGINE_BRIEF.md §7")
