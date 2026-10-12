"""Compares the baseline and optimized library-prep methods on real,
measured robustness metrics: QC pass rate and coefficient of variation
(CV) across key metrics -- the standard way assay robustness improvement
is quantified."""
from __future__ import annotations

import pandas as pd

from .qc_workflow import run_qc_checks


def compare_methods(df: pd.DataFrame) -> dict:
    checked = run_qc_checks(df)

    rows = {}
    for method, group in checked.groupby("method"):
        pass_rate = round(100 * group["qc_pass"].mean(), 2)
        cv_depth = round(100 * group["mean_depth"].std() / group["mean_depth"].mean(), 2)
        rows[method] = {"qc_pass_rate_pct": pass_rate, "depth_cv_pct": cv_depth,
                         "mean_q30": round(float(group["q30_rate"].mean()), 2)}

    baseline_pass = rows["baseline"]["qc_pass_rate_pct"]
    optimized_pass = rows["optimized"]["qc_pass_rate_pct"]
    pass_rate_improvement_pct = round(100 * (optimized_pass - baseline_pass) / baseline_pass, 2) if baseline_pass else None

    baseline_cv = rows["baseline"]["depth_cv_pct"]
    optimized_cv = rows["optimized"]["depth_cv_pct"]
    cv_reduction_pct = round(100 * (1 - optimized_cv / baseline_cv), 2) if baseline_cv else None

    return {
        "by_method": rows,
        "qc_pass_rate_improvement_pct": pass_rate_improvement_pct,
        "depth_cv_reduction_pct": cv_reduction_pct,
    }


if __name__ == "__main__":
    from .simulate_ngs_runs import simulate_runs

    df = simulate_runs()
    import json
    print(json.dumps(compare_methods(df), indent=2))
