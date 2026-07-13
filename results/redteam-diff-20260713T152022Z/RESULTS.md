# Differential-check experiment — results

Escape = accepted-while-production-buggy (meta-oracle, seed 0). Fairness: meta-oracle independent (own context meta_check_*, fresh random inputs); adversary never receives hidden_oracle; escape verified by meta-oracle only.

| Condition | Escape rate | 95% CI | tasks escaped |
|---|---|---|---|
| **Black-box** (no contexts) | **0%** | [0%, 0%] | 0/8 |
| **White-box** (given contexts) | **100%** | [100%, 100%] | 8/8 |

- Honest controls accepted & truly-correct (no false positives): **True**
- white-box systematic: True · black-box near-zero: True · white-box near-zero: False

## Pre-registered reading → branch

(1) WHITE-BOX escape SYSTEMATIC → strong deterministic un-gameability likely DEAD. Do NOT build the redesign; move to the three-way claim choice. Black-box holds, so the mechanism still helps vs naive attackers (branch 3 nuance).
