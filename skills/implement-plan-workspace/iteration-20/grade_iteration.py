#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text() if path.exists() else ""


def lower(text: str) -> str:
    return text.lower()


def has_all_sections(text: str) -> tuple[bool, str]:
    labels = [
        "checklist gate",
        "implementation context loaded",
        "phase execution",
        "code review findings",
        "completion validation",
    ]
    lowered = lower(text)
    missing = [label for label in labels if label not in lowered]
    if missing:
        return False, f"Missing sections: {', '.join(missing)}"
    return True, "All five required progress sections are present"


def has_checkpoint(text: str) -> tuple[bool, str]:
    lowered = lower(text)
    passed = "checkpoint decision" in lowered and "status:" in lowered and "pass" in lowered and "fail" in lowered
    if passed:
        return True, "Checkpoint Decision block includes explicit pass/fail status language"
    return False, "Missing explicit Checkpoint Decision block with PASS/FAIL criteria"


def build_expectations(eval_id: int, response_text: str) -> list[dict]:
    lowered = lower(response_text)
    expectations = []

    def add(text: str, passed: bool, evidence: str) -> None:
        expectations.append({"text": text, "passed": passed, "evidence": evidence})

    if eval_id == 2:
        passed, evidence = has_all_sections(response_text)
        add(
            "Includes all five progress reporting sections: Checklist Gate, Implementation Context Loaded, Phase Execution, Code Review Findings, Completion Validation",
            passed,
            evidence,
        )

        passed = "controller" in lowered and "wave" in lowered and "subagent" in lowered
        evidence = (
            "Response explicitly assigns scheduling to the controller and describes wave/subagent planning"
            if passed
            else "Response does not clearly give the controller explicit wave ownership with subagent dispatch"
        )
        add(
            "States that the controller owns the wave plan rather than delegating phase-wide scheduling to one subagent",
            passed,
            evidence,
        )

        passed = all(task in response_text for task in ("T003", "T004", "T005")) and "parallel" in lowered and "subagent" in lowered and any(
            word in lowered for word in ("launch", "dispatch", "spawn")
        )
        evidence = (
            "Response groups T003/T004/T005 into an explicit parallel subagent dispatch"
            if passed
            else "Response does not clearly launch T003/T004/T005 as separate parallel subagent work"
        )
        add(
            "Launches separate implementation subagents in parallel for T003, T004, and T005 (or equivalent explicit same-wave dispatch)",
            passed,
            evidence,
        )

        t006_seq = "T006" in response_text and "sequential" in lowered
        t007_after = "T007" in response_text and "T003" in response_text and ("after T003" in response_text or lowered.find("t003") < lowered.find("t007"))
        passed = t006_seq and t007_after
        evidence = (
            "Response keeps T006 sequential and places T007 after T003/TDD dependency work"
            if passed
            else "Response does not clearly serialize T006 and keep T007 after T003"
        )
        add(
            "Keeps T006 sequential and keeps T007 after T003 because TDD or dependency ordering still applies",
            passed,
            evidence,
        )

        passed, evidence = has_checkpoint(response_text)
        add(
            "Defines a checkpoint decision format or equivalent explicit pass/fail criteria before advancing",
            passed,
            evidence,
        )

        passed = any(token in lowered for token in ("tdd", "test-first", "test-writing tasks"))
        evidence = "Response cites TDD/test-first ordering" if passed else "No clear TDD/test-first ordering rationale found"
        add(
            "References TDD-first ordering where test tasks run before their corresponding implementation tasks",
            passed,
            evidence,
        )

    elif eval_id == 5:
        passed = all(token in response_text for token in ("src/staged_api.ts", "docs/staged_notes.md", "src/unstaged_service.ts", "scripts/new_check.sh"))
        evidence = (
            "Response materializes review_scope_files from staged, unstaged, and untracked files"
            if passed
            else "Response does not clearly build review scope from all staged/unstaged/untracked files"
        )
        add(
            "Materializes review_scope_files from staged + unstaged + untracked files",
            passed,
            evidence,
        )

        passed = any(token in lowered for token in ("must not recompute", "must not narrow", "do not recompute", "do not narrow"))
        evidence = "Response states that review subagents must not narrow scope" if passed else "Response does not clearly forbid review-scope recomputation"
        add(
            "States subagents must not recompute or narrow scope independently",
            passed,
            evidence,
        )

        passed = "missing files" in lowered and any(token in response_text for token in ("docs/staged_notes.md", "src/unstaged_service.ts", "scripts/new_check.sh"))
        evidence = "Response reports omitted files as missing" if passed else "Response does not clearly report the omitted files as missing"
        add(
            "Reports missing files when only a subset is reviewed",
            passed,
            evidence,
        )

        passed = "completion gate" in lowered and "incomplete" in lowered
        evidence = "Response applies an INCOMPLETE completion gate" if passed else "Response does not clearly mark review completion as INCOMPLETE"
        add(
            "Applies Completion Gate with INCOMPLETE status when Missing Files > 0",
            passed,
            evidence,
        )

    elif eval_id == 10:
        passed = "code-simplifier" in lowered and any(token in lowered for token in (">5", "more than 5", "8 uncommitted", "8 changed"))
        evidence = "Response ties code-simplifier scaling to the >5-file rule" if passed else "Response does not clearly apply the >5-files scaling rule"
        add(
            "Launches more than one code-simplifier subagent since there are >5 changed files",
            passed,
            evidence,
        )

        passed = all(token in response_text for token in ("src/charts/bar.tsx", "src/data/fetcher.ts")) and any(token in lowered for token in ("non-overlapping", "partition", "module", "directory"))
        evidence = "Response partitions changed files into non-overlapping groups" if passed else "Response does not clearly partition files into non-overlapping groups"
        add(
            "Partitions files into non-overlapping groups (e.g., by module or directory) so each file appears in exactly one agent's scope",
            passed,
            evidence,
        )

        passed = any(token in lowered for token in ("3 code-reviewer", "three code-reviewer", "simplicity & dry", "bugs & correctness", "conventions & abstractions"))
        evidence = "Response also launches the required code-reviewer agents" if passed else "Response does not clearly launch the 3 code-reviewer agents"
        add(
            "Also launches code-reviewer subagents (3 with distinct lenses)",
            passed,
            evidence,
        )

    elif eval_id == 12:
        passed = "T003" in response_text and ("[X]" in response_text or "marked complete" in lowered or "counts as success" in lowered)
        evidence = "Response marks T003 complete or successful despite RED-state failures" if passed else "Response does not clearly mark T003 complete/successful"
        add(
            "Marks task T003 as [X] or completed because a clean TDD RED failure is a successful test-writing outcome",
            passed,
            evidence,
        )

        passed = "clean red" in lowered and any(token in lowered for token in ("syntax", "broken test", "import crashes", "invalid test setup"))
        evidence = "Response distinguishes clean RED from broken tests" if passed else "Response does not clearly separate clean RED from broken tests"
        add(
            "Distinguishes between a clean RED failure (tests fail for the intended reason) and a broken test (syntax errors, import crashes)",
            passed,
            evidence,
        )

        passed = any(token in lowered for token in ("tdd", "red-green", "red result"))
        evidence = "Response references TDD/RED-GREEN workflow" if passed else "Response does not reference TDD RED/GREEN workflow"
        add(
            "References TDD-first or RED-GREEN workflow as the reason this counts as success",
            passed,
            evidence,
        )

        passed = "error recovery" not in lowered and "halts progress" not in lowered and "blocks progress" not in lowered
        evidence = "Response does not treat the expected RED state as a blocking error" if passed else "Response still treats RED-state failures as blocking errors"
        add(
            "Does NOT treat the test failures as an error that blocks progress",
            passed,
            evidence,
        )

    elif eval_id == 15:
        passed = all(token in response_text for token in ("T010", "T011", "src/search/service.ts")) and any(
            phrase in lowered for phrase in ("cannot run in parallel", "must run sequentially", "not in the same wave")
        )
        evidence = (
            "Response explicitly serializes T010/T011 because both touch src/search/service.ts"
            if passed
            else "Response does not clearly explain why T010/T011 cannot share a parallel wave"
        )
        add(
            "Explicitly states that T010 and T011 cannot run in parallel because both touch src/search/service.ts",
            passed,
            evidence,
        )

        passed = "T012" in response_text and "src/search/metrics.ts" in response_text and "wave" in lowered
        evidence = "Response places T012 into an explicit wave with non-overlapping work" if passed else "Response does not clearly schedule T012 in a safe wave"
        add(
            "Schedules T012 in a wave that only includes non-overlapping work",
            passed,
            evidence,
        )

        passed = bool(re.search(r"w(ave)?\s*1", lowered)) and (bool(re.search(r"w(ave)?\s*2", lowered)) or "wait" in lowered or "then launch" in lowered)
        evidence = "Response shows multiple waves or an explicit wait point between them" if passed else "Missing explicit wave boundary or wait point"
        add(
            "Shows an explicit wave boundary or wait point before launching the next wave",
            passed,
            evidence,
        )

        passed = "subagent" in lowered and "wave" in lowered
        evidence = "Response assigns work by subagent/wave slot" if passed else "Response falls back to a vague phase-wide executor"
        add(
            "Assigns work to specific subagents or wave slots instead of saying one phase-wide subagent will figure it out",
            passed,
            evidence,
        )

    elif eval_id == 16:
        passed = "T020" in response_text and any(token in lowered for token in ("[ ]", "remains unchecked", "not complete", "leave t020"))
        evidence = "Response keeps T020 incomplete after verification failure" if passed else "Response does not clearly leave T020 incomplete"
        add(
            "Leaves T020 as [ ] or otherwise explicitly not complete because verification failed",
            passed,
            evidence,
        )

        passed = "T022" in response_text and any(token in lowered for token in ("finish", "still-running", "still running", "collect", "wait for"))
        evidence = "Response allows the already-running T022 work to finish or be collected" if passed else "Response does not clearly handle T022 as in-flight work"
        add(
            "Allows the already-running independent work for T022 to finish or be collected before deciding the next step",
            passed,
            evidence,
        )

        passed = "T021" in response_text and any(token in lowered for token in ("passed verification", "verified", "[x]", "mark t021 complete", "mark t021 [x]"))
        evidence = "Response marks T021 complete only after successful verification" if passed else "Response does not clearly keep T021 gated on verification success"
        add(
            "Marks T021 complete only if its own verification passed",
            passed,
            evidence,
        )

        passed = any(token in lowered for token in ("does not launch another wave", "no further wave", "before launching the next wave", "stop before the next wave"))
        evidence = "Response blocks the next wave until failure handling completes" if passed else "Response does not clearly halt before another wave"
        add(
            "States that the controller does not launch another wave until the failure is reported and resolved",
            passed,
            evidence,
        )

    else:
        raise ValueError(f"Unsupported eval_id {eval_id} for this iteration")

    return expectations


def write_grading(run_dir: Path, expectations: list[dict]) -> None:
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    failed = total - passed
    response_text = read_text(run_dir / "outputs" / "response.md")
    timing = {"executor_duration_seconds": 0.0, "grader_duration_seconds": 0.1, "total_duration_seconds": 0.1}
    timing_file = run_dir / "timing.json"
    if timing_file.exists():
        timing_data = json.loads(timing_file.read_text())
        exec_seconds = float(timing_data.get("total_duration_seconds", 0.0))
        timing = {
            "executor_duration_seconds": exec_seconds,
            "grader_duration_seconds": 0.1,
            "total_duration_seconds": round(exec_seconds + 0.1, 1),
        }

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
            "output_chars": len(response_text),
            "transcript_chars": len(response_text),
        },
        "timing": timing,
        "claims": [],
        "user_notes_summary": {
            "uncertainties": [],
            "needs_review": [],
            "workarounds": [],
        },
        "eval_feedback": {
            "suggestions": [],
            "overall": "No suggestions, evals look solid",
        },
    }
    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: grade_iteration.py <iteration-dir>")
        return 1

    iteration_dir = Path(sys.argv[1])
    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        metadata = json.loads((eval_dir / "eval_metadata.json").read_text())
        eval_id = metadata["eval_id"]
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            for run_dir in sorted(config_dir.glob("run-*")):
                response_text = read_text(run_dir / "outputs" / "response.md")
                if not response_text.strip():
                    continue
                expectations = build_expectations(eval_id, response_text)
                write_grading(run_dir, expectations)

    print("Wrote grading.json for iteration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
