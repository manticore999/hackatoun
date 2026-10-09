"""Loop 2 (between decisions): decision log + retrieval of similar past rejections -> rule proposals.

Each log entry: proposal, explanation facts, response (accept/modify/reject), reason, modifiers, outcome.
A modifier applied >= 3 times in similar contexts is proposed as a permanent rule.
"""
from __future__ import annotations


class DecisionLog:
    def append(self, entry: dict) -> None:
        raise NotImplementedError

    def similar(self, context: dict, k: int = 5) -> list[dict]:
        raise NotImplementedError

    def rule_proposals(self) -> list[dict]:
        raise NotImplementedError
