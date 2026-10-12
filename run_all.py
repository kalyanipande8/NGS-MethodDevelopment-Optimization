"""End-to-end: simulate NGS runs under baseline/optimized methods, run the
QC workflow (validated against known-injected failures), and compare
method robustness."""
import json
import os

from src.simulate_ngs_runs import simulate_runs
from src.qc_workflow import inject_known_failures, run_qc_checks, qc_accuracy
from src.method_comparison import compare_methods

os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

print("=== Simulating 400 NGS runs (baseline vs. optimized method) ===")
df = simulate_runs()
df.to_csv("data/ngs_runs.csv", index=False)
print(df.groupby("method").mean(numeric_only=True))

print("\n=== QC workflow validation (against known-injected failures) ===")
df_with_failures = inject_known_failures(df)
checked = run_qc_checks(df_with_failures)
checked.to_csv("data/qc_checked_runs.csv", index=False)
accuracy = qc_accuracy(checked)
print(accuracy)

print("\n=== Method comparison (baseline vs. optimized) ===")
comparison = compare_methods(df)
print(json.dumps(comparison, indent=2))

summary = {
    "n_samples": 400,
    "qc_detection_rate_pct": accuracy["detection_rate_pct"],
    "qc_false_fail_rate_pct": accuracy["false_fail_rate_pct"],
    "qc_pass_rate_improvement_pct": comparison["qc_pass_rate_improvement_pct"],
    "depth_cv_reduction_pct": comparison["depth_cv_reduction_pct"],
    "by_method": comparison["by_method"],
}
with open("results/summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n=== Summary ===")
print(json.dumps(summary, indent=2))
