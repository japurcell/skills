#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


FILLER_PHRASES = [
    "let me know",
    "if you'd like",
    "if you would like",
    "happy to help",
    "happy to",
    "i can also",
]


def read_text(path: Path) -> str:
    return path.read_text(errors="replace") if path.exists() else ""


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def contains_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def count_numbered_steps(text: str) -> int:
    return len(re.findall(r"(?m)^\s*\d+\.\s+", text))


def mentions_targeted_tool_output(text: str) -> bool:
    return contains_any(
        text,
        [
            "tail",
            "head",
            "line range",
            "specific lines",
            "filtered",
            "grep",
            "rg",
            "quiet flag",
            "--quiet",
            "small slice",
            "targeted slice",
        ],
    )


def avoids_full_dump(text: str) -> bool:
    return contains_any(
        text,
        [
            "avoid full log",
            "avoid dumping the full",
            "not dump the full",
            "not the full log",
            "not the full file",
            "instead of dumping",
            "rather than dumping",
            "rather than read the full",
            "smallest useful slice",
        ],
    )


def make_expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def load_timing(run_dir: Path) -> dict:
    timing_path = run_dir / "timing.json"
    if not timing_path.exists():
        return {}
    try:
        return json.loads(timing_path.read_text())
    except json.JSONDecodeError:
        return {}


def transcript_text(run_dir: Path) -> str:
    return read_text(run_dir / "transcript.md") + read_text(run_dir / "session.jsonl")


def find_response_text(run_dir: Path) -> str:
    candidates = [
        run_dir / "outputs" / "response.md",
        run_dir / "outputs" / "output.md",
        run_dir / "response.md",
        run_dir / "output.md",
    ]
    for path in candidates:
        if path.exists():
            return read_text(path)
    return ""


def build_grading(expectations: list[dict], run_dir: Path) -> dict:
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    timing = load_timing(run_dir)
    duration_seconds = timing.get("total_duration_seconds", 0.0)
    output_chars = sum(len(read_text(path)) for path in (run_dir / "outputs").rglob("*") if path.is_file()) if (run_dir / "outputs").exists() else 0
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
            "transcript_chars": len(transcript_text(run_dir)),
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


def grade(eval_id: int, response: str) -> list[dict]:
    text = normalize(response)
    lower = response.strip().lower()
    words = word_count(response)
    filler_free = not contains_any(text, FILLER_PHRASES)

    if eval_id == 0:
        return [
            make_expectation(
                "Opens with completion or fix status instead of process narration.",
                lower.startswith(("fixed", "done", "resolved", "updated", "duplicate webhook")),
                response or "missing response.md",
            ),
            make_expectation(
                "Mentions duplicate webhook deliveries or event ID de-duping.",
                contains_any(text, ["duplicate webhook", "webhook deliver", "event id", "dedup", "de-dup"]),
                response or "missing response.md",
            ),
            make_expectation(
                "Stays brief, roughly 40 words or fewer.",
                words <= 40,
                f"word_count={words}",
            ),
            make_expectation(
                "Does not add an offer to continue or a recap.",
                filler_free,
                response or "missing response.md",
            ),
        ]

    if eval_id == 1:
        return [
            make_expectation(
                "Clearly says the work is still in progress.",
                contains_any(text, ["still working", "in progress", "working on it", "still investigating"]),
                response or "missing response.md",
            ),
            make_expectation(
                "Mentions the race between cache invalidation and session creation.",
                contains_any(text, ["race", "cache invalidation", "session creation"]),
                response or "missing response.md",
            ),
            make_expectation(
                "Does not ask the user to do anything.",
                "?" not in response and not contains_any(text, ["please send", "please provide", "need you"]),
                response or "missing response.md",
            ),
            make_expectation(
                "Stays brief, roughly 45 words or fewer.",
                words <= 45,
                f"word_count={words}",
            ),
        ]

    if eval_id == 2:
        return [
            make_expectation(
                "Opens with blocked or cannot continue status.",
                lower.startswith(("blocked", "can't continue", "cannot continue", "can't proceed", "cannot proceed")),
                response or "missing response.md",
            ),
            make_expectation(
                "Mentions the missing production API key.",
                contains_any(text, ["production api key", "api key"]) and contains_any(text, ["missing", "not set"]),
                response or "missing response.md",
            ),
            make_expectation(
                "Asks only for the secret name or value needed to proceed.",
                contains_any(text, ["secret name", "secret value", "api key value", "provide", "share"])
                and response.count("?") <= 1,
                response or "missing response.md",
            ),
            make_expectation(
                "Stays brief, roughly 50 words or fewer.",
                words <= 50,
                f"word_count={words}",
            ),
        ]

    if eval_id == 3:
        return [
            make_expectation(
                "Asks exactly one direct question.",
                response.count("?") == 1,
                response or "missing response.md",
            ),
            make_expectation(
                "Mentions the branch or hotfix target.",
                contains_any(text, ["branch", "hotfix"]),
                response or "missing response.md",
            ),
            make_expectation(
                "Avoids extra explanation or preamble.",
                "\n" not in response.strip() and not contains_any(text, ["i can finish", "to proceed", "once you tell me"]),
                response or "missing response.md",
            ),
            make_expectation(
                "Stays very short, roughly 20 words or fewer.",
                words <= 20,
                f"word_count={words}",
            ),
        ]

    if eval_id == 4:
        return [
            make_expectation(
                "Briefly states that the deployment failed because the TLS certificate expired.",
                contains_any(text, ["expired tls certificate", "tls certificate expired", "certificate expired"]),
                response or "missing response.md",
            ),
            make_expectation(
                "Includes exactly three remediation steps.",
                count_numbered_steps(response) == 3,
                response or "missing response.md",
            ),
            make_expectation(
                "Keeps the steps concise rather than turning them into a long essay.",
                words <= 120,
                f"word_count={words}",
            ),
            make_expectation(
                "Does not add filler beyond the requested explanation and steps.",
                filler_free,
                response or "missing response.md",
            ),
        ]

    if eval_id == 5:
        return [
            make_expectation(
                "Mentions using targeted slices such as tail, filtered search hits, or line ranges.",
                mentions_targeted_tool_output(text),
                response or "missing response.md",
            ),
            make_expectation(
                "Explicitly avoids dumping the full log or full file.",
                avoids_full_dump(text),
                response or "missing response.md",
            ),
            make_expectation(
                "Keeps the answer concise, roughly 60 words or fewer.",
                words <= 60,
                f"word_count={words}",
            ),
            make_expectation(
                "Does not add filler or an unnecessary offer to continue.",
                filler_free,
                response or "missing response.md",
            ),
        ]

    return [make_expectation("Unknown eval id.", False, f"eval_id={eval_id}")]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 skills/concise-response/evals/grade_benchmark.py skills/concise-response-workspace/<iteration-dir>")
        return 1

    iteration_dir = Path(sys.argv[1])
    if not iteration_dir.exists():
        print(f"Iteration directory not found: {iteration_dir}")
        return 1

    for eval_dir in sorted(path for path in iteration_dir.iterdir() if path.is_dir() and path.name.startswith("eval-")):
        eval_match = re.match(r"eval-(\d+)", eval_dir.name)
        if not eval_match:
            continue
        eval_id = int(eval_match.group(1))
        config_dirs = [path for path in sorted(eval_dir.iterdir()) if path.is_dir()]
        for config_dir in config_dirs:
            run_dirs = [path for path in sorted(config_dir.glob("run-*")) if path.is_dir()]
            if not run_dirs:
                run_dirs = [config_dir]
            for run_dir in run_dirs:
                response = find_response_text(run_dir)
                expectations = grade(eval_id, response)
                (run_dir / "grading.json").write_text(json.dumps(build_grading(expectations, run_dir), indent=2) + "\n")

    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
