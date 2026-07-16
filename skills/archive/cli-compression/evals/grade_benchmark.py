#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(errors="replace") if path.exists() else ""


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def load_timing(run_dir: Path) -> dict:
    timing_path = run_dir / "timing.json"
    if not timing_path.exists():
        return {}
    try:
        return json.loads(timing_path.read_text())
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


def non_comment_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]


def all_lines_use_rtk(text: str) -> bool:
    lines = non_comment_lines(text)
    return bool(lines) and all(line.startswith("rtk ") for line in lines)


def contains_git_log_10(text: str) -> bool:
    return bool(re.search(r"\bgit\b.*\blog\b.*(?:\s-10\b|\s--max-count(?:=|\s+)10\b)", text))


def contains_short_status(text: str) -> bool:
    return "status --short" in text or "status -s" in text


def contains_diff_summary(text: str) -> bool:
    return "diff --stat" in text or "diff --summary" in text


def contains_read_or_smart_for_readme(text: str) -> bool:
    return "rtk read README.md" in text or "rtk smart README.md" in text


def contains_pytest(text: str) -> bool:
    return bool(re.search(r"\brtk\s+pytest\b", text))


def contains_raw_command(text: str, command: str) -> bool:
    return bool(re.search(rf"(?m)^{re.escape(command)}\s*$", text))


def prefers_builtin_tools(text: str) -> bool:
    normalized = normalize(text)
    return (
        ("built-in" in normalized or "built in" in normalized or "prefer" in normalized)
        and ("view" in normalized)
        and ("rg" in normalized)
        and ("first" in normalized or "instead" in normalized or "before" in normalized)
    )


def looks_like_shell_list(text: str) -> bool:
    return any(line.startswith("rtk ") or line.startswith("git ") or line.startswith("bash ") for line in non_comment_lines(text))


def uses_standalone_git_u(text: str) -> bool:
    return bool(re.search(r"\bgit\b[^\n]*\s-u(?:\s|$)", text))


def find_output_text(run_dir: Path) -> tuple[str, str]:
    for relative_path in ("outputs/commands.sh", "outputs/decision.md", "commands.sh", "decision.md"):
        path = run_dir / relative_path
        if path.exists():
            return relative_path, read_text(path)
    return "", ""


def eval_id_for(eval_dir: Path) -> int | None:
    metadata_path = eval_dir / "eval_metadata.json"
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text())
            if "eval_id" in metadata:
                return int(metadata["eval_id"])
        except (json.JSONDecodeError, ValueError, TypeError):
            pass
    match = re.match(r"eval-(\d+)", eval_dir.name)
    if match:
        return int(match.group(1))
    return None


def grade(eval_id: int, output_path: str, output_text: str) -> list[dict]:
    if eval_id == 0:
        return [
            expectation(
                "Every non-comment command line starts with `rtk`.",
                output_path.endswith("commands.sh") and all_lines_use_rtk(output_text),
                output_text or "missing commands.sh",
            ),
            expectation(
                "The command list includes repository status, a diff summary, and a short commit log.",
                all(token in output_text for token in ("status", "diff", "log")),
                output_text or "missing commands.sh",
            ),
            expectation(
                "Git status uses a compact form such as `status --short`.",
                contains_short_status(output_text),
                output_text or "missing commands.sh",
            ),
            expectation(
                "Git diff uses a compact summary form such as `diff --stat`.",
                contains_diff_summary(output_text),
                output_text or "missing commands.sh",
            ),
        ]

    if eval_id == 1:
        return [
            expectation(
                "Every non-comment command line starts with `rtk`.",
                output_path.endswith("commands.sh") and all_lines_use_rtk(output_text),
                output_text or "missing commands.sh",
            ),
            expectation(
                "The rewrite uses `rtk read` or `rtk smart` for `README.md`.",
                contains_read_or_smart_for_readme(output_text),
                output_text or "missing commands.sh",
            ),
            expectation(
                "The rewrite keeps a pytest command.",
                contains_pytest(output_text),
                output_text or "missing commands.sh",
            ),
            expectation(
                "The rewrite avoids raw `cat README.md`, `git status`, and `git diff` lines.",
                not any(
                    contains_raw_command(output_text, command)
                    for command in ("cat README.md", "git status", "git diff")
                ),
                output_text or "missing commands.sh",
            ),
        ]

    if eval_id == 2:
        normalized = normalize(output_text)
        return [
            expectation(
                "The decision note prefers built-in tools first.",
                prefers_builtin_tools(output_text),
                output_text or "missing decision.md",
            ),
            expectation(
                "The note mentions `view` for line-range inspection.",
                "view" in normalized,
                output_text or "missing decision.md",
            ),
            expectation(
                "The note mentions `rg` for repo search.",
                "rg" in normalized,
                output_text or "missing decision.md",
            ),
            expectation(
                "The note does not turn the answer into a shell command list.",
                output_path.endswith("decision.md") and not looks_like_shell_list(output_text),
                output_text or "missing decision.md",
            ),
        ]

    if eval_id == 3:
        return [
            expectation(
                "Every non-comment command line starts with `rtk`.",
                output_path.endswith("commands.sh") and all_lines_use_rtk(output_text),
                output_text or "missing commands.sh",
            ),
            expectation(
                "The command uses `git log -10` or an equivalent 10-commit form.",
                contains_git_log_10(output_text),
                output_text or "missing commands.sh",
            ),
            expectation(
                "The command includes `--ultra-compact`.",
                "--ultra-compact" in output_text,
                output_text or "missing commands.sh",
            ),
            expectation(
                "The command does not use the standalone Git flag `-u`.",
                not uses_standalone_git_u(output_text),
                output_text or "missing commands.sh",
            ),
        ]

    return [expectation("Unknown eval id.", False, f"eval_id={eval_id}")]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 skills/cli-compression/evals/grade_benchmark.py skills/cli-compression-workspace/<iteration-dir>")
        return 1

    iteration_dir = Path(sys.argv[1])
    if not iteration_dir.exists():
        print(f"Iteration directory not found: {iteration_dir}")
        return 1

    for eval_dir in sorted(path for path in iteration_dir.iterdir() if path.is_dir() and path.name.startswith("eval-")):
        eval_id = eval_id_for(eval_dir)
        if eval_id is None:
            continue
        config_dirs = [path for path in sorted(eval_dir.iterdir()) if path.is_dir()]
        for config_dir in config_dirs:
            run_dirs = [path for path in sorted(config_dir.glob("run-*")) if path.is_dir()]
            if not run_dirs:
                run_dirs = [config_dir]
            for run_dir in run_dirs:
                output_path, output_text = find_output_text(run_dir)
                grading = build_grading(grade(eval_id, output_path, output_text), run_dir)
                (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
