#!/usr/bin/env python3
import json
import re
import shutil
from pathlib import Path

ITER_DIR = Path(__file__).resolve().parent
EVAL_DIRS = sorted([p for p in ITER_DIR.glob("eval-*") if p.is_dir()])

MANDATORY_SECTIONS = [
    "## User Scenarios & Testing",
    "## Requirements",
    "## Success Criteria",
    "## Assumptions",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def find_checklist(outputs_dir: Path) -> Path | None:
    primary = outputs_dir / "requirements.md"
    alt = outputs_dir / "checklists" / "requirements.md"
    if primary.exists():
        return primary
    if alt.exists():
        return alt
    return None


def evaluate_run(spec_path: Path, checklist_path: Path | None) -> list[dict]:
    spec = read_text(spec_path)
    checklist = read_text(checklist_path) if checklist_path else ""

    fr_count = len(re.findall(r"\*\*FR-\d+\*\*", spec))
    sc_count = len(re.findall(r"\*\*SC-\d+\*\*", spec))
    unchecked = len(re.findall(r"^- \[ \]", checklist, flags=re.MULTILINE))

    has_sections = all(section in spec for section in MANDATORY_SECTIONS)
    no_clarification = "[NEEDS CLARIFICATION" not in spec
    checklist_ok = bool(checklist_path) and unchecked == 0

    return [
        {
            "text": "Spec contains all mandatory sections: User Scenarios & Testing, Requirements, Success Criteria, Assumptions",
            "passed": has_sections,
            "evidence": "All mandatory section headings found" if has_sections else "One or more mandatory headings are missing",
        },
        {
            "text": "Spec has at least 8 functional requirements",
            "passed": fr_count >= 8,
            "evidence": f"Found {fr_count} FR items",
        },
        {
            "text": "Spec has at least 3 measurable success criteria",
            "passed": sc_count >= 3,
            "evidence": f"Found {sc_count} SC items",
        },
        {
            "text": "Spec contains no [NEEDS CLARIFICATION] markers",
            "passed": no_clarification,
            "evidence": "No clarification markers present" if no_clarification else "Found unresolved clarification marker(s)",
        },
        {
            "text": "Checklist exists and has no unchecked items",
            "passed": checklist_ok,
            "evidence": "Checklist exists and all boxes are checked" if checklist_ok else ("Checklist missing" if not checklist_path else f"Checklist has {unchecked} unchecked item(s)"),
        },
    ]


def write_run(eval_dir: Path, config: str):
    outputs_dir = eval_dir / config / "outputs"
    if not outputs_dir.exists():
        return

    run_dir = eval_dir / config / "run-1"
    run_outputs = run_dir / "outputs"
    run_outputs.mkdir(parents=True, exist_ok=True)

    for item in outputs_dir.iterdir():
        target = run_outputs / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)

    spec_path = run_outputs / "spec.md"
    checklist_path = find_checklist(run_outputs)

    expectations = evaluate_run(spec_path, checklist_path)
    passed = sum(1 for e in expectations if e["passed"])
    total = len(expectations)
    failed = total - passed
    pass_rate = (passed / total) if total else 0.0

    grading = {
        "expectations": expectations,
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": total,
            "pass_rate": round(pass_rate, 4),
        },
        "execution_metrics": {
            "tool_calls": {},
            "total_tool_calls": 0,
            "total_steps": 0,
            "errors_encountered": 0,
            "output_chars": len(read_text(spec_path)) + (len(read_text(checklist_path)) if checklist_path else 0),
            "transcript_chars": 0,
        },
        "timing": {
            "total_duration_seconds": 0.0
        },
        "claims": [],
        "user_notes_summary": {
            "uncertainties": [],
            "needs_review": [],
            "workarounds": [],
        },
    }

    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2), encoding="utf-8")
    (run_dir / "timing.json").write_text(
        json.dumps({"total_tokens": 0, "duration_ms": 0, "total_duration_seconds": 0.0}, indent=2),
        encoding="utf-8",
    )


for eval_dir in EVAL_DIRS:
    write_run(eval_dir, "with_skill")
    write_run(eval_dir, "old_skill")

print(f"Processed {len(EVAL_DIRS)} eval directories")
