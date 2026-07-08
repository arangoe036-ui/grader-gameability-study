"""Control B — LLM-judge grader.

Build plan §3 WS3 + §7 review note 4: "Pin Control B's inputs ... state it so the
comparison is fair." This is a PIN POINT that must be confirmed by a human before scoring.

  >>> DECISION TO PIN (spec §4): Control B inputs are one of:
  >>>   (a) SAME information as A2 (patch + problem statement + visible tests + hidden oracle), or
  >>>   (b) a pure NO-ORACLE opinion judge (patch + problem statement + visible tests only).
  >>> Provisional default here = (b) no-oracle opinion judge. DO NOT SCORE until a human
  >>> confirms this choice and it is recorded in PREREGISTRATION.md.

STATUS: STUB (no model wired; no key in the sandbox by design). Inputs pinned as a flag only.
"""
from __future__ import annotations

from grader_interface import Grader, Verdict, validate_verdict

# The frozen input policy for B. Change requires integrator + prereg entry.
B_INPUTS = "no_oracle_opinion"   # or "same_as_a2"; MUST be confirmed before scoring.


class ControlB(Grader):
    name = "control_b"

    def __init__(self, inputs: str = B_INPUTS):
        assert inputs in ("no_oracle_opinion", "same_as_a2"), inputs
        self.inputs = inputs

    def grade(self, attempt: dict, task: dict) -> Verdict:
        # TODO(spec §4): build the judge prompt from exactly the pinned inputs and call the
        # pinned judge model. No credentials are available inside the sandbox by design (§0.4);
        # the judge call, if any, happens outside the untrusted-code container.
        return validate_verdict(Verdict(
            pass_=False,
            notes=f"B STUB: LLM-judge not wired. inputs='{self.inputs}' (PIN via prereg before scoring).",
        ))
