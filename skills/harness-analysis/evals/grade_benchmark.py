#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(errors="replace") if path.exists() else ""


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence[:1200]}


def has_any(text: str, needles: list[str]) -> bool:
    lowered = normalize(text)
    return any(needle.lower() in lowered for needle in needles)


def has_all(text: str, needles: list[str]) -> bool:
    lowered = normalize(text)
    return all(needle.lower() in lowered for needle in needles)


def recommendations_after_evidence(output: str) -> bool:
    evidence = output.find("## Evidence:")
    uncertainty = output.find("## Uncertainty:")
    recs = output.find("## Candidate Recommendations")
    if recs == -1:
        recs = output.find("## Highest-Impact Recommendations")
    return evidence != -1 and uncertainty != -1 and recs != -1 and evidence < recs and uncertainty < recs


def grade(eval_id: int, output: str) -> list[dict]:
    lowered = normalize(output)
    if eval_id == 0:
        return [
            expectation(
                "The report includes `## Evidence:` and `## Uncertainty:` sections before recommendations.",
                recommendations_after_evidence(output),
                output or "missing outputs/report.md",
            ),
            expectation(
                "The report mentions that structured session queries returned 0 rows and local logs were used instead.",
                has_all(output, ["0 rows", "local logs"]),
                output or "missing outputs/report.md",
            ),
            expectation(
                "The recommendations are phrased as candidate or tentative when impact is inferred from counts.",
                has_any(output, ["candidate", "tentative", "inferred"]),
                output or "missing outputs/report.md",
            ),
            expectation(
                "The report does not claim measured latency or proven token savings.",
                not has_any(output, ["measured latency", "proven token savings", "definitely saves", "will reduce latency"]),
                output or "missing outputs/report.md",
            ),
        ]
    if eval_id == 1:
        return [
            expectation(
                "The report groups path, LSP, fetch, and regex failures instead of listing every duplicate line.",
                has_all(output, ["Path", "LSP", "fetch", "regex"]) and lowered.count("path does not exist") <= 2,
                output or "missing outputs/report.md",
            ),
            expectation(
                "The report recommends verifying paths after one miss.",
                has_any(output, ["after one path miss", "after one missing path", "verify path", "verify with glob"]),
                output or "missing outputs/report.md",
            ),
            expectation(
                "The report recommends stopping LSP attempts after `No LSP client available`.",
                has_any(output, ["stop LSP", "No LSP client available", "unavailable tool"]),
                output or "missing outputs/report.md",
            ),
            expectation(
                "The report recommends capping guessed URL variants and switching to fixed-string or escaped search after regex parse errors.",
                has_any(output, ["cap", "two failed URL", "stop guessing"]) and has_any(output, ["fixed-string", "escape", "escaped"]),
                output or "missing outputs/report.md",
            ),
        ]
    if eval_id == 2:
        return [
            expectation(
                "The output says this is not a harness-analysis audit task.",
                has_any(output, ["not a harness-analysis", "not a harness analysis", "normal implementation"]),
                output or "missing outputs/report.md",
            ),
            expectation(
                "The output does not perform or invent an audit.",
                "## Candidate Recommendations" not in output and "## Evidence:" not in output,
                output or "missing outputs/report.md",
            ),
            expectation(
                "The output redirects to normal coding/debugging workflow.",
                has_any(output, ["normal coding", "debugging workflow", "implementation workflow"]),
                output or "missing outputs/report.md",
            ),
        ]
    if eval_id == 3:
        return [
            expectation(
                "The report states that session and hook log evidence is unavailable.",
                has_any(output, ["no session logs", "no hook logs", "logs were unavailable", "log evidence is unavailable"]),
                output or "missing outputs/report.md",
            ),
            expectation(
                "Recommendations are tentative and grounded only in available instruction files.",
                has_any(output, ["tentative", "limited evidence", "instruction files"]),
                output or "missing outputs/report.md",
            ),
            expectation(
                "The report does not fabricate counts, failures, or log paths.",
                not re.search(r"\b\d{2,}\b.*(failures|events|tool calls|hook events)", lowered),
                output or "missing outputs/report.md",
            ),
            expectation(
                "The report includes `Evidence:` and `Uncertainty:` sections.",
                "## Evidence:" in output and "## Uncertainty:" in output,
                output or "missing outputs/report.md",
            ),
        ]
    return [expectation(f"Unknown eval id {eval_id}.", False, "Unsupported eval")]


def build_grading(expectations: list[dict], run_dir: Path) -> dict:
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
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
            "output_chars": len(read_text(run_dir / "outputs" / "report.md")),
            "transcript_chars": len(read_text(run_dir / "transcript.md")) + len(read_text(run_dir / "session.jsonl")),
        },
        "timing": {
            "executor_duration_seconds": 0.0,
            "grader_duration_seconds": 0.0,
            "total_duration_seconds": 0.0,
        },
        "claims": [],
        "user_notes_summary": {
            "uncertainties": [],
            "needs_review": [],
            "workarounds": [],
        },
        "eval_feedback": {
            "suggestions": [],
            "overall": "Deterministic checks focus on evidence, uncertainty, bounded retries, and non-trigger behavior.",
        },
    }


def eval_id_for(eval_dir: Path) -> int | None:
    match = re.match(r"eval-(\d+)", eval_dir.name)
    return int(match.group(1)) if match else None


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
        for run_dir in sorted(eval_dir.glob("*_skill/run-*")) + sorted(eval_dir.glob("without_skill/run-*")):
            output = read_text(run_dir / "outputs" / "report.md")
            grading = build_grading(grade(eval_id, output), run_dir)
            (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
