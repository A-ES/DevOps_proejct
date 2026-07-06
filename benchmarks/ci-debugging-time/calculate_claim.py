#!/usr/bin/env python3
"""Calculate CI debugging-time reduction from benchmark results.

Usage:
    python benchmarks/ci-debugging-time/calculate_claim.py \
        benchmarks/ci-debugging-time/results.csv
"""

from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path


REQUIRED_COLUMNS = {
    "case_id",
    "failure_type",
    "manual_minutes",
    "agent_minutes",
    "agent_opened_pr",
    "agent_pr_passed_ci",
}


def _parse_float(value: str, field_name: str, case_id: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"{case_id}: {field_name} must be a number") from exc
    if parsed <= 0:
        raise ValueError(f"{case_id}: {field_name} must be greater than 0")
    return parsed


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise ValueError(f"CSV is missing required columns: {missing_list}")

        return list(reader)


def completed_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    completed: list[dict[str, object]] = []
    for row in rows:
        case_id = row["case_id"].strip() or "<unknown>"
        manual_raw = row["manual_minutes"].strip()
        agent_raw = row["agent_minutes"].strip()
        if not manual_raw and not agent_raw:
            continue
        if not manual_raw or not agent_raw:
            raise ValueError(f"{case_id}: both manual_minutes and agent_minutes are required")

        manual = _parse_float(manual_raw, "manual_minutes", case_id)
        agent = _parse_float(agent_raw, "agent_minutes", case_id)
        opened_pr = _parse_bool(row["agent_opened_pr"])
        passed_ci = _parse_bool(row["agent_pr_passed_ci"])

        completed.append(
            {
                "case_id": case_id,
                "failure_type": row["failure_type"].strip(),
                "manual_minutes": manual,
                "agent_minutes": agent,
                "agent_opened_pr": opened_pr,
                "agent_pr_passed_ci": passed_ci,
                "reduction_percent": (manual - agent) / manual * 100,
            }
        )

    return completed


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: calculate_claim.py <results.csv>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    rows = completed_rows(load_rows(path))
    if not rows:
        print("No completed benchmark rows found.")
        print("Fill in manual_minutes and agent_minutes in results.csv, then rerun.")
        return 1

    manual_times = [float(row["manual_minutes"]) for row in rows]
    agent_times = [float(row["agent_minutes"]) for row in rows]
    opened_pr_count = sum(1 for row in rows if row["agent_opened_pr"])
    passed_ci_count = sum(1 for row in rows if row["agent_pr_passed_ci"])

    manual_avg = statistics.mean(manual_times)
    agent_avg = statistics.mean(agent_times)
    reduction = (manual_avg - agent_avg) / manual_avg * 100

    print("CI debugging-time benchmark")
    print(f"Completed cases: {len(rows)}")
    print(f"Manual mean time-to-fix-PR: {manual_avg:.2f} minutes")
    print(f"Agent mean time-to-fix-PR: {agent_avg:.2f} minutes")
    print(f"Mean reduction: {reduction:.1f}%")
    print(f"Agent opened PRs: {opened_pr_count}/{len(rows)}")
    print(f"Agent PRs passed CI: {passed_ci_count}/{len(rows)}")
    print()

    if reduction >= 65:
        print("Result: supports a 65% debugging-time reduction claim.")
        print(
            "Resume wording: "
            f"Benchmarked across {len(rows)} representative CI failures, "
            f"reducing mean time-to-fix-PR by {reduction:.0f}% versus manual debugging."
        )
    else:
        print("Result: does not support a 65% claim.")
        print(
            "Resume wording: "
            f"Benchmarked across {len(rows)} representative CI failures, "
            f"reducing mean time-to-fix-PR by {reduction:.0f}% versus manual debugging."
        )

    print()
    print("Per-case reductions:")
    for row in rows:
        print(
            f"- {row['case_id']} ({row['failure_type']}): "
            f"{row['reduction_percent']:.1f}%"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
