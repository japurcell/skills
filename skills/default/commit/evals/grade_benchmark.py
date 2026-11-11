#!/usr/bin/env python3

import json
import re
import subprocess
import sys
from pathlib import Path


COPILOT_TRAILER = "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
REQUIRED_HEADINGS = [
    "## Overview",
    "## When to Use",
    "## Workflow",
    "## Specific Techniques",
    "## Common Rationalizations",
    "## Red Flags",
    "## Verification",
]


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(errors="replace")


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def has_required_skill_shape() -> tuple[bool, str]:
    text = read_text(Path("skills/default/commit/SKILL.md"))
    ok = all(heading in text for heading in REQUIRED_HEADINGS)
    return ok, "all anatomy headings present" if ok else "missing one or more anatomy headings"


def has_commit_message_shape(commit_message: str, commit_type: str, subject: str) -> tuple[bool, str]:
    lines = commit_message.splitlines()
    if len(lines) < 8:
        return False, commit_message or "missing commit_message"
    header_pattern = rf"^{re.escape(commit_type)}(?:\([^)]+\))?: {re.escape(subject)}$"
    if re.match(header_pattern, lines[0]) is None:
        return False, lines[0]
    if lines[1] != "":
        return False, "missing blank line after subject"
    index = 2
    for heading in ("Summary:", "Rationale:", "Tests:"):
        while index < len(lines) and lines[index] == "":
            index += 1
        if index >= len(lines) or lines[index] != heading:
            return False, f"missing {heading}"
        index += 1
        bullet_count = 0
        while index < len(lines) and lines[index].startswith("- "):
            bullet_count += 1
            index += 1
        if bullet_count == 0:
            return False, f"missing bullet under {heading}"
    while index < len(lines) and lines[index] == "":
        index += 1
    trailer_lines = lines[index:]
    if not trailer_lines:
        return False, "missing issue/co-author trailers"
    if "" in trailer_lines:
        return False, "blank line found inside trailers"
    if not any(line.startswith("Co-authored-by: ") for line in trailer_lines):
        return False, "missing Co-authored-by trailer"
    return True, lines[0]


def build_grading(run_dir: Path, expectations: list[dict]) -> dict:
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    transcript = read_text(run_dir / "transcript.md") + read_text(run_dir / "outputs" / "transcript.md")
    output_chars = 0
    outputs_dir = run_dir / "outputs"
    if outputs_dir.exists():
        for path in outputs_dir.rglob("*"):
            if path.is_file():
                output_chars += len(read_text(path))
    timing = read_json(run_dir / "timing.json")
    total_duration = timing.get("total_duration_seconds", 0.0)
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
            "executor_duration_seconds": total_duration,
            "grader_duration_seconds": 0.0,
            "total_duration_seconds": total_duration,
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


def eval_zero(result: dict) -> list[dict]:
    skill_ok, skill_evidence = has_required_skill_shape()
    commit_ok, commit_evidence = has_commit_message_shape(
        result.get("commit_message", ""),
        result.get("commit_type", ""),
        result.get("subject", ""),
    )
    branch = result.get("branch", "")
    return [
        expectation("The rewritten skill keeps the standard anatomy headings.", skill_ok, skill_evidence),
        expectation("Returns a commit decision instead of a stop.", result.get("status") == "commit", result.get("status", "<missing>")),
        expectation(
            "Selects only src/invoice/export_csv.py.",
            result.get("selected_paths") == ["src/invoice/export_csv.py"],
            str(result.get("selected_paths")),
        ),
        expectation(
            "Creates a non-main feature branch using issue 123.",
            branch not in {"", "main", "master"} and re.match(r"^feat/123-[a-z0-9-]+$", branch) is not None,
            branch or "<missing branch>",
        ),
        expectation("Uses commit type feat.", result.get("commit_type") == "feat", result.get("commit_type", "<missing>")),
        expectation("Uses commit message shape with Summary, Rationale, Tests, and trailer block.", commit_ok, commit_evidence),
        expectation(
            "Uses Refs #123 and the default Copilot trailer.",
            "Summary:" in result.get("commit_message", "") and "Rationale:" in result.get("commit_message", "") and "Tests:" in result.get("commit_message", "") and "Refs #123" in result.get("commit_message", "") and COPILOT_TRAILER in result.get("commit_message", ""),
            result.get("commit_message", "<missing commit_message>"),
        ),
        expectation(
            "Plans a push but no PR.",
            result.get("should_push") is True and result.get("should_create_pr") is False,
            json.dumps({"should_push": result.get("should_push"), "should_create_pr": result.get("should_create_pr")}),
        ),
    ]


def eval_one(result: dict) -> list[dict]:
    commit_ok, commit_evidence = has_commit_message_shape(
        result.get("commit_message", ""),
        result.get("commit_type", ""),
        result.get("subject", ""),
    )
    return [
        expectation("Returns a commit decision instead of a stop.", result.get("status") == "commit", result.get("status", "<missing>")),
        expectation(
            "Selects only the staged bugfix files and excludes unstaged README noise.",
            result.get("selected_paths") == ["src/rate_limit.py", "tests/test_rate_limit.py"],
            str(result.get("selected_paths")),
        ),
        expectation(
            "Keeps branch fix/rate-limit-backoff.",
            result.get("branch") == "fix/rate-limit-backoff",
            result.get("branch", "<missing branch>"),
        ),
        expectation("Uses commit type fix.", result.get("commit_type") == "fix", result.get("commit_type", "<missing>")),
        expectation("Uses commit message shape with Summary, Rationale, Tests, and trailer block.", commit_ok, commit_evidence),
        expectation(
            "Uses Fixes #456 and the default Copilot trailer.",
            "Summary:" in result.get("commit_message", "") and "Rationale:" in result.get("commit_message", "") and "Tests:" in result.get("commit_message", "") and "Fixes #456" in result.get("commit_message", "") and COPILOT_TRAILER in result.get("commit_message", ""),
            result.get("commit_message", "<missing commit_message>"),
        ),
        expectation(
            "Plans both push and PR creation.",
            result.get("should_push") is True and result.get("should_create_pr") is True,
            json.dumps({"should_push": result.get("should_push"), "should_create_pr": result.get("should_create_pr")}),
        ),
        expectation(
            "Sets the PR title to the commit subject and includes the issue in the body.",
            result.get("pr_title") == result.get("subject") and "Fixes #456" in result.get("pr_body", ""),
            json.dumps({"pr_title": result.get("pr_title"), "subject": result.get("subject"), "pr_body": result.get("pr_body")}),
        ),
    ]


def eval_two(result: dict) -> list[dict]:
    stop_reason = normalize(result.get("stop_reason", ""))
    next_action = normalize(result.get("next_action", ""))
    return [
        expectation("Returns a stop decision.", result.get("status") == "stop", result.get("status", "<missing>")),
        expectation(
            "Explains that the file scope is ambiguous.",
            "ambiguous" in stop_reason or "which files" in stop_reason or "top-level" in stop_reason,
            result.get("stop_reason", "<missing stop_reason>"),
        ),
        expectation(
            "Asks the user which files to commit next.",
            "which files" in next_action or "select" in next_action,
            result.get("next_action", "<missing next_action>"),
        ),
        expectation(
            "Does not plan a push or PR.",
            result.get("should_push") is False and result.get("should_create_pr") is False,
            json.dumps({"should_push": result.get("should_push"), "should_create_pr": result.get("should_create_pr")}),
        ),
    ]


def eval_three(result: dict) -> list[dict]:
    stop_reason = normalize(result.get("stop_reason", ""))
    next_action = normalize(result.get("next_action", ""))
    return [
        expectation("Returns a stop decision.", result.get("status") == "stop", result.get("status", "<missing>")),
        expectation(
            "Flags generated artifacts instead of committing them automatically.",
            "artifact" in stop_reason or "generated" in stop_reason or "screenshot" in stop_reason or "video" in stop_reason,
            result.get("stop_reason", "<missing stop_reason>"),
        ),
        expectation(
            "Asks for confirmation before versioning those artifacts.",
            "confirm" in next_action or "version" in next_action or "ask" in next_action,
            result.get("next_action", "<missing next_action>"),
        ),
        expectation(
            "Does not plan a push or PR.",
            result.get("should_push") is False and result.get("should_create_pr") is False,
            json.dumps({"should_push": result.get("should_push"), "should_create_pr": result.get("should_create_pr")}),
        ),
    ]


def eval_validation_workflow(run_dir: Path) -> list[dict]:
    try:
        events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text().splitlines()]
        fixture = json.loads((run_dir / "fixture.json").read_text())
        expected = json.loads((Path(__file__).parent / "files/validation-before-commit/input.json").read_text())
        if not isinstance(expected, dict) or any(not isinstance(expected.get(key), str) for key in ("draft", "after")):
            raise ValueError("the source fixture needs the original draft and expected file content")
        if not events or any(not isinstance(event, dict) for event in events):
            raise ValueError("missing or malformed observation events")
        for event in events:
            if event.get("kind") not in ("validation", "commit") or not isinstance(event.get("message"), str):
                raise ValueError("each observation needs a known kind and string message")
            if event["kind"] == "validation" and (
                type(event.get("exit_code")) is not int or not isinstance(event.get("path"), str)
            ):
                raise ValueError("validation observations need an integer exit_code and string path")
        if not isinstance(fixture, dict) or not isinstance(fixture.get("initial_head"), str):
            raise ValueError("fixture metadata needs the initial commit SHA")
        validations = [(index, event) for index, event in enumerate(events) if event.get("kind") == "validation"]
        commits = [(index, event) for index, event in enumerate(events) if event.get("kind") == "commit"]
        if not validations or not commits:
            raise ValueError("missing validator or commit observations")
        repo = run_dir / "repo"

        def git(*args):
            return subprocess.run(
                ["git", *args], cwd=repo, capture_output=True, text=True, check=True, timeout=10,
            ).stdout

        count = git("rev-list", "--count", f"{fixture['initial_head']}..HEAD").strip()
        paths = git("diff", "--name-only", fixture["initial_head"], "HEAD").splitlines()
        message = git("log", "-1", "--format=%B").rstrip("\n")
        first = validations[0][1]
        last_index, last = validations[-1]
        commit_index, commit = commits[0]
        scoped_files = all(Path(event["path"]).resolve().is_relative_to(run_dir.resolve()) for _, event in validations)
        final_message = last.get("message", "")
        return [
            expectation("The initial malformed draft fails validation.",
                        first.get("exit_code") == 1 and first["message"] == expected["draft"]
                        and first["path"] == str((run_dir / "message.txt").resolve()),
                        json.dumps(first)),
            expectation("The repaired draft is revalidated successfully before committing.",
                        len(validations) >= 2 and scoped_files and last.get("exit_code") == 0 and last_index < commit_index,
                        json.dumps({"validations": validations, "commit_index": commit_index})),
            expectation("Exactly one commit follows validation and contains only the scoped change.",
                        len(commits) == 1 and count == "1" and paths == ["notes.txt"]
                        and git("show", "HEAD:notes.txt") == expected["after"] and git("status", "--porcelain") == "",
                        json.dumps({"attempts": len(commits), "commits": count, "paths": paths})),
            expectation("The committed message matches the validated content and has real body lines.",
                        final_message.rstrip("\n") == commit.get("message", "").rstrip("\n") == message
                        and "\u2028" not in message and all("\n\n" + heading + "\n- " in message for heading in ("Summary:", "Rationale:", "Tests:")),
                        message),
        ]
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        return [expectation("Observed workflow evidence is complete and readable.", False, str(error))]


def grade_expectations(eval_id: int, run_dir: Path) -> list[dict]:
    if eval_id == 4:
        return eval_validation_workflow(run_dir)
    result = read_json(run_dir / "outputs" / "result.json")
    if not result:
        return [expectation("result.json exists and is valid JSON.", False, "missing or invalid outputs/result.json")]
    if eval_id == 0:
        return eval_zero(result)
    if eval_id == 1:
        return eval_one(result)
    if eval_id == 2:
        return eval_two(result)
    if eval_id == 3:
        return eval_three(result)
    return [expectation(f"Unknown eval id {eval_id}.", False, f"Unsupported eval_id={eval_id}")]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 skills/default/commit/evals/grade_benchmark.py skills/default/commit-workspace/<iteration-dir>")
        return 1

    iteration_dir = Path(sys.argv[1])
    if not iteration_dir.exists():
        print(f"Iteration directory not found: {iteration_dir}")
        return 1

    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        metadata = read_json(eval_dir / "eval_metadata.json")
        eval_id = metadata.get("eval_id")
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            run_dirs = sorted(config_dir.glob("run-*"))
            if not run_dirs:
                continue
            for run_dir in run_dirs:
                expectations = grade_expectations(eval_id, run_dir)
                grading = build_grading(run_dir, expectations)
                (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
