#!/usr/bin/env python3
"""Grade skillify benchmark runs against structural expectations."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        return {}, text

    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text

    raw = text[4:end].splitlines()
    body = text[end + 5 :]
    data: dict[str, object] = {}
    index = 0

    while index < len(raw):
        line = raw[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue

        if ":" not in line:
            index += 1
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value == "":
            items: list[str] = []
            index += 1
            while index < len(raw):
                child = raw[index]
                if child.startswith("- "):
                    items.append(child[2:].strip().strip('"\''))
                    index += 1
                    continue
                if child.startswith("  - "):
                    items.append(child[4:].strip().strip('"\''))
                    index += 1
                    continue
                break
            data[key] = items
            continue

        if value.startswith("[") and value.endswith("]"):
            stripped = value[1:-1].strip()
            if stripped:
                data[key] = [item.strip().strip('"\'') for item in stripped.split(",")]
            else:
                data[key] = []
        else:
            data[key] = value.strip('"\'')
        index += 1

    return data, body


def load_text(path: Path) -> str:
    try:
        return path.read_text()
    except OSError:
        return ""


def compute_output_chars(outputs_dir: Path) -> int:
    total = 0
    for child in outputs_dir.iterdir():
        if child.is_file():
            try:
                total += len(child.read_text(errors="replace"))
            except OSError:
                continue
    return total


def major_steps(body: str) -> list[str]:
    return re.findall(r"^###\s+(?!Step structure tips)(.+)$", body, flags=re.MULTILINE)


def count_success_criteria(body: str) -> int:
    return len(re.findall(r"\*\*Success criteria\*\*:", body))


def has_human_checkpoint(body: str) -> bool:
    return "Human checkpoint" in body


def has_task_agent(body: str) -> bool:
    return "Task agent" in body or re.search(r"^\s*\d+[a-z]?\.\s", body, flags=re.MULTILINE) is not None


def has_explicit_task_agent_execution(body: str) -> bool:
    return re.search(r"\*\*Execution\*\*:\s*Task agent", body) is not None


def normalize_allowed_tools(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return []


def expectation_checks(eval_id: int, frontmatter: dict[str, object], body: str, output_text: str) -> list[tuple[str, bool, str]]:
    allowed_tools = normalize_allowed_tools(frontmatter.get("allowed-tools"))
    arguments = frontmatter.get("arguments")
    if isinstance(arguments, list):
        argument_list = [str(item) for item in arguments]
    elif isinstance(arguments, str):
        argument_list = [arguments]
    else:
        argument_list = []
    step_count = len(major_steps(body))
    success_count = count_success_criteria(body)

    common_frontmatter = bool(frontmatter.get("name")) and bool(frontmatter.get("description"))
    common_success = step_count >= 3 and success_count >= step_count

    checks: dict[int, list[tuple[str, bool, str]]] = {
        0: [
            (
                "Frontmatter includes name, description, and allowed-tools entries inferred from the session",
                common_frontmatter and any(tool.startswith("Bash(git:*)") for tool in allowed_tools) and any(tool.startswith("Bash(gh:*)") for tool in allowed_tools),
                f"allowed-tools={allowed_tools}",
            ),
            (
                "The generated skill is inline or user-interactive rather than forked for the hotfix workflow",
                str(frontmatter.get("context", "")).strip() != "fork",
                f"context={frontmatter.get('context', '(omitted)')}",
            ),
            (
                "Every major step includes explicit success criteria",
                common_success,
                f"major_steps={step_count}, success_criteria={success_count}",
            ),
            (
                "The merge or deploy step includes a human checkpoint",
                has_human_checkpoint(body),
                "Found Human checkpoint annotation" if has_human_checkpoint(body) else "No Human checkpoint annotation found",
            ),
            (
                "Frontmatter includes argument metadata for pr_number and target_environment",
                set(["pr_number", "target_environment"]).issubset(set(argument_list)) and bool(frontmatter.get("argument-hint")),
                f"arguments={argument_list}, argument-hint={frontmatter.get('argument-hint')}",
            ),
        ],
        1: [
            (
                "Frontmatter includes arguments and argument-hint for the confirmed inputs",
                bool(frontmatter.get("arguments")) and bool(frontmatter.get("argument-hint")),
                f"arguments={frontmatter.get('arguments')}, argument-hint={frontmatter.get('argument-hint')}",
            ),
            (
                "Frontmatter includes a when_to_use trigger description tailored to doc-to-sop requests",
                "doc" in str(frontmatter.get("when_to_use", "")).lower() and "sop" in str(frontmatter.get("when_to_use", "")).lower(),
                f"when_to_use={frontmatter.get('when_to_use')}",
            ),
            (
                "Every major step includes explicit success criteria",
                common_success,
                f"major_steps={step_count}, success_criteria={success_count}",
            ),
            (
                "allowed-tools stays within document-oriented tools and does not add Bash",
                all(not tool.startswith("Bash") for tool in allowed_tools) and {"Read", "Grep", "Glob", "Edit", "Write"}.issubset(set(allowed_tools)),
                f"allowed-tools={allowed_tools}",
            ),
            (
                "The workflow explicitly avoids inventing shell commands or package installation steps unless the source requires them",
                "Do not add shell commands" in body or "Do not invent shell commands" in body or "package installation" in body,
                "Checked body for an explicit rule against inventing shell or package-install steps",
            ),
        ],
        2: [
            (
                "Frontmatter includes context: fork",
                str(frontmatter.get("context", "")).strip() == "fork",
                f"context={frontmatter.get('context', '(omitted)')}",
            ),
            (
                "The skill assigns representative deep dives to task agents via an explicit Execution annotation",
                has_explicit_task_agent_execution(body),
                "Found **Execution**: Task agent annotation on a representative deep-dive step" if has_explicit_task_agent_execution(body) else "No explicit **Execution**: Task agent annotation found",
            ),
            (
                "Every major step includes explicit success criteria",
                common_success,
                f"major_steps={step_count}, success_criteria={success_count}",
            ),
            (
                "allowed-tools includes the benchmark-analysis core tool mix from the session summary",
                {"Read", "Grep", "Glob", "Write", "Bash(python:*)"}.issubset(set(allowed_tools)),
                f"allowed-tools={allowed_tools}",
            ),
            (
                "Frontmatter includes argument metadata and trigger language for benchmark_path triage requests",
                argument_list == ["benchmark_path"] and bool(frontmatter.get("argument-hint")) and "benchmark" in str(frontmatter.get("when_to_use", "")).lower(),
                f"arguments={argument_list}, argument-hint={frontmatter.get('argument-hint')}, when_to_use={frontmatter.get('when_to_use')}",
            ),
        ],
    }
    return checks[eval_id]


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a skillify benchmark run")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--eval-id", type=int, required=True)
    args = parser.parse_args()

    run_dir = args.run_dir
    outputs_dir = run_dir / "outputs"
    skill_path = outputs_dir / "SKILL.md"
    output_path = outputs_dir / "output.md"

    skill_text = load_text(skill_path)
    output_text = load_text(output_path)
    frontmatter, body = parse_frontmatter(skill_text)

    expectations = []
    passed = 0
    for text, ok, evidence in expectation_checks(args.eval_id, frontmatter, body, output_text):
        expectations.append({"text": text, "passed": ok, "evidence": evidence})
        if ok:
            passed += 1

    total = len(expectations)
    failed = total - passed
    output_chars = compute_output_chars(outputs_dir) if outputs_dir.exists() else 0

    timing = {}
    timing_path = run_dir / "timing.json"
    if timing_path.exists():
        try:
            timing = json.loads(timing_path.read_text())
        except json.JSONDecodeError:
            timing = {}

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
            "total_steps": len(major_steps(body)),
            "errors_encountered": 0 if skill_text else 1,
            "output_chars": output_chars,
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
    }

    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")


if __name__ == "__main__":
    main()