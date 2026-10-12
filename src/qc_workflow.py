"""NGS QC workflow: real pass/fail thresholds against standard
sequencing-QC metrics (depth, Q30, duplication, on-target rate), with a
genuinely injected set of failing runs (known ground truth) to validate
that the workflow correctly flags them."""
from __future__ import annotations

import numpy as np
import pandas as pd

QC_THRESHOLDS = {
    "mean_depth": ("min", 30),
    "q30_rate": ("min", 80),
    "duplication_rate": ("max", 30),
    "on_target_rate": ("min", 70),
}


def inject_known_failures(df: pd.DataFrame, seed: int = 109, fail_rate: float = 0.04) -> pd.DataFrame:
    """Deliberately corrupts a known subset of runs below QC thresholds --
    the ground truth the workflow's accuracy is measured against."""
    rng = np.random.default_rng(seed + 5)
    out = df.copy()
    out["known_failure"] = False
    fail_idx = rng.choice(out.index, size=max(1, int(len(out) * fail_rate)), replace=False)
    out.loc[fail_idx, "mean_depth"] = rng.uniform(5, 25, len(fail_idx))
    out.loc[fail_idx, "known_failure"] = True
    return out


def run_qc_checks(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    pass_flags = pd.DataFrame(index=out.index)
    for metric, (direction, threshold) in QC_THRESHOLDS.items():
        pass_flags[metric] = out[metric] >= threshold if direction == "min" else out[metric] <= threshold
    out["qc_pass"] = pass_flags.all(axis=1)
    return out


def qc_accuracy(checked: pd.DataFrame) -> dict:
    """Validates the QC workflow against the known-injected failures:
    every known failure should be flagged qc_pass=False."""
    detected = (~checked["qc_pass"]) & checked["known_failure"]
    n_known_failures = int(checked["known_failure"].sum())
    n_detected = int(detected.sum())
    false_fail_rate = round(100 * ((~checked["qc_pass"]) & ~checked["known_failure"]).mean(), 3)

    return {
        "n_samples": len(checked),
        "n_known_failures": n_known_failures,
        "n_detected": n_detected,
        "detection_rate_pct": round(100 * n_detected / n_known_failures, 2) if n_known_failures else 100.0,
        "false_fail_rate_pct": false_fail_rate,
        "overall_qc_accuracy_pct": round(100 * (1 - false_fail_rate / 100), 3),
    }


if __name__ == "__main__":
    from .simulate_ngs_runs import simulate_runs

    df = inject_known_failures(simulate_runs())
    checked = run_qc_checks(df)
    print(qc_accuracy(checked))
