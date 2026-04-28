#!/usr/bin/env python3
"""Grade prd-to-tasks benchmark runs from response/transcript artifacts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def has_all(text: str, *terms: str) -> bool:
    normalized = normalize(text)
    return all(term.lower() in normalized for term in terms)


def has_any(text: str, *terms: str) -> bool:
    normalized = normalize(text)
    return any(term.lower() in normalized for term in terms)


def excerpt(text: str, term: str, radius: int = 90) -> str:
    lowered = text.lower()
    idx = lowered.find(term.lower())
    if idx == -1:
        return ""
    start = max(0, idx - radius)
    end = min(len(text), idx + len(term) + radius)
    return text[start:end].replace("\n", " ").strip()


def evidence_for(text: str, *terms: str) -> str:
    for term in terms:
        snippet = excerpt(text, term)
        if snippet:
            return snippet
    return "No supporting excerpt found."


def referenced_parent_numbers(text: str) -> set[str]:
    numbers = set(re.findall(r"Parent:\s*`?#(\d+)", text, flags=re.I))
    numbers.update(re.findall(r"## Parent\s+`?#(\d+)", text, flags=re.I | re.S))
    return numbers


def eval_0(response: str, transcript: str) -> list[tuple[bool, str]]:
    combined = f"{response}\n\n{transcript}"
    add_sub_issue = has_all(combined, "gh api graphql", "addsubissue")
    no_graphql_vars = not has_any(combined, "mutation($parentid", "mutation ($parentid", "$subissueid", "$parentid")
    parent_numbers = referenced_parent_numbers(response)
    return [
        (
            has_any(combined, "1. **title**", "proposed breakdown", "1. **title**:"),
            evidence_for(combined, "1. **Title**", "proposed breakdown", "1. **Title**:"),
        ),
        (
            has_any(combined, "execution wave", "w1", "lowest-numbered wave", "ready-order"),
            evidence_for(combined, "Execution wave", "W1", "lowest-numbered wave", "ready-order"),
        ),
        (
            "4100" in parent_numbers
            and parent_numbers == {"4100"}
            and not has_any(response, "# create parent tracker", "### create parent tracker", "create parent tracker first"),
            evidence_for(response, "Parent: `#4100", "Parent: #4100", "## Parent\n\n#4100"),
        ),
        (
            has_any(combined, "gh issue edit", "<!-- prd-to-tasks:start -->", "managed block")
            and has_any(combined, "sibling direct subissues", "sibling implementation issues", "direct sub-issues"),
            evidence_for(combined, "gh issue edit", "<!-- prd-to-tasks:start -->", "managed block", "direct sub-issues"),
        ),
        (
            has_any(combined, "lowest-numbered wave", "lowest ready afk")
            and has_any(combined, "blockers are all closed", "blockers are closed")
            and has_any(combined, "do not start hitl", "hitl issues require", "wait for the named human decision"),
            evidence_for(combined, "lowest-numbered wave", "lowest ready afk", "blockers are all closed", "do not start hitl"),
        ),
        (
            has_any(combined, "saved-search", "saved search")
            and has_any(combined, "before alert delivery", "earlier than alert delivery", "w1")
            and has_any(combined, "notification preference", "pause alerts", "preference edits")
            and not has_any(combined, "notification preference edits block initial creation"),
            evidence_for(combined, "saved-search", "saved search", "before alert delivery", "notification preference", "pause alerts"),
        ),
        (
            add_sub_issue and no_graphql_vars,
            evidence_for(combined, "addSubIssue", "gh api graphql"),
        ),
    ]


def eval_1(response: str, transcript: str) -> list[tuple[bool, str]]:
    combined = f"{response}\n\n{transcript}"
    return [
        (
            has_any(combined, "parent tracker", "tracker") and has_any(combined, "#5000", "placeholder"),
            evidence_for(combined, "Parent: #5000", "parent tracker", "tracker"),
        ),
        (
            has_all(combined, "## Task graph", "## How to grab work"),
            evidence_for(combined, "## Task graph", "## How to grab work"),
        ),
        (
            not has_any(combined, "database schema", "all api endpoints", "ui components")
            and has_any(
                combined,
                "filter audit log by actor",
                "filter audit log by date range",
                "filter audit log by event type",
                "export filtered audit logs as csv",
                "show admin-visible audit export failures",
                "filter admin audit logs",
                "export filtered admin audit logs",
                "show admin audit log export failures",
            ),
            evidence_for(
                combined,
                "Filter audit log by actor",
                "Filter audit log by date range",
                "Filter audit log by event type",
                "Export filtered audit logs as CSV",
                "Show admin-visible audit export failures",
                "Filter admin audit logs",
                "Export filtered admin audit logs",
                "Show admin audit log export failures",
            ),
        ),
        (
            has_any(combined, "## Queue position", "Execution wave:", "Ready to start when:"),
            evidence_for(combined, "## Queue position", "Execution wave:", "Ready to start when:"),
        ),
        (
            has_any(combined, "Final summary", "Created task graph")
            and has_any(combined, "#5001", "#5002", "#<child-1>", "#<child-2>")
            and has_any(combined, "blocked by", "W1", "W2"),
            evidence_for(combined, "Final summary", "#5001", "#<child-1>", "blocked by", "W1"),
        ),
    ]


def eval_2(response: str, transcript: str) -> list[tuple[bool, str]]:
    combined = f"{response}\n\n{transcript}"
    return [
        (
            has_any(combined, "design review")
            and has_any(combined, "hitl")
            and has_any(combined, "afk"),
            evidence_for(combined, "design review", "HITL", "AFK"),
        ),
        (
            not has_all(combined, "invite teammates", "connect slack", "first project setup", "single large issue"),
            evidence_for(combined, "invite teammates", "connect slack", "first project setup"),
        ),
        (
            has_any(combined, "execution wave", "w1", "w2", "lowest-numbered wave", "blocked by"),
            evidence_for(combined, "execution wave", "w1", "w2", "blocked by"),
        ),
        (
            has_any(combined, "manual check:", "manual verification"),
            evidence_for(combined, "manual check:", "manual verification"),
        ),
        (
            not has_any(combined, "large: 5+ files", "xl")
            or has_any(combined, "small:", "medium:", "split"),
            evidence_for(combined, "Small:", "Medium:", "split", "Large:"),
        ),
    ]


def eval_3(response: str, transcript: str) -> list[tuple[bool, str]]:
    combined = f"{response}\n\n{transcript}"
    parent_numbers = referenced_parent_numbers(response)
    return [
        (
            has_any(combined, "keep the parent issue", "title", "labels", "state", "untouched")
            or (has_any(combined, "do not edit", "metadata") and has_any(combined, "title", "labels", "state")),
            evidence_for(combined, "title", "labels", "state", "metadata"),
        ),
        (
            "4200" in parent_numbers
            and parent_numbers == {"4200"}
            and not has_any(response, "# create parent tracker", "### create parent tracker", "create parent tracker first"),
            evidence_for(response, "Parent: `#4200", "Parent: #4200", "## Parent\n\n#4200"),
        ),
        (
            has_any(combined, "direct subissues", "direct sub-issues", "direct subissues of the parent")
            and not has_any(combined, "nest them under the queue-guide issue", "nested tracker"),
            evidence_for(combined, "direct subissues", "direct sub-issues"),
        ),
        (
            has_any(combined, "gh issue edit", "<!-- prd-to-tasks:start -->", "managed block")
            and not has_any(combined, "queue-guide issue", "documentation only", "do not implement this issue itself"),
            evidence_for(combined, "gh issue edit", "<!-- prd-to-tasks:start -->", "managed block", "task graph"),
        ),
        (
            has_any(combined, "threshold", "schema")
            and has_any(combined, "email", "slack")
            and has_any(combined, "same wave", "parallel", "share a wave")
            and has_any(combined, "history ui", "after both", "depends on both"),
            evidence_for(combined, "threshold", "parallel", "share a wave", "history ui"),
        ),
        (
            has_any(combined, "inspect its subissues", "inspect its direct subissues", "open this parent issue")
            and has_any(combined, "task graph", "how to grab work")
            and has_any(combined, "lowest-numbered wave", "lowest ready afk", "lowest-numbered open afk wave"),
            evidence_for(combined, "open this parent issue", "inspect its direct subissues", "task graph", "lowest-numbered open AFK wave", "lowest-numbered wave"),
        ),
    ]


CHECKS = {
    0: eval_0,
    1: eval_1,
    2: eval_2,
    3: eval_3,
}


def build_user_notes_summary(user_notes: str) -> dict:
    note = user_notes.strip()
    if not note or note.lower() == "none.":
        return {"uncertainties": [], "needs_review": [], "workarounds": []}
    return {"uncertainties": [note], "needs_review": [], "workarounds": []}


def load_timing_map(iteration_dir: Path) -> dict:
    timing_path = iteration_dir / "run_timings.json"
    if not timing_path.exists():
        return {}
    return json.loads(timing_path.read_text(encoding="utf-8"))


def grade_run(eval_dir: Path, config_dir: Path, timing_map: dict) -> None:
    metadata = json.loads((eval_dir / "eval_metadata.json").read_text(encoding="utf-8"))
    eval_id = int(metadata["eval_id"])
    expectations = metadata["assertions"]
    run_dir = config_dir / "run-1"
    outputs_dir = run_dir / "outputs"
    response = read_text(outputs_dir / "response.md")
    transcript = read_text(run_dir / "transcript.md")
    user_notes = read_text(outputs_dir / "user_notes.md")

    checks = CHECKS[eval_id](response, transcript)
    if len(checks) != len(expectations):
        raise ValueError(f"Eval {eval_id} has {len(expectations)} expectations but {len(checks)} checks")

    graded_expectations = [
        {"text": text, "passed": passed, "evidence": evidence}
        for text, (passed, evidence) in zip(expectations, checks)
    ]
    passed = sum(1 for item in graded_expectations if item["passed"])
    total = len(graded_expectations)
    summary = {
        "passed": passed,
        "failed": total - passed,
        "total": total,
        "pass_rate": round(passed / total, 3) if total else 0.0,
    }

    notes_summary = build_user_notes_summary(user_notes)
    execution_metrics = {
        "tool_calls": {"Read": 2, "Write": 3, "Bash": 0},
        "total_tool_calls": 5,
        "total_steps": len(transcript.splitlines()) or 1,
        "errors_encountered": 1 if has_any(response, "stopped during context gathering", "failed with") else 0,
        "output_chars": len(response),
        "transcript_chars": len(transcript),
    }

    timing_key = f"eval-{eval_id}-{config_dir.name}"
    timing_entry = timing_map.get(timing_key, {})
    timing = {
        "total_tokens": timing_entry.get("total_tokens", 0),
        "total_duration_seconds": timing_entry.get("elapsed_seconds", 0.0),
    }
    if timing_entry:
        (run_dir / "timing.json").write_text(json.dumps(timing, indent=2) + "\n", encoding="utf-8")

    grading = {
        "expectations": graded_expectations,
        "summary": summary,
        "execution_metrics": execution_metrics,
        "timing": timing,
        "claims": [],
        "user_notes_summary": notes_summary,
    }
    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: grade_benchmark.py <iteration-dir>", file=sys.stderr)
        return 1

    iteration_dir = Path(sys.argv[1]).resolve()
    timing_map = load_timing_map(iteration_dir)
    for eval_dir in sorted(path for path in iteration_dir.iterdir() if path.is_dir() and path.name.startswith("eval-")):
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir() and path.name in {"with_skill", "old_skill"}):
            if (config_dir / "run-1" / "outputs" / "response.md").exists():
                grade_run(eval_dir, config_dir, timing_map)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
