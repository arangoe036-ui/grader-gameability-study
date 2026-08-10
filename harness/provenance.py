"""provenance.py — capture what a run was actually run WITH (Prime Directive §0.6).

BUILD_PLAN §0.6 and PREREGISTRATION.md ("Fixed design") require pinning container images by
digest and logging seeds, so a result can be tied to the exact code and image that produced it.
The two committed runs under `results/` predate this module and therefore carry NO image digest,
git commit or interpreter version — that gap is stated in README.md and cannot be repaired after
the fact (results are write-once, §5). Every future result dict embeds `provenance(...)`.

Note the images are still referenced by the MUTABLE tag `python:3.11-slim` at every call site
(graders/oracle_runner.py, redteam/diff_prototype/check.py, harness/run_agent.py). This module
records the digest that tag resolved to at run time, which is what makes the record meaningful;
it does not by itself make the reference immutable.

Pure stdlib + the `docker` CLI.
"""
from __future__ import annotations

import os
import platform
import subprocess
import sys
from typing import Optional

_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def _git(*args: str) -> str:
    try:
        p = subprocess.run(["git", "-C", _ROOT, *args], capture_output=True, text=True)
    except OSError:
        return ""
    return p.stdout.strip() if p.returncode == 0 else ""


def git_state() -> dict:
    """HEAD commit + whether the working tree was dirty when the run started."""
    head = _git("rev-parse", "HEAD")
    if not head:
        return {"commit": None, "dirty": None,
                "note": "not a git checkout (or git unavailable): code version unrecorded"}
    return {"commit": head, "short": head[:7], "dirty": bool(_git("status", "--porcelain"))}


def provenance(image: Optional[str] = None, seeds: Optional[dict] = None) -> dict:
    """The provenance block every result dict should carry."""
    out = {
        "git": git_state(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "seeds": dict(seeds or {}),
    }
    if image:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from sandbox_runner import image_digest  # noqa: E402  (local import: docker CLI optional)
        digest = image_digest(image)
        out["image"] = {"tag": image, "digest": digest or None,
                        "note": None if digest else
                        "digest unavailable (image not pulled / docker absent) — run NOT pinned"}
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(provenance(image="python:3.11-slim", seeds={"meta_seed": 0}), indent=2))
