#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(errors="replace") if path.exists() else ""


def normalize(text: str) -> str:
    return " ".join(text.lower().replace("*", "").split())


def load_timing(run_dir: Path) -> dict:
    path = run_dir / "timing.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


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


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


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


def find_output(run_dir: Path) -> tuple[str, str]:
    for relative_path in ("outputs/report.md", "outputs/decision.md", "outputs/conflict.md"):
        path = run_dir / relative_path
        if path.exists():
            return relative_path, read_text(path)
    return "", ""


def has_all(text: str, items: list[str]) -> bool:
    lowered = normalize(text)
    return all(item.lower() in lowered for item in items)


def has_url_host(text: str, host: str) -> bool:
    return host.lower() in normalize(text)


def looks_negative_applicability(text: str) -> bool:
    lowered = normalize(text)
    return (
        "does not apply" in lowered
        or "this skill does not apply" in lowered
        or "not apply" in lowered
        or "not needed" in lowered
        or "not necessary" in lowered
    )


def mentions_framework_agnostic_reason(text: str) -> bool:
    lowered = normalize(text)
    return "framework-agnostic" in lowered or "version-independent" in lowered or "version independent" in lowered


def asks_for_version(text: str) -> bool:
    lowered = normalize(text)
    return (
        "which version" in lowered
        or "exact version" in lowered
        or "exact sdk version" in lowered
        or "exact foosdk version" in lowered
        or "share the version" in lowered
        or "need the version" in lowered
        or "need exact version" in lowered
        or "need exact" in lowered and "version" in lowered
        or "please provide the version" in lowered
        or "without an exact" in lowered and "version" in lowered
    )


def missing_or_unclear_version(text: str) -> bool:
    lowered = normalize(text)
    return (
        "missing" in lowered
        or "unclear" in lowered
        or "no version specifier" in lowered
        or "not pinned" in lowered
        or "not stated" in lowered
    )


def presents_router_choice(text: str) -> bool:
    lowered = normalize(text)
    return (
        "which should i follow" in lowered
        or "which path" in lowered
        or "needs decision" in lowered
        or "options (do not apply yet)" in lowered
        or "choose one explicitly" in lowered
        or "choose pages router" in lowered
        or "choose app router" in lowered
        or "pages router code" in lowered and "app router code" in lowered
        or "deciding intended router mode" in lowered
        or "confirmation before editing" in lowered
        or "determine helper runtime context" in lowered
        or "follow-up before implementation" in lowered
    )


def mentions_two_failed_url_stop(text: str) -> bool:
    lowered = normalize(text)
    return (
        ("two failed" in lowered or "2 failed" in lowered or "after two failures" in lowered)
        and ("stop guessing" in lowered or "stopped guessing" in lowered or "stop url guessing" in lowered)
    )


def mentions_index_or_search_fallback(text: str) -> bool:
    lowered = normalize(text)
    return has_url_host(text, "reactrouter.com") and ("index" in lowered or "search" in lowered)


def grade(eval_id: int, output_text: str) -> list[dict]:
    normalized = normalize(output_text)

    if eval_id == 0:
        return [
            expectation(
                "The report uses the requested STACK DETECTED, OFFICIAL SOURCES, IMPLEMENTATION NOTES, and UNVERIFIED sections.",
                has_all(output_text, ["STACK DETECTED", "OFFICIAL SOURCES", "IMPLEMENTATION NOTES", "UNVERIFIED"]),
                output_text or "missing report.md",
            ),
            expectation(
                "The report detects `react-router-dom` version `7.6.2`.",
                "react-router-dom" in normalized and "7.6.2" in normalized,
                output_text or "missing report.md",
            ),
            expectation(
                "The report cites an official `reactrouter.com` source.",
                has_url_host(output_text, "reactrouter.com"),
                output_text or "missing report.md",
            ),
            expectation(
                "The implementation notes recommend `useNavigate`.",
                "usenavigate" in normalized,
                output_text or "missing report.md",
            ),
        ]

    if eval_id == 1:
        return [
            expectation(
                "The decision says the skill does not apply.",
                looks_negative_applicability(output_text),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision explains that the task is framework-agnostic or version-independent.",
                mentions_framework_agnostic_reason(output_text),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision does not cite or instruct fetching official docs.",
                "http://" not in normalized
                and "https://" not in normalized
                and "official sources" not in normalized
                and "fetch official docs" not in normalized,
                output_text or "missing decision.md",
            ),
        ]

    if eval_id == 2:
        return [
            expectation(
                "The conflict note detects `next` version `15.3.1`.",
                "next" in normalized and "15.3.1" in normalized,
                output_text or "missing conflict.md",
            ),
            expectation(
                "The conflict note cites an official `nextjs.org` source.",
                has_url_host(output_text, "nextjs.org"),
                output_text or "missing conflict.md",
            ),
            expectation(
                "The conflict note names both `next/navigation` and `next/router`.",
                has_all(output_text, ["next/navigation", "next/router"]),
                output_text or "missing conflict.md",
            ),
            expectation(
                "The conflict note asks which path to follow or presents explicit options.",
                presents_router_choice(output_text) or ("a)" in normalized and "b)" in normalized),
                output_text or "missing conflict.md",
            ),
        ]

    if eval_id == 3:
        return [
            expectation(
                "The report says the FooSDK version is missing or unclear.",
                "foosdk" in normalized and missing_or_unclear_version(output_text),
                output_text or "missing report.md",
            ),
            expectation(
                "The report asks for the exact version instead of guessing.",
                asks_for_version(output_text),
                output_text or "missing report.md",
            ),
            expectation(
                "The report marks the pattern `UNVERIFIED`.",
                "unverified" in normalized,
                output_text or "missing report.md",
            ),
        ]

    if eval_id == 4:
        return [
            expectation(
                "The report detects `react-router-dom` version `7.6.2`.",
                "react-router-dom" in normalized and "7.6.2" in normalized,
                output_text or "missing report.md",
            ),
            expectation(
                "The report says it stopped guessing direct URLs after two failed official variants.",
                mentions_two_failed_url_stop(output_text),
                output_text or "missing report.md",
            ),
            expectation(
                "The report cites an official `reactrouter.com` source and mentions index or search fallback.",
                mentions_index_or_search_fallback(output_text),
                output_text or "missing report.md",
            ),
            expectation(
                "The report marks the unresolved pattern `UNVERIFIED`.",
                "unverified" in normalized,
                output_text or "missing report.md",
            ),
        ]

    if eval_id == 5:
        has_cache_note = "cache hit" in normalized or "cache_hit" in normalized or "official-sources-cache.json" in normalized or "scratchpad" in normalized
        return [
            expectation(
                "The report detects `react-router-dom` version `7.6.2`.",
                "react-router-dom" in normalized and "7.6.2" in normalized,
                output_text or "missing report.md",
            ),
            expectation(
                "The report notes a CACHE HIT or loading from `.agents/scratchpad/official-sources-cache.json`.",
                has_cache_note,
                output_text or "missing report.md",
            ),
            expectation(
                "The report reuses the cached findings and citations.",
                has_cache_note or "usenavigate" in normalized,
                output_text or "missing report.md",
            ),
        ]

    return [expectation(f"Unknown eval id {eval_id}.", False, "Unsupported eval")]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 skills/official-sources/evals/grade_benchmark.py skills/official-sources-workspace/<iteration-dir>")
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
                _, output_text = find_output(run_dir)
                grading = build_grading(grade(eval_id, output_text), run_dir)
                (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
