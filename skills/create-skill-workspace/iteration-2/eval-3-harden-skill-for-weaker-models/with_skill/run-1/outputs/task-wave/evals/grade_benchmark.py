#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(errors="replace")


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def load_timing(run_dir: Path) -> dict:
    return load_json(run_dir / "timing.json")


def normalize_text(text: str) -> str:
    normalized = text.lower()
    replacements = {
        "`": "",
        "**": "",
        "→": " to ",
        "≤": " <= ",
        "≥": " >= ",
    }
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return " ".join(normalized.split())


def has_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def has_all(text: str, phrases: list[str]) -> bool:
    return all(phrase in text for phrase in phrases)


def expectation(text: str, passed: bool, success: str, failure: str) -> dict:
    return {
        "text": text,
        "passed": passed,
        "evidence": success if passed else failure,
    }


def has_multiple_waves(text: str) -> bool:
    return "wave 1" in text and "wave 2" in text


def has_exit_conditions(text: str) -> bool:
    return text.count("exit:") >= 1


def contains_generic_npm(text: str) -> bool:
    return "npm test" in text or "npm run build" in text


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def grade(eval_id: int | None, eval_name: str, response_text: str) -> list[dict]:
    normalized = normalize_text(response_text)
    compact_words = word_count(response_text)

    if eval_id == 0:
        return [
            expectation(
                "Uses multiple dependency-ordered waves instead of one list.",
                has_multiple_waves(normalized),
                "Found Wave 1 and Wave 2 structure.",
                response_text,
            ),
            expectation(
                "Names the exact create-skill files from the prompt.",
                has_all(normalized, [
                    "skills/create-skill/skill.md",
                    "skills/create-skill/evals/evals.json",
                ]),
                "Named both create-skill paths.",
                response_text,
            ),
            expectation(
                "Uses the exact repo validation and refresh commands.",
                has_all(normalized, [
                    "python3 skills/skill-creator/scripts/quick_validate.py skills/create-skill",
                    "./scripts/copilot-install.sh",
                ]),
                "Included quick_validate and refresh commands.",
                response_text,
            ),
            expectation(
                "Avoids generic npm validation language.",
                not contains_generic_npm(normalized),
                "No generic npm commands found.",
                response_text,
            ),
            expectation(
                "Includes wave exit conditions.",
                has_exit_conditions(normalized),
                "Found Exit lines in the wave plan.",
                response_text,
            ),
        ]

    if eval_id == 1:
        return [
            expectation(
                "Removes vague verbs like `figure out` and `finish up`.",
                not has_any(normalized, ["figure out", "finish up", "usual tests"]),
                "Vague phrases are absent from the rewritten plan.",
                response_text,
            ),
            expectation(
                "Names the exact build skill paths from the prompt.",
                has_all(normalized, [
                    "skills/build-review/skill.md",
                    "skills/build-review/evals/evals.json",
                ]),
                "Named both build paths.",
                response_text,
            ),
            expectation(
                "Uses the exact build-skill validation command.",
                "python3 skills/skill-creator/scripts/quick_validate.py skills/build-review" in normalized,
                "Included quick_validate for skills/build-review.",
                response_text,
            ),
            expectation(
                "Includes the py_compile command when the grader is mentioned.",
                "python3 -m py_compile skills/build-review/evals/grade_benchmark.py" in normalized,
                "Included py_compile for the build grader.",
                response_text,
            ),
            expectation(
                "Uses exit conditions in the rewritten wave plan.",
                has_exit_conditions(normalized),
                "Found Exit lines in the rewritten plan.",
                response_text,
            ),
        ]

    if eval_id == 2:
        return [
            expectation(
                "Names both installer scripts.",
                has_all(normalized, [
                    "scripts/copilot-install.sh",
                    "scripts/addy-install.sh",
                ]),
                "Named both installer paths.",
                response_text,
            ),
            expectation(
                "Uses the exact copilot installer validation command.",
                "bash -n scripts/copilot-install.sh" in normalized,
                "Included bash -n for the Copilot installer.",
                response_text,
            ),
            expectation(
                "Uses the exact addy installer validation command.",
                "bash -n scripts/addy-install.sh && bash scripts/test-addy-install.sh" in normalized,
                "Included the combined addy validation command.",
                response_text,
            ),
            expectation(
                "Uses explicit exit conditions for the waves.",
                has_exit_conditions(normalized),
                "Found Exit lines in the installer plan.",
                response_text,
            ),
            expectation(
                "Avoids generic npm validation language.",
                not contains_generic_npm(normalized),
                "No generic npm commands found.",
                response_text,
            ),
        ]

    if eval_id == 3:
        says_no_waves = has_any(normalized, [
            "no waves needed",
            "waves are not needed",
            "do not create waves",
            "waves are unnecessary",
        ])
        invents_extra_waves = has_any(normalized, ["wave 2", "wave 3"])
        return [
            expectation(
                "Says waves are not needed for the one-step typo fix.",
                says_no_waves,
                "Response explicitly says waves are unnecessary.",
                response_text,
            ),
            expectation(
                "Names README.md as the file to change.",
                "readme.md" in normalized,
                "Response names README.md.",
                response_text,
            ),
            expectation(
                "Does not invent multiple waves for the typo fix.",
                not invents_extra_waves and compact_words <= 120,
                "No extra waves were invented for the single-step change.",
                response_text,
            ),
        ]

    return [
        expectation(
            "Eval metadata identifies a supported task-wave eval.",
            False,
            "",
            f"Unsupported eval metadata: eval_id={eval_id!r}, eval_name={eval_name!r}",
        )
    ]


def load_eval_metadata(run_dir: Path) -> dict:
    eval_dir = run_dir.parent.parent
    return load_json(eval_dir / "eval_metadata.json")


def response_path_for(run_dir: Path) -> Path:
    outputs_dir = run_dir / "outputs"
    if (outputs_dir / "response.md").exists():
        return outputs_dir / "response.md"
    return outputs_dir / "output.md"


def write_grading(run_dir: Path) -> None:
    metadata = load_eval_metadata(run_dir)
    eval_id = metadata.get("eval_id")
    eval_name = metadata.get("eval_name", run_dir.parent.parent.name)
    response_path = response_path_for(run_dir)
    response_text = read_text(response_path)
    expectations = grade(eval_id, eval_name, response_text)
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    failed = total - passed
    timing = load_timing(run_dir)

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
            "transcript_chars": 0,
        },
        "timing": {
            "executor_duration_seconds": timing.get("total_duration_seconds", 0.0),
            "grader_duration_seconds": 0.0,
            "total_duration_seconds": timing.get("total_duration_seconds", 0.0),
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

    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")


def iter_run_dirs(path: Path) -> list[Path]:
    if (path / "outputs").exists() and (
        (path / "outputs" / "response.md").exists() or (path / "outputs" / "output.md").exists()
    ):
        return [path]

    eval_dirs = sorted(path.glob("eval-*"))
    if not eval_dirs:
        return []

    run_dirs: list[Path] = []
    for eval_dir in eval_dirs:
        for run_dir in sorted(eval_dir.glob("*/run-*")):
            outputs_dir = run_dir / "outputs"
            if (outputs_dir / "response.md").exists() or (outputs_dir / "output.md").exists():
                run_dirs.append(run_dir)
    return run_dirs


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: grade_benchmark.py <run-dir-or-iteration-dir>", file=sys.stderr)
        return 2

    target = Path(sys.argv[1]).resolve()
    run_dirs = iter_run_dirs(target)
    if not run_dirs:
        print(f"No benchmark run directories found under {target}", file=sys.stderr)
        return 2

    for run_dir in run_dirs:
        write_grading(run_dir)
        print(f"Graded {run_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
