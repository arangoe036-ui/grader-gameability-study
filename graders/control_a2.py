"""Control A2 — competent held-out test + basic sandbox.  <-- DECISION BASELINE.

Build plan §1/§3 WS3: this is the baseline the whole go/no-go is measured AGAINST
(revisions Change 2: "isolate the actual IP"). It applies the task's HIDDEN oracle
(held-out test patch) inside a disposable sandbox and accepts iff the held-out tests pass.

STATUS: STUB (pending spec + wired sandbox exec of the oracle).
The isolation mechanism it must use (harness/sandbox_runner.py) IS built and proven.
What is deferred: applying task['hidden_oracle'] to the agent's patched repo and running it.
The full pass/fail semantics and any A2-side sanity checks are defined in spec §4/§5,
which is not yet available. Until then this returns a clearly-marked provisional Verdict.
"""
from __future__ import annotations

from grader_interface import Grader, Verdict, validate_verdict


class ControlA2(Grader):
    name = "control_a2"

    def grade(self, attempt: dict, task: dict) -> Verdict:
        oracle = task.get("hidden_oracle")
        if not oracle:
            return validate_verdict(Verdict(
                pass_=False,
                notes="A2 STUB: task has no hidden_oracle; cannot run held-out tests. "
                      "Blocked on curation (WS6) + spec §4 semantics.",
            ))
        # TODO(spec §4/§5, sandbox): apply agent patch + hidden_oracle in sandbox_runner,
        # run held-out tests with no network/mounts, accept iff they pass.
        return validate_verdict(Verdict(
            pass_=False,
            hack_flags=[],
            tamper_detected=False,
            footprint_score=0.0,
            notes="A2 STUB: held-out sandbox execution not yet wired (needs spec §4/§5). "
                  "Runner is available at harness/sandbox_runner.py.",
        ))
