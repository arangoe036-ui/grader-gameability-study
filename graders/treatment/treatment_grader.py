"""Treatment — Cuarzo: hidden oracle + tamper detection + footprint localization.

Build plan §1: graders/treatment/ = "Cuarzo: hidden oracle + tamper detect + footprint localize".
This is the crown-jewel IP under test and the thing the entire go/no-go decides on.

STATUS: STUB — INTENTIONALLY NOT IMPLEMENTED.
The three mechanisms and their exact scoring are defined in the v2 spec, which is NOT
available in this build. Implementing them from guesswork would corrupt the experiment
(a Treatment that doesn't match the spec makes every downstream number meaningless).
This stub exists only to satisfy the frozen grader interface so analysis/harness can be
smoke-tested on fixtures. It must be replaced with the real implementation, sourced from
the spec, before ANY Tier 0 scoring.

Components to implement from spec:
  1. Hidden oracle    — apply task['hidden_oracle'] in sandbox; correctness signal.
  2. Tamper detection — detect edits to tests / grading harness / environment (sets tamper_detected).
  3. Footprint localize — region/signal match of patch vs task['footprint'] -> footprint_score (review note 3).
"""
from __future__ import annotations

from grader_interface import Grader, Verdict, validate_verdict


class Treatment(Grader):
    name = "treatment"

    def grade(self, attempt: dict, task: dict) -> Verdict:
        raise NotImplementedError(
            "Treatment grader is intentionally unimplemented: its logic and scoring live in "
            "the v2 spec, which is missing from this build. Do not fabricate it. "
            "See graders/treatment/treatment_grader.py docstring and README STATUS BOARD."
        )

    def stub_verdict(self, attempt: dict, task: dict) -> Verdict:
        """Structural placeholder for fixture smoke-tests ONLY. Never use for scoring."""
        return validate_verdict(Verdict(
            pass_=False,
            notes="TREATMENT STUB — not a real verdict; blocked on v2 spec.",
        ))
