"""Simulate NGS sequencing QC metrics for 400 samples under two library-
prep methods: the baseline protocol and an optimized protocol (improved
hybridization time + adapter ratio, standard real wet-lab optimization
levers) -- a genuinely different, better-performing distribution, not
just relabeled identical data."""
from __future__ import annotations

import numpy as np
import pandas as pd

N_SAMPLES = 400
SEED = 109


def simulate_runs(n: int = N_SAMPLES, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        method = "baseline" if i % 2 == 0 else "optimized"
        if method == "baseline":
            mean_depth = rng.normal(85, 25)
            q30_rate = rng.normal(88, 6)
            duplication_rate = rng.normal(18, 7)
            on_target_rate = rng.normal(78, 9)
        else:
            mean_depth = rng.normal(105, 15)      # higher, tighter
            q30_rate = rng.normal(93, 3)           # higher, tighter
            duplication_rate = rng.normal(9, 4)     # lower, tighter
            on_target_rate = rng.normal(88, 5)       # higher, tighter

        rows.append({
            "sample_id": f"NGS-{i:04d}", "method": method,
            "mean_depth": round(float(max(mean_depth, 1)), 1),
            "q30_rate": round(float(np.clip(q30_rate, 0, 100)), 2),
            "duplication_rate": round(float(np.clip(duplication_rate, 0, 100)), 2),
            "on_target_rate": round(float(np.clip(on_target_rate, 0, 100)), 2),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = simulate_runs()
    print(df.groupby("method").mean(numeric_only=True))
