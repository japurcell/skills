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


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


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


def eval_id_for(eval_dir: Path) -> int | None:
    metadata_path = eval_dir / "eval_metadata.json"
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text())
            if "eval_id" in metadata:
                return int(metadata["eval_id"])
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    match = re.match(r"eval-(\d+)", eval_dir.name)
    if match:
        return int(match.group(1))
    return None


def count_lines(path: Path) -> int:
    return len(read_text(path).splitlines())


def report_has_sections(report_text: str, sections: list[str]) -> bool:
    return all(section.lower() in report_text.lower() for section in sections)


def any_scoped_agents(repo_dir: Path) -> bool:
    return any(path.name == "AGENTS.md" and path.parent != repo_dir for path in repo_dir.rglob("AGENTS.md"))


def grade_create_root(run_dir: Path) -> list[dict]:
    repo_dir = run_dir / "outputs" / "repo"
    agents_text = read_text(repo_dir / "AGENTS.md")
    report_text = read_text(run_dir / "outputs" / "report.md")
    normalized = normalize(agents_text)
    return [
        expectation(
            "outputs/repo/AGENTS.md is created.",
            (repo_dir / "AGENTS.md").exists(),
            agents_text or "missing outputs/repo/AGENTS.md",
        ),
        expectation(
            "outputs/repo/AGENTS.md captures the deploy validation command, sync test command, and generated-client rule.",
            "python3 scripts/check-config.py" in agents_text
            and "pytest tests/integration/test_sync.py -q" in agents_text
            and "src/generated" in normalized,
            agents_text or "missing outputs/repo/AGENTS.md",
        ),
        expectation(
            "outputs/repo/AGENTS.md excludes one-off noise like opening the README.",
            "readme" not in normalized and "opened" not in normalized and "laptop fan" not in normalized,
            agents_text or "missing outputs/repo/AGENTS.md",
        ),
        expectation(
            "outputs/report.md includes Learnings and Applied updates.",
            report_has_sections(report_text, ["Learnings", "Applied updates"]),
            report_text or "missing outputs/report.md",
        ),
    ]


def grade_scoped_refactor(run_dir: Path) -> list[dict]:
    repo_dir = run_dir / "outputs" / "repo"
    root_path = repo_dir / "AGENTS.md"
    root_text = read_text(root_path)
    web_text = read_text(repo_dir / "web" / "AGENTS.md")
    api_text = read_text(repo_dir / "api" / "AGENTS.md")
    report_text = read_text(run_dir / "outputs" / "report.md")
    source_root = Path("skills/self-improve/evals/files/scoped-refactor-fixture/AGENTS.md")
    return [
        expectation(
            "outputs/repo/web/AGENTS.md includes the serial web test command.",
            "pnpm --dir web test -- --runInBand" in web_text,
            web_text or "missing outputs/repo/web/AGENTS.md",
        ),
        expectation(
            "outputs/repo/api/AGENTS.md includes the schema validation command.",
            "python3 scripts/validate_schema.py" in api_text,
            api_text or "missing outputs/repo/api/AGENTS.md",
        ),
        expectation(
            "outputs/repo/AGENTS.md is shorter than the source root AGENTS.md and no longer owns the moved scoped commands.",
            count_lines(root_path) < count_lines(source_root)
            and "pnpm --dir web test -- --runInBand" not in root_text
            and "python3 scripts/validate_schema.py" not in root_text,
            root_text or "missing outputs/repo/AGENTS.md",
        ),
        expectation(
            "outputs/report.md includes Moved guidance and Grouped files.",
            report_has_sections(report_text, ["Moved guidance", "Grouped files"]),
            report_text or "missing outputs/report.md",
        ),
    ]


def grade_linked_doc(run_dir: Path) -> list[dict]:
    repo_dir = run_dir / "outputs" / "repo"
    root_text = read_text(repo_dir / "AGENTS.md")
    release_text = read_text(repo_dir / "docs" / "release.md")
    report_text = read_text(run_dir / "outputs" / "report.md")
    return [
        expectation(
            "outputs/repo/docs/release.md includes the new release sanity command.",
            "python3 scripts/release_sanity.py" in release_text,
            release_text or "missing outputs/repo/docs/release.md",
        ),
        expectation(
            "outputs/repo/AGENTS.md still links release detail to docs/release.md and does not inline the new command.",
            "docs/release.md" in root_text and "python3 scripts/release_sanity.py" not in root_text,
            root_text or "missing outputs/repo/AGENTS.md",
        ),
        expectation(
            "outputs/report.md includes Learnings and Applied updates.",
            report_has_sections(report_text, ["Learnings", "Applied updates"]),
            report_text or "missing outputs/report.md",
        ),
    ]


def grade_noop(run_dir: Path) -> list[dict]:
    repo_dir = run_dir / "outputs" / "repo"
    source_path = Path("skills/self-improve/evals/files/noop-fixture/AGENTS.md")
    output_path = repo_dir / "AGENTS.md"
    source_text = read_text(source_path)
    output_text = read_text(output_path)
    report_text = read_text(run_dir / "outputs" / "report.md")
    normalized_report = normalize(report_text)
    return [
        expectation(
            "outputs/repo/AGENTS.md matches the source fixture AGENTS.md.",
            output_text == source_text,
            output_text or "missing outputs/repo/AGENTS.md",
        ),
        expectation(
            "No new scoped AGENTS.md files are created.",
            not any_scoped_agents(repo_dir),
            "no extra scoped AGENTS.md files" if not any_scoped_agents(repo_dir) else "unexpected scoped AGENTS.md created",
        ),
        expectation(
            "outputs/report.md says none qualified or no changes were made.",
            "none qualified" in normalized_report
            or "no changes" in normalized_report
            or "no durable learning qualified" in normalized_report,
            report_text or "missing outputs/report.md",
        ),
    ]


def grade_progress_fixture(run_dir: Path) -> list[dict]:
    repo_dir = run_dir / "outputs" / "repo"
    root_text = read_text(repo_dir / "AGENTS.md")
    auth_text = read_text(repo_dir / "docs" / "auth.md")
    report_text = read_text(run_dir / "outputs" / "report.md")
    normalized_auth = normalize(auth_text)
    return [
        expectation(
            "outputs/repo/docs/auth.md captures representative progress-file learnings for validation, replay bugs, accessibility, and stable tests.",
            (
                ("decoded" in normalized_auth or "prefix" in normalized_auth)
                and ("nested `it`" in auth_text or "nested it" in normalized_auth)
                and ("cached stream" in normalized_auth or "fresh-fetch" in normalized_auth or "replay" in normalized_auth or "sharereplay(1)" in normalized_auth)
                and "aria-describedby" in normalized_auth
                and ("time-based" in normalized_auth or "time range" in normalized_auth or "avoid flake" in normalized_auth or "single-rule" in normalized_auth or "placeholder" in normalized_auth)
            ),
            auth_text or "missing outputs/repo/docs/auth.md",
        ),
        expectation(
            "outputs/repo/docs/auth.md preserves the staged production-artifact startup-test guidance.",
            "wwwroot/dist/browser/index.html" in auth_text
            or ("production" in normalized_auth and "startup" in normalized_auth and "artifact" in normalized_auth),
            auth_text or "missing outputs/repo/docs/auth.md",
        ),
        expectation(
            "outputs/repo/AGENTS.md still links auth detail to docs/auth.md and does not inline the detailed auth rules.",
            "docs/auth.md" in root_text
            and "aria-describedby" not in root_text
            and "shareReplay(1)" not in root_text
            and "decoded" not in normalize(root_text),
            root_text or "missing outputs/repo/AGENTS.md",
        ),
        expectation(
            "outputs/report.md includes Learnings, Applied updates, and Assumptions.",
            report_has_sections(report_text, ["Learnings", "Applied updates", "Assumptions"]),
            report_text or "missing outputs/report.md",
        ),
    ]


def grade(eval_id: int, run_dir: Path) -> list[dict]:
    if eval_id == 0:
        return grade_create_root(run_dir)
    if eval_id == 1:
        return grade_scoped_refactor(run_dir)
    if eval_id == 2:
        return grade_linked_doc(run_dir)
    if eval_id == 3:
        return grade_noop(run_dir)
    if eval_id == 4:
        return grade_progress_fixture(run_dir)
    return [expectation(f"Unknown eval id {eval_id}.", False, "Unsupported eval")]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: grade_benchmark.py <iteration-dir>")
        return 1

    iteration_dir = Path(sys.argv[1]).resolve()
    if not iteration_dir.exists():
        print(f"Iteration directory not found: {iteration_dir}")
        return 1

    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        eval_id = eval_id_for(eval_dir)
        if eval_id is None:
            print(f"Skipping {eval_dir}: could not determine eval id")
            continue
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            for run_dir in sorted(config_dir.glob("run-*")):
                grading = build_grading(grade(eval_id, run_dir), run_dir)
                (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
