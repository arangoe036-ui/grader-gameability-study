# Cuarzo Go/No-Go

A **decision experiment**, not a product build. Question: does Cuarzo's un-gameable,
footprint-relative grading beat current lab best-practice (a competent hidden-test baseline,
"A2") by a commercially decisive margin — under optimization pressure?

Built strictly to `BUILD_PLAN.md` (the execution contract). The scientific source of truth is
the v2 spec — see the ⛔ blocker below. Working principles (build plan §0): **cheapest kill
first · hard tier gates · sandbox the cheaters · freeze thresholds before scoring · human gate
at every tier · stop at the first RED.**

---

## ⛔ BLOCKER — the v2 spec was not provided

`cuarzo-benchmark-go-no-go-spec-v2.md` (the "scientific source of truth", required by build
plan §1 and the §6 kickoff) **was not in the handoff**, and neither was the original spec it
revises. Only the build plan and a *revisions* companion were available.

Everything the build plan **fully specifies on its own** is built and tested. Everything that
requires the spec's exact content is left as an **honest, clearly-marked placeholder** — I did
**not** fabricate spec text, §8 thresholds, or the Treatment grader, and I did **not**
`git tag prereg-locked`. Drop the v2 spec in and follow `SPEC.md` → "To unblock".

---

## STATUS BOARD

**Phase:** A (Foundation) — partially complete, blocked on the missing v2 spec.
**Gates:** Tier 0 ❌ not run · Tier 1 🔒 gated · Tier 2 🔒 gated. `prereg-locked` tag: **absent** (correct).

| WS | Item | State | Notes |
|----|------|-------|-------|
| WS1 | Repo layout (§1) | ✅ done | matches §1; `tests/` added for WS4 unit tests |
| WS1 | `contracts/verdict_schema.json` | ✅ frozen | fully specified in build plan §2 |
| WS1 | `contracts/trajectory_schema.json` | ✅ frozen | §2/§68; enforces net-off + no-mounts invariants |
| WS1 | `contracts/task_schema.json` | 🟡 DRAFT | needs reconciliation with **spec §4**; blocks curation only |
| WS1 | `SPEC.md` | ⛔ blocked | verbatim copy of v2 spec — file not provided |
| WS1 | `PREREGISTRATION.md` + `prereg-locked` tag | ⛔ blocked | needs **spec §8**; must not invent thresholds (§0.3) |
| WS2 | `harness/sandbox_runner.py` | ✅ done + **proven** | `--smoke` passes: no net, no mounts, writable workdir, clean env |
| WS2 | `harness/run_agent.py` | 🟡 real sandbox, dummy agent | emits schema-valid trajectory; OpenHands+model wiring deferred (§13) |
| WS2 | `harness/rollout.py` | 🟡 scaffold | sharded, write-once; runs dummy agent |
| WS3 | `graders/control_a.py` | ✅ done | naive visible-test floor (real; no detection by design) |
| WS3 | `graders/control_a2.py` | 🟡 stub | held-out sandbox exec deferred to spec §4/§5 |
| WS3 | `graders/control_b.py` | 🟡 stub | LLM-judge; **inputs to pin** (review note 4) |
| WS3 | `graders/treatment/` | ⛔ stub (refuses) | crown-jewel IP; needs v2 spec — must not fabricate |
| WS4 | `analysis/metrics.py` | ✅ done + tested | confusion matrix, catch rates, footprint match, bootstrap CIs |
| WS4 | `analysis/power_check.py` | ✅ done + tested | sizes the A2-surviving hack sub-bucket (review note 1) |
| WS4 | `analysis/report.py` | ✅ done + tested | scientific vs commercial separated; warns while prereg unfrozen |
| WS5 | small labeled set | ⛔ not started | Phase B; needs spec + human labels |
| Tier 0 | `experiments/tier0_separation.py` | 🟡 guarded | refuses to run until prereg+Treatment+labels exist |
| Tier 1/2 | experiments | 🔒 gated | tripwires raise `NotImplementedError` (§0.2, §6) |

Legend: ✅ done · 🟡 partial/scaffold · ⛔ blocked on spec · 🔒 intentionally gated.

---

## Proven now (no spec required)

```bash
python3 harness/sandbox_runner.py --smoke   # PROVE isolation on a real container
python3 harness/run_agent.py                # one agent -> one schema-valid trajectory
python3 tests/test_smoke.py                  # analysis + graders unit tests (5/5)
python3 analysis/power_check.py              # sub-bucket sizing table
```

The sandbox smoke test asserts all four Prime-Directive §0.4 guarantees: network egress
blocked, no host bind-mounts, workdir writable (realistic condition), and no host secrets
leaked (image-declared env like `GPG_KEY` is correctly excluded).

## What is intentionally NOT built (scope discipline, §0.7)

Tier 1/Tier 2 experiments, the full task suite / curation, the RL run, and any production or
scale infrastructure. These are gated behind tier reviews and, first, the missing spec.

## Layout
See `BUILD_PLAN.md` §1. `REVISIONS.md` is the v2-review companion (its four notes are folded
into the build plan §7 and referenced throughout the code).
