#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(errors="replace")


def load_timing(run_dir: Path) -> dict:
    timing_path = run_dir / "timing.json"
    if timing_path.exists():
        try:
            return json.loads(timing_path.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def grade(eval_name: str, report_text: str) -> list[dict]:
    text = report_text.lower()

    if eval_name == "command-injection-export":
        return [
            {
                "text": "Report identifies a command injection issue in app.py",
                "passed": ("command injection" in text or "shell" in text) and "app.py" in text,
                "evidence": "Report mentions app.py with command execution risk" if (("command injection" in text or "shell" in text) and "app.py" in text) else "No app.py command injection finding found in findings.md"
            },
            {
                "text": "Report marks the command injection finding as High severity",
                "passed": "severity: high" in text or "- severity: high" in text,
                "evidence": "Report contains High severity marker" if ("severity: high" in text or "- severity: high" in text) else "No High severity marker found for the command injection finding"
            },
            {
                "text": "Report does not flag the README.md example token",
                "passed": "readme.md" not in text and "local-dev-token-123" not in text,
                "evidence": "Report does not mention README.md token bait" if ("readme.md" not in text and "local-dev-token-123" not in text) else "Report incorrectly references README.md token bait"
            },
        ]

    if eval_name == "path-traversal-download":
        return [
            {
                "text": "Report identifies a path traversal issue in files.py",
                "passed": ("path traversal" in text or "directory traversal" in text) and "files.py" in text,
                "evidence": "Report mentions files.py with path traversal risk" if (("path traversal" in text or "directory traversal" in text) and "files.py" in text) else "No files.py path traversal finding found in findings.md"
            },
            {
                "text": "Report marks the path traversal finding as Medium or High severity",
                "passed": any(marker in text for marker in ["severity: medium", "severity: high", "- severity: medium", "- severity: high"]),
                "evidence": "Report contains Medium/High severity marker" if any(marker in text for marker in ["severity: medium", "severity: high", "- severity: medium", "- severity: high"]) else "No Medium or High severity marker found for the path traversal finding"
            },
            {
                "text": "Report does not flag regex or logging bait in audit.py",
                "passed": "audit.py" not in text and "regex" not in text and "logging" not in text,
                "evidence": "Report ignores excluded regex/logging bait" if ("audit.py" not in text and "regex" not in text and "logging" not in text) else "Report incorrectly references audit.py regex/logging bait"
            },
        ]

    if eval_name == "excluded-patterns-only":
        return [
            {
                "text": "Report states that there are no HIGH or MEDIUM findings",
                "passed": "no high or medium findings" in text,
                "evidence": "Report explicitly states there are no HIGH or MEDIUM findings" if "no high or medium findings" in text else "Report did not state that there were no HIGH or MEDIUM findings"
            },
            {
                "text": "Report does not flag README.md examples",
                "passed": "readme.md" not in text and "demo-token-for-docs-only" not in text,
                "evidence": "Report ignores README.md documentation bait" if ("readme.md" not in text and "demo-token-for-docs-only" not in text) else "Report incorrectly references README.md documentation bait"
            },
            {
                "text": "Report does not flag tests or logging-only changes",
                "passed": "test_runner.py" not in text and "tests/" not in text and "log spoof" not in text and "logging" not in text,
                "evidence": "Report ignores test-only and logging-only bait" if ("test_runner.py" not in text and "tests/" not in text and "log spoof" not in text and "logging" not in text) else "Report incorrectly references excluded tests/logging bait"
            },
        ]

    raise ValueError(f"Unknown eval name: {eval_name}")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: grade_reports.py <run-dir>", file=sys.stderr)
        return 2

    run_dir = Path(sys.argv[1]).resolve()
    metadata_path = run_dir.parent.parent / "eval_metadata.json"
    outputs_dir = run_dir / "outputs"
    report_path = outputs_dir / "findings.md"
    transcript_path = outputs_dir / "transcript.md"

    metadata = json.loads(metadata_path.read_text())
    report_text = read_text(report_path)
    transcript_text = read_text(transcript_path)
    expectations = grade(metadata["eval_name"], report_text)
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    failed = total - passed
    timing = load_timing(run_dir)

    output_chars = 0
    transcript_chars = len(transcript_text)
    for file_path in outputs_dir.iterdir():
        if file_path.is_file():
            output_chars += len(read_text(file_path))

    grading = {
        "expectations": expectations,
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": total,
            "pass_rate": round(passed / total, 2) if total else 0.0,
        },
        "execution_metrics": {
            "tool_calls": {},
            "total_tool_calls": 0,
            "total_steps": 0,
            "errors_encountered": 0,
            "output_chars": output_chars,
            "transcript_chars": transcript_chars,
        },
        "timing": {
            "executor_duration_seconds": timing.get("total_duration_seconds", 0.0),
            "grader_duration_seconds": 0.0,
            "total_duration_seconds": timing.get("total_duration_seconds", 0.0),
        },
        "claims": [],
        "user_notes_summary": {
            "uncertainties": [],
            "needs_review": [],
            "workarounds": [],
        },
        "eval_feedback": {
            "suggestions": [],
            "overall": "No suggestions, evals look solid"
        }
    }

    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())