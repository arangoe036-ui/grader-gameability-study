# data/

Populated during **Phase C (WS6 curation)** — which is **GATED behind the Tier 0 human review**
(build plan §3, §6). Empty now on purpose.

- `tasks/` — one JSON per task, validated against `contracts/task_schema.json` (DRAFT until spec §4).
- `images/` — Dockerfile / pinned image **digest** per task (Prime Directive §6).
- `labels/` — human-adjudicated ground truth for hard classes (WS8: two blind reviewers +
  tiebreaker, established *before and separately from* the Treatment oracle, §6). Also holds the
  small labeled set for **Tier 0 / WS5**.
- `contamination_log.csv` — layered contamination control (§4 / review note 6): not just
  post-cutoff date, but `repo_stars`, `public_writeup`, and a human `novelty_checked` flag.
