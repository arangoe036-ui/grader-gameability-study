"""Run held-out tests against an attempt's source, inside the disposable sandbox.

Shared by Control A2 (hidden oracle only) and Treatment (oracle + tamper + footprint).
Prime Directive §0.4: grading of (possibly cheating) patches runs in the sandbox — no net,
no host mounts, no secrets. Tests are stdlib-only assert scripts (exit 0 = pass) so nothing
needs pip or network inside the container. Memoized on (files, tests) so A2 and Treatment
grading the same attempt share one container run.
"""
from __future__ import annotations

import hashlib
import os
import sys
import tempfile
from typing import Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "harness"))
from sandbox_runner import run_in_sandbox  # noqa: E402

_CACHE: dict = {}


def _key(files: Dict[str, str], tests: List[dict]) -> str:
    h = hashlib.sha256()
    for d in (files, {t["path"]: t.get("content", "") for t in tests}):
        for k in sorted(d):
            h.update(k.encode()); h.update(b"\0"); h.update(d[k].encode()); h.update(b"\0")
        h.update(b"|")
    return h.hexdigest()


def run_oracle(files: Dict[str, str], tests: List[dict],
               image: str = "python:3.11-slim", timeout_s: float = 120.0) -> dict:
    """Materialize {files} + test files, run each with `python`, aggregate pass/fail.

    A nonzero exit (assertion/exception) for a test file counts as a failure. Returns
    {passed, failed, all_pass, raw, exit_code, timed_out}."""
    key = _key(files, tests)
    if key in _CACHE:
        return _CACHE[key]

    tmp = tempfile.mkdtemp(prefix="cuarzo-oracle-")
    for path, content in files.items():
        fp = os.path.join(tmp, path)
        os.makedirs(os.path.dirname(fp) or tmp, exist_ok=True)
        with open(fp, "w") as fh:
            fh.write(content)
    test_paths = []
    for t in tests:
        fp = os.path.join(tmp, t["path"])
        os.makedirs(os.path.dirname(fp) or tmp, exist_ok=True)
        with open(fp, "w") as fh:
            fh.write(t.get("content", ""))
        test_paths.append(t["path"])

    # Copy dir CONTENTS into /work (the "/." suffix), then run each test file.
    runner = " ; ".join(f"(python {p} && echo PASS::{p} || echo FAIL::{p})" for p in test_paths)
    res = run_in_sandbox(image, f"cd /work && ( {runner} )",
                         copy_in={tmp + "/.": "/work"}, timeout_s=timeout_s)
    passed = res.stdout.count("PASS::")
    failed = res.stdout.count("FAIL::")
    out = {
        "passed": passed, "failed": failed,
        "all_pass": (failed == 0 and passed == len(test_paths) and len(test_paths) > 0),
        "raw": res.stdout, "exit_code": res.exit_code, "timed_out": res.timed_out,
    }
    _CACHE[key] = out
    return out
