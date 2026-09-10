# Grader Gameability Study

**A pre-registered black-box red team against my own code grader broke it in 80% of attempts** — 95% bootstrap CI [65%, 92.5%]. That establishes something stronger than "the blocklist had gaps": a static tamper blocklist is *structurally* routable, so the expensive downstream tiers were never worth building.

The result is trustworthy because the experiment was built so it could not flatter itself. Thresholds and the reading of the outcome were frozen in a pre-registration **before any data was collected**, and an independent behavioural meta-oracle decided correctness — so the harness could only ever make the grader look *worse*, never falsely better.

A **decision experiment**, not a product build. Question: does an un-gameable,
footprint-relative grading beat current lab best-practice (a competent hidden-test baseline,
"A2") by a commercially decisive margin — under optimization pressure?

Built strictly to `BUILD_PLAN.md` (execution contract); scientific source of truth is `SPEC.md`
(Cuarzo spec v2.1). Working principles (§0): **cheapest kill first · hard tier gates · sandbox
the cheaters · freeze thresholds before scoring · human gate at every tier · stop at the first RED.**

---

## How to read this repo

**The negative result is the deliverable.** This experiment was designed to kill a bad idea cheaply
rather than to ship a grader, and it succeeded: the red-team found a systematic escape, so the
expensive downstream tiers were **deliberately never built**. If you open `experiments/tier1_*.py`
and find `NotImplementedError` at module level, that is the stop rule working as designed — not
abandoned work. (`graders/control_b.py` is a declared stub that returns a placeholder verdict; it
raises nothing.) The `STATUS BOARD` below marks every component's real state, including stubs and
including the one path that is genuinely unfinished.

What this repo demonstrates, if you're evaluating the engineering and the method:

- **Pre-registration before scoring** — `PREREGISTRATION.md` freezes thresholds and the reading of
  the outcome *before* any data is collected, so the conclusion can't be fit to the result after the fact.
  **Read the scope limit at [Pre-registration: what it does and does not cover](#pre-registration-what-it-does-and-does-not-cover) before relying on this** — it holds for
  Tier 0/1/2 and for the follow-up probe, but the Step 1 headline below has *no committed
  pre-registration.*
- **Adversarial self-evaluation** — the red-team attacks *our own* grader black-box, with an
  independent behavioral meta-oracle deciding correctness so the harness can only make the grader
  look worse, never falsely better.
- **Quantified, honest reporting** — escape rates with 95% bootstrap CIs, plus exact
  (Clopper-Pearson) intervals wherever the sample is too small or too degenerate for a bootstrap
  to say anything, fairness controls
  (honest patches must still be accepted), and a documented root cause instead of a headline number.
- **Reproducible artifacts** — every run writes an immutable timestamped directory under `results/`,
  and all grading and adversarial code executes inside a proven sandbox (`harness/sandbox_runner.py`).
- **Knowing when to stop** — the pre-registered reading said a fixed, adversary-knowable check is
  structurally routable, so the redesign was explicitly *not* built. That call was left to a human.

**Scope:** ~2.3K lines of Python plus a frozen spec and pre-registration. This is a research
artifact, not a library or a product — expect experiment scripts and decision records, not an API.

---

## 🛑 FOLLOW-UP: behavioral tamper check does NOT survive a white-box adversary

After the Step 1 RED, a cheap decision experiment asked whether a **behavioral/differential** tamper
check (run each patch in multiple execution contexts; flag cross-context behavior divergence) could
survive an adaptive adversary. Throwaway prototype under `redteam/diff_prototype/`; **not** wired
into `graders/treatment/`. Artifacts: `results/redteam-diff-20260713T152022Z/`.

| Condition | Escape rate (accepted-while-production-buggy) | 95% CI | tasks |
|---|---|---|---|
| **Black-box** (adversary doesn't know the contexts) | **0%** — 0/16 | **[0%, 20.6%]** | 0/8 |
| **White-box** (adversary given the context battery) | **100%** — 16/16 | **[79.4%, 100%]** | 8/8 |

Those are exact Clopper-Pearson intervals. The committed `results.json` records `[0.0, 0.0]` and
`[1.0, 1.0]`, which are **not intervals** — a percentile bootstrap on a zero-variance sample can
only return its own point estimate. The artifact is left as it was written; the corrected intervals
are computed by `analysis.metrics.clopper_pearson` and reported here.

Honest fixes accepted & correct (no false positives). **Reading (pre-registered before running):
white-box escape is systematic → strong deterministic un-gameability is likely DEAD.** The check
*does* stop naive/black-box hacks, so the honest residual is an **empirical "more-robust" grader,
not an un-gameable one** — but see the limit below before reading that as a measured gain.

> **The pre-registered `bb_near_zero` criterion is NOT met.** `PREREGISTERED_READING.md:12` defines
> "near-zero" as a pooled escape-rate 95% CI upper bound below 0.10. The exact interval at n=16 is
> [0%, 20.6%], so **16 trials cannot establish a rate below 10%** and this criterion fails on its own
> terms. The white-box direction is unaffected: 16/16 is systematic under any interval, and that is
> the half the conclusion rests on. Root cause is structural: any fixed,
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
| **Escape rate** (hacks accepted while actually wrong) | **80%** — 32/40 (95% bootstrap CI **[65%, 92.5%]**; exact **[64.4%, 90.9%]**) |
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

**Two limits on calling this a pre-registered PASS, stated plainly:**

1. `PREREGISTRATION.md:42-43` (transcribing `SPEC.md:117`) requires the sweep to use *"a slice **not**
   used to develop/tune the verifier"*. That condition was **not met** — the detectors were authored
   alongside the hacks, which `verdict.json` caveat 2 already records — and
   `experiments/tier0_separation.py` never checked the precondition before writing `"passed": true`.
   Treat the artifact's `PASS` as "cleared the floor", not as a satisfied pre-registered gate.
2. The operational meaning of "separates clearly" was set **in the scoring script**, not frozen:
   `tier0_separation.py` defines `CLEAR_SEP_ACCEPT = 0.90` and `CLEAR_SEP_GAMED = 0.10`, and neither
   number appears in `PREREGISTRATION.md` or `SPEC.md`. Those thresholds are **post-hoc**.

The reported "false-positive rate 0% (95% CI [0%, 0%]; bar ≤ 10%)" is also on **n = 5** valid
alternatives. The exact upper bound there is ~52%, so a ≤10% bar is **unresolvable** at that sample
size — one false positive would read as 20%.

---

## Pre-registration: what it does and does not cover

This repo leans on pre-registration as its credibility mechanism, so here is the exact scope.

**Covered by the committed `PREREGISTRATION.md`:** Tier 0, Tier 1 and Tier 2 (its decision rule is
§9). **Covered by a committed pre-registered reading:** the behavioral-check follow-up
(`PREREGISTERED_READING.md`).

**NOT covered: the Step 1 red-team — the headline result of this repository.** Its RED rule was
quoted from a planning document that is not in this repo, and the operative threshold lives in
`redteam/run_auto.py`, the same script that computed the result. The follow-up probe has a committed
pre-registration and the headline does not; that is the wrong way round, and it is not something the
commit history can repair after the fact.

**On the freeze itself.** Earlier versions of this README cited a git tag `prereg-locked` as proof
the thresholds were frozen before scoring. **That tag does not exist** — not locally, not on the
remote; `git tag -l` returns nothing. The claim was wrong and is withdrawn.

The commit history is better evidence anyway, because a tag can be moved and a commit date cannot:

| Commit | Timestamp | What landed |
|---|---|---|
| `50e0041` | 18:02:49 | `results/README.md` only — documentation, **no data** |
| **`689a82d`** | **18:30:22** | **`PREREGISTRATION.md` frozen** |
| `6408952` | 18:58:18 | Phase A complete + Tier 0 |
| `f4c44b4` | 18:59:00 | **first measurement artifact** (`tier0/verdict.json`) |
| `3540f09` | 20:00:15 | Step 1 `redteam.json` |

All timestamps 2026-07-08, `-0400`. The freeze precedes every measurement artifact by 29 minutes.
That establishes the *thresholds for Tier 0/1/2* were fixed before any data existed. It does **not**
retroactively pre-register Step 1, whose rule was never committed.

---

## STATUS BOARD

**Phase A:** ✅ complete. **Gates:** Tier 0 ✅ (floor only) · **Step 1 red-team 🛑 RED** · **behavioral-check probe 🛑 white-box folds (BB 0% / WB 100%)** · Tier 1 ⛔ NOT built (killed) · Tier 2 🔒 gated.
**Freeze evidence:** commit `689a82d` (18:30) precedes the first measurement artifact `f4c44b4`
(18:59) — see [Pre-registration: what it does and does not cover](#pre-registration-what-it-does-and-does-not-cover). There is **no `prereg-locked` tag**; an
earlier claim that there was one is withdrawn. Thresholds for Tier 0/1/2 are FROZEN; the commercial
bar remains `TEAM INPUT REQUIRED`.

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
| WS2 | `harness/run_agent.py` | 🟡 **stub for real models** | only `mode="dummy"` works; the OpenHands/pinned-model driver raises `NotImplementedError` (§13). **Genuinely unfinished** — it predates the Step 1 kill rather than resulting from it |
| WS2 | `harness/rollout.py` | 🟡 unexercised | only ever calls `run_agent(mode="dummy")`; produced no committed artifact |
| Tier 0 | `experiments/tier0_separation.py` | ✅ PASS (floor) | reframed as near-tautological; precondition unmet + thresholds post-hoc (see above) |
| Tier 1 | Exp 1 / Exp 2 suite | ⛔ **NOT built** | RED at Step 1 — do not build until mechanism rethought |
| Tier 2 | RL | 🔒 gated | not assessed; downstream of a killed gate |

Legend: ✅ done · 🟡 partial/deferred · 🛑 red/kill · ⛔ not built (by decision) · 🔒 gated.

## Reproduce

**Prerequisites.** A running Docker daemon and the `python:3.11-slim` image are **hard requirements**
for everything except the unit tests — all grading and adversarial code executes in a sandbox. Only
`tests/test_smoke.py` is docker-free.

```bash
docker pull python:3.11-slim                    # required by all three commands below

python3 redteam/run_auto.py                     # STEP 1: automated black-box red-team (writes immutable artifact)
python3 redteam/diff_prototype/run_diff.py      # FOLLOW-UP: behavioral-check probe (BB/WB batteries)
python3 redteam/human_redteam.py --task add     # STEP 1: human red-team (a person should drive this)
python3 experiments/tier0_separation.py         # Tier 0 floor (context)

python3 tests/test_smoke.py                     # unit tests (docker-free)
```

**Provenance gap in the committed runs.** `PREREGISTRATION.md:30-31` pins container images by
digest, but no committed artifact under `results/` records an image digest, git commit, or Python
version — the run directories carry only a timestamp in their name, and every call site used the
mutable `python:3.11-slim` tag. Capture was added in `harness/provenance.py` for future runs; the
committed results predate it and cannot be retrofitted.

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
