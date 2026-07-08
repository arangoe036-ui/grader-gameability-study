"""Control B — LLM-judge grader (the "smart competitor" baseline, Patronus-style).

Spec v2.1 §5 — inputs PINNED (no longer a provisional choice): B is given THE TASK, THE
VISIBLE TESTS, and THE CANDIDATE PATCH, and it MAY execute the visible tests. It is NOT given
the hidden oracle or the footprint answer key — otherwise it collapses into A2/Treatment and
stops being a genuine judge. Mirrored in PREREGISTRATION.md.

STATUS: STUB — the judge MODEL is not wired. Per Prime Directive §0.4 no credentials live in
the untrusted-code sandbox, so the judge call (if any) happens OUTSIDE that container. Not
needed for Tier 0 (Treatment-only); required for Tier 1 Exp 1, which is gated.
"""
from __future__ import annotations

from grader_interface import Grader, Verdict, validate_verdict

# Pinned by spec v2.1 §5. Do NOT widen to hidden oracle / footprint (would collapse into A2/Treatment).
B_INPUTS = ("task", "visible_tests", "candidate_patch")  # may execute visible tests only


class ControlB(Grader):
    name = "control_b"

    def grade(self, attempt: dict, task: dict) -> Verdict:
        # TODO(Tier 1): build the judge prompt from exactly B_INPUTS and call the pinned judge
        # model OUTSIDE the untrusted sandbox. Must never receive task['hidden_oracle'] or
        # task['fault_footprint'].
        return validate_verdict(Verdict(
            pass_=False,
            notes=f"B STUB: LLM-judge not wired. inputs pinned={B_INPUTS} (spec §5). Gated to Tier 1.",
        ))
