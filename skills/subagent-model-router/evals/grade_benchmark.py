#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


FAST_MODELS = {
    "gpt-5-mini",
    "gpt-5.4-mini",
    "gpt-5.4-nano",
    "gemini-3-flash",
    "haiku",
}

STANDARD_MODELS = {
    "gpt-5.3-codex",
    "gpt-4.1",
    "gemini-3.1-pro",
    "gpt-5.4",
    "sonnet",
}

PREMIUM_MODELS = {
    "gpt-5.5",
    "opus",
}

REVIEW_AGENTS = {
    "code-review",
    "code-reviewer",
    "addy-code-reviewer",
    "security-review",
    "addy-security-auditor",
}

NONE_VALUES = {"", "none", "n/a", "na", "null", "not_applicable"}


def read_text(path: Path) -> str:
    return path.read_text(errors="replace") if path.exists() else ""


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def normalize(value: object) -> str:
    return " ".join(str(value).strip().lower().split())


def load_timing(run_dir: Path) -> dict:
    data = load_json(run_dir / "timing.json")
    return data if isinstance(data, dict) else {}


def output_chars(outputs_dir: Path) -> int:
    total = 0
    if not outputs_dir.exists():
        return total
    for path in outputs_dir.rglob("*"):
        if path.is_file():
            total += len(read_text(path))
    return total


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def build_grading(expectations: list[dict], run_dir: Path) -> dict:
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    timing = load_timing(run_dir)
    duration_seconds = timing.get("total_duration_seconds", 0.0)
    transcript = read_text(run_dir / "transcript.md") + read_text(run_dir / "session.jsonl")
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
            "output_chars": output_chars(run_dir / "outputs"),
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
    metadata = load_json(eval_dir / "eval_metadata.json")
    if "eval_id" in metadata:
        try:
            return int(metadata["eval_id"])
        except (TypeError, ValueError):
            return None
    match = re.match(r"eval-(\d+)", eval_dir.name)
    return int(match.group(1)) if match else None


def load_decision(run_dir: Path) -> tuple[str, dict]:
    path = run_dir / "outputs" / "decision.json"
    return read_text(path), load_json(path)


def model_is_fast(model: str) -> bool:
    return model in FAST_MODELS


def model_is_standard(model: str) -> bool:
    return model in STANDARD_MODELS


def none_like(value: object) -> bool:
    return normalize(value) in NONE_VALUES


def justification_mentions(text: str, *terms: str) -> bool:
    normalized = normalize(text)
    return any(term in normalized for term in terms)


def mentions_no_launch_reason(text: str) -> bool:
    normalized = normalize(text)
    explicit_no_launch = any(
        term in normalized
        for term in (
            "no delegated launch",
            "no delegated subagent launch",
            "no subagent launch",
            "no subagent is being launched",
            "not launching",
            "do not spawn anything",
            "no spawn",
            "no delegation",
            "direct inspection",
            "routing decision is needed",
        )
    )
    return explicit_no_launch or (
        "not applicable" in normalized and any(term in normalized for term in ("spawn", "subagent", "routing"))
    )


def grade(eval_id: int, decision: dict, raw_text: str) -> list[dict]:
    applicable = bool(decision.get("applicable"))
    agent_type = normalize(decision.get("agent_type", ""))
    model_tier = normalize(decision.get("model_tier", ""))
    model = normalize(decision.get("model", ""))
    justification = normalize(decision.get("justification", ""))
    fallback = normalize(decision.get("fallback_strategy", ""))
    evidence = raw_text or json.dumps(decision, indent=2) or "missing decision.json"

    if eval_id == 0:
        return [
            expectation("The decision marks the skill as applicable.", applicable, evidence),
            expectation("The agent type is `task`.", agent_type == "task", evidence),
            expectation("The model tier is `fast`.", model_tier == "fast", evidence),
            expectation(
                "The chosen model is a fast-tier model rather than a standard or premium model.",
                model_is_fast(model) and model not in STANDARD_MODELS and model not in PREMIUM_MODELS,
                evidence,
            ),
        ]

    if eval_id == 1:
        return [
            expectation("The decision marks the skill as applicable.", applicable, evidence),
            expectation("The agent type is `general-purpose`.", agent_type == "general-purpose", evidence),
            expectation("The model tier is `standard`.", model_tier == "standard", evidence),
            expectation(
                "The chosen model is not `gpt-5-mini`.",
                model != "gpt-5-mini"
                and (
                    model_is_standard(model)
                    or justification_mentions(justification, "code", "cross-file", "debug", "refactor")
                ),
                evidence,
            ),
        ]

    if eval_id == 2:
        return [
            expectation("The decision marks the skill as applicable.", applicable, evidence),
            expectation("The agent type is a review specialist.", agent_type in REVIEW_AGENTS, evidence),
            expectation("The model tier stays `standard`.", model_tier == "standard", evidence),
            expectation(
                "The chosen model is not `gpt-5.4` and the fallback mentions availability or same-tier fallback.",
                model != "gpt-5.4"
                and model_is_standard(model)
                and justification_mentions(fallback + " " + justification, "availability", "same tier", "same-tier", "unavailable"),
                evidence,
            ),
        ]

    if eval_id == 3:
        return [
            expectation("The decision marks the skill as not applicable.", not applicable, evidence),
            expectation(
                "The decision does not choose a real agent type.",
                none_like(agent_type),
                evidence,
            ),
            expectation(
                "The justification says there is no delegated launch.",
                mentions_no_launch_reason(justification),
                evidence,
            ),
        ]

    if eval_id == 4:
        reuse_terms = ("reuse", "re-use", "same launch group", "unchanged", "batch")
        reuse_text = fallback + " " + justification
        return [
            expectation("The decision marks the skill as applicable.", applicable, evidence),
            expectation(
                "The route stays in `task` + `fast` for the bounded batch work.",
                agent_type == "task" and model_tier == "fast" and model_is_fast(model),
                evidence,
            ),
            expectation(
                "The justification or fallback says to reuse prior routing for repeated launches because context is unchanged.",
                justification_mentions(reuse_text, *reuse_terms),
                evidence,
            ),
        ]

    if eval_id == 5:
        reroute_terms = (
            "fresh routing",
            "re-route",
            "reroute",
            "changed",
            "material",
            "stakes",
            "ambigu",
            "constraint",
        )
        reroute_text = fallback + " " + justification
        return [
            expectation("The decision marks the skill as applicable.", applicable, evidence),
            expectation(
                "The route does not keep the old bounded-run lane (`task` + `fast`) for this materially changed launch.",
                not (agent_type == "task" and model_tier == "fast" and model_is_fast(model)),
                evidence,
            ),
            expectation(
                "The justification or fallback explicitly requires fresh routing because work class, stakes, ambiguity, or model constraint changed.",
                justification_mentions(reroute_text, *reroute_terms),
                evidence,
            ),
        ]

    if eval_id == 6:
        retry_terms = (
            "retry",
            "fail",
            "support",
            "api",
            "tier",
            "error",
            "400",
            "switch",
            "alternative",
            "fallback",
        )
        retry_text = fallback + " " + justification
        return [
            expectation("The decision marks the skill as applicable.", applicable, evidence),
            expectation("The model tier stays `standard`.", model_tier == "standard", evidence),
            expectation(
                "The chosen model is not `gpt-4.1` and the fallback/justification explains switching models within the tier to retry instead of falling back to direct work.",
                model != "gpt-4.1"
                and model_is_standard(model)
                and justification_mentions(retry_text, *retry_terms),
                evidence,
            ),
        ]

    return [expectation(f"Unknown eval id {eval_id}.", False, f"Unsupported eval: {eval_id}")]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 skills/subagent-model-router/evals/grade_benchmark.py skills/subagent-model-router-workspace/<iteration-dir>")
        return 1

    iteration_dir = Path(sys.argv[1]).resolve()
    if not iteration_dir.exists():
        print(f"Iteration directory not found: {iteration_dir}")
        return 1

    for eval_dir in sorted(path for path in iteration_dir.iterdir() if path.is_dir() and path.name.startswith("eval-")):
        eval_id = eval_id_for(eval_dir)
        if eval_id is None:
            print(f"Skipping {eval_dir}: could not determine eval id")
            continue
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            for run_dir in sorted(path for path in config_dir.iterdir() if path.is_dir() and path.name.startswith("run-")):
                raw_text, decision = load_decision(run_dir)
                grading = build_grading(grade(eval_id, decision, raw_text), run_dir)
                (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
