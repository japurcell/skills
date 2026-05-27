#!/usr/bin/env python3

import json
import re
import subprocess
import sys
from pathlib import Path


ANATOMY_HEADINGS = [
    "## Overview",
    "## When to Use",
    "## Workflow",
    "## Specific Techniques",
    "## Common Rationalizations",
    "## Red Flags",
    "## Verification",
]

REFERENCE_PHRASES = [
    "This document describes the structure and format of agent-skills skill files.",
    "Every verification checkbox requires proof.",
    "Do not summarize the workflow",
]


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(errors="replace")


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def line_count(path: Path) -> int:
    return len(read_text(path).splitlines())


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return {}
    frontmatter = {}
    for line in parts[0].splitlines()[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip()
    return frontmatter


def run_quick_validate(skill_dir: Path) -> tuple[bool, str]:
    if not skill_dir.exists():
        return False, f"missing skill directory: {skill_dir}"
    command = [
        "python3",
        "skills/skill-creator/scripts/quick_validate.py",
        str(skill_dir),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    output = (completed.stdout + completed.stderr).strip()
    return completed.returncode == 0, output or f"quick_validate exit={completed.returncode}"


def compile_python(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, f"missing python file: {path}"
    command = ["python3", "-m", "py_compile", str(path)]
    completed = subprocess.run(command, capture_output=True, text=True)
    output = (completed.stdout + completed.stderr).strip()
    return completed.returncode == 0, output or f"py_compile exit={completed.returncode}"


def evals_count(path: Path) -> int:
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError:
        return 0
    return len(data.get("evals", []))


def has_headings(text: str) -> bool:
    return all(heading in text for heading in ANATOMY_HEADINGS)


def description_has_use_when(frontmatter: dict[str, str]) -> bool:
    description = frontmatter.get("description", "")
    return "use when" in description.lower() and len(description.split()) >= 8


def copies_reference(text: str) -> bool:
    lowered = text.lower()
    return any(phrase.lower() in lowered for phrase in REFERENCE_PHRASES)


def mentions_new_skill_baseline(text: str) -> bool:
    lowered = normalize(text)
    return "without_skill" in lowered or "without skill" in lowered


def mentions_modified_skill_baseline(text: str) -> bool:
    lowered = normalize(text)
    return "old_skill" in lowered or "old skill" in lowered or "skill-snapshot" in lowered or "snapshot" in lowered


def has_positive_generic_npm_instruction(text: str) -> bool:
    for raw_line in text.lower().splitlines():
        line = raw_line.strip()
        if "npm test" not in line and "npm run build" not in line:
            continue
        if (
            "do not" in line
            or "don't" in line
            or "dont" in line
            or "instead of" in line
            or "there is no" in line
            or "no single" in line
            or "avoid " in line
            or "falls back to" in line
        ):
            continue
        return True
    return False


def has_workspace_layout_reference(text: str) -> bool:
    lowered = text.lower()
    if "skills/<skill>-workspace/iteration-n" in lowered:
        return True
    return re.search(r"skills/[a-z0-9-]+-workspace/iteration-\d+", lowered) is not None


def relative_skill_dir(run_dir: Path, name: str) -> Path:
    return run_dir / "outputs" / name


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def grade_eval_zero(run_dir: Path) -> list[dict]:
    skill_dir = relative_skill_dir(run_dir, "release-notes-skill")
    skill_md = skill_dir / "SKILL.md"
    skill_text = read_text(skill_md)
    frontmatter = parse_frontmatter(skill_text)
    validate_ok, validate_evidence = run_quick_validate(skill_dir)
    grader_ok, grader_evidence = compile_python(skill_dir / "evals" / "grade_benchmark.py")
    output_md = read_text(run_dir / "outputs" / "output.md")
    eval_count = evals_count(skill_dir / "evals" / "evals.json")
    return [
        expectation("Generated skill passes quick_validate.", validate_ok, validate_evidence),
        expectation(
            "Generated SKILL.md uses the anatomy sections Overview, When to Use, Workflow, Specific Techniques, Common Rationalizations, Red Flags, and Verification.",
            has_headings(skill_text),
            "all anatomy headings present" if has_headings(skill_text) else "missing one or more anatomy headings",
        ),
        expectation(
            "Generated description says what the skill does and includes 'Use when' trigger language.",
            description_has_use_when(frontmatter),
            frontmatter.get("description", "<missing description>"),
        ),
        expectation(
            "Generated evals.json includes at least 3 evals.",
            eval_count >= 3,
            f"eval_count={eval_count}",
        ),
        expectation("Generated grade_benchmark.py compiles.", grader_ok, grader_evidence),
        expectation(
            "output.md lists quick_validate and ./scripts/install.sh.",
            "quick_validate.py" in output_md and "./scripts/install.sh" in output_md,
            output_md or "missing output.md",
        ),
        expectation(
            "output.md names without_skill as the baseline for a new skill benchmark.",
            mentions_new_skill_baseline(output_md),
            output_md or "missing output.md",
        ),
    ]


def grade_eval_one(run_dir: Path) -> list[dict]:
    skill_dir = relative_skill_dir(run_dir, "review-handoff")
    skill_md = skill_dir / "SKILL.md"
    skill_text = read_text(skill_md)
    frontmatter = parse_frontmatter(skill_text)
    validate_ok, validate_evidence = run_quick_validate(skill_dir)
    src_lines = line_count(Path("skills/create-skill/evals/files/review-handoff-draft/SKILL.md"))
    dst_lines = line_count(skill_md)
    has_assets = (skill_dir / "evals" / "evals.json").exists() and (skill_dir / "evals" / "grade_benchmark.py").exists()
    return [
        expectation(
            "Generated skill preserves the name review-handoff.",
            frontmatter.get("name") == "review-handoff",
            f"name={frontmatter.get('name', '<missing>')}",
        ),
        expectation("Generated skill passes quick_validate.", validate_ok, validate_evidence),
        expectation(
            "Generated SKILL.md is shorter than the source draft.",
            dst_lines < src_lines,
            f"source_lines={src_lines}, generated_lines={dst_lines}",
        ),
        expectation(
            "Generated SKILL.md avoids verbatim copy from references/skill-anatomy.md.",
            not copies_reference(skill_text),
            "no distinctive anatomy prose copied" if not copies_reference(skill_text) else "copied anatomy prose detected",
        ),
        expectation(
            "Generated eval assets include evals.json and grade_benchmark.py.",
            has_assets,
            "eval assets present" if has_assets else "missing eval assets",
        ),
        expectation(
            "output.md names old_skill or a snapshot as the baseline for modifying an existing skill.",
            mentions_modified_skill_baseline(read_text(run_dir / "outputs" / "output.md")),
            read_text(run_dir / "outputs" / "output.md") or "missing output.md",
        ),
    ]


def grade_eval_two(run_dir: Path) -> list[dict]:
    decision_text = read_text(run_dir / "outputs" / "decision.md")
    normalized = normalize(decision_text)
    outputs_root = run_dir / "outputs"
    created_plan_maker = any(path.name == "plan-maker" for path in outputs_root.iterdir()) if outputs_root.exists() else False
    revised_skill_paths = list(outputs_root.glob("*/SKILL.md"))
    revised_names = [parse_frontmatter(read_text(path)).get("name", "") for path in revised_skill_paths]
    names_existing = any(name in {"create-plan", "create-tasks"} for name in revised_names)
    return [
        expectation(
            "decision.md recommends reusing or refining an existing skill instead of creating plan-maker.",
            ("reuse" in normalized or "refine" in normalized or "update" in normalized) and "plan-maker" in normalized,
            decision_text or "missing decision.md",
        ),
        expectation(
            "decision.md names create-plan or create-tasks as the closer existing skill.",
            "create-plan" in normalized or "create-tasks" in normalized,
            decision_text or "missing decision.md",
        ),
        expectation(
            "No new plan-maker/SKILL.md is created.",
            not created_plan_maker and not (outputs_root / "plan-maker" / "SKILL.md").exists(),
            "no duplicate skill created" if not created_plan_maker else "plan-maker directory created",
        ),
        expectation(
            "If a revised skill is proposed, it preserves the existing skill name.",
            not revised_skill_paths or names_existing,
            f"revised_names={revised_names}",
        ),
    ]


def grade_eval_three(run_dir: Path) -> list[dict]:
    skill_dir = relative_skill_dir(run_dir, "task-wave")
    skill_md = skill_dir / "SKILL.md"
    skill_text = read_text(skill_md)
    frontmatter = parse_frontmatter(skill_text)
    validate_ok, validate_evidence = run_quick_validate(skill_dir)
    output_md = read_text(run_dir / "outputs" / "output.md")
    eval_count = evals_count(skill_dir / "evals" / "evals.json")
    repo_specific = (
        "python3 skills/skill-creator/scripts/quick_validate.py" in skill_text
        and "./scripts/install.sh" in skill_text
        and not has_positive_generic_npm_instruction(skill_text)
    )
    workspace_layout = has_workspace_layout_reference(output_md)
    return [
        expectation(
            "Generated skill preserves the name task-wave.",
            frontmatter.get("name") == "task-wave",
            f"name={frontmatter.get('name', '<missing>')}",
        ),
        expectation("Generated skill passes quick_validate.", validate_ok, validate_evidence),
        expectation(
            "Generated skill uses exact repo validation commands instead of positive generic npm test or npm run build instructions.",
            repo_specific,
            "repo-specific commands present and generic npm commands absent" if repo_specific else skill_text,
        ),
        expectation(
            "Generated output describes sibling workspace layout skills/<skill>-workspace/iteration-N.",
            workspace_layout,
            output_md or "missing output.md",
        ),
        expectation(
            "Generated evals.json includes at least 3 evals.",
            eval_count >= 3,
            f"eval_count={eval_count}",
        ),
    ]


def grade_expectations(eval_name: str, run_dir: Path) -> list[dict]:
    if eval_name == "create-new-skill-with-benchmarks":
        return grade_eval_zero(run_dir)
    if eval_name == "modify-existing-skill-to-dedupe":
        return grade_eval_one(run_dir)
    if eval_name == "reuse-existing-skill-instead-of-duplicating":
        return grade_eval_two(run_dir)
    if eval_name == "harden-skill-for-weaker-models":
        return grade_eval_three(run_dir)
    raise ValueError(f"Unknown eval name: {eval_name}")


def load_timing(run_dir: Path) -> dict:
    timing_path = run_dir / "timing.json"
    if not timing_path.exists():
        return {}
    try:
        return json.loads(timing_path.read_text())
    except json.JSONDecodeError:
        return {}


def build_grading(run_dir: Path, expectations: list[dict], timing: dict) -> dict:
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    transcript = read_text(run_dir / "transcript.md") + read_text(run_dir / "outputs" / "transcript.md")
    output_chars = 0
    outputs_dir = run_dir / "outputs"
    if outputs_dir.exists():
        for path in outputs_dir.rglob("*"):
            if path.is_file():
                output_chars += len(read_text(path))
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


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 skills/create-skill/evals/grade_benchmark.py skills/create-skill-workspace/<iteration-dir>")
        return 1

    iteration_dir = Path(sys.argv[1])
    if not iteration_dir.exists():
        print(f"Iteration directory not found: {iteration_dir}")
        return 1

    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        metadata = json.loads((eval_dir / "eval_metadata.json").read_text())
        eval_name = metadata["eval_name"]
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            run_dirs = sorted(config_dir.glob("run-*"))
            if not run_dirs:
                continue
            for run_dir in run_dirs:
                expectations = grade_expectations(eval_name, run_dir)
                grading = build_grading(run_dir, expectations, load_timing(run_dir))
                (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
