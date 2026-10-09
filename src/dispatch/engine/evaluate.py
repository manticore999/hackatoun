"""Route evaluation and plan scoring: the building block everything else calls. Brief §6.1."""
from __future__ import annotations

from dataclasses import dataclass, field

from dispatch.engine.types import Incident, Plan, ScoreBreakdown, State, Team


@dataclass
class RouteEval:
    feasible: bool
    cost: float = 0.0                     # Σ w_i (C_i - r_i) over the route
    end_time: float = 0.0
    timings: list[tuple[str, float, float, float]] = field(default_factory=list)  # (id, depart, start, end)


def weight(incident: Incident, cfg) -> float:
    """w_i = customers × (1 + β × sensitive)."""
    return incident.customers * (1 + cfg.objective.beta_sensitive * incident.sensitive)


def evaluate_route(team: Team, route: list[Incident], cfg) -> RouteEval:
    """Simulate one team's ordered route under the work rules (C2, C4, C5, C6). Return cost + timings."""
    raise NotImplementedError("RO workstream: see docs/RO_ENGINE_BRIEF.md §6.1")


def score(plan: Plan, state: State, cfg) -> ScoreBreakdown:
    """Full objective (§3): main term + stability + travel + fairness, plus KPIs."""
    raise NotImplementedError("RO workstream: see docs/RO_ENGINE_BRIEF.md §3")
