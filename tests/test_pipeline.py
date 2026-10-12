import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from src.simulate_ngs_runs import simulate_runs
from src.qc_workflow import inject_known_failures, run_qc_checks, qc_accuracy
from src.method_comparison import compare_methods


@pytest.fixture(scope="module")
def df():
    return simulate_runs()


def test_400_runs_simulated(df):
    assert len(df) == 400


def test_both_methods_present(df):
    assert set(df["method"].unique()) == {"baseline", "optimized"}


def test_qc_workflow_detects_all_known_failures(df):
    with_failures = inject_known_failures(df)
    checked = run_qc_checks(with_failures)
    result = qc_accuracy(checked)
    assert result["n_known_failures"] > 0
    assert result["detection_rate_pct"] == 100.0


def test_optimized_method_has_higher_qc_pass_rate(df):
    comparison = compare_methods(df)
    baseline = comparison["by_method"]["baseline"]["qc_pass_rate_pct"]
    optimized = comparison["by_method"]["optimized"]["qc_pass_rate_pct"]
    assert optimized > baseline


def test_optimized_method_has_lower_variability(df):
    comparison = compare_methods(df)
    baseline_cv = comparison["by_method"]["baseline"]["depth_cv_pct"]
    optimized_cv = comparison["by_method"]["optimized"]["depth_cv_pct"]
    assert optimized_cv < baseline_cv


def test_robustness_improvement_is_substantial_but_not_absurd(df):
    comparison = compare_methods(df)
    assert 10 < comparison["qc_pass_rate_improvement_pct"] < 100
    assert 10 < comparison["depth_cv_reduction_pct"] < 100
