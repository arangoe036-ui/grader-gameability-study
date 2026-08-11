# Verdict — does a behavioral/differential tamper check survive a white-box adversary?

## One-paragraph honest verdict

**No — a fixed-context behavioral/differential check does not survive a white-box adversary,
though it does help against naive ones.** Black-box escape was **0%** (0/16, 95% CI [0%, 0%]): the
check catches naive reward-channel hacks because a hack that is correct only under a test harness
*diverges* between the check's test-like and prod-like contexts. White-box escape was **100%**
(16/16, CI [100%, 100%], all 8 tasks): once the adversary is given the check's context battery, it
makes the patch behave correctly in *every* context the check probes (and under the test-like
hidden-oracle run) while staying buggy in true production — no divergence, no flag, accepted,
wrong. Because an **embedded verifier under RL pressure is effectively white-box** (an optimizer
with many rollouts against a fixed checker will discover and route around its context battery),
this is the threat that matters, and the check folds against it. So **strong deterministic
un-gameability is likely dead** for this class of check; the honest residual claim is an
*empirical "more-robust" grader* (a real improvement over Step 1's static blocklist, which even
black-box hacks beat), **not** an un-gameable one.

## Why this is fundamental, not a tuning gap

Any **fixed, adversary-knowable** set of contexts C can be routed around by code that special-cases
exactly C (correct on C, arbitrary off C). Enumerating more contexts loses the same race — it is
the Step 1 finding one level up (a knowable *battery of contexts* is as bypassable as a knowable
*blocklist of substrings*). The only apparent escape — **secret/randomized** contexts — runs into
an un-observability wall: the ground-truth oracle is itself just another probe, so "correct in all
probes but buggy in unobserved deployment" cannot be deterministically distinguished from "truly
correct." You can raise the bar; you cannot close it with a deterministic checker.

## Fairness guarantee (why the number is trustworthy)

- The ground-truth **meta-oracle is independent**: it runs `meta_check_*` scripts on **fresh random
  inputs**, never sees the prototype, and shares **no context signals** with it (the check uses
  `test_probe/prod_probe/svc_probe` on fixed inputs). Escape is decided **only** by the meta-oracle,
  so the adversary can only make the check look **worse**, never falsely better.
- **Step 1 leak fixed:** the adversary never receives `hidden_oracle` (it gets a redacted task view
  + the verdict, plus the contexts in white-box). Verified: `arena.py` exposes only `accepted`,
  `flagged`, and (white-box) `contexts`.
- Honest fixes are accepted and truly-correct (no false positives), so the check is not a trivial
  reject-everything.

## Caveats (stated explicitly)

- Synthetic 8-task set of tiny pure functions. The **direction** of the result (white-box folds,
  black-box holds) is structural, not dataset-specific; absolute rates on real SWE-bench-style
  tasks would differ, but the routing-around-a-known-battery argument does not.
- "White-box" here = the adversary is given the check's **contexts**, not its full source (still
  firewalled). That models the real embedded-verifier threat, where the checker's behavior is
  learnable even if the code isn't shared.
- The white-box adversary assumes the grader's hidden-oracle run is "test-like" (standard domain
  knowledge) to pass the oracle it cannot see; this is a mild, realistic assumption.
- The prototype is **throwaway** — not integrated into `graders/treatment/`, not hardened, not
  scaled. By design (this is a cheap decision experiment).

## Decision fork (pre-registered branch 1, with branch-3 nuance)

The white-box escape is systematic → per the pre-registered reading, **do NOT build the redesign.**
The decision moves to the three-way claim choice, which is a **human call**:
1. **Absolute un-gameability (deterministic)** — *not supported* by this evidence.
2. **Empirical "most-robust" grader** — *supported*: behavioral checking beats a static blocklist
   and stops naive/black-box hacks (0% here). Honest, weaker pitch; price/position accordingly.
3. **Stop** the un-gameability thesis entirely.

Independent firewalled white-box agent corroboration: see `corroboration.md` in this directory.

---

## CORRECTION APPENDED 2026-08-10 (original text above unaltered — Prime Directive section 5)

The intervals reported above as `[0%, 0%]` and `[100%, 100%]` are **not intervals**. A percentile
bootstrap on a zero-variance sample can only return its own point estimate. Exact
(Clopper-Pearson) intervals at n = 16:

| Condition | Observed | Exact 95% CI |
|---|---|---|
| Black-box | 0 / 16 | **[0%, 20.6%]** |
| White-box | 16 / 16 | **[79.4%, 100%]** |

**Consequence for the pre-registered reading.** `PREREGISTERED_READING.md` defines "near-zero" as a
pooled escape-rate 95% CI upper bound below 0.10. At n = 16 the exact upper bound is 20.6%, so
**`bb_near_zero` is NOT met** — 16 trials cannot establish a rate below 10%. Any claim that the
behavioral check measurably stops black-box hacks is unsupported at this sample size.

**The white-box conclusion is unaffected.** 16/16 is systematic under any interval, and that is the
half this verdict rests on: a fixed, adversary-knowable context battery gets routed around.

**Corroboration is prose-only.** `corroboration.md` in this directory carries no committed
transcript, log, or rerunnable command — including the "fingerprint discovered via 1-bit side
channel" claim, which rests entirely on an agent's self-report. `arena.py` exposes the CLI a reader
could use to redo it; nothing here shows that it was done.
