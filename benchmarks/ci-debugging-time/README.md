# CI Debugging-Time Benchmark

This benchmark measures whether the agent reduces CI debugging time versus manual debugging.

## Claim Being Tested

```text
Reduced average debugging time by 65%
```

Use the claim only if the measured reduction is at least 65% across representative CI failures.

## Metric

Measure time to an opened fix PR, not time to merge:

```text
debugging_time_reduction_percent =
  (manual_avg_minutes - agent_avg_minutes) / manual_avg_minutes * 100
```

## What Counts As Time

Manual baseline:

- Start: developer opens the failed GitHub Actions run.
- Stop: developer has opened a fix PR.

Agent-assisted:

- Start: the GitHub webhook for the failed workflow is received.
- Stop: the agent opens a fix PR.

Use the same failing commit or the same seeded failure for both paths.

## Suggested Failure Set

Run at least 8-10 cases across common CI failures:

- missing Python dependency
- missing npm dependency
- import or module path error
- failing unit test from a simple logic bug
- TypeScript or Python type error
- lint or formatting failure
- bad environment/config variable handling
- outdated test expectation
- build command failure
- migration/schema mismatch

## Files

- `cases.csv`: planned benchmark cases.
- `results.csv`: measured timings.
- `calculate_claim.py`: computes averages, reduction percent, and pass/fail for the 65% claim.

## How To Run

Fill in `results.csv`, then run:

```bash
python benchmarks/ci-debugging-time/calculate_claim.py benchmarks/ci-debugging-time/results.csv
```

## Resume Wording

If the result is at least 65%:

```text
Benchmarked across N representative CI failures, reducing mean time-to-fix-PR by Z% versus manual debugging.
```

If the result is below 65%, use the measured number instead. If the benchmark is not complete, do not include the percentage.
