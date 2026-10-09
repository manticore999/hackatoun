"""Event-driven simulator: applies plans, enforces the world's truth, calls the engine at every event.

Responsibilities
- hold the event queue (sources + events it generates: team on site, repair done, shift end)
- hold the TRUE durations (estimate × noise) and reveal them only on REPAIR_DONE
- build the State the engine sees (no future incidents, estimates only) and call policy.plan()
- dispatch accepted next jobs, log every decision and outcome
- record the timeline for scoring, the app and the benchmark
"""
from __future__ import annotations

from dataclasses import dataclass, field

from dispatch.engine.types import Plan, State
from dispatch.sim.events import Event


@dataclass
class Result:
    restored_at: dict[str, float] = field(default_factory=dict)   # incident_id -> actual C_i
    events: list[Event] = field(default_factory=list)
    plans: list[tuple[float, Plan]] = field(default_factory=list)


class Simulator:
    def __init__(self, cfg, sources, policy, teams):
        self.cfg, self.sources, self.policy, self.teams = cfg, sources, policy, teams

    def state(self) -> State:
        raise NotImplementedError

    def step(self) -> list[Event]:
        """Process the next group of events, re-plan, dispatch. Used by the live app."""
        raise NotImplementedError

    def run(self) -> Result:
        """Run to the end (benchmark mode, no wall clock)."""
        raise NotImplementedError
