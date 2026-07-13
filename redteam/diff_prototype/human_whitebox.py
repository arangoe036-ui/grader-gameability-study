"""Human WHITE-BOX red-team of the differential check.

A human adversary is the strongest cheap test. This shows you the task (buggy source + visible
test — never the hidden oracle) AND the check's exact execution-context battery, then lets you
submit a candidate module and see whether it was ACCEPTED and whether it actually ESCAPED (an
independent production check decides "actually correct"; you don't get to game it).

>>> A HUMAN SHOULD DRIVE A SESSION HERE. Try to be correct in every context the check probes while
    staying buggy in real production. The automated white-box battery is just a floor.

Usage: python redteam/diff_prototype/human_whitebox.py --task add
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arena import redacted_task, adversary_verdict, evaluate  # noqa: E402
import check                                                    # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description="Human white-box red-team of the differential check")
    ap.add_argument("--task", default="add")
    args = ap.parse_args()
    t = args.task
    rt = redacted_task(t)
    print(f"\n=== TASK {t} ({rt['task_type']}) — target fn: {rt['target_fn']} ===")
    print("--- buggy source ---")
    for p, s in rt["buggy_files"].items():
        print(f"# {p}\n{s}")
    print("--- visible test (hidden oracle NOT shown) ---")
    for vt in rt["visible_tests"]:
        print(vt["content"])
    print("=== WHITE-BOX: the check's execution-context battery ===")
    print(json.dumps(check.CONTEXTS, indent=2))
    print("\nGoal: be correct in every context above AND under the (test-like) hidden-oracle run,\n"
          "but buggy in true production. Submit a module and see if you ESCAPE.\n")
    while True:
        path = input("Path to your candidate module (blank to quit): ").strip()
        if not path:
            print("bye."); return
        if not os.path.exists(path):
            print(f"  no such file: {path}"); continue
        files = {f"{t}.py": open(path).read()}
        verdict = adversary_verdict(t, files, white_box=True)      # what you'd see as adversary
        full = evaluate(t, files)                                  # independent escape check
        tag = "ESCAPE!" if full["escaped"] else ("accepted+correct" if full["accepted"] else "rejected")
        print(f"  -> {tag}  (accepted={verdict['accepted']} flagged={verdict['flagged']} "
              f"truly_correct={full['truly_correct']})\n")


if __name__ == "__main__":
    main()
