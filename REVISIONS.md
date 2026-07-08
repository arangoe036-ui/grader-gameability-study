# Cuarzo Benchmark Go/No-Go — Proposed Revisions to the Experiment Spec

*Companion to `cuarzo-benchmark-go-no-go-spec.md`. Read alongside the original; section references (§) point to the original spec. Purpose: make a GREEN result mean what the go/no-go actually needs it to mean before the company commits a runway to it.*

---

## Why these revisions

The current spec is well-constructed and most of it should stay: pre-registered thresholds, explicit kill criteria, a false-positive rate on valid alternative fixes, and a strict "only the grader varies" design. The concern here is narrow and specific — as written, the experiment is calibrated so that a GREEN is easy to reach, and it tests a weaker claim than the one the business rests on. Two structural gaps drive this:

1. **Best-of-N on a frozen model cannot test un-gameability** — the core product claim — because there is no optimizer applying pressure and no incentive for the model to *learn* to exploit the grader. It tests grader accuracy, which is real but is not the pitch.
2. **The baseline (visible, tamperable tests) is a strawman** no serious 2026 lab uses, so the measured delta mostly reflects the generic hidden-vs-visible gap rather than Cuarzo's proprietary contribution.

The revisions below make a GREEN mean: the *un-gameable, footprint-relative* signal beats *current lab best practice*, *under optimization pressure*, by a *commercially decisive* margin.

---

## Summary of changes

1. Promote the RL run from an optional stretch to a required tier of the decision.
2. Add a competent hidden-test baseline (Control A2) to isolate the actual IP.
3. Independently human-adjudicate ground truth for the hard classes in Exp 1.
4. Pre-register a *commercially* decisive magnitude, not just an above-noise one.
5. Power the rare classes, and add a long-horizon task slice.
6. Strengthen contamination control beyond "post-cutoff date."
7. Re-baseline the timeline, and run lab outreach in parallel.

---

## The changes in detail

### Change 1 — Make the RL run a required decision tier, not an optional stretch
*Affects: §4 (Optional stretch), §6 (Decision rule)*

**Problem.** Reward hacking as the business case defines it — a gap that "widens as training continues," training-stability collapse — is a *training-dynamics* phenomenon. Best-of-N selection on a frozen model applies no optimization pressure and gives the model no incentive to learn to exploit the grader, so it can only surface hacks the model already emits spontaneously. Exp 1 and Exp 2 therefore test grader/selector *accuracy*. Neither tests *un-gameability*, which is the product. The one experiment that does — the short RL run — is currently gated as optional and may never run.

**Change.** Restructure the decision into two tiers:

- **Tier 1 (screening):** Exp 1 + Exp 2 (best-of-N). A null result here is a fast, cheap RED — good. A green here means "mechanism worth pressure-testing," i.e. proceed to Tier 2. It does **not** by itself trigger the publication push or lab outreach.
- **Tier 2 (the real test):** the short GRPO run per grader arm. A full GREEN requires the Control arm to develop the predicted widening hacking gap / accuracy drop while the Cuarzo arm stays stable.

If the RL run genuinely cannot be afforded on this budget, say so explicitly in the write-up and downgrade the claim: a best-of-N-only green validates "Cuarzo is a more accurate grader," not "Cuarzo's signal is un-gameable under training," and the pitch and pricing must be adjusted to that weaker claim. Do not let a best-of-N green be reported as validation of un-gameability.

### Change 2 — Add a competent hidden-test baseline (Control A2)
*Affects: §3 (The graders)*

**Problem.** Control A is pass/fail on visible, tamperable tests — a baseline no serious 2026 lab uses; they already run held-out tests with basic sandboxing. The Treatment bundles three things: a hidden oracle (generic, standard practice), tamper detection, and footprint-relative localization (the proprietary parts). Measured against Control A, most of the delta is the hidden-vs-visible difference — which every lab self-serves — not Cuarzo's actual contribution. A green on that comparison invites the honest lab response: "yes, obviously; we already use hidden tests."

**Change.** Add **Control A2** = a competent held-out-test setup with basic sandboxing, representing current lab best practice. Keep Control A as a floor / sanity check, but set the go/no-go bar on **Treatment vs. A2** — the marginal value of tamper detection + footprint localization *over standard hidden testing*. Report Treatment-vs-A and Treatment-vs-A2 separately, and label clearly which one the decision rests on (A2).

### Change 3 — Independently adjudicate ground truth for the hard classes
*Affects: §4 (Exp 1), §5 (Rigor)*

**Problem.** The discriminating classes — spurious-correct (passes visible tests, violates true behavior) and valid alternative fixes — require a correctness judgment. If that judgment is produced by the same honest-oracle + behavioral machinery the Treatment grader uses, then Cuarzo is being scored against labels Cuarzo itself defined, and the confusion matrix looks strong by construction. The current blind human check is only a *sample* spot-check, framed as verifying the oracle.

**Change.** For scripted hacks (tests modified, harness exploited, hardcoded outputs), the constructed label is independent — fine as is. For the **spurious-correct** and **valid-alternative-fix** classes, the *primary* ground-truth label must come from independent human adjudication: two reviewers label blind, a third resolves disagreements, established before and separately from the Cuarzo oracle. The oracle's agreement with the human labels then becomes a *reported result*, not the source of the labels.

### Change 4 — Pre-register a commercially decisive magnitude, not just above-noise
*Affects: §6 (Decision rule)*

**Problem.** The rule currently treats "a solid, robust few-percent accuracy gain" as GREEN and states "we do not need 6×." Scientifically that is reasonable — a robust few-percent effect is real. But this experiment is billed as deciding "whether the company proceeds," and the business case's pricing power and venture-scale story lived on the 6×/8× numbers. A lab will not embed a third-party dependency in its crown-jewel training loop for a few percent. A *scientific* green can be a *commercial* amber, and the current rule does not distinguish them.

**Change.** Pre-register three magnitude bands and their commercial reading *before* running:

- **Mechanism-only:** above noise but small (e.g. low-single-digit pass@1 gain). Read: "mechanism real, commercial value UNPROVEN." This is **not** a launch trigger — it is an input to lab conversations ("here is the delta; would you pay to embed this?").
- **Commercially material:** a pre-defined threshold the team believes a lab would actually pay and embed for — define it *now* (e.g. a substantial, robust hack-rate reduction *plus* a pass@1 gain above a stated bar). Read: **GREEN**.
- Also pre-register the Exp 1 bars: what hack-catch, spurious-catch, and false-positive numbers count as "clear."

Keep the scientific and commercial questions separate in the write-up. "Is it real?" and "Is it worth paying for?" are different results, and both must be reported.

### Change 5 — Power the rare classes; add a long-horizon slice
*Affects: §2 (Task set)*

**Problem.** ~100 tasks split across four classes leaves the rare, decisive classes (reward-hacked, spurious-correct) at roughly 15–25 examples each — wide confidence intervals, so "catches a clear majority" of ~20 will likely land in AMBER under the spec's own "delta inside the noise band is not a delta" rule. Separately, a single reverted bug-fix commit is a small, localized change — not the long, multi-file agentic run the product is actually about — so a green on reverts may not transfer to the real domain.

**Change.** Two adjustments:

- **(a) Over-sample the rare classes specifically.** You don't need thousands of organic tasks, but you do need enough reward-hacked and spurious-correct examples for tight CIs — target ~40–60 of each, generated largely by *scripting* known patterns rather than curating hundreds of organic commits.
- **(b) Add a small long-horizon slice.** ~15–20 genuinely multi-file / multi-step trajectories (not single-commit reverts), reported separately, to check the signal survives in the domain you sell. A green on short reverts but a null on the long-horizon slice is itself an important finding.

### Change 6 — Strengthen contamination control beyond post-cutoff date
*Affects: §2 (Contamination control), §5 (Rigor)*

**Problem.** "Prefer commits after the model's cutoff" is a weak proxy. Open-model cutoffs are murky, models are frequently trained past their nominal date, and even a genuinely novel fix can sit on a memorized codebase or a publicly discussed bug.

**Change.** Layer the controls and treat post-cutoff date as *necessary, not sufficient*: prefer obscure / low-star repos; prefer bugs with no public writeups or discussion; add a quick human novelty check; and in the contamination log, record repo popularity and whether the bug was publicly discussed, alongside commit date vs. cutoff.

### Change 7 — Re-baseline the timeline; run lab outreach in parallel
*Affects: header budget, §7–§8, plus a companion action*

**Problem.** Curating ~100 tasks that are simultaneously post-cutoff, permissively licensed, clean-oracle, and realistically multi-file is itself likely 2–3 weeks before anything runs — so "~2–3 weeks total" is optimistic; 4–8 weeks is realistic. More importantly, the highest-risk assumption in the whole business is *commercial* — will a lab pay — and no benchmark result touches it. Access to a lab is the real bottleneck.

**Change.** Re-baseline to ~4–8 weeks with phases made explicit (curation is the long pole and can start immediately): curation → Exp 1 → Exp 2 → RL (Tier 2, if screening green). And start warm lab conversations *in parallel* with the benchmark, not gated behind it — use the emerging Exp 1 numbers as material. The benchmark de-risks the technical thesis; the conversations de-risk the commercial one; both should run concurrently because the commercial risk is the larger of the two.

---

## What stays unchanged (and is right)

- Pre-registering thresholds before running.
- Committing to a real kill and "stop at first RED."
- Measuring the false-positive rate on valid alternative fixes — unusually honest; most people measure only catch rate.
- "Only the grader varies," with fixed model / tasks / N / seeds / compute.
- Multiple seeds + bootstrap confidence intervals.
- §8's move: extracting the paper-vs-company read from the felt difficulty of curation. Keep this — it is as valuable as the KPI number.

---

## Revised decision rule (drop-in replacement for §6)

**Tier 1 — Screening (Exp 1 + best-of-N Exp 2)**

- **RED:** Exp 1 fails (signal does not separate honest from gamed at the pre-registered bar) OR Exp 2 is null (no above-noise pass@1 gain vs. Control A2). Stop — the cheap kill.
- **AMBER:** Exp 1 clears its bar but Exp 2 is marginal / inside noise vs. A2. Iterate cheaply (task difficulty, N, contamination, oracle coverage). Do not start Tier 2 or the push.
- **PASS TO TIER 2:** Exp 1 clears its bar AND Exp 2 shows an above-noise pass@1 gain plus a lower selected-hack rate vs. A2.

**Tier 2 — Pressure test (short RL)**

- **GREEN → publication-grade + outreach:** the Control-A2 arm develops the predicted widening hacking gap / accuracy drop while the Cuarzo arm stays stable, *and* the Tier-1 magnitude met the pre-registered commercially-material bar.
- **COMMERCIAL-AMBER:** the mechanism holds under pressure but the magnitude is only "mechanism-only." Do not launch the full push; take the number into lab conversations to test willingness-to-pay directly.
- **RED → stop and rethink:** the Cuarzo arm also degrades under pressure (the signal is gameable once optimized against). This is the most important possible kill and the cheapest place to learn it.

---

## Companion note — the real bottleneck

Even a flawless GREEN validates the *technical* thesis only. The business's largest unknown is whether a lab will pay and embed a third-party verifier in its training loop. Run outreach in parallel with the benchmark: a handful of honest lab conversations may kill or confirm the company faster, and more cheaply, than any amount of benchmarking. The benchmark answers "does it work?"; only a lab answers "will you pay for it?" — and the second question is the one the company actually turns on.
