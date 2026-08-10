"""run_agent.py — produce ONE trajectory for one task, fully sandboxed.

Build plan §1: "OpenHands wrapper -> one trajectory". Emits a dict conforming to
contracts/trajectory_schema.json and consumed by graders.

STATUS: real sandboxing + trajectory assembly + schema validation are DONE.
The OpenHands + pinned-model wiring is a STUB (`mode="dummy"`), so the harness can be
proven end-to-end (isolation + valid trajectory captured, the WS2 DoD) WITHOUT a model.
Replace `_run_openhands` with the real driver once the model + image are pinned (spec §13).
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(__file__))
from sandbox_runner import run_in_sandbox, image_digest  # noqa: E402

_now = lambda: _dt.datetime.now(_dt.timezone.utc).isoformat()


def _validate_trajectory(traj: dict) -> dict:
    try:
        import jsonschema
        with open(os.path.join(os.path.dirname(__file__), "..", "contracts",
                               "trajectory_schema.json"), encoding="utf-8") as fh:
            jsonschema.validate(traj, json.load(fh))
    except ImportError:
        md = traj["harness_metadata"]
        assert md["network_disabled"] is True and md["mounts"] == [], "isolation invariants violated"
        for k in ("task_id", "attempt_id", "final_patch", "action_log", "visible_test_results"):
            assert k in traj, f"missing {k}"
    return traj


def _run_dummy(task: dict, image: str, seed: int) -> dict:
    """Stub agent: touches a file and runs a trivial visible test IN the sandbox.
    Proves isolation + trajectory capture without a model."""
    cmd = ("echo 'print(1+1)' > /work/patch_probe.py && "
           "python /work/patch_probe.py && echo 'PASS: 1 passed'")
    res = run_in_sandbox(image, cmd, timeout_s=120)
    passed = 1 if "PASS" in res.stdout else 0
    return {
        "final_patch": "",  # dummy makes no real patch
        "action_log": [
            {"step": 0, "action": "write_file", "args": {"path": "/work/patch_probe.py"}, "observation": "ok"},
            {"step": 1, "action": "run_tests", "args": {}, "observation": res.stdout.strip()},
        ],
        "visible_test_results": {"passed": passed, "failed": 0 if passed else 1, "raw": res.stdout},
        "_sandbox": res.to_dict(),
    }


def run_agent(task: dict, image: str = "python:3.11-slim", seed: int = 0, mode: str = "dummy") -> dict:
    if mode != "dummy":
        raise NotImplementedError("OpenHands + pinned-model driver not wired yet (spec §13).")
    started = _now()
    body = _run_dummy(task, image, seed)
    traj = {
        "task_id": task.get("id", "unknown"),
        "attempt_id": f"{task.get('id','t')}-s{seed}-{uuid.uuid4().hex[:8]}",
        "final_patch": body["final_patch"],
        "action_log": body["action_log"],
        "visible_test_results": body["visible_test_results"],
        "harness_metadata": {
            "model_id": f"DUMMY-STUB(mode={mode})",
            "image_digest": image_digest(image),
            "base_commit": task.get("base_commit", ""),
            "seed": seed,
            "network_disabled": True,
            "mounts": [],
            "started_at": started,
            "ended_at": _now(),
        },
    }
    return _validate_trajectory(traj)


if __name__ == "__main__":
    demo_task = {"id": "demo-task-0", "base_commit": "0" * 40}
    t = run_agent(demo_task)
    print(json.dumps({k: v for k, v in t.items() if k != "action_log"}, indent=2))
    print("\nTRAJECTORY: valid & schema-checked (dummy agent, real sandbox).")
