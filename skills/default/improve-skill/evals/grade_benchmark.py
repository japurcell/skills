#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(errors="replace") if path.exists() else ""


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def normalize(value: object) -> str:
    return " ".join(str(value).strip().lower().split())


def load_timing(run_dir: Path) -> dict:
    data = load_json(run_dir / "timing.json")
    return data if isinstance(data, dict) else {}


def output_chars(outputs_dir: Path) -> int:
    total = 0
    if not outputs_dir.exists():
        return total
    for path in outputs_dir.rglob("*"):
        if path.is_file():
            total += len(read_text(path))
    return total


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def build_grading(expectations: list[dict], run_dir: Path) -> dict:
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    timing = load_timing(run_dir)
    duration_seconds = timing.get("total_duration_seconds", 0.0)
    transcript = read_text(run_dir / "transcript.md") + read_text(run_dir / "session.jsonl")
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
            "output_chars": output_chars(run_dir / "outputs"),
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
    metadata = load_json(eval_dir / "eval_metadata.json")
    if "eval_id" in metadata:
        try:
            return int(metadata["eval_id"])
        except (TypeError, ValueError):
            return None
    match = re.match(r"eval-(\d+)", eval_dir.name)
    return int(match.group(1)) if match else None


def grade(eval_id: int, run_dir: Path) -> list[dict]:
    outputs_dir = run_dir / "outputs"

    if eval_id == 0:
        commit_skill_path = outputs_dir / "commit" / "SKILL.md"
        exists = commit_skill_path.exists()
        content = read_text(commit_skill_path)
        evidence = f"File exists: {exists}. Content snippet:\n{content[:500]}"

        has_git_status = "git status" in content.lower() or "status" in content.lower()
        is_minimal = len(content) > 100 and len(content) < 10000

        return [
            expectation("outputs/commit/SKILL.md is created.", exists, evidence),
            expectation("outputs/commit/SKILL.md mentions 'git status' or 'status'.", has_git_status, evidence),
            expectation("The update is minimal and preserves general structure.", is_minimal, evidence),
        ]

    if eval_id == 1:
        review_skill_path = outputs_dir / "code-review" / "SKILL.md"
        exists = review_skill_path.exists()
        content = read_text(review_skill_path)
        evidence = f"File exists: {exists}. Content snippet:\n{content[:500]}"

        has_lint = "lint" in content.lower() or "npm run lint" in content.lower()
        is_minimal = len(content) > 100 and len(content) < 10000

        return [
            expectation("outputs/code-review/SKILL.md is created.", exists, evidence),
            expectation("outputs/code-review/SKILL.md mentions 'lint' or 'npm run lint'.", has_lint, evidence),
            expectation("The update is minimal and preserves general structure.", is_minimal, evidence),
        ]

    if eval_id == 2:
        explore_skill_path = outputs_dir / "explore" / "SKILL.md"
        exists = explore_skill_path.exists()
        content = read_text(explore_skill_path)
        
        # If it doesn't exist, that is actually correct since noop means no changes!
        # If it exists, it should be identical to the original explore skill.
        orig_explore_path = Path("skills/explore/SKILL.md")
        orig_content = read_text(orig_explore_path)
        is_identical = content == orig_content if exists else True
        
        explanation = read_text(run_dir / "transcript.md") + read_text(run_dir / "session.jsonl")
        no_durable_noted = any(x in explanation.lower() for x in ["temporary", "noise", "no change", "noop", "non-durable"])
        
        evidence = f"File exists: {exists}. No-change explanation found: {no_durable_noted}."

        return [
            expectation("outputs/explore/SKILL.md is either not created or remains identical to source.", is_identical, evidence),
            expectation("The run explanation notes that the learning was non-durable or noise.", no_durable_noted, evidence),
        ]

    return [expectation(f"Unknown eval id {eval_id}.", False, f"Unsupported eval: {eval_id}")]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 skills/improve-skill/evals/grade_benchmark.py skills/improve-skill-workspace/<iteration-dir>")
        return 1

    iteration_dir = Path(sys.argv[1]).resolve()
    if not iteration_dir.exists():
        print(f"Iteration directory not found: {iteration_dir}")
        return 1

    for eval_dir in sorted(path for path in iteration_dir.iterdir() if path.is_dir() and path.name.startswith("eval-")):
        eval_id = eval_id_for(eval_dir)
        if eval_id is None:
            print(f"Skipping {eval_dir}: could not determine eval id")
            continue
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            for run_dir in sorted(path for path in config_dir.iterdir() if path.is_dir() and path.name.startswith("run-")):
                grading = build_grading(grade(eval_id, run_dir), run_dir)
                (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
