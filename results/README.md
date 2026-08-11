Write-once, immutable, timestamped run dirs land here (run-<ts>/shard-<k>/). Never edit a result after the fact (Prime Directive §5).

## Layouts actually present in this repo

The `run-<ts>/shard-<k>/` layout described above is the *planned* Phase-A shape and **no committed
result uses it** — the agent-rollout path that would have produced shards was never built (see the
README STATUS BOARD). What is actually here:

| Directory | Produced by | Contents |
|---|---|---|
| `run-<ts>/tier0/` | `experiments/tier0_separation.py` | `verdict.json`, `summary.md` |
| `redteam-<ts>/` | `redteam/run_auto.py` | `redteam.json`, `summary.md`, `STEP1_REDTEAM.md`, `corroboration.md` |
| `redteam-diff-<ts>/` | `redteam/diff_prototype/run_diff.py` | `results.json`, `RESULTS.md`, `VERDICT.md`, `PREREGISTERED_READING.md`, `corroboration.md` |

Corrections to committed results are **appended** as dated blocks, never applied by altering the
original prose or the JSON.
