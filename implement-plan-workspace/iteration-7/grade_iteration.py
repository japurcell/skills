#!/usr/bin/env python3
import json
import re
import shutil
from pathlib import Path

ITER_DIR = Path(__file__).resolve().parent
EVAL_DIRS = sorted([path for path in ITER_DIR.glob("eval-*") if path.is_dir()])

SECTION_HEADERS = [
    "## Checklist Gate",
    "## Implementation Context Loaded",
    "## Phase Execution",
    "## Code Review Findings",
    "## Completion Validation",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def copy_outputs(eval_dir: Path, config: str) -> tuple[Path, str]:
    outputs_dir = eval_dir / config / "outputs"
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

    return run_dir, read_text(run_outputs / "response.md")


def has_line(text: str, pattern: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE) is not None


def expect(text: str, passed: bool, ok_evidence: str, fail_evidence: str) -> dict:
    return {
        "text": text,
        "passed": passed,
        "evidence": ok_evidence if passed else fail_evidence,
    }


def evaluate(eval_id: int, response: str) -> list[dict]:
    lower = response.lower()

    if eval_id == 0:
        return [
            expect(
                "Includes the checklist status table with Checklist, Total, Completed, Incomplete, and Status columns",
                has_line(response, r"\|\s*Checklist\s*\|\s*Total\s*\|\s*Completed\s*\|\s*Incomplete\s*\|\s*Status\s*\|"),
                "Checklist status table columns found.",
                "Checklist status table columns not found.",
            ),
            expect(
                "Asks the exact incomplete-checklist gate question",
                "some checklists are incomplete. do you want to proceed with implementation anyway? (yes/no)" in lower,
                "Exact gate question found.",
                "Exact gate question missing.",
            ),
            expect(
                "States that execution pauses pending user confirmation",
                ("pause" in lower or "halt" in lower or "stop" in lower) and ("confirmation" in lower or "reply" in lower or "replies" in lower or "response" in lower),
                "Response states that execution waits for user confirmation.",
                "Response does not clearly pause for user confirmation.",
            ),
        ]

    if eval_id == 1:
        return [
            expect(
                "Explicitly states that tasks.md is missing",
                "tasks.md" in lower and "missing" in lower,
                "tasks.md missing is stated.",
                "tasks.md missing is not stated clearly.",
            ),
            expect(
                "Instructs the user to run /create-tasks or regenerate planning artifacts",
                "/create-tasks" in response or "regenerate planning artifacts" in lower,
                "Recovery instruction found.",
                "Recovery instruction missing.",
            ),
            expect(
                "States that execution is halted before phase execution",
                ("halt" in lower or "block" in lower or "stop" in lower) and "phase execution" in lower,
                "Response blocks phase execution.",
                "Response does not clearly block before phase execution.",
            ),
        ]

    if eval_id == 2:
        return [
            expect(
                "Includes all five required output section headers",
                all(header in response for header in SECTION_HEADERS),
                "All required section headers found.",
                "One or more required section headers are missing.",
            ),
            expect(
                "Explains the overlap-based [P] parallelization rule",
                "[p]" in lower and "parallel" in lower and "overlap" in lower,
                "Overlap-based parallelization rule found.",
                "Overlap-based parallelization rule missing.",
            ),
            expect(
                "Includes the Checkpoint Decision block or equivalent explicit checkpoint criteria",
                "checkpoint decision" in lower and "status:" in lower and "next action:" in lower,
                "Checkpoint decision block found.",
                "Checkpoint decision block missing.",
            ),
        ]

    if eval_id == 3:
        return [
            expect(
                "Defines review scope from all uncommitted changed files including staged, unstaged, and untracked work",
                "uncommitted" in lower and "staged" in lower and "unstaged" in lower and "untracked" in lower,
                "All uncommitted file states are referenced.",
                "Review scope does not cover staged, unstaged, and untracked files clearly.",
            ),
            expect(
                "Excludes .gitignore from review scope",
                ".gitignore" in response and "exclude" in lower,
                ".gitignore exclusion found.",
                ".gitignore exclusion missing.",
            ),
            expect(
                "Includes the full Review Scope Coverage block",
                all(label in response for label in [
                    "Review Scope Coverage",
                    "- Total Changed (Uncommitted) Files:",
                    "- Total Reviewed Files:",
                    "- Missing Files:",
                    "- Missing File List:",
                    "- Excluded Files:",
                    "- Completion Gate:",
                ]),
                "Coverage block found.",
                "Coverage block is incomplete.",
            ),
            expect(
                "States that missing files keep review INCOMPLETE unless deferred or approved",
                "missing files > 0 => incomplete" in lower or ("incomplete" in lower and ("deferred" in lower or "approved" in lower)),
                "Missing-file gate found.",
                "Missing-file gate missing.",
            ),
        ]

    if eval_id == 4:
        return [
            expect(
                "Lists deleted files under exclusions rather than review scope",
                "src/legacy.ts" in response and "deleted" in lower and "excluded files" in lower,
                "Deleted-file exclusion found.",
                "Deleted-file exclusion missing.",
            ),
            expect(
                "Lists .gitignore under exclusions rather than review scope",
                ".gitignore" in response and "excluded files" in lower,
                ".gitignore exclusion found.",
                ".gitignore exclusion missing.",
            ),
            expect(
                "Uses the Review Scope Coverage block including Completion Gate",
                "Review Scope Coverage" in response and "- Completion Gate:" in response,
                "Coverage block and completion gate found.",
                "Coverage block or completion gate missing.",
            ),
            expect(
                "Coverage counts reflect only the non-excluded review target files",
                "Total Reviewed Files: 2" in response and "Missing Files: 0" in response,
                "Coverage counts match the two non-excluded files.",
                "Coverage counts do not match the expected two non-excluded files.",
            ),
        ]

    if eval_id == 5:
        return [
            expect(
                "Materializes review_scope_files from staged, unstaged, and untracked files",
                "review_scope_files" in response and "staged" in lower and "unstaged" in lower and "untracked" in lower,
                "review_scope_files and file states found.",
                "review_scope_files materialization is not explicit.",
            ),
            expect(
                "States that subagents must not recompute or narrow scope",
                ("must not" in lower or "do not let" in lower) and ("recompute" in lower or "narrow" in lower),
                "No-recompute rule found.",
                "No-recompute rule missing.",
            ),
            expect(
                "Reports missing files when only a subset is reviewed",
                all(name in response for name in ["docs/staged_notes.md", "scripts/new_check.sh", "src/unstaged_service.ts"]),
                "Missing files are enumerated.",
                "Missing files are not enumerated clearly.",
            ),
            expect(
                "Marks completion INCOMPLETE when files are omitted",
                "incomplete" in lower and "completion gate" in lower,
                "INCOMPLETE completion gate found.",
                "INCOMPLETE completion gate missing.",
            ),
        ]

    if eval_id == 6:
        return [
            expect(
                "Uses controller review_scope_files as authoritative",
                "review_scope_files" in response and "authoritative" in lower,
                "Authoritative controller list found.",
                "Authoritative controller list missing.",
            ),
            expect(
                "Detects reviewer file-list mismatch",
                "mismatch" in lower or "scope conflict" in lower or "out-of-scope" in lower or "did not follow the fixed scope requirement" in lower,
                "Reviewer mismatch detected.",
                "Reviewer mismatch not detected.",
            ),
            expect(
                "Reports missing and extra files after reconciliation",
                "docs/notes.md" in response and "scripts/helper.sh" in response,
                "Missing and extra files are reported.",
                "Missing and extra files are not both reported.",
            ),
            expect(
                "Keeps completion status INCOMPLETE until reconciled or explicitly deferred",
                "incomplete" in lower and ("reconciled" in lower or "deferred" in lower or "approval" in lower),
                "INCOMPLETE gating found.",
                "INCOMPLETE gating missing.",
            ),
        ]

    raise ValueError(f"Unexpected eval id: {eval_id}")


def grade_run(eval_dir: Path, config: str) -> None:
    outputs_dir = eval_dir / config / "outputs"
    if not outputs_dir.exists():
        return

    run_dir, response = copy_outputs(eval_dir, config)
    eval_id = json.loads((eval_dir / "eval_metadata.json").read_text(encoding="utf-8"))["eval_id"]
    expectations = evaluate(eval_id, response)
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    failed = total - passed
    output_chars = len(response)

    grading = {
        "run_id": f"{eval_dir.name}-{config}",
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": total,
            "pass_rate": round(passed / total, 4) if total else 0.0,
        },
        "expectations": expectations,
        "execution_metrics": {
            "tool_calls": {},
            "total_tool_calls": 0,
            "total_steps": 0,
            "errors_encountered": 0,
            "output_chars": output_chars,
            "transcript_chars": 0,
        },
        "timing": {
            "total_duration_seconds": 0.0,
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
        json.dumps({"total_tokens": output_chars, "duration_ms": 0, "total_duration_seconds": 0.0}, indent=2),
        encoding="utf-8",
    )


for eval_dir in EVAL_DIRS:
    for config_name in ("with_skill", "old_skill"):
        grade_run(eval_dir, config_name)

print(f"Processed {len(EVAL_DIRS)} eval directories")