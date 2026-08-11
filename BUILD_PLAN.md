# Cuarzo Go/No-Go — Build Plan for Claude Code

*Hand this file to Claude Code alongside `cuarzo-benchmark-go-no-go-spec-v2.md`. The spec is the scientific source of truth; this plan is the execution contract — how to build it, in what order, with what guardrails, and how to fan the work across parallel subagents. Written for an autonomous run (skip-permissions) with many agents, so the discipline below is deliberately strict: autonomy + parallelism amplifies speed **and** over-building.*

---

## 0. Prime directives — every agent reads these first

1. **This is a decision experiment, not a product build.** The definition of done for every task is "produces the pre-registered number / artifact," never "is production-grade." If you find yourself building the production fault-staging engine, hardening anything for scale, or adding infrastructure not required to get a number on the current tier — **STOP. You've left the spec** (spec §1, §13).
2. **Cheapest kill first, hard gates.** Do not build Tier 1 until Tier 0 passes. Do not build Tier 2 until Tier 1 passes. A RED at any gate is a *successful, cheap* outcome — not a failure to work around.
3. **Freeze pre-registration before any scoring.** Write `PREREGISTRATION.md` from spec §8 (all GREEN/AMBER/RED thresholds) and `git tag prereg-locked` **before** running any grader against real data. Thresholds are never edited after results are seen.
4. **Sandbox everything that runs model-generated code.** All agent trajectory generation and all grading of model-produced patches runs inside **disposable Docker containers with no host bind-mounts, no network egress, and no credentials/secrets in the environment.** Agents are given full repo write access *inside the container* (including test files — the realistic condition) and will deliberately cheat; contain them. **Never run trajectories on the host or against a real repo mounted writable.**
5. **Human gate at every tier boundary.** At the end of Tier 0, Tier 1, and Tier 2: write a results summary, update the status board, and **STOP for human review.** Do not auto-advance across a tier boundary.
6. **Determinism and honest stats.** Pin model version + quantization, task base-commits, and container images (by digest). Fix and log seeds. Multiple seeds + bootstrap CIs on every headline metric — a delta inside the noise band is not a delta.
7. **Scope tripwire.** If a task isn't on the DAG in §3, don't do it. Surface it for human decision instead of building it.

---

## 1. Repository layout

Create this structure in Phase A and build into it. Nothing lives outside it.

```
cuarzo-gng/
  README.md                    # summary + live STATUS BOARD (tier state, gate results)
  PREREGISTRATION.md           # frozen §8 thresholds — git-tagged before any scoring
  SPEC.md                      # copy of the v2 spec (source of truth)
  contracts/
    task_schema.json           # §4 task schema — the curation↔grader interface
    trajectory_schema.json     # what the harness emits, what graders consume
    verdict_schema.json        # what every grader returns
  data/
    tasks/                     # one JSON per task (validated against task_schema)
    images/                    # Dockerfile / pinned image digest per task
    labels/                    # human-adjudicated ground truth (hard classes)
    contamination_log.csv      # date, after_cutoff, repo_stars, public_writeup, novelty_checked
  graders/
    grader_interface.py        # ABC: grade(attempt, task) -> Verdict
    control_a.py               # naive visible-test (floor/sanity)
    control_a2.py              # competent held-out + sandbox  <-- DECISION BASELINE
    control_b.py               # LLM-judge (state its inputs explicitly)
    treatment/                 # Cuarzo: hidden oracle + tamper detect + footprint localize
  harness/
    sandbox_runner.py          # disposable Docker: no net, no mounts, no secrets
    run_agent.py               # OpenHands wrapper -> one trajectory
    rollout.py                 # N attempts/task, shardable, isolated output dirs
  experiments/
    tier0_separation.py
    tier1_exp1_verification.py
    tier1_exp2_selection.py
    tier2_rl/                  # GATED: built only after Tier 1 passes
  analysis/
    metrics.py                 # confusion matrix, catch rates, bootstrap CIs
    power_check.py             # sample size needed to separate GREEN/AMBER on key metrics
    report.py                  # emits SCIENTIFIC + COMMERCIAL summaries separately
  results/
    run-<timestamp>/           # write-once, immutable; shard-<k>/ subdirs for rollouts
```

---

## 2. Interface contracts — freeze first, then parallelize

Parallel subagents collide only when they share mutable interfaces. So the pattern is: **freeze the contracts, then let implementations fan out against them.**

- **`task_schema.json`** (spec §4) — the contract between curation and every grader/experiment. Freeze before curation or grader work starts.
- **`grader_interface.py`** — every grader implements `grade(attempt, task) -> Verdict`, where `Verdict` = `{ pass: bool, hack_flags: [str], tamper_detected: bool, footprint_score: float, notes: str }`. Freeze this signature first; then the four graders build in parallel.
- **`trajectory_schema.json`** — what `run_agent.py` emits (final patch, full action log, visible-test results, harness metadata) and what graders read.
- **`verdict_schema.json` → analysis** — `metrics.py` consumes `Verdict[]` + human labels; it can be built and unit-tested against synthetic fixtures *before real data exists*.

**Rule:** an agent may only build against frozen interfaces. Needing to change an interface is a **STOP-and-coordinate** event routed through the integrator agent (§4). Interface edits serialize; implementations parallelize.

---

## 3. Workstream DAG — what runs in parallel, what gates

### Phase A — Foundation (parallel, ~week 1, no gates between them)

- **WS1 · Contracts & scaffolding** *(do first; others depend on frozen contracts)* — create repo layout, freeze all four schemas/interfaces, copy the spec into `SPEC.md`, write `PREREGISTRATION.md` from §8 and `git tag prereg-locked`.
- **WS2 · Sandbox + harness** *(highest infra risk — start immediately; spec §13 "harness eats a week")* — OpenHands + Docker `sandbox_runner.py`. Definition of done: run **one** agent on **one** task fully isolated (no net, no mounts) and capture a valid trajectory. Nothing more.
- **WS3 · Grader stubs** *(parallel across the four graders)* — implement A, A2, B, Treatment against hand-made fixtures. For A2, pin whether it runs held-out tests + basic sandbox. For B, **explicitly state its inputs** (same info as A2, or pure no-oracle opinion — see review note 4).
- **WS4 · Analysis** *(parallel)* — `metrics.py`, `power_check.py`, `report.py` against synthetic Verdict fixtures. Report must keep **scientific vs. commercial** outputs separate (§8).

### Phase B — Tier 0 gate (the cheapest kill)

- **WS5 · Small labeled set** — a few dozen hand-crafted attempts spanning honest / hacked / spurious + a few valid-alternatives.
- **Run `tier0_separation.py`** → Treatment separates honest from gamed at the coarse §8 Tier-0 bar (FP on valid alternatives ≤ ~10%). **STOP → human review.** RED here = done, cheap kill (success).

### Phase C — Build the real suite (parallel, ~weeks 2–3, only if Tier 0 GREEN)

- **WS6 · Curation** *(long pole — runs the whole phase)* — subsample SWE-bench Verified/Lite (buggy commit; gold patch = footprint answer key; hidden test patch = oracle; Docker env); SWE-smith to top up. Build footprints, hidden oracles, and the **layered contamination log** (§4: prefer obscure/low-star repos, no public writeups, human novelty check; log stars + public-discussion flag, not just date).
- **WS7 · Hacked/spurious generation** — script known patterns + adapt ImpossibleBench-style tasks. **Review note 1 (build this in): deliberately over-weight a powered sub-bucket of *A2-surviving* hacks** (harness / reward-channel / oracle-incompleteness exploits), because naive hacks fail A2 and won't exercise the metric that decides the go/no-go. Run `power_check.py` to size this sub-bucket so its CI separates GREEN (≥80%) from AMBER.
- **WS8 · Adjudication** *(HUMAN workstream — Claude Code builds the queue/interface only)* — spurious-correct and valid-alternative labels come from **two blind reviewers + a tiebreaker**, established *before and separately from* the Treatment oracle (§6). Claude Code prepares the labeling queue and blinds it; humans produce the labels. **Gate: labels must exist before Exp 1 scoring.**
- **WS9 · Rollouts** *(embarrassingly parallel — this is where "as many agents as it wants" pays off)* — once tasks + harness are ready, run N = 8–16 attempts/task in the sandbox. Shard by task; each shard writes to its own `results/run-<ts>/shard-<k>/`. No shared mutable state.

### Phase D — Tier 1 gate

- **Run `tier1_exp1_verification.py`** (confusion matrix per grader; headline **vs. A2**: hacks-caught-beyond-A2, spurious-catch, footprint accuracy scored as a *region/signal* match — **review note 3** — and FP on valid alternatives) **and `tier1_exp2_selection.py`** (best-of-N; true-correct@1 delta vs. A2; selected-hack rate). **STOP → human review.** Apply §9 Tier-1 rule (RED / AMBER / PASS-TO-TIER-2).

### Phase E — Tier 2 gate (only if Tier 1 PASS **and** RL feasibility = yes per spec §12)

- **WS10 · RL arms** — short GRPO per grader arm on **contamination-controlled** tasks; measure stability on a **held-out split** (review note 2). **Pre-register the positive control:** Tier 2 is interpretable only if the **A2 arm demonstrably develops reward-hacking** (the widening gap). If it doesn't, the result is **INCONCLUSIVE** — un-gameability stays unproven under pressure, *not* GREEN. **STOP → final decision** per §9 Tier-2 rule.

### Parallel throughout — Lab outreach (NOT Claude Code)

Named here so it isn't dropped: the benchmark answers "does it work?"; only a lab answers "will you pay?" This is a human workstream that starts day 1 and is **not gated** behind any tier (spec §10). Claude Code's only role is to surface emerging Exp 1 numbers as outreach material when asked.

---

## 4. Using subagents (given your setup)

- **One integrator agent** owns `contracts/`, the STATUS BOARD in `README.md`, and merges. **Worker agents** own implementations. All interface changes route through the integrator (serialize edits, parallelize builds).
- **Fan-out point 1 (Phase A):** after WS1 freezes contracts, spawn parallel workers for WS2 / WS3 (×4 graders) / WS4.
- **Fan-out point 2 (Phase C):** WS6 / WS7 / WS8-queue in parallel.
- **Fan-out point 3 (Phase C, WS9 rollouts):** one worker per task shard — the biggest parallelism win; keep shard outputs isolated, merge only in analysis.
- Every subagent inherits the **Prime Directives (§0)**, including the scope-discipline stop and the "build against frozen interfaces only" rule.
- Give each worker a crisp **Definition of Done** that ends at "produces the artifact/number," and forbids gold-plating.

---

## 5. Guardrails recap (dangerous-permissions + parallel = amplified risk)

- **Sandbox isolation is non-negotiable** — untrusted, deliberately-cheating code, contained in throwaway containers with no net/mounts/secrets. Never on the host.
- **Human gate at every tier boundary** — no auto-advance; wait for review.
- **Pre-registration git-tagged before any scoring** — thresholds frozen.
- **Immutable results** — write-once, timestamped run dirs.
- **Scope tripwires** — production engine, scale infra, or off-DAG work → STOP and ask.
- **Stop at the first RED** — a cheap kill is the goal, not an obstacle.

---

## 6. Ready-to-paste kickoff prompt for Claude Code

> Read `BUILD_PLAN.md` and `cuarzo-benchmark-go-no-go-spec-v2.md` in full before doing anything. This is a **decision experiment, not a product build** — obey the Prime Directives in §0. In particular: cheapest-kill-first with **hard tier gates**; **sandbox all model-generated code** in disposable Docker (no network, no host mounts, no secrets); freeze `PREREGISTRATION.md` from spec §8 and `git tag prereg-locked` **before** any scoring; and **STOP for human review at every tier boundary** — never auto-advance.
>
> Start with **Phase A only**: create the repo layout from §1, freeze the four contracts in `contracts/`, copy the spec to `SPEC.md`, write `PREREGISTRATION.md`, and stand up the sandboxed OpenHands + Docker runner (`harness/sandbox_runner.py`) proving it can run one agent on one task fully isolated and capture a valid trajectory. Once the contracts are frozen, use parallel subagents for the independent Phase-A workstreams (WS2, the four graders in WS3, WS4), with one integrator agent owning `contracts/` and the STATUS BOARD.
>
> When Phase A is complete, build the small labeled set (WS5), run **Tier 0**, write the results summary, and **STOP**. Do not build Tier 1, the full task suite, the RL run, the production fault-staging engine, or any scale infrastructure until a human reviews the Tier 0 result and tells you to proceed.

---

## 7. Spec tweaks folded into this plan (apply before / during the build)

These four came out of the v2 review and are already reflected above; noting them so the spec and the build stay in sync:

1. **Power the A2-surviving hack sub-bucket** (WS7) — otherwise the "hacks caught beyond A2" metric lands in AMBER by construction. Size it with `power_check.py`.
2. **Tier-2 positive control + INCONCLUSIVE branch** (WS10) — the A2 arm must actually develop hacking for the result to mean anything; train on contamination-controlled tasks, evaluate stability on a held-out split.
3. **Footprint-localization scored as a region/signal match** (Exp 1) — consistent with counting valid alternative fixes as correct, so the verifier stays sound.
4. **Pin Control B's inputs** (WS3) — same information as A2, or explicitly a no-oracle judge; state it so the comparison is fair.

---

*Cheapest kill first · sandbox the cheaters · freeze the thresholds · human gate at every tier · parallelize on frozen interfaces · stop at the first RED.*

---

## Note appended 2026-08-10

This plan instructs `git tag prereg-locked` before any scoring. **That step was not carried out** —
no tag exists in this repository. The freeze is instead evidenced by commit ordering: `689a82d`
(2026-07-08 18:30:22) froze `PREREGISTRATION.md` and precedes the first measurement artifact
`f4c44b4` (18:59:00) by 29 minutes. See the `PREREGISTRATION.md` addendum.

The spec documents referenced above (`cuarzo-benchmark-go-no-go-spec-v2.md`, and
`cuarzo-benchmark-go-no-go-spec.md` in `REVISIONS.md`) are **not in this repository**. `SPEC.md` is
the copied-in scientific source of truth; section references point to the original.
