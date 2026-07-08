"""Frozen grader interface (build plan §2).

Every grader implements grade(attempt, task) -> Verdict.
This signature is FROZEN. Changes route through the integrator agent.

    attempt : dict  # conforms to contracts/trajectory_schema.json
    task    : dict  # conforms to contracts/task_schema.json  (DRAFT, pending spec §4)
    Verdict : dataclass mirroring contracts/verdict_schema.json
"""
from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import List

_CONTRACTS = os.path.join(os.path.dirname(__file__), "..", "contracts")


@dataclass
class Verdict:
    """Return value of every grader. Mirrors contracts/verdict_schema.json."""
    pass_: bool                                   # 'pass' is a keyword; serialize as "pass"
    hack_flags: List[str] = field(default_factory=list)
    tamper_detected: bool = False
    footprint_score: float = 0.0                  # region/signal match in [0,1] (review note 3)
    notes: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["pass"] = d.pop("pass_")
        return d

    @staticmethod
    def from_dict(d: dict) -> "Verdict":
        return Verdict(
            pass_=bool(d["pass"]),
            hack_flags=list(d.get("hack_flags", [])),
            tamper_detected=bool(d.get("tamper_detected", False)),
            footprint_score=float(d.get("footprint_score", 0.0)),
            notes=str(d.get("notes", "")),
        )


def validate_verdict(v: Verdict) -> Verdict:
    """Light structural check against verdict_schema.json (uses jsonschema if present)."""
    d = v.to_dict()
    try:
        import jsonschema  # optional
        with open(os.path.join(_CONTRACTS, "verdict_schema.json")) as fh:
            jsonschema.validate(d, json.load(fh))
    except ImportError:
        assert isinstance(d["pass"], bool)
        assert isinstance(d["hack_flags"], list)
        assert isinstance(d["tamper_detected"], bool)
        assert 0.0 <= float(d["footprint_score"]) <= 1.0
        assert isinstance(d["notes"], str)
    return v


class Grader(ABC):
    """Abstract base for all graders (build plan §2)."""
    name: str = "grader"

    @abstractmethod
    def grade(self, attempt: dict, task: dict) -> Verdict:
        ...
