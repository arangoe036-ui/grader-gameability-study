# PREREGISTRATION.md — frozen §8 thresholds

## STATUS: BLOCKED — cannot be written without spec §8

Prime Directive §0.3: *"Write `PREREGISTRATION.md` from spec §8 (all GREEN/AMBER/RED
thresholds) and `git tag prereg-locked` **before** running any grader against real data.
Thresholds are never edited after results are seen."*

The v2 spec — which contains §8 — **is not available in this build** (see `SPEC.md`).
Pre-registration thresholds are the single most load-bearing artifact in a decision
experiment: inventing numbers here and later reconciling them against the real spec would be
indistinguishable from moving the goalposts after seeing data. **So no thresholds are written,
and `git tag prereg-locked` has NOT been created.** No scoring may occur until this is real.

### The one threshold stated in the build plan itself (not from §8)
- Tier 0 coarse bar (build plan §3 Phase B): FP on valid alternatives **≤ ~10%**.
  Encoded as `FP_VALID_ALT_BAR = 0.10` in `experiments/tier0_separation.py` for scaffolding
  only — it does **not** constitute pre-registration and is not tagged.

### To freeze (once the v2 spec is provided)
Transcribe, verbatim, from spec §8 — do not paraphrase or infer:
- [ ] Tier 0 separation bar(s) (honest vs gamed; FP-on-valid-alternatives ceiling).
- [ ] Tier 1 GREEN/AMBER/RED per §9 — Exp 1 (hacks-caught-beyond-A2, spurious-catch,
      footprint region-match, FP on valid alternatives) and Exp 2 (true-correct@1 delta vs A2,
      selected-hack rate).
- [ ] **Commercially decisive** magnitude vs A2, not merely above-noise (review note 4).
- [ ] Tier 2 GREEN vs **INCONCLUSIVE** rule incl. the A2-arm positive control (review note 2).
- [ ] Control B input policy: `same_as_a2` **or** `no_oracle_opinion` (review note 4).
- [ ] Seeds, model + quantization, image digests, base commits (Prime Directive §6).

Then: `git add PREREGISTRATION.md && git commit && git tag prereg-locked`.
