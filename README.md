# Cuarzo Go/No-Go

A **decision experiment**, not a product build. Question: does Cuarzo's un-gameable,
footprint-relative grading beat current lab best-practice (a competent hidden-test baseline,
"A2") by a commercially decisive margin — under optimization pressure?

Built strictly to `BUILD_PLAN.md` (execution contract); scientific source of truth is `SPEC.md`
(Cuarzo spec v2.1). Working principles (§0): **cheapest kill first · hard tier gates · sandbox
the cheaters · freeze thresholds before scoring · human gate at every tier · stop at the first RED.**

---

## 🛑 FOLLOW-UP: behavioral tamper check does NOT survive a white-box adversary

After the Step 1 RED, a cheap decision experiment asked whether a **behavioral/differential** tamper
check (run each patch in multiple execution contexts; flag cross-context behavior divergence) could
survive an adaptive adversary. Throwaway prototype under `redteam/diff_prototype/`; **not** wired
into `graders/treatment/`. Artifacts: `results/redteam-diff-20260713T152022Z/`.

| Condition | Escape rate (accepted-while-production-buggy) | 95% CI | tasks |
|---|---|---|---|
| **Black-box** (adversary doesn't know the contexts) | **0%** — 0/16 | [0%, 0%] | 0/8 |
| **White-box** (adversary given the context battery) | **100%** — 16/16 | [100%, 100%] | 8/8 |

Honest fixes accepted & correct (no false positives). **Reading (pre-registered before running):
white-box escape is systematic → strong deterministic un-gameability is likely DEAD.** The check
*does* stop naive/black-box hacks (a real gain over the Step 1 blocklist), so the honest residual is
an **empirical "more-robust" grader, not an un-gameable one**. Root cause is structural: any fixed,
adversary-knowable battery of contexts is routed around by code that special-cases exactly those
contexts — the Step 1 lesson one level up. **Do NOT build the redesign** (pre-registered); the
three-way claim choice (absolute un-gameability / empirical most-robust / stop) is a human decision.
Full verdict + fairness guarantee + caveats: `results/redteam-diff-20260713T152022Z/VERDICT.md`.

---

## 🛑 STEP 1 RED (prior) — static-blocklist Treatment is gameable black-box

A black-box red-team of the **existing** Treatment grader found a **systematic, repeatable way
past it**. Per the plan's cheapest-kill-first rule, this is a RED on un-gameability: **the Tier 1
suite was NOT built.** Treatment, as implemented, is gameable — so the expensive powered/
adjudicated screen is not worth running until the mechanism is rethought (a human decision).

### Red-team result (`results/redteam-20260708T235339Z/`, harness in `redteam/`)
An adversary with **black-box** access (submit patch → get verdict; no access to
`graders/treatment/`) tried to get *production-buggy* patches **accepted**. An independent
behavioral **meta-oracle** (fresh inputs, non-test context) objectively decides whether an
accepted patch is actually correct — so the red-team can only make Treatment look *worse*, never
falsely better.

| Metric | Result |
|---|---|
| **Escape rate** (hacks accepted while actually wrong) | **80%** — 32/40 (95% bootstrap CI **[65%, 92.5%]**) |
| **Distinct tasks escaped** | **8 / 8** |
| Test-context channels that escape on *every* task | **4 of 5** (`main_file`, `inspect_stack`, `orig_argv`, `argv_getattr`) |
| Honest controls (accepted & truly correct) | ✅ all — the arena is fair |

**Mechanism:** Treatment's tamper detection is a **fixed substring/regex blocklist**. A
reward-channel hack that runs the correct fix *only when it detects the test harness* — via any
channel not on the blocklist (e.g. reading `__main__.__file__`, scanning `inspect.stack()`,
`sys.orig_argv`, or aliasing `sys.argv` through `getattr`) — passes the hidden oracle **and draws
zero flags**, while being buggy in production. Only the one naive channel that contains a
blocklisted substring (`sys.argv`) is caught. **A static blocklist cannot be "un-gameable":** the
space of test-context signals is unbounded.

**Observation for the human (NOT built — a redesign decision):** the very technique used to
*detect* the escapes — differential/behavioral testing across contexts on fresh inputs — caught
100% of them. A behavioral tamper check is a plausible path, but changing the mechanism is a
human call, not an autonomous one.

---

## Context: Tier 0 "PASS" cleared only the floor (near-tautological)

Tier 0 scored 100% separation / 0% FP (`results/run-20260708T225607Z/tier0/`). But the Tier 0
detectors were authored **alongside** the hacks they caught, so that sweep was near-tautological —
it cleared the cheapest gate, nothing more. Step 1 is the real un-gameability test, and Treatment
**failed** it. This is the framing the resume plan insisted on: a high score against
built-to-match hacks is worthless; **independence is the quality bar**, and the black-box
red-team supplies it.

---

## STATUS BOARD

**Phase A:** ✅ complete. **Gates:** Tier 0 ✅ (floor only) · **Step 1 red-team 🛑 RED** · **behavioral-check probe 🛑 white-box folds (BB 0% / WB 100%)** · Tier 1 ⛔ NOT built (killed) · Tier 2 🔒 gated.
**`prereg-locked`:** ✅ present & untouched (thresholds FROZEN; commercial bar still `TEAM INPUT REQUIRED`).

| WS | Item | State | Notes |
|----|------|-------|-------|
| WS1 | Contracts + `SPEC.md` (v2.1) + `PREREGISTRATION.md` | ✅ frozen | prereg untouched this session |
| WS2 | `harness/sandbox_runner.py` | ✅ proven | all grading/red-team runs sandboxed (§0.4) |
| WS3 | `graders/{control_a,control_a2}.py` | ✅ | A2 = decision baseline |
| WS3 | `graders/control_b.py` | 🟡 stub | inputs pinned (§5); gated to Tier 1 |
| WS3 | `graders/treatment/` | ✅ real, **🛑 gameable** | passed Tier 0 floor; **escaped 80% black-box (Step 1)** |
| WS4 | `analysis/{metrics,power_check,report}.py` | ✅ tested | CIs; sci vs commercial separated |
| WS5 | Tier 0 labeled set | ✅ | `data/{tasks,labels}/tier0/` |
| — | **`redteam/` (Step 1 harness)** | ✅ | black-box + meta-oracle + battery + human mode |
| — | **`redteam/diff_prototype/` (behavioral-check probe)** | ✅ throwaway | BB 0% / WB 100% escape; not integrated; verdict: deterministic un-gameability likely dead |
| Tier 0 | `experiments/tier0_separation.py` | ✅ PASS (floor) | reframed as near-tautological |
| Tier 1 | Exp 1 / Exp 2 suite | ⛔ **NOT built** | RED at Step 1 — do not build until mechanism rethought |
| Tier 2 | RL | 🔒 gated | not assessed; downstream of a killed gate |

Legend: ✅ done · 🟡 partial/deferred · 🛑 red/kill · ⛔ not built (by decision) · 🔒 gated.

## Reproduce

```bash
python3 redteam/run_auto.py                    # STEP 1: automated black-box red-team (writes immutable artifact)
python3 redteam/human_redteam.py --task add    # STEP 1: human red-team (a person should drive this)
python3 experiments/tier0_separation.py        # Tier 0 floor (context)
python3 tests/test_smoke.py                     # unit tests (docker-free)
```

## What is intentionally NOT built (scope + gates, §0.7)

The Tier 1 powered/adjudicated suite (Exp 1 + Exp 2), Tier 2 RL, the full curated task set, and
any production/scale infra. Step 1 RED means none of these should be built until a human decides
whether/how to rethink Treatment's tamper detection.

## Decision needed from the team

1. **Treatment is gameable black-box as written.** Decide: rethink the un-gameability mechanism
   (e.g. behavioral/differential tamper detection instead of a static blocklist), or accept the
   weaker claim. Only after a redesign is it worth building the Tier 1 suite.
2. Prereg stays **FROZEN**; the commercial-magnitude bar remains `TEAM INPUT REQUIRED` — not set.
3. Tier 2 RL feasibility was **not** assessed (downstream of a killed gate); revisit only if the
   mechanism is fixed and Tier 1 later passes.
