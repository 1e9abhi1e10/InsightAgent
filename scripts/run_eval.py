#!/usr/bin/env python3
"""Run the evaluation harness and print a report.

Usage:
    python3 scripts/run_eval.py            # default (no delay)
    python3 scripts/run_eval.py --delay 4  # 4s between cases (avoid rate limits)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from src.evaluation import CaseResult, run_evaluation  # noqa: E402
from src.seed_data import seed_database  # noqa: E402


def _print_progress(i: int, total: int, result: CaseResult) -> None:
    status = "PASS" if result.passed else "FAIL"
    ground = f"{result.groundedness:.0%}" if result.groundedness is not None else "  - "
    print(
        f"  [{status}] ({i:>2}/{total}) "
        f"{result.latency_ms:>6.0f}ms  g={ground}  {result.question[:52]}"
    )
    if not result.passed and result.error:
        print(f"         error: {result.error[:90]}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=0.0, help="seconds between cases")
    args = parser.parse_args()

    seed_database(force=True)

    print("=" * 70)
    print("Conversational Data Analyst — Evaluation Harness")
    print("=" * 70)

    report = run_evaluation(on_progress=_print_progress, delay_seconds=args.delay)

    print("\n" + "-" * 70)
    print("Summary")
    print("-" * 70)
    print(f"  Overall pass rate : {report.passed}/{report.total} ({report.pass_rate:.0%})")
    print(f"  Avg latency       : {report.avg_latency_ms:.0f} ms")
    print(f"  Avg groundedness  : {report.avg_groundedness:.0%}")
    print("\n  By category:")
    for category, (passed, total) in sorted(report.by_category().items()):
        print(f"    {category:<12} {passed}/{total}")
    print("=" * 70)

    return 0 if report.pass_rate == 1.0 else 1


if __name__ == "__main__":
    sys.exit(main())
