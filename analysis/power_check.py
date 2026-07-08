"""power_check.py — how many items to separate GREEN from AMBER on a key rate.

Build plan §1/§3 WS7 + §7 review note 1: the A2-surviving hack sub-bucket must be sized
so its CI separates GREEN (>=80%) from AMBER. This computes that n.

Normal-approximation sample size for a one-sample proportion whose lower CI bound must clear
an AMBER ceiling. Pure stdlib. For final sizing, cross-check with the bootstrap in metrics.py.
"""
from __future__ import annotations

import math
from typing import Dict

_Z = {0.90: 1.6449, 0.95: 1.9600, 0.975: 2.2414, 0.99: 2.5758}


def _z(conf: float) -> float:
    return _Z.get(round(conf, 3), 1.9600)


def n_to_separate(true_rate: float = 0.85, amber_ceiling: float = 0.80,
                  conf: float = 0.95, n_max: int = 5000) -> Dict[str, float]:
    """Smallest n such that the one-sided lower CI of an observed `true_rate` clears
    `amber_ceiling` (i.e. we can call GREEN with `conf`). Wald interval."""
    if true_rate <= amber_ceiling:
        return {"feasible": False, "reason": "true_rate must exceed amber_ceiling to ever separate",
                "true_rate": true_rate, "amber_ceiling": amber_ceiling}
    z = _z(conf)
    p, margin = true_rate, true_rate - amber_ceiling
    for n in range(5, n_max + 1):
        half_width = z * math.sqrt(p * (1 - p) / n)
        if half_width <= margin:
            return {"feasible": True, "n": n, "true_rate": p, "amber_ceiling": amber_ceiling,
                    "conf": conf, "ci_half_width": round(half_width, 4)}
    return {"feasible": False, "reason": f"n exceeds n_max={n_max}", "true_rate": p, "amber_ceiling": amber_ceiling}


def separation_table(green: float = 0.80, conf: float = 0.95) -> Dict[str, dict]:
    """Sizing across a range of plausible true rates above the GREEN bar."""
    return {f"true={r:.2f}": n_to_separate(r, green, conf) for r in (0.82, 0.85, 0.88, 0.90, 0.95)}


if __name__ == "__main__":
    import json
    print("GREEN>=0.80 vs AMBER; n needed so lower 95% CI clears 0.80:")
    print(json.dumps(separation_table(), indent=2))
