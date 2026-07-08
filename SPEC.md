# SPEC.md — copy of the v2 spec (source of truth)

## STATUS: BLOCKED — source file not provided

Per the build plan (§1, §6), this file must be a **verbatim copy of
`cuarzo-benchmark-go-no-go-spec-v2.md`**, which is "the scientific source of truth."

**That file was not present in the handoff.** The build plan was provided
(`cuarzo-gng-build-plan_2.md` → copied here as `BUILD_PLAN.md`), and a companion
*revisions* document was found (`cuarzo-benchmark-revisions.md` → `REVISIONS.md`), but neither
the v2 spec **nor** the original `cuarzo-benchmark-go-no-go-spec.md` it revises is available.

I have **not fabricated** the spec. Doing so would corrupt the experiment: the spec defines
§4 (task schema), §5 (sandbox/grading semantics), §6 (adjudication), §8 (GREEN/AMBER/RED
thresholds), §9 (tier decision rules), §12 (RL feasibility), §13 (harness). Guessing any of
these — especially the §8 thresholds — violates Prime Directive §0.3.

### To unblock
Drop `cuarzo-benchmark-go-no-go-spec-v2.md` into this repo. Then:
1. Copy it verbatim over this file.
2. Reconcile `contracts/task_schema.json` with §4 (currently a marked DRAFT) and re-freeze.
3. Fill `PREREGISTRATION.md` from §8 and `git tag prereg-locked` (before any scoring).
4. Implement the real `graders/treatment/` from the spec (replacing the stub).
5. Pin Control B's inputs in prereg (review note 4).
