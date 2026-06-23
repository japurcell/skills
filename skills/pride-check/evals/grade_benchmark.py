#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(errors="replace") if path.exists() else ""


def normalize(text: str) -> str:
    return " ".join(text.lower().replace("*", "").replace("`", "").split())


def load_timing(run_dir: Path) -> dict:
    path = run_dir / "timing.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


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


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


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


def find_output(run_dir: Path) -> str:
    for relative_path in ("outputs/pride.md", "outputs/decision.md"):
        path = run_dir / relative_path
        if path.exists():
            return read_text(path)
    return ""


def has_all(text: str, items: list[str]) -> bool:
    lowered = normalize(text)
    return all(item.lower() in lowered for item in items)


def has_any(text: str, items: list[str]) -> bool:
    lowered = normalize(text)
    return any(item.lower() in lowered for item in items)


def starts_with_pride_check(text: str) -> bool:
    return text.lstrip().startswith("Pride Check:")


def has_pride_labels(text: str) -> bool:
    return has_all(
        text,
        [
            "Senior respect:",
            "Self-explaining:",
            "Edge cases:",
            "Simplicity:",
            "Codebase better:",
        ],
    )


def looks_negative_applicability(text: str) -> bool:
    lowered = normalize(text)
    return (
        "does not apply yet" in lowered
        or "not applicable yet" in lowered
        or "does not apply" in lowered
        or "not applicable" in lowered
    )


def mentions_no_change_reason(text: str) -> bool:
    lowered = normalize(text)
    return (
        "no non-trivial code change" in lowered
        or "no code change" in lowered
        or "read-only" in lowered
        or "before i touch anything" in lowered
        or "before coding" in lowered
    )


def grade(eval_id: int, output_text: str) -> list[dict]:
    normalized = normalize(output_text)

    if eval_id == 0:
        return [
            expectation(
                "The output starts with `Pride Check:`.",
                starts_with_pride_check(output_text),
                output_text or "missing pride.md",
            ),
            expectation(
                "The output includes `Senior respect`, `Self-explaining`, `Edge cases`, `Simplicity`, and `Codebase better` labels.",
                has_pride_labels(output_text),
                output_text or "missing pride.md",
            ),
            expectation(
                "The output mentions both `src/auth_session.py` and `tests/test_auth_session.py`.",
                has_all(output_text, ["src/auth_session.py", "tests/test_auth_session.py"]),
                output_text or "missing pride.md",
            ),
            expectation(
                "The output mentions a real edge case from the fixture such as missing token, missing expiry, the refresh window, or a boundary timestamp.",
                has_any(output_text, ["missing token", "missing expiry", "refresh window", "boundary", "expired"]),
                output_text or "missing pride.md",
            ),
        ]

    if eval_id == 1:
        return [
            expectation(
                "The output starts with `Pride Check:`.",
                starts_with_pride_check(output_text),
                output_text or "missing pride.md",
            ),
            expectation(
                "The output includes `Senior respect`, `Self-explaining`, `Edge cases`, `Simplicity`, and `Codebase better` labels.",
                has_pride_labels(output_text),
                output_text or "missing pride.md",
            ),
            expectation(
                "The output mentions `src/report_builder.py`, `src/report_formatter.py`, and `tests/test_report_builder.py`.",
                has_all(
                    output_text,
                    ["src/report_builder.py", "src/report_formatter.py", "tests/test_report_builder.py"],
                ),
                output_text or "missing pride.md",
            ),
            expectation(
                "The output mentions either duplicate formatting removal, blank-row handling, or missing-owner handling.",
                has_any(output_text, ["duplicate", "blank row", "missing owner", "format_row", "formatting"]),
                output_text or "missing pride.md",
            ),
        ]

    if eval_id == 2:
        return [
            expectation(
                "The decision says the skill does not apply yet or is not applicable yet.",
                looks_negative_applicability(output_text),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision explains that no non-trivial code change has happened yet, or that the task is read-only / before coding.",
                mentions_no_change_reason(output_text),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision does not contain a `Pride Check:` block.",
                "pride check:" not in normalized,
                output_text or "missing decision.md",
            ),
        ]

    return [expectation(f"Unknown eval id {eval_id}.", False, "Unsupported eval")]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: grade_benchmark.py <iteration-dir>")
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
                output_text = find_output(run_dir)
                grading = build_grading(grade(eval_id, output_text), run_dir)
                (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
