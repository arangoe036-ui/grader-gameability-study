"""rollout.py — N attempts/task, shardable, isolated write-once output dirs.

Build plan §1 + §3 WS9: "N = 8-16 attempts/task in the sandbox. Shard by task; each shard
writes to its own results/run-<ts>/shard-<k>/. No shared mutable state." Immutable results (§5).

STATUS: sharding + isolation + write-once semantics are DONE. Uses run_agent(mode="dummy")
until the real model driver lands. Massively parallel rollouts (one worker per shard) are the
Phase C win — NOT run now (Phase C is gated behind the Tier 0 human review, §3/§6).
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from run_agent import run_agent  # noqa: E402
from provenance import provenance  # noqa: E402

_RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")


def _run_dir(ts: str | None = None) -> str:
    ts = ts or _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return os.path.join(_RESULTS, f"run-{ts}")


def rollout(tasks: list[dict], n_attempts: int = 8, shard_index: int = 0,
            n_shards: int = 1, run_dir: str | None = None, mode: str = "dummy") -> str:
    """Run n_attempts per task for this shard's slice; write-once to shard-<k>/."""
    assert 8 <= n_attempts <= 16 or mode == "dummy", "spec: N in [8,16] (relaxed for dummy)"
    run_dir = run_dir or _run_dir()
    shard_dir = os.path.join(run_dir, f"shard-{shard_index}")
    if os.path.exists(shard_dir):
        raise FileExistsError(f"write-once violated: {shard_dir} exists (results are immutable, §5)")
    os.makedirs(shard_dir)

    my_tasks = tasks[shard_index::n_shards]  # deterministic shard slice
    manifest = {"shard": shard_index, "n_shards": n_shards, "n_attempts": n_attempts,
                "mode": mode, "seeds": list(range(n_attempts)),
                "provenance": provenance(image="python:3.11-slim",
                                         seeds={"attempt_seeds": list(range(n_attempts))}),
                "tasks": []}
    for task in my_tasks:
        for seed in range(n_attempts):
            traj = run_agent(task, seed=seed, mode=mode)
            out = os.path.join(shard_dir, f"{traj['attempt_id']}.json")
            with open(out, "w", encoding="utf-8") as fh:
                json.dump(traj, fh, indent=2)
        manifest["tasks"].append(task.get("id"))
    with open(os.path.join(shard_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    return shard_dir


if __name__ == "__main__":
    demo = [{"id": f"demo-{i}", "base_commit": "0" * 40} for i in range(3)]
    d = rollout(demo, n_attempts=2)  # tiny dummy rollout
    print(f"wrote shard: {d}")
    print("files:", sorted(os.listdir(d)))
