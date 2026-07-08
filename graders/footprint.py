"""Footprint localization — region/signal overlap, NOT exact-line-match (spec §8‡).

A valid alternative fix that resolves the true fault at a different location counts as correct,
so footprint is a *reported signal*, never a reject gate (enforced in Treatment).
"""
from __future__ import annotations

import difflib
from typing import Dict, Set


def changed_base_lines(base: str, new: str) -> Set[int]:
    """1-indexed BASE line numbers changed or deleted by the edit (insertions attributed
    to the boundary base line)."""
    b, n = base.splitlines(), new.splitlines()
    changed: Set[int] = set()
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=b, b=n, autojunk=False).get_opcodes():
        if tag in ("replace", "delete"):
            changed.update(range(i1 + 1, i2 + 1))
        elif tag == "insert":
            changed.add(max(1, i1))
    return changed


def footprint_overlap(task: dict, attempt: dict) -> float:
    """Fraction of fault_footprint regions the attempt's source edits touch (base coords)."""
    regions = task.get("fault_footprint", [])
    if not regions:
        return 0.0
    base_files: Dict[str, str] = task.get("files", {})
    new_files: Dict[str, str] = attempt.get("files", {})
    matched = 0
    for reg in regions:
        f = reg["file"]
        base = base_files.get(f, "")
        new = new_files.get(f, base)
        changed = changed_base_lines(base, new)
        lo, hi = reg.get("start_line"), reg.get("end_line")
        if lo and hi:
            if any(lo <= ln <= hi for ln in changed):
                matched += 1
        elif changed:  # symbol-only region: any change in the file counts (coarse)
            matched += 1
    return matched / len(regions)
