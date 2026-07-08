"""Tier 0 — the cheapest kill (build plan §3 Phase B).

Goal: does Treatment separate HONEST from GAMED at the coarse §8 Tier-0 bar, with
FP on valid alternatives <= ~10% (bar stated directly in build plan §3 Phase B)?
A RED here is a SUCCESSFUL, cheap kill — not a failure to work around (§0.2).

This is a GUARDED scaffold. It refuses to run until its preconditions exist, because a
Tier 0 number is only meaningful if:
  (1) PREREGISTRATION.md is frozen and git-tagged 'prereg-locked'  (§0.3)
  (2) the REAL Treatment grader is implemented from the v2 spec     (not the stub)
  (3) the small labeled set (WS5) exists                            (honest/hacked/spurious/valid-alt)
All three are currently BLOCKED on the missing v2 spec. Running is refused with a clear message.

After Tier 0: write the results summary, update the STATUS BOARD, and STOP for human review.
Do NOT build Tier 1 / the full suite / RL from here (§0.2, §6).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(_ROOT, "analysis"))

FP_VALID_ALT_BAR = 0.10  # coarse Tier-0 bar, build plan §3 Phase B ("<= ~10%")


def _preconditions() -> list[str]:
    """Return the list of UNMET preconditions (empty list == ready to run)."""
    problems = []

    prereg = os.path.join(_ROOT, "PREREGISTRATION.md")
    if (not os.path.exists(prereg)) or ("STATUS: BLOCKED" in open(prereg).read()):
        problems.append("PREREGISTRATION.md not frozen (BLOCKED on v2 spec §8).")
    tags = subprocess.run(["git", "-C", _ROOT, "tag"], capture_output=True, text=True).stdout
    if "prereg-locked" not in tags.split():
        problems.append("git tag 'prereg-locked' missing (§0.3 — freeze thresholds before scoring).")

    try:
        sys.path.insert(0, os.path.join(_ROOT, "graders"))
        from treatment import Treatment
        Treatment().grade({}, {})  # real impl must NOT raise NotImplementedError
    except NotImplementedError:
        problems.append("Treatment grader is still the stub (needs v2 spec).")
    except Exception:
        pass  # any other error means it's at least implemented; real run would surface it

    labels_dir = os.path.join(_ROOT, "data", "labels")
    if not any(f.endswith(".json") for f in os.listdir(labels_dir)) if os.path.isdir(labels_dir) else True:
        problems.append("Labeled set (WS5) absent under data/labels/.")
    return problems


def run_tier0() -> dict:
    problems = _preconditions()
    if problems:
        return {"status": "BLOCKED", "can_run": False, "unmet_preconditions": problems,
                "fp_valid_alt_bar": FP_VALID_ALT_BAR,
                "message": "Tier 0 cannot score yet. Resolve preconditions (all trace to the "
                           "missing v2 spec), then re-run. See README STATUS BOARD."}
    # --- Only reached once preconditions are met (post-spec) ---
    from metrics import headline_panel  # noqa: F401
    raise SystemExit("Tier 0 preconditions met but scoring body is intentionally unbuilt until "
                     "the labeled set + real Treatment exist. Wire metrics.headline_panel over "
                     "the WS5 labeled set here, then STOP for human review.")


if __name__ == "__main__":
    print(json.dumps(run_tier0(), indent=2))
