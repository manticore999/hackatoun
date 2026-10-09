"""Reference strategies required by the README; also test oracles. Brief §6.2."""
from __future__ import annotations

from typing import Protocol

from dispatch.engine.types import Plan, State


class Policy(Protocol):
    name: str

    def plan(self, state: State, cfg) -> Plan: ...


class FifoPolicy:
    """Oldest pending incident -> team that can reach it earliest."""
    name = "fifo"

    def plan(self, state: State, cfg) -> Plan:
        raise NotImplementedError


class NearestPolicy:
    """Each team, when free, takes the nearest pending incident."""
    name = "nearest"

    def plan(self, state: State, cfg) -> Plan:
        raise NotImplementedError


class MaxCustomersPolicy:
    """Most customers (sensitive first) -> earliest-arriving team."""
    name = "max_customers"

    def plan(self, state: State, cfg) -> Plan:
        raise NotImplementedError


BASELINES: dict[str, type] = {p.name: p for p in (FifoPolicy, NearestPolicy, MaxCustomersPolicy)}
