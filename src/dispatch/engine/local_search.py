"""Improvement: relocate / swap / reorder moves, then ALNS destroy-repair, within a time budget. Brief §6.4."""
from __future__ import annotations

from dispatch.engine.types import Plan, State


def improve(plan: Plan, state: State, cfg, budget_ms: int) -> Plan:
    """Return the best feasible plan found before the budget runs out (deterministic with cfg.solver.seed)."""
    raise NotImplementedError("RO workstream: see docs/RO_ENGINE_BRIEF.md §6.4")
