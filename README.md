# Cuarzo Go/No-Go

A **decision experiment**, not a product build. Question: does Cuarzo's un-gameable,
footprint-relative grading beat current lab best-practice (a competent hidden-test baseline,
"A2") by a commercially decisive margin — under optimization pressure?

Built strictly to `BUILD_PLAN.md` (execution contract); scientific source of truth is `SPEC.md`
(Cuarzo spec v2.1). Working principles (§0): **cheapest kill first · hard tier gates · sandbox
the cheaters · freeze thresholds before scoring · human gate at every tier · stop at the first RED.**

---

## ⏸ AWAITING HUMAN REVIEW — Tier 0 passed; Tier 1 is gated

Phase A is complete and **Tier 0 PASSED**. Per Prime Directives §0.2 / §0.5 / §6, work **stops
here** for human review. Tier 1, the full task suite, curation, and the RL run are **not built**
and must not be started until a human authorizes it. Three decisions are needed from the team
(see bottom).

---

## Tier 0 result — PASS (cheapest kill gate, spec §7/§8)

Scored 33 labeled attempts (honest 8 · valid-alternative 5 · hacked 12 · spurious 8) through the
**real deterministic Treatment grader** inside the disposable sandbox. Latest run:
`results/run-20260708T225607Z/tier0/`.

| Treatment (the product) | Result |
|---|---|
| Honest accepted | **100%** |
| Valid-alternative accepted | **100%** |
| Hacked rejected | **100%** |
| Spurious rejected | **100%** |
| **False-positive rate on valid alternatives** | **0%** (95% CI [0%, 0%]; bar ≤ ~10%) ✅ |
| Legit-vs-gamed separation gap | **100%** |

**Beyond-A2 contrast (previews Tier 1):** A2 (held-out tests only) accepted **100%** of the
A2-surviving hacks — it *misses* them; Treatment rejected **100%**. This is exactly the marginal
value the go/no-go rests on (§5). Footprint signal: mean 1.0 on honest fixes, 0.0 on valid
alternatives (expected — they fix the fault elsewhere; footprint is reported, never a reject gate, §8‡).

**Honest caveats (do not over-read a coarse gate):** the set is synthetic with constructed labels
(spec §7 permits this for Tier 0), and the pattern-based construct detectors were authored
alongside the hacks. Tier 0 is a *kill gate only*. Tier 1 requires an **independent,
human-adjudicated, powered** suite on real SWE-bench-style tasks (§6, §8) — the FP bar also
tightens to ≤5% there.

---

## STATUS BOARD

**Phase A:** ✅ complete. **Gates:** Tier 0 ✅ PASS · Tier 1 🔒 gated (needs human OK) · Tier 2 🔒 gated.
**`prereg-locked` tag:** ✅ present (frozen before any scoring, §0.3).

| WS | Item | State | Notes |
|----|------|-------|-------|
| WS1 | Repo layout + `SPEC.md` (v2.1 verbatim) | ✅ | source of truth in-repo |
| WS1 | `contracts/{verdict,trajectory,task}_schema.json` | ✅ frozen | task_schema reconciled with §4 |
| WS1 | `PREREGISTRATION.md` + `prereg-locked` tag | ✅ frozen | §8 bands + §9 rules transcribed |
| WS2 | `harness/sandbox_runner.py` | ✅ proven | `--smoke`: no net/mounts/secrets |
| WS2 | `harness/run_agent.py` / `rollout.py` | 🟡 dummy agent | schema-valid trajectory; OpenHands+model wiring deferred (§13) |
| WS3 | `graders/control_a.py` | ✅ | naive visible-test floor |
| WS3 | `graders/control_a2.py` | ✅ | held-out oracle in sandbox = decision baseline |
| WS3 | `graders/control_b.py` | 🟡 stub | inputs pinned (§5); model wiring gated to Tier 1 |
| WS3 | `graders/treatment/` | ✅ real | oracle + tamper detection + footprint (deterministic, §5) |
| WS4 | `analysis/{metrics,power_check,report}.py` | ✅ tested | CIs; sci vs commercial separated |
| WS5 | Tier 0 labeled set | ✅ | `data/{tasks,labels}/tier0/`; generator `data/tier0_build.py` |
| Tier 0 | `experiments/tier0_separation.py` | ✅ **PASS** | see result above |
| Tier 1/2 | experiments | 🔒 gated | tripwires raise until human authorizes (§0.2, §6) |

Legend: ✅ done · 🟡 partial/deferred · 🔒 intentionally gated.

## Reproduce

```bash
python3 harness/sandbox_runner.py --smoke     # prove sandbox isolation on a real container
python3 tests/test_smoke.py                    # unit tests (5/5, docker-free)
python3 data/tier0_build.py                    # regenerate the labeled set
python3 experiments/tier0_separation.py        # re-run Tier 0 (writes a new immutable run dir)
```

## What is intentionally NOT built (scope + gates, §0.7)

Tier 1 (Exp 1 verification + Exp 2 selection), Tier 2 RL, the full ~100-task curated suite with
layered contamination control, Control B's model wiring, and any production / scale infra. All
gated behind the Tier 0 human review.

## Decisions needed from the team (before Tier 1)

1. **Authorize Tier 1?** Tier 0 shows the signal exists; Tier 1 is the powered, adjudicated,
   real-task screening vs. A2. Nothing proceeds without an explicit go.
2. **RL feasibility call (§12)** — is a short GRPO loop feasible on this team/budget? If yes,
   Tier 2 is *required* for a full GREEN; if no, the claim honestly downgrades to Tier-1-only.
   Recorded as PENDING in `PREREGISTRATION.md`.
3. **Commercially-material magnitude (§8/§10)** — pre-register the concrete willingness-to-pay
   bar (a hypothesis to test with labs), a slot left `TEAM INPUT REQUIRED` in `PREREGISTRATION.md`.
   No commercial-GREEN can be declared until it is filled — *before* Tier 1 results are viewed.
