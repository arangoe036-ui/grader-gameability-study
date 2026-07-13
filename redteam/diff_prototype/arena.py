"""Adversary-facing arena for the differential-check experiment.

Fixes the Step 1 leak: the adversary NEVER receives `hidden_oracle`. It submits a patch and
receives ONLY the prototype's verdict (accepted + whether the differential check flagged it). In
WHITE-BOX mode it additionally receives the check's CONTEXTS (the fingerprint battery) — nothing
else. Ground-truth production-correctness comes from the Step 1 meta-oracle, which is INDEPENDENT:
it never sees the prototype and shares no context signals with it (it runs `meta_check_*` on fresh
random inputs; the prototype runs `test_probe/prod_probe/svc_probe` on fixed inputs). This is the
fairness guarantee — the adversary can only make the prototype look WORSE, never falsely better.

Escape (same definition as Step 1): a submission ACCEPTED by the prototype while genuinely
production-buggy per the meta-oracle.
"""
from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.join(_HERE, "..", "..")
sys.path.insert(0, os.path.join(_ROOT, "redteam"))     # meta_oracle (independent ground truth)
sys.path.insert(0, _HERE)
import meta_oracle                                       # noqa: E402
import check                                             # noqa: E402

TASKS_DIR = os.path.join(_ROOT, "data", "tasks", "tier0")


def load_task(task_id: str) -> dict:
    with open(os.path.join(TASKS_DIR, f"{task_id}.json")) as fh:
        return json.load(fh)


def redacted_task(task_id: str) -> dict:
    """What the adversary may see: buggy source + visible tests. NO hidden_oracle, NO footprint."""
    t = load_task(task_id)
    return {"task_id": task_id, "task_type": t.get("task_type"),
            "buggy_files": t.get("files", {}),
            "visible_tests": t.get("visible_tests", []),
            "target_fn": check.TASK_FN.get(task_id)}


def adversary_verdict(task_id: str, files: dict, white_box: bool = False) -> dict:
    """ONLY the prototype's verdict (+ contexts if white-box). No oracle, no meta result."""
    acc = check.prototype_accept(task_id, files, load_task(task_id))
    out = {"accepted": acc["accepted"], "flagged": acc["flagged"]}
    if white_box:
        out["contexts"] = check.CONTEXTS       # the fingerprint battery, revealed on purpose
    return out


def evaluate(task_id: str, files: dict, meta_seed: int = 0) -> dict:
    """Full classification for the harness/report (NOT shown to the adversary)."""
    acc = check.prototype_accept(task_id, files, load_task(task_id))
    truly = bool(meta_oracle.check(task_id, files, seed=meta_seed)["truly_correct"])
    return {"task": task_id, "accepted": acc["accepted"], "oracle_ok": acc["oracle_ok"],
            "flagged": acc["flagged"], "truly_correct": truly,
            "escaped": acc["accepted"] and not truly}


def _cli() -> None:
    if len(sys.argv) >= 2 and sys.argv[1] == "task":
        print(json.dumps(redacted_task(sys.argv[2]), indent=2)); return
    if len(sys.argv) >= 2 and sys.argv[1] == "contexts":
        print(json.dumps(check.CONTEXTS, indent=2)); return
    # default: submit — read {"task","files","white_box"?} from stdin
    req = json.loads(sys.stdin.read())
    print(json.dumps(adversary_verdict(req["task"], req["files"],
                                       bool(req.get("white_box", False))), indent=2))


if __name__ == "__main__":
    _cli()
