#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(errors="replace") if path.exists() else ""


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def load_timing(run_dir: Path) -> dict:
    timing_path = run_dir / "timing.json"
    if not timing_path.exists():
        return {}
    try:
        return json.loads(timing_path.read_text())
    except json.JSONDecodeError:
        return {}


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def build_grading(expectations: list[dict], run_dir: Path) -> dict:
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    outputs_dir = run_dir / "outputs"
    output_chars = 0
    if outputs_dir.exists():
        for path in outputs_dir.rglob("*"):
            if path.is_file():
                output_chars += len(read_text(path))
    transcript = read_text(run_dir / "transcript.md") + read_text(run_dir / "session.jsonl")
    timing = load_timing(run_dir)
    duration_seconds = timing.get("total_duration_seconds", 0.0)
    return {
        "expectations": expectations,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 2) if total else 0.0,
        },
        "execution_metrics": {
            "tool_calls": {},
            "total_tool_calls": 0,
            "total_steps": 0,
            "errors_encountered": 0,
            "output_chars": output_chars,
            "transcript_chars": len(transcript),
        },
        "timing": {
            "executor_duration_seconds": duration_seconds,
            "grader_duration_seconds": 0.0,
            "total_duration_seconds": duration_seconds,
        },
        "claims": [],
        "user_notes_summary": {
            "uncertainties": [],
            "needs_review": [],
            "workarounds": [],
        },
        "eval_feedback": {
            "suggestions": [],
            "overall": "No evaluator suggestions.",
        },
    }


def eval_id_for(eval_dir: Path) -> int | None:
    metadata_path = eval_dir / "eval_metadata.json"
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text())
            if "eval_id" in metadata:
                return int(metadata["eval_id"])
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    match = re.match(r"eval-(\d+)", eval_dir.name)
    if match:
        return int(match.group(1))
    return None


def has_all(text: str, items: list[str]) -> bool:
    lowered = normalize(text)
    return all(item.lower() in lowered for item in items)


def line_count(text: str) -> int:
    return len(text.splitlines())


def path_matches(value: str, expected_suffix: str) -> bool:
    return value == expected_suffix or value.endswith("/" + expected_suffix)


def grade_root_create(run_dir: Path) -> list[dict]:
    handoff_path = run_dir / "outputs" / "repo" / ".agents" / "scratchpad" / "handoff.md"
    result_path = run_dir / "outputs" / "result.json"
    handoff_text = read_text(handoff_path)
    result = read_json(result_path)
    normalized_handoff = normalize(handoff_text)
    return [
        expectation(
            "outputs/repo/.agents/scratchpad/handoff.md is created.",
            handoff_path.exists(),
            handoff_text or "missing outputs/repo/.agents/scratchpad/handoff.md",
        ),
        expectation(
            "The handoff captures goal, status, exact next step, and verification state.",
            has_all(handoff_text, ["goal", "status", "next step", "verification state"]),
            handoff_text or "missing handoff.md",
        ),
        expectation(
            "The handoff names `src/auth_refresh.py:2`, `tests/test_auth_refresh.py:5`, and `logs/test-failure.txt`.",
            has_all(handoff_text, ["src/auth_refresh.py:2", "tests/test_auth_refresh.py:5", "logs/test-failure.txt"]),
            handoff_text or "missing handoff.md",
        ),
        expectation(
            "The handoff includes the retry-backoff focus, review correction or rejected jitter option, and redacts the secret token.",
            ("retry backoff" in normalized_handoff or "build_retry_schedule" in normalized_handoff)
            and ("jitter" in normalized_handoff or "code review" in normalized_handoff or "review" in normalized_handoff)
            and "tok_live_abc123secret" not in normalized_handoff,
            handoff_text or "missing handoff.md",
        ),
        expectation(
            "outputs/result.json reports the root-scoped handoff path and next step.",
            path_matches(result.get("written_path", ""), ".agents/scratchpad/handoff.md")
            and result.get("scope") == "root-scoped"
            and ("build_retry_schedule" in result.get("next_step", "") or "retry backoff" in normalize(result.get("next_step", ""))),
            json.dumps(result) if result else "missing outputs/result.json",
        ),
    ]


def grade_feature_update(run_dir: Path) -> list[dict]:
    handoff_path = run_dir / "outputs" / "repo" / ".agents" / "scratchpad" / "payments" / "handoff.md"
    result_path = run_dir / "outputs" / "result.json"
    handoff_text = read_text(handoff_path)
    result = read_json(result_path)
    normalized_handoff = normalize(handoff_text)
    return [
        expectation(
            "outputs/repo/.agents/scratchpad/payments/handoff.md is updated in place.",
            handoff_path.exists(),
            handoff_text or "missing outputs/repo/.agents/scratchpad/payments/handoff.md",
        ),
        expectation(
            "The updated handoff includes retry-metrics and docs focus plus the benchmark delta.",
            "retry metrics" in normalized_handoff
            and "docs" in normalized_handoff
            and "p95" in normalized_handoff
            and "480ms" in normalized_handoff
            and "310ms" in normalized_handoff,
            handoff_text or "missing handoff.md",
        ),
        expectation(
            "The updated handoff names `src/payment_retry.py:2` and `tests/test_payment_retry.py:5`.",
            has_all(handoff_text, ["src/payment_retry.py:2", "tests/test_payment_retry.py:5"]),
            handoff_text or "missing handoff.md",
        ),
        expectation(
            "The stale `inspect legacy YAML toggles` step is removed and review context is preserved.",
            "inspect legacy yaml toggles" not in normalized_handoff
            and ("code review" in normalized_handoff or "review" in normalized_handoff),
            handoff_text or "missing handoff.md",
        ),
        expectation(
            "outputs/result.json reports the feature-scoped handoff path.",
            path_matches(result.get("written_path", ""), ".agents/scratchpad/payments/handoff.md")
            and result.get("scope") == "feature-scoped",
            json.dumps(result) if result else "missing outputs/result.json",
        ),
    ]


def grade_fallback_noise(run_dir: Path) -> list[dict]:
    repo_dir = run_dir / "outputs" / "repo"
    handoff_path = repo_dir / ".agents" / "scratchpad" / "handoff.md"
    invalid_path = repo_dir / "docs" / "handoff.md"
    result_path = run_dir / "outputs" / "result.json"
    handoff_text = read_text(handoff_path)
    result = read_json(result_path)
    normalized_handoff = normalize(handoff_text)
    return [
        expectation(
            "outputs/repo/.agents/scratchpad/handoff.md is created.",
            handoff_path.exists(),
            handoff_text or "missing outputs/repo/.agents/scratchpad/handoff.md",
        ),
        expectation(
            "`outputs/repo/docs/handoff.md` is not created.",
            not invalid_path.exists(),
            "docs/handoff.md absent" if not invalid_path.exists() else "unexpected docs/handoff.md created",
        ),
        expectation(
            "The handoff references `logs/retry.log` and `diffs/patch.diff` by path and anchors `src/sync_retry.py:2` plus `tests/test_sync_retry.py:5`.",
            has_all(
                handoff_text,
                [
                    "logs/retry.log",
                    "diffs/patch.diff",
                    "src/sync_retry.py:2",
                    "tests/test_sync_retry.py:5",
                ],
            ),
            handoff_text or "missing handoff.md",
        ),
        expectation(
            "The handoff stays concise and does not expose the secret token or raw stack frame spam.",
            "tok_prod_999secret" not in normalized_handoff
            and "stack frame 27" not in normalized_handoff
            and line_count(handoff_text) <= 90,
            handoff_text or "missing handoff.md",
        ),
        expectation(
            "outputs/result.json reports the root-scoped fallback path.",
            path_matches(result.get("written_path", ""), ".agents/scratchpad/handoff.md")
            and result.get("scope") == "root-scoped",
            json.dumps(result) if result else "missing outputs/result.json",
        ),
    ]


def grade(eval_id: int, run_dir: Path) -> list[dict]:
    if eval_id == 0:
        return grade_root_create(run_dir)
    if eval_id == 1:
        return grade_feature_update(run_dir)
    if eval_id == 2:
        return grade_fallback_noise(run_dir)
    return [expectation(f"Unknown eval id {eval_id}.", False, "Unsupported eval")]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 skills/handoff/evals/grade_benchmark.py skills/handoff-workspace/<iteration-dir>")
        return 1

    iteration_dir = Path(sys.argv[1]).resolve()
    if not iteration_dir.exists():
        print(f"Iteration directory not found: {iteration_dir}")
        return 1

    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        eval_id = eval_id_for(eval_dir)
        if eval_id is None:
            print(f"Skipping {eval_dir}: could not determine eval id")
            continue
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            for run_dir in sorted(config_dir.glob("run-*")):
                grading = build_grading(grade(eval_id, run_dir), run_dir)
                (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
