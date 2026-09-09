#!/usr/bin/env python3

import json
import sys
from pathlib import Path


SUMMARY_KEYS = ("passed", "failed", "total", "pass_rate")


def read_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 sync_benchmark.py <iteration-dir>", file=sys.stderr)
        return 1

    iteration = Path(sys.argv[1])
    benchmark_path = iteration / "benchmark.json"
    try:
        benchmark = read_object(benchmark_path)
        runs = benchmark["runs"]
        if not isinstance(runs, list):
            raise ValueError(f"expected a runs list: {benchmark_path}")

        for run in runs:
            eval_id = run["eval_id"]
            candidates = [iteration / f"eval-{eval_id}", *iteration.glob(f"eval-{eval_id}-*")]
            matches = [path for path in candidates if path.is_dir()]
            if len(matches) != 1:
                raise ValueError(f"expected one directory for eval {eval_id}, found {len(matches)}")
            grading_path = matches[0] / run["configuration"] / f"run-{run['run_number']}" / "grading.json"
            grading = read_object(grading_path)
            summary = grading["summary"]
            result = run["result"]
            if any(result[key] != summary[key] for key in SUMMARY_KEYS):
                raise ValueError(f"score changed for {grading_path}; run a supported full aggregation")
            run["expectations"] = grading["expectations"]
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"Benchmark synchronization failed: {error}", file=sys.stderr)
        return 1

    benchmark_path.write_text(json.dumps(benchmark, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Synchronized benchmark expectations for {len(runs)} run(s) in {benchmark_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
