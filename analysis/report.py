"""report.py — emit SCIENTIFIC and COMMERCIAL summaries SEPARATELY.

Build plan §3 WS4 + spec §8: the report must keep the scientific claim (does the signal
hold, with CIs, honestly) apart from the commercial claim (is the margin decisive vs current
lab best-practice = A2). Mixing them is how a weak result gets sold as a strong one
(revisions doc, "make a GREEN mean what the go/no-go needs it to mean").

STATUS: structure DONE; consumes metrics.headline_panel output per grader. The exact
GREEN/AMBER/RED wording and thresholds come from spec §8 -> PREREGISTRATION.md, which is
BLOCKED on the missing v2 spec. Thresholds are read from PREREGISTRATION.md at runtime,
never hardcoded here (Prime Directive §0.3).
"""
from __future__ import annotations

import json
import os
from typing import Dict

_PREREG = os.path.join(os.path.dirname(__file__), "..", "PREREGISTRATION.md")


def _prereg_frozen() -> bool:
    """True only if PREREGISTRATION.md exists and is NOT the BLOCKED placeholder."""
    if not os.path.exists(_PREREG):
        return False
    with open(_PREREG, encoding="utf-8") as fh:
        return "STATUS: BLOCKED" not in fh.read()


def scientific_summary(panels: Dict[str, dict]) -> dict:
    """Per-grader honest signal: rates + CIs. No commercial framing."""
    out = {}
    for grader, panel in panels.items():
        out[grader] = {
            "hacks_caught": panel["hacks_caught"],
            "spurious_caught": panel["spurious_caught"],
            "fp_on_valid_alternatives": panel["fp_on_valid_alternatives"],
            "false_reject_honest": panel["false_reject_honest"],
            "footprint": panel["footprint"],
        }
    return {"kind": "SCIENTIFIC", "graders": out,
            "note": "Rates with 95% bootstrap CIs. A delta inside the noise band is not a delta."}


def commercial_summary(panels: Dict[str, dict], baseline: str = "control_a2") -> dict:
    """Treatment margin vs the DECISION BASELINE (A2). This is the pitch-relevant delta."""
    if baseline not in panels:
        return {"kind": "COMMERCIAL", "error": f"baseline '{baseline}' not in panels"}
    base = panels[baseline]
    deltas = {}
    for grader, panel in panels.items():
        if grader == baseline:
            continue
        deltas[grader + "_vs_" + baseline] = {
            "hacks_caught_beyond_baseline":
                round(panel["hacks_caught"]["rate"] - base["hacks_caught"]["rate"], 4),
            "spurious_caught_delta":
                round(panel["spurious_caught"]["rate"] - base["spurious_caught"]["rate"], 4),
            "extra_fp_on_valid_alternatives":
                round(panel["fp_on_valid_alternatives"]["rate"] - base["fp_on_valid_alternatives"]["rate"], 4),
        }
    return {"kind": "COMMERCIAL", "baseline": baseline, "deltas": deltas,
            "note": "Delta vs current lab best-practice (A2). Decisiveness judged against "
                    "the commercial magnitude pre-registered in spec §8 (review note 4)."}


def full_report(panels: Dict[str, dict], baseline: str = "control_a2") -> dict:
    return {
        "prereg_frozen": _prereg_frozen(),
        "WARNING": None if _prereg_frozen() else
        "PREREGISTRATION.md is not frozen (BLOCKED on v2 spec). Any verdict below is NON-BINDING.",
        "scientific": scientific_summary(panels),
        "commercial": commercial_summary(panels, baseline),
    }


if __name__ == "__main__":
    print(json.dumps({"prereg_frozen": _prereg_frozen()}, indent=2))
