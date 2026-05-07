#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


SECTION_ORDER = [
    "## Goal",
    "## Current Status",
    "## Decisions and Constraints",
    "## Relevant Files",
    "## Open Questions or Blockers",
    "## Recommended Next Step",
]


def read_text(path: Path) -> str:
    return path.read_text(errors="replace") if path.exists() else ""


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def section_positions(text: str) -> dict[str, int]:
    positions = {}
    for section in SECTION_ORDER:
        idx = text.find(section)
        if idx != -1:
            positions[section] = idx
    return positions


def parse_bullets(block: str) -> list[str]:
    bullets = []
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return bullets


def extract_section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    rest = text[start + len(heading) :]
    end = len(rest)
    for next_heading in SECTION_ORDER:
        if next_heading == heading:
            continue
        idx = rest.find(next_heading)
        if idx != -1 and idx < end:
            end = idx
    return rest[:end].strip()


def relevant_file_reason_count(section: str) -> tuple[int, int]:
    bullets = parse_bullets(section)
    with_reason = sum(1 for bullet in bullets if " — " in bullet or " - " in bullet)
    return len(bullets), with_reason


def make_expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def grade_run(run_dir: Path, expected_scope: str) -> list[dict]:
    save_session = read_text(run_dir / "outputs" / "save-session.md")
    response = read_text(run_dir / "outputs" / "response.md")
    transcript = read_text(run_dir / "transcript.md") + read_text(run_dir / "session.jsonl")

    positions = section_positions(save_session)
    has_title = save_session.startswith("# Save Session")
    ordered = list(positions.values()) == sorted(positions.values()) and len(positions) == len(SECTION_ORDER)
    relevant_section = extract_section(save_session, "## Relevant Files")
    relevant_count, relevant_with_reason = relevant_file_reason_count(relevant_section)
    word_count = len(re.findall(r"\S+", save_session))
    has_scope = "Scope:" in response
    has_path = "save-session.md" in response
    has_note = "Most important note" in response
    scope_text = expected_scope in response
    has_no_handoff = "handoff" not in normalize(save_session + "\n" + response)

    return [
        make_expectation(
            "The save-session artifact starts with the Save Session title.",
            has_title,
            save_session.splitlines()[0] if save_session else "<empty>",
        ),
        make_expectation(
            "The save-session artifact includes the required section headings in the correct order.",
            ordered,
            "all headings present" if ordered else f"found={list(positions.keys())}",
        ),
        make_expectation(
            "The Relevant Files section includes at least one bullet and each bullet has a short reason.",
            relevant_count >= 1 and relevant_count == relevant_with_reason,
            f"bullets={relevant_count}, with_reason={relevant_with_reason}",
        ),
        make_expectation(
            "The save-session stays concise.",
            word_count <= 350,
            f"word_count={word_count}",
        ),
        make_expectation(
            "The response names the absolute path, the scope, and the next-session note.",
            has_scope and has_path and has_note,
            response or "missing response.md",
        ),
        make_expectation(
            "The response scope matches the expected feature-vs-root pattern for this run.",
            scope_text,
            response or "missing response.md",
        ),
        make_expectation(
            "The saved output avoids stale handoff wording.",
            has_no_handoff,
            "no stale handoff text" if has_no_handoff else "stale handoff text found",
        ),
    ]


def build_grading(expectations: list[dict], run_dir: Path) -> dict:
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    transcript_chars = len(transcript_text(run_dir))
    output_chars = sum(len(read_text(path)) for path in (run_dir / "outputs").rglob("*") if path.is_file())
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
            "transcript_chars": transcript_chars,
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


def load_timing(run_dir: Path) -> dict:
    timing_path = run_dir / "timing.json"
    if not timing_path.exists():
        return {}
    try:
        return json.loads(timing_path.read_text())
    except json.JSONDecodeError:
        return {}


def transcript_text(run_dir: Path) -> str:
    return read_text(run_dir / "transcript.md") + read_text(run_dir / "session.jsonl")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 skills/save-session/evals/grade_benchmark.py skills/save-session-workspace/<iteration-dir>")
        return 1

    iteration_dir = Path(sys.argv[1])
    if not iteration_dir.exists():
        print(f"Iteration directory not found: {iteration_dir}")
        return 1

    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        expected_scope = "root-scoped" if "root" in eval_dir.name else "feature-scoped"
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            for run_dir in sorted(config_dir.glob("run-*")):
                expectations = grade_run(run_dir, expected_scope)
                (run_dir / "grading.json").write_text(json.dumps(build_grading(expectations, run_dir), indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
