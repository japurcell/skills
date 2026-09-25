#!/usr/bin/env python3
"""Grade router decisions against the current tier and output contract."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

CATALOG = Path(__file__).resolve().parents[1] / "reference/model-catalog.md"
SCENARIOS = {
    0: "ordinary-review", 1: "style-review", 2: "security-review",
    3: "review-fallback", 4: "bounded-work", 5: "connected-work",
    6: "environment-failure",
}
REQUIRED_TIERS = {
    "ordinary-review": "standard", "style-review": "fast",
    "security-review": "premium", "review-fallback": "standard",
    "bounded-work": "fast", "connected-work": "standard",
    "environment-failure": "fast",
}


def catalog_models(tier: str) -> set[str]:
    catalog = CATALOG.read_text(encoding="utf-8")
    section = catalog.split(f"## {tier.title()}\n", 1)[1].split("\n## ", 1)[0]
    models = set(re.findall(r"^\| [^|]+ \| `([^`]+)`", section, re.MULTILINE))
    if not models:
        raise ValueError(f"No models found for tier {tier}")
    return models


def normalize(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


def model_matches_tier(model: str, tier: str, effort: str) -> bool:
    if model == "gpt-6-luna":
        return (tier, effort) in {("fast", "medium"), ("standard", "max")}
    if model == "gpt-5.6-luna":
        # The bounded-work default names this fallback below the tier tables.
        return tier == "fast"
    if model == "gpt-6-sol" and tier == "premium":
        return effort in {"high", "xhigh", "max", "ultra"}
    return model in catalog_models(tier)


def expectation(text: str, passed: bool) -> dict:
    return {"text": text, "passed": passed}


def grade(scenario: str, decision: dict) -> list[dict]:
    if scenario not in REQUIRED_TIERS:
        raise ValueError(f"Unknown router scenario: {scenario}")
    tier = normalize(decision.get("tier"))
    model = normalize(decision.get("model"))
    effort = normalize(decision.get("effort"))
    reason = normalize(decision.get("reason"))
    expected_tier = REQUIRED_TIERS[scenario]
    results = [
        expectation(f"Route uses {expected_tier.title()} tier.", tier == expected_tier),
        expectation("Model belongs to the selected capability tier.",
                    model_matches_tier(model, expected_tier, effort)),
        expectation("Reason explains the routing decision.", bool(reason)),
    ]
    if scenario == "review-fallback":
        fallback = normalize(decision.get("fallback"))
        results.append(expectation(
            "Fallback records unavailable Sol and a same-tier replacement.",
            "gpt-6-sol" in fallback and "unavailable" in fallback
            and ("same-tier" in fallback or "same tier" in fallback)
            and model != "gpt-6-sol",
        ))
    if scenario == "environment-failure":
        results.append(expectation(
            "Reason diagnoses the missing dependency before escalation.",
            ("dependency" in reason or "environment" in reason)
            and "diagnos" in reason,
        ))
    return results


def scenario_for(eval_dir: Path) -> str:
    metadata_path = eval_dir / "eval_metadata.json"
    if metadata_path.is_file():
        eval_id = json.loads(metadata_path.read_text(encoding="utf-8")).get("eval_id")
        return SCENARIOS[int(eval_id)]
    match = re.match(r"eval-(\d+)", eval_dir.name)
    if match:
        return SCENARIOS[int(match.group(1))]
    raise ValueError(f"Cannot identify router scenario: {eval_dir}")


def grade_iteration(iteration_dir: Path) -> int:
    if not iteration_dir.is_dir():
        print(f"Iteration directory not found: {iteration_dir}", file=sys.stderr)
        return 1
    runs = 0
    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        if not eval_dir.is_dir():
            continue
        scenario = scenario_for(eval_dir)
        for run_dir in sorted(eval_dir.glob("*/run-*")):
            if not run_dir.is_dir():
                continue
            decision_path = run_dir / "outputs/decision.json"
            try:
                decision = json.loads(decision_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                decision = {}
            checks = grade(scenario, decision if isinstance(decision, dict) else {})
            passed = sum(item["passed"] for item in checks)
            result = {
                "expectations": checks,
                "summary": {"passed": passed, "failed": len(checks) - passed,
                            "total": len(checks), "pass_rate": passed / len(checks)},
            }
            (run_dir / "grading.json").write_text(
                json.dumps(result, indent=2) + "\n", encoding="utf-8"
            )
            runs += 1
    print(f"Graded {runs} router runs in {iteration_dir}")
    return 0


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: grade_benchmark.py ITERATION_DIR", file=sys.stderr)
        return 1
    return grade_iteration(Path(sys.argv[1]).resolve())


if __name__ == "__main__":
    raise SystemExit(main())
