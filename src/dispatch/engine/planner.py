"""Main entry point called by the simulator at every event."""
from __future__ import annotations

from dispatch.engine.construct import list_scheduling, warm_start
from dispatch.engine.local_search import improve
from dispatch.engine.types import Plan, State


def plan(state: State, cfg, budget_ms: int | None = None) -> Plan:
    """Greedy (or warm start), then local search. Always returns a feasible plan."""
    budget_ms = budget_ms if budget_ms is not None else cfg.solver.budget_ms
    initial = warm_start(state, cfg) if state.previous_plan else list_scheduling(state, cfg)
    return improve(initial, state, cfg, budget_ms)


class OptimisedPolicy:
    name = "optimised"

    def plan(self, state: State, cfg) -> Plan:
        return plan(state, cfg)
