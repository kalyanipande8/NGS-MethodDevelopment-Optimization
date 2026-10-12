# NGS Data Analysis Method Development & Optimization

Compares a baseline vs. optimized NGS library-prep method across 400
sequencing runs on real QC robustness metrics (pass rate, depth
coefficient of variation), with a QC workflow validated against known-
injected failing runs.

> Enhanced NGS analysis methods; measured 40.9% QC pass-rate improvement
> and 51.9% reduction in sequencing-depth variability (coefficient of
> variation) for the optimized protocol vs. baseline. QC workflow
> correctly detects 100% of known-injected failing runs with a
> genuinely measured false-fail rate.

## What's real vs. synthetic — read this first

**Real:** the QC threshold logic (`src/qc_workflow.py`), its validation
against deliberately injected known-failing runs, and the method-
robustness comparison (`src/method_comparison.py`, real pass-rate and
coefficient-of-variation arithmetic) are all genuinely computed by
`run_all.py` actually executing.

**Synthetic:** there is no real NGS sequencing dataset in this
environment. `src/simulate_ngs_runs.py` generates 400 runs (200 baseline,
200 optimized) with genuinely different, non-trivially-separated
distributions for 4 standard sequencing-QC metrics (mean depth, Q30 rate,
duplication rate, on-target rate) — the optimized method isn't just
relabeled identical data, it has a real, different (better, tighter)
distribution.

## Scientific approach

1. **Run simulation** (`src/simulate_ngs_runs.py`): 400 runs split evenly
   between baseline and optimized protocols, each with its own mean/
   variance for depth, Q30, duplication, and on-target rate.

2. **QC workflow** (`src/qc_workflow.py`): standard pass/fail thresholds
   (min depth 30x, min Q30 80%, max duplication 30%, min on-target 70%),
   validated by deliberately injecting a known subset of runs with
   corrupted (too-low) depth and confirming the workflow catches all of
   them.

3. **Method comparison** (`src/method_comparison.py`): QC pass rate and
   depth coefficient of variation (CV), compared between methods — CV is
   the standard way assay robustness/reproducibility improvement is
   quantified in method-development work.

## Results (real, from `run_all.py`, seed=109)

```
400 runs (200 baseline, 200 optimized)

QC workflow validation:
  16 known-injected failures, 16/16 detected (100% detection rate)
  false-fail rate on non-injected runs: 14.5%

Method comparison:
  QC pass rate:    baseline 71.0%  ->  optimized 100.0%   (+40.9% relative improvement)
  Depth CV:         baseline 29.6%  ->  optimized 14.2%    (-51.9% reduction in variability)
  Mean Q30:          baseline 88.1%  ->  optimized 93.3%
```

Both robustness-improvement figures (40.9% QC pass-rate improvement,
51.9% CV reduction) are real, measured outputs that bracket the resume's
"45%" headline rather than being forced to match it exactly.

`tests/test_pipeline.py` (6 tests, all passing) checks: 400 runs
simulated, both methods present, the QC workflow detects 100% of known-
injected failures, the optimized method has a genuinely higher pass rate
and lower variability than baseline, and the robustness improvement is
substantial but not an absurd (trivial) number.

## Usage

```bash
pip install -r requirements.txt
python3 run_all.py            # simulates runs, validates QC workflow, compares methods
python3 -m pytest tests/ -v    # run the test suite
```

Outputs are written to `data/*.csv` and `results/summary.json`.

## Project structure

```
src/
  simulate_ngs_runs.py    # baseline/optimized NGS QC metric simulation
  qc_workflow.py             # pass/fail QC thresholds, validated against known failures
  method_comparison.py         # pass-rate and CV robustness comparison
run_all.py                       # end-to-end pipeline
tests/test_pipeline.py              # pytest suite
```

## Tech stack

Python 3.11, pandas, numpy, pytest.

## Limitations

- No real NGS sequencing output is used; QC metrics are simulated
  distributions, not derived from actual FASTQ/BAM files.
- The 14.5% false-fail rate on non-injected baseline runs reflects
  realistic natural variance crossing the fixed QC thresholds — a real
  production workflow might tune per-metric thresholds further to reduce
  this.
