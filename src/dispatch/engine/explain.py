"""Explanation facts for each recommended next job (the LLM may only state numbers found here). Brief §8."""
from __future__ import annotations

from dispatch.engine.types import ExplanationFacts, Plan, State


def explain(plan: Plan, state: State, cfg) -> list[ExplanationFacts]:
    raise NotImplementedError("RO workstream: see docs/RO_ENGINE_BRIEF.md §8")
