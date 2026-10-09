"""Offline reference solver (OR-Tools Routing) to check heuristic quality and compute a hindsight bound. Brief §6.6.

Mapping: vehicles = teams; transit(i->j) = p_i + τ(i,j) in minutes; Σ w·C via
SetCumulVarSoftUpperBound(index_i, 0, w_i); shifts via SetBreakIntervalsOfVehicle;
forced/forbidden via SetAllowedVehiclesForIndex; accessible_from via CumulVar(i).SetMin(t).
Requires the `bench` extra: pip install -e ".[bench]".
"""
from __future__ import annotations

from dispatch.engine.types import Plan, State


def solve(state: State, cfg, time_limit_s: int = 30) -> Plan:
    raise NotImplementedError("Phase 2: see docs/RO_ENGINE_BRIEF.md §6.6")
