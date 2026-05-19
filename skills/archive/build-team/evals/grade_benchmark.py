#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(errors="replace")


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError:
        return {}


def find_response_text(run_dir: Path) -> str:
    candidates = [
        run_dir / "outputs" / "response.md",
        run_dir / "outputs" / "output.md",
        run_dir / "outputs" / "transcript.md",
        run_dir / "response.md",
        run_dir / "output.md",
        run_dir / "transcript.md",
    ]
    for path in candidates:
        if path.exists():
            return path.read_text(errors="replace")
    return ""


def normalize(text: str) -> str:
    return " ".join(text.lower().translate(str.maketrans("", "", "*`$")).split())


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def summary(expectations: list[dict]) -> dict:
    passed = sum(1 for item in expectations if item.get("passed"))
    total = len(expectations)
    failed = total - passed
    return {
        "passed": passed,
        "failed": failed,
        "total": total,
        "pass_rate": passed / total if total else 0.0,
    }


def iter_eval_runs(iteration_dir: Path):
    for eval_dir in sorted(p for p in iteration_dir.iterdir() if p.is_dir() and p.name.startswith("eval-")):
        nested_run_dirs = [
            run_dir
            for config_dir in sorted(p for p in eval_dir.iterdir() if p.is_dir())
            for run_dir in sorted(config_dir.glob("run-*"))
            if run_dir.is_dir()
        ]
        if nested_run_dirs:
            for run_dir in nested_run_dirs:
                yield eval_dir, run_dir
        else:
            yield eval_dir, eval_dir


def contains_all(text: str, phrases: list[str]) -> bool:
    return all(phrase in text for phrase in phrases)


def contains_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def mentions_plan(text: str) -> bool:
    return contains_any(text, ["plan.md", "the plan", "plan file"])


def mentions_dispatch(text: str) -> bool:
    return contains_any(
        text,
        [
            "implementer subagent",
            "fresh implementer",
            "fresh subagent",
            "dispatch",
            "implementer-prompt.md",
        ],
    )


def mentions_review_scope(text: str) -> bool:
    return contains_any(text, ["review_scope_files", "review scope", "scope for review"]) and contains_any(
        text,
        ["touched files", "changed files", "files changed", "files reported", "uncommitted files", "git status"],
    )


def mentions_simplification_and_review(text: str) -> bool:
    return contains_any(text, ["code simplification", "simplification task", "simplifier"]) and contains_any(
        text,
        ["code review", "review task", "reviewer"],
    )


def grade(eval_id: int, response_text: str) -> list[dict]:
    text = normalize(response_text)

    if eval_id == 0:
        return [
            expectation(
                "Selects the next pending task from `plan.md`.",
                mentions_plan(text)
                and contains_any(
                    text,
                    [
                        "next pending task",
                        "next ready pending task",
                        "next ready task",
                        "pick the next pending task",
                        "select the next pending task",
                    ],
                ),
                response_text or "missing response",
            ),
            expectation(
                "Invokes `subagent-model-selection`.",
                contains_any(text, ["subagent-model-selection", "model selection"]),
                response_text or "missing response",
            ),
            expectation(
                "Dispatches a fresh implementer subagent with `implementer-prompt.md`.",
                mentions_dispatch(text),
                response_text or "missing response",
            ),
            expectation(
                "Updates and re-reads `plan.md` only after `DONE`.",
                contains_any(text, ["done", "status: done", "if the implementer reports done"])
                and contains_any(
                    text,
                    [
                        "update plan.md",
                        "mark the task complete in plan.md",
                        "update the plan",
                        "persist completion in plan.md",
                        "record completion in plan.md",
                        "write the finished state to plan.md",
                        "update t014 as complete in plan.md",
                        "mark complete in plan.md",
                    ],
                )
                and contains_any(text, ["re-read", "reread", "reopen", "verify in plan.md", "read plan.md again"]),
                response_text or "missing response",
            ),
            expectation(
                "Builds the post-implementation review scope from touched and uncommitted files.",
                mentions_review_scope(text),
                response_text or "missing response",
            ),
            expectation(
                "Adds code simplification and code review tasks before stopping.",
                mentions_simplification_and_review(text),
                response_text or "missing response",
            ),
            expectation(
                "Leaves the work uncommitted.",
                contains_any(text, ["uncommitted", "do not commit", "leave it uncommitted"]),
                response_text or "missing response",
            ),
        ]

    if eval_id == 1:
        return [
            expectation(
                "Resumes from the next pending task instead of redoing completed work.",
                contains_any(text, ["next pending task", "resume", "skip completed work", "t015"]),
                response_text or "missing response",
            ),
            expectation(
                "Respects dependency order between tasks.",
                contains_any(text, ["depends on", "dependency order", "after t015", "t016 depends on t015"]),
                response_text or "missing response",
            ),
            expectation(
                "Handles `NEEDS_CONTEXT` by providing context and re-dispatching.",
                contains_any(text, ["needs_context", "needs context"])
                and contains_any(text, ["provide missing context", "give more context", "re-dispatch", "redispatch", "send more context"]),
                response_text or "missing response",
            ),
            expectation(
                "Does not mark the task done or move to T016 before `plan.md` is updated.",
                contains_any(text, ["do not mark", "not mark", "keep t015 open", "keep the task open"])
                and contains_any(
                    text,
                    [
                        "before moving to t016",
                        "do not move to t016",
                        "do not advance to t016",
                        "until plan.md is updated",
                        "until t015 is complete in plan.md",
                        "until t015 reports done",
                    ],
                ),
                response_text or "missing response",
            ),
        ]

    if eval_id == 2:
        return [
            expectation(
                "Does not start the build-team workflow without an existing `plan.md`.",
                contains_any(
                    text,
                    [
                        "no existing plan.md",
                        "no active plan.md",
                        "no plan.md",
                        "requires an existing plan",
                        "requires an existing plan.md",
                        "does not use the build-team skill",
                    ],
                ),
                response_text or "missing response",
            ),
            expectation(
                "Says the skill is not for plan creation or task breakdown.",
                contains_any(
                    text,
                    [
                        "not for plan creation",
                        "not for task breakdown",
                        "not for planning",
                        "not for creating a plan",
                        "for execution, not planning",
                        "create the plan first",
                    ],
                ),
                response_text or "missing response",
            ),
            expectation(
                "Routes the user to planning or another appropriate workflow.",
                contains_any(text, ["planning", "create-plan", "task breakdown"]),
                response_text or "missing response",
            ),
        ]

    if eval_id == 3:
        return [
            expectation(
                "Mentions `DONE_WITH_CONCERNS` explicitly.",
                contains_any(text, ["done_with_concerns", "done with concerns"]),
                response_text or "missing response",
            ),
            expectation(
                "Does not mark the task complete immediately.",
                contains_any(
                    text,
                    [
                        "do not mark",
                        "not mark",
                        "do not mark it complete",
                        "before marking the task complete",
                        "only then mark the task complete",
                        "only then mark",
                        "do not move on",
                    ],
                ),
                response_text or "missing response",
            ),
            expectation(
                "Resolves correctness or scope concerns before updating `plan.md`.",
                contains_any(text, ["correctness", "scope", "risk", "issue", "problem"])
                and contains_any(text, ["resolve", "address"])
                and contains_any(
                    text,
                    [
                        "before updating plan.md",
                        "before marking the task complete",
                        "before updating the plan",
                        "before moving on",
                        "before continuing",
                        "only then mark the task complete",
                        "only then mark",
                    ],
                ),
                response_text or "missing response",
            ),
        ]

    if eval_id == 4:
        return [
            expectation(
                "Builds a deduped review scope from touched files plus filtered uncommitted files.",
                mentions_review_scope(text) and contains_any(text, ["dedupe", "deduped", "deduplicate", "unique"]),
                response_text or "missing response",
            ),
            expectation(
                "Excludes the deleted path from the review scope.",
                (
                    contains_any(text, ["src/old.ts", "src/old"])
                    and contains_any(text, ["exclude", "omit", "do not include", "skip", "leave out"])
                )
                or contains_any(text, ["exclude deleted", "omit deleted", "do not include deleted files", "skip deleted"]),
                response_text or "missing response",
            ),
            expectation(
                "Adds Code Simplification and Code Review tasks to `plan.md`.",
                mentions_simplification_and_review(text) and mentions_plan(text),
                response_text or "missing response",
            ),
            expectation(
                "Routes `DONE_WITH_FINDINGS` fixes through a reopened plan task and fresh implementer.",
                contains_any(text, ["done_with_findings", "done with findings"])
                and contains_any(text, ["re-open", "reopen", "open the affected task"])
                and contains_any(text, ["fresh implementer", "implementer subagent"])
                and contains_any(text, ["do not patch inline", "instead of patching inline", "not patch inline"]),
                response_text or "missing response",
            ),
        ]

    return []


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: grade_benchmark.py <iteration-dir>", file=sys.stderr)
        return 2

    iteration_dir = Path(sys.argv[1])
    if not iteration_dir.exists():
        print(f"missing iteration dir: {iteration_dir}", file=sys.stderr)
        return 2

    for eval_dir, run_dir in iter_eval_runs(iteration_dir):
        metadata_path = eval_dir / "eval_metadata.json"
        eval_id = read_json(metadata_path).get("eval_id") if metadata_path.exists() else None
        response_text = find_response_text(run_dir)
        expectations = grade(eval_id, response_text) if eval_id is not None else []
        grading = {
            "expectations": expectations,
            "summary": summary(expectations),
            "execution_metrics": read_json(run_dir / "outputs" / "metrics.json"),
            "timing": read_json(run_dir / "timing.json"),
        }
        (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
