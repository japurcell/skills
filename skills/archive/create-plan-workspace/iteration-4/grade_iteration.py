#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


EXPECTED_TECH_KEYWORDS = {
    0: ["fastapi", "postgres", "react", "typescript", "openapi"],
    1: ["redis", "object storage", "csv", "json"],
    2: ["node", "next.js", "playwright", "jest"],
}


def read_text(path: Path) -> str:
    return path.read_text() if path.exists() else ""


def file_summary(path: Path) -> str:
    return "exists with substantive content" if path.exists() and path.stat().st_size > 80 else "missing or too small"


def has_required_report_sections(report_text: str) -> bool:
    labels = [
        "Plan path:",
        "Artifacts generated:",
        "Gate results:",
        "Open risks:",
        "Next command:",
    ]
    positions = []
    for label in labels:
        idx = report_text.find(label)
        if idx == -1:
            return False
        positions.append(idx)
    return positions == sorted(positions)


def quickstart_expectation(quickstart_text: str) -> tuple[bool, str]:
    headings = [
        "## Prerequisites",
        "## 1. Implement",
        "## 2. Validate",
        "## 3. Rollout/Operate",
    ]
    missing = [heading for heading in headings if heading not in quickstart_text]
    if missing:
        return False, f"Missing headings: {', '.join(missing)}"

    implement_section = quickstart_text.split("## 1. Implement", 1)[1].split("## 2. Validate", 1)[0]
    validate_section = quickstart_text.split("## 2. Validate", 1)[1].split("## 3. Rollout/Operate", 1)[0]

    command_pattern = re.compile(r"^\s*[-*]?\s*Command:", re.MULTILINE)
    implement_has_command = "```bash" in implement_section or bool(command_pattern.search(implement_section))
    validate_has_command = "```bash" in validate_section or bool(command_pattern.search(validate_section))
    expected_outcomes = len(re.findall(r"Expected outcome:", quickstart_text)) >= 2

    if implement_has_command and validate_has_command and expected_outcomes:
        return True, "Required headings, commands, and expected outcomes present"

    problems = []
    if not implement_has_command:
        problems.append("Implement section lacks a concrete command")
    if not validate_has_command:
        problems.append("Validate section lacks a concrete command")
    if not expected_outcomes:
        problems.append("Expected outcomes are missing or too sparse")
    return False, "; ".join(problems)


def official_docs_expectation(eval_id: int, research_text: str) -> tuple[bool, str]:
    has_docs = "Official docs reviewed:" in research_text
    has_version = "Version/context checked:" in research_text
    keywords = EXPECTED_TECH_KEYWORDS.get(eval_id, [])
    matched = [keyword for keyword in keywords if keyword in research_text.lower()]

    if has_docs and has_version and len(matched) >= max(2, min(len(keywords), 2)):
        return True, (
            "Found `Official docs reviewed` and `Version/context checked` entries "
            f"with relevant technology references: {', '.join(matched)}"
        )

    problems = []
    if not has_docs:
        problems.append("missing `Official docs reviewed` entries")
    if not has_version:
        problems.append("missing `Version/context checked` entries")
    if len(matched) < 2:
        problems.append(
            "insufficient relevant technology coverage"
            + (f" (matched: {', '.join(matched)})" if matched else "")
        )
    return False, "; ".join(problems)


def has_decision_and_rationale(research_text: str) -> bool:
    decision_patterns = [
        r"^\s*-?\s*Decision:",
        r"^\s*\*\*Decision\*\*",
        r"^\s*##\s*Decision\b",
    ]
    rationale_patterns = [
        r"^\s*-?\s*Rationale:",
        r"^\s*\*\*Rationale\*\*",
        r"^\s*##\s*Rationale\b",
    ]
    return any(re.search(pattern, research_text, re.MULTILINE) for pattern in decision_patterns) and any(
        re.search(pattern, research_text, re.MULTILINE) for pattern in rationale_patterns
    )


def build_expectations(eval_id: int, outputs_dir: Path, assertions: list[str]) -> list[dict]:
    plan_text = read_text(outputs_dir / "plan.md")
    research_text = read_text(outputs_dir / "research.md")
    data_model_text = read_text(outputs_dir / "data-model.md")
    quickstart_text = read_text(outputs_dir / "quickstart.md")
    report_text = read_text(outputs_dir / "report.md")

    results = []
    for assertion in assertions:
        if assertion == "Output indicates an implementation plan artifact was produced":
            passed = bool(plan_text.strip()) and len(plan_text) > 200
            evidence = f"plan.md {file_summary(outputs_dir / 'plan.md')}"
        elif assertion == "Output includes a research artifact with decisions/rationale":
            passed = has_decision_and_rationale(research_text)
            evidence = (
                "research.md includes Decision and Rationale content"
                if passed
                else "research.md is missing Decision and/or Rationale entries"
            )
        elif "Official docs reviewed" in assertion and "Version/context checked" in assertion:
            passed, evidence = official_docs_expectation(eval_id, research_text)
        elif assertion == "Output includes a data model artifact":
            passed = bool(data_model_text.strip()) and len(data_model_text) > 120
            evidence = f"data-model.md {file_summary(outputs_dir / 'data-model.md')}"
        elif assertion.startswith("quickstart.md includes required headings"):
            passed, evidence = quickstart_expectation(quickstart_text)
        elif assertion.startswith("Final report conforms exactly to the 5-section output contract"):
            passed = has_required_report_sections(report_text)
            evidence = (
                "All required section labels present in correct order with actionable next command"
                if passed
                else "report.md is missing required section labels or order"
            )
        elif assertion == "Gate results capture both pre-research and post-design checks with pass/fail rationale":
            passed = "Pre-research" in report_text and "Post-design" in report_text and "PASS" in report_text
            evidence = (
                "Report includes pre-research and post-design gate outcomes with pass/fail language"
                if passed
                else "report.md does not clearly capture both gate checks with pass/fail rationale"
            )
        else:
            passed = False
            evidence = "No grading rule implemented for this assertion"

        results.append({"text": assertion, "passed": passed, "evidence": evidence})
    return results


def write_grading(run_dir: Path, expectations: list[dict]) -> None:
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    failed = total - passed
    outputs_dir = run_dir / "outputs"
    output_files = [path for path in outputs_dir.rglob("*") if path.is_file()]
    output_chars = sum(len(read_text(path)) for path in output_files if path.suffix in {".md", ".yaml", ".yml", ".json", ".txt"})
    transcript_chars = len(read_text(outputs_dir / "output.md"))

    timing = {"executor_duration_seconds": 0.0, "grader_duration_seconds": 0.0, "total_duration_seconds": 0.0}
    timing_file = run_dir / "timing.json"
    if timing_file.exists():
        timing.update(json.loads(timing_file.read_text()))

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
        "timing": timing,
        "claims": [],
        "user_notes_summary": {
            "uncertainties": [],
            "needs_review": [],
            "workarounds": [],
        },
    }

    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")
    (run_dir.parent / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: grade_iteration.py <iteration-dir>")
        return 1

    iteration_dir = Path(sys.argv[1])
    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        metadata = json.loads((eval_dir / "eval_metadata.json").read_text())
        eval_id = metadata["eval_id"]
        assertions = metadata["assertions"]
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            for run_dir in sorted(config_dir.glob("run-*")):
                outputs_dir = run_dir / "outputs"
                if not outputs_dir.exists():
                    continue
                expectations = build_expectations(eval_id, outputs_dir, assertions)
                write_grading(run_dir, expectations)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
