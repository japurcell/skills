#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(errors="replace") if path.exists() else ""


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def clean_decision_text(text: str) -> str:
    cleaned_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append(line)
            continue
        if stripped == "I_CAN_SEE_SESSIONSTART_CONTEXT":
            continue
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}T[^ ]+", stripped):
            continue
        if stripped.startswith("I_CAN_SEE_SESSIONSTART_CONTEXT") and "<promise>COMPLETE</promise>" in stripped:
            stripped = stripped.replace("I_CAN_SEE_SESSIONSTART_CONTEXT", "", 1).strip()
            if stripped:
                cleaned_lines.append(stripped)
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()


def load_timing(run_dir: Path) -> dict:
    timing_path = run_dir / "timing.json"
    if not timing_path.exists():
        return {}
    try:
        return json.loads(timing_path.read_text())
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


def decision_text(run_dir: Path) -> str:
    return clean_decision_text(read_text(run_dir / "outputs" / "decision.md"))


def has_all(text: str, items: list[str]) -> bool:
    lowered = normalize(text)
    return all(item.lower() in lowered for item in items)


def mentions_forbidden_progress_fallback(text: str) -> bool:
    lowered = normalize(text)
    return any(
        token in lowered
        for token in [
            "session-state",
            "~/.copilot",
            ".copilot/session-state",
            "$home/.copilot",
            "scratchpad",
            "scratchpads",
            "temp-artifact",
            "temporary artifact",
        ]
    )


def mentions_progress_path(text: str, expected_path_hint: str) -> bool:
    lowered = normalize(text)
    return 'dirname(prd_file) + "/progress.txt"' in text or expected_path_hint.lower() in lowered


def mentions_active_wave(text: str, batch: int, story_ids: list[str]) -> bool:
    lowered = normalize(text)
    batch_ok = str(batch) in lowered and any(token in lowered for token in ["parallelbatch", "parallel batch", "batch"])
    stories_ok = all(story_id.lower() in lowered for story_id in story_ids)
    return batch_ok and stories_ok


def grade(eval_id: int, output_text: str) -> list[dict]:
    normalized = normalize(output_text)

    if eval_id == 0:
        return [
            expectation(
                "The decision says `prd_file` is official source of truth and `progress_file` is supplemental.",
                (
                    "prd_file" in normalized and "source of truth" in normalized and "progress_file" in normalized
                )
                or (
                    "official" in normalized
                    and ("prd.json" in normalized or "/prd.json" in normalized)
                    and "progress_file" in normalized
                    and ("supplemental" in normalized or "resume data" in normalized)
                ),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision resolves the default `progress_file` to `dirname(prd_file) + \"/progress.txt\"` or the fixture `startup-fixture/progress.txt` path, not a session-state fallback.",
                mentions_progress_path(output_text, "startup-fixture/progress.txt"),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision selects active `parallelBatch` 2 with ready stories `US-002` and `US-003`.",
                mentions_active_wave(output_text, 2, ["US-002", "US-003"]),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision dispatches one fresh implementer per parallel-safe story before story-specific discovery and does not start higher-batch work.",
                (
                    (
                        "dispatch fresh implementer per parallel-safe story" in normalized
                        or "dispatch one fresh implementer per parallel-safe story" in normalized
                        or "one fresh implementer per ready story" in normalized
                    )
                    and ("story-specific discovery" in normalized or "before any story-specific" in normalized)
                ),
                output_text or "missing decision.md",
            ),
        ]

    if eval_id == 1:
        return [
            expectation(
                "The decision identifies the current wave as ready stories `US-002` and `US-003` in `parallelBatch` 2.",
                mentions_active_wave(output_text, 2, ["US-002", "US-003"]),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision says the stories must be serialized instead of dispatched in parallel.",
                ("serial" in normalized or "serialize" in normalized or "one at a time" in normalized)
                and ("instead of" in normalized or "not parallel" in normalized or "not dispatch both in parallel" in normalized),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision cites the overlap reason using the shared owner surface or `src/ui/BillingSettingsPage.tsx`.",
                (
                    "src/ui/billingsettingspage.tsx" in normalized
                    or "billing settings page" in normalized
                    or ("overlap" in normalized and "owner surface" in normalized)
                    or ("same file" in normalized and "billing" in normalized)
                ),
                output_text or "missing decision.md",
            ),
        ]

    if eval_id == 2:
        return [
            expectation(
                "The decision appends the implementer `Progress block` before acting on it.",
                "progress block" in normalized
                and "append" in normalized
                and ("before" in normalized or "then rerun" in normalized or "then run" in normalized),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision reruns `code-simplifier` and `addy-code-reviewer` after the review fix.",
                has_all(output_text, ["code-simplifier", "addy-code-reviewer"])
                and ("rerun" in normalized or "run again" in normalized)
                and (
                    "review fix" in normalized
                    or "review_fix" in normalized
                    or "finalization reset" in normalized
                    or "implementer `progress block`" in normalized
                    or "fresh implementer `progress block`" in normalized
                    or "combined final state" in normalized
                ),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision keeps `passes: true` blocked until review is clean and final checks pass.",
                (
                    "passes: true" in output_text
                    or "`passes: true`" in output_text
                    or "passes: false" in output_text
                )
                and ("do not" in normalized or "leave" in normalized or "blocked" in normalized or "keep" in normalized)
                and "review is clean" in normalized
                and ("checks" in normalized or "verify" in normalized or "final-state checks" in normalized),
                output_text or "missing decision.md",
            ),
        ]

    if eval_id == 3:
        return [
            expectation(
                "The decision stops because the review-fix iteration limit is reached.",
                (
                    "review-fix" in normalized
                    and "limit" in normalized
                    and ("reached" in normalized or "already 3" in normalized or "iteration count is 3" in normalized)
                )
                or (
                    "stop" in normalized
                    and "do not dispatch another review-fix implementer" in normalized
                    and "append stop-state entry" in normalized
                ),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision says not to fix findings directly or dispatch another review-fix implementer.",
                (
                    ("do not" in normalized or "cannot" in normalized)
                    and ("fix directly" in normalized or "another review_fix" in normalized or "another review-fix" in normalized)
                )
                or (
                    "review-fix iteration limit reached" in normalized
                    and (
                        "must stop" in normalized
                        or "will not dispatch further review-fix implementers" in normalized
                        or "will not dispatch another review-fix implementer" in normalized
                    )
                ),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision rereads `prd_file`, appends stop state to `progress_file`, and asks the user to decide the blocker.",
                (
                    has_all(output_text, ["prd_file", "progress_file"])
                    and ("stop-state" in normalized or "stop state" in normalized)
                    and ("ask user" in normalized or "ask the user" in normalized or "human decision required" in normalized)
                    and ("blocker" in normalized or "decide" in normalized)
                )
                or (
                    ("prd.json" in output_text or "prd_file" in normalized)
                    and (
                        "please decide how to unblock this" in normalized
                        or "reply with chosen option" in normalized
                        or "awaiting user decision" in normalized
                        or "choose one" in normalized
                    )
                    and ("progress stop-state" in normalized or "append stop-state" in normalized or "progress_file" in normalized)
                ),
                output_text or "missing decision.md",
            ),
        ]

    if eval_id == 4:
        return [
            expectation(
                "The output is exactly `<promise>COMPLETE</promise>`.",
                output_text.strip() == "<promise>COMPLETE</promise>",
                output_text or "missing decision.md",
            )
        ]

    if eval_id == 5:
        return [
            expectation(
                "The decision tells `self-improve` to mine both `## Codebase Patterns` and every `Learnings for future iterations` block.",
                (
                    "codebase patterns" in normalized
                    and "learnings for future iterations" in normalized
                    and "self-improve" in normalized
                )
                or (
                    "codebase patterns" in normalized
                    and "self-improve" in normalized
                    and ("finalization" in normalized or "progress.txt sections" in normalized or "mine these" in normalized)
                )
                or (
                    "codebase patterns" in normalized
                    and "validation/safety" in normalized
                    and "cache/state/replay" in normalized
                    and "ux/accessibility" in normalized
                    and "testing/anti-flake" in normalized
                ),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision preserves durable validation, replay/cache, accessibility, and test-stability learnings from progress.",
                (
                    (
                        ("decoded" in normalized or "decode return-url" in normalized or "prefix safety" in normalized)
                        and ("cached stream" in normalized or "fresh-fetch" in normalized or "replay" in normalized or "sharereplay(1)" in normalized)
                        and "aria-describedby" in normalized
                        and (
                            "time-based" in normalized
                            or "time-claim ranges" in normalized
                            or "time range" in normalized
                            or "avoid flake" in normalized
                            or "single-rule" in normalized
                            or "placeholder" in normalized
                        )
                    )
                    or has_all(
                        output_text,
                        [
                            "validation/safety",
                            "cache/state/replay",
                            "UX/accessibility",
                            "testing/anti-flake",
                        ],
                    )
                ),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision preserves the staged production-artifact startup-test learning.",
                "wwwroot/dist/browser/index.html" in output_text
                or ("production" in normalized and "artifact" in normalized and "startup" in normalized)
                or ("dist artifact" in normalized and "startup" in normalized)
                or ("staged-dist" in normalized and "startup" in normalized)
                or ("wwwroot/dist path" in normalized)
                or (
                    ("environment/setup" in normalized or "environment / setup" in normalized)
                    and ("finalization entry" in normalized or "latest implementer notes" in normalized)
                ),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision writes only reusable guidance into nearby `AGENTS.md` or linked docs, not story-specific notes.",
                (
                    ("agents.md" in normalized or "linked docs" in normalized or "linked doc" in normalized)
                    and (
                        "reusable guidance" in normalized
                        or "durable" in normalized
                        or "standing guidance" in normalized
                        or "distilled reusable rules" in normalized
                        or "distilled reusable summary" in normalized
                    )
                    and (
                        "not story-specific" in normalized
                        or "drop story-specific" in normalized
                        or "not story specific" in normalized
                        or "story-only notes" in normalized
                        or "story-only" in normalized
                        or "story ids" in normalized
                        or "story ids, timestamps" in normalized
                    )
                )
                or (
                    ("agents.md" in normalized or "linked docs" in normalized or "linked doc" in normalized)
                    and (
                        "reusable rules only" in normalized
                        or "not raw progress history" in normalized
                        or "drop story ids" in normalized
                    )
                ),
                output_text or "missing decision.md",
            ),
        ]

    if eval_id == 6:
        return [
            expectation(
                "The decision resolves default `progress_file` to `dirname(prd_file) + \"/progress.txt\"` or the fixture `default-progress-path-fixture/progress.txt` path.",
                mentions_progress_path(output_text, "default-progress-path-fixture/progress.txt"),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision says the sibling path should be created on first append if it does not exist yet.",
                ("first append" in normalized or "on first append" in normalized or "first write" in normalized)
                and ("create" in normalized or "created" in normalized)
                and (
                    "does not exist yet" in normalized
                    or "if absent" in normalized
                    or "missing" in normalized
                    or "otherwise create" in normalized
                    or "create (if missing)" in normalized
                    or "append/create" in normalized
                ),
                output_text or "missing decision.md",
            ),
            expectation(
                "The decision explicitly forbids session-state, scratchpad, temp-artifact, or `~/.copilot/...` fallback paths.",
                ("do not" in normalized or "never" in normalized or "forbid" in normalized)
                and mentions_forbidden_progress_fallback(output_text),
                output_text or "missing decision.md",
            ),
        ]

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
                grading = build_grading(grade(eval_id, decision_text(run_dir)), run_dir)
                (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
