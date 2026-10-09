"""Construction heuristic: list scheduling with the Smith index w / (travel + repair). Target < 10 ms. Brief §6.3."""
from __future__ import annotations

from dispatch.engine.types import Plan, State


def list_scheduling(state: State, cfg) -> Plan:
    """Earliest-free team repeatedly takes the feasible incident with max w_i / (τ(pos_k, i) + p_i)."""
    raise NotImplementedError("RO workstream: see docs/RO_ENGINE_BRIEF.md §6.3")


def warm_start(state: State, cfg) -> Plan:
    """previous_plan minus finished jobs, new incidents inserted at their cheapest position. Brief §6.5."""
    raise NotImplementedError
