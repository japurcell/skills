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


def load_spawns(run_dir: Path) -> tuple[str, list]:
    path = run_dir / "outputs" / "spawns.json"
    raw = read_text(path)
    data = load_json(path)
    if isinstance(data, dict) and "spawns" in data:
        return raw, data["spawns"]
    if isinstance(data, list):
        return raw, data
    return raw, []


def load_decision(run_dir: Path) -> tuple[str, dict]:
    path = run_dir / "outputs" / "decision.json"
    return read_text(path), load_json(path)


def grade(eval_id: int, run_dir: Path) -> list[dict]:
    if eval_id == 0:
        raw_text, spawns = load_spawns(run_dir)
        evidence = raw_text or "missing spawns.json"
        
        has_spawns = len(spawns) > 0
        correct_count = 1 <= len(spawns) <= 3
        all_code_explorer = all(normalize(s.get("agent_name", "")) == "code-explorer" for s in spawns) if has_spawns else False
        parallel = all(not s.get("wait_for_previous", False) for s in spawns) if has_spawns else False
        
        # Verify spawns cover backend/auth, frontend pages, database schema
        areas_covered = False
        if has_spawns:
            prompts_text = " ".join(normalize(s.get("prompt", "")) for s in spawns)
            has_backend = "backend" in prompts_text or "auth" in prompts_text
            has_frontend = "frontend" in prompts_text or "page" in prompts_text
            has_db = "database" in prompts_text or "schema" in prompts_text or "db" in prompts_text
            areas_covered = has_backend or has_frontend or has_db

        return [
            expectation("The JSON output has 1 to 3 subagent spawns.", correct_count, evidence),
            expectation("Each spawn uses the 'code-explorer' agent.", all_code_explorer, evidence),
            expectation("Spawns run in parallel (wait_for_previous is false or omitted).", parallel, evidence),
            expectation("Spawns describe relevant codebase areas.", areas_covered, evidence),
        ]

    if eval_id == 1:
        raw_text, decision = load_decision(run_dir)
        evidence = raw_text or "missing decision.json"
        should_explore = decision.get("should_explore")
        reason = normalize(decision.get("reason", ""))
        
        reuse_mentioned = any(x in reason for x in ["reuse", "scratchpad", "exist", "already", "prior", "previous"])
        
        return [
            expectation("The decision sets 'should_explore' to false.", should_explore is False, evidence),
            expectation("The reason mentions reusing prior scratchpad or session context.", reuse_mentioned, evidence),
        ]

    if eval_id == 2:
        raw_text, decision = load_decision(run_dir)
        evidence = raw_text or "missing decision.json"
        should_explore = decision.get("should_explore")
        reason = normalize(decision.get("reason", ""))
        
        localized_mentioned = any(x in reason for x in ["local", "trivial", "known", "grep", "read_file", "specific", "single"])

        return [
            expectation("The decision sets 'should_explore' to false.", should_explore is False, evidence),
            expectation("The reason explains that the bug is localized or has a known path.", localized_mentioned, evidence),
        ]

    return [expectation(f"Unknown eval id {eval_id}.", False, f"Unsupported eval: {eval_id}")]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 skills/explore/evals/grade_benchmark.py skills/explore-workspace/<iteration-dir>")
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
