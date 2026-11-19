#!/usr/bin/env python3

import json
import importlib.util
import argparse
import re
import subprocess
import sys
import os
from pathlib import Path


_validator_path = Path(__file__).resolve().parents[1] / "scripts" / "validate_message.py"
_spec = importlib.util.spec_from_file_location("commit_validator", _validator_path)
_validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_validator)


REQUIRED_HEADINGS = [
    "## Overview",
    "## When to Use",
    "## Workflow",
    "## Specific Techniques",
    "## Common Rationalizations",
    "## Red Flags",
    "## Verification",
]


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(errors="replace")


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def expectation(text: str, passed: bool, evidence: str) -> dict:
    return {"text": text, "passed": passed, "evidence": evidence}


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def has_required_skill_shape() -> tuple[bool, str]:
    text = read_text(Path("skills/default/commit/SKILL.md"))
    ok = all(heading in text for heading in REQUIRED_HEADINGS)
    return ok, "all anatomy headings present" if ok else "missing one or more anatomy headings"


def has_commit_message_shape(commit_message: str, commit_type: str, subject: str) -> tuple[bool, str]:
    try:
        header, _, trailers = _validator.parse_message(commit_message)
        _validator.validate_trailers(trailers, None)
    except ValueError as error:
        return False, str(error)
    header_pattern = rf"^{re.escape(commit_type)}(?:\([^()\s]+\))?: {re.escape(subject)}$"
    if re.fullmatch(header_pattern, header) is None:
        return False, header
    return True, header



def build_grading(run_dir: Path, expectations: list[dict]) -> dict:
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    transcript = read_text(run_dir / "transcript.md") + read_text(run_dir / "outputs" / "transcript.md")
    output_chars = 0
    outputs_dir = run_dir / "outputs"
    if outputs_dir.exists():
        for path in outputs_dir.rglob("*"):
            if path.is_file():
                output_chars += len(read_text(path))
    timing = read_json(run_dir / "timing.json")
    total_duration = timing.get("total_duration_seconds", 0.0)
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
            "executor_duration_seconds": total_duration,
            "grader_duration_seconds": 0.0,
            "total_duration_seconds": total_duration,
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


def expected_trailers(result: dict, fixture_name: str) -> tuple[bool, str]:
    fixture = read_json(Path(__file__).resolve().parent / "files" / fixture_name / "input.json")
    inputs = fixture.get("inputs", {})
    issues = inputs.get("issue_numbers")
    fixes = inputs.get("fixes")
    author = inputs.get("co_author")
    if not isinstance(issues, list) or not isinstance(fixes, list) or not isinstance(author, str):
        return False, "missing scenario issue or contributor expectations"
    expected = [f"{'Fixes' if issue.lstrip('#') in fixes else 'Refs'} #{issue.lstrip('#')}" for issue in issues]
    expected.append(f"Co-authored-by: {author}")
    try:
        _, _, trailers = _validator.parse_message(result.get("commit_message", ""))
        _validator.validate_trailers(trailers.copy(), None)
    except (TypeError, ValueError) as error:
        return False, str(error)
    actual = [line for line in trailers if line.startswith(("Refs ", "Fixes ", "Co-authored-by: "))]
    return actual == expected, f"expected {expected}; observed {actual}"


def pr_issue_intent(body: str, fixture_name: str) -> tuple[bool, str]:
    fixture = read_json(Path(__file__).resolve().parent / "files" / fixture_name / "input.json")
    inputs = fixture.get("inputs", {})
    issues, fixes = inputs.get("issue_numbers"), inputs.get("fixes")
    if not isinstance(body, str) or not isinstance(issues, list) or not isinstance(fixes, list):
        return False, "missing PR body or scenario issue expectations"
    # Closing keywords can appear anywhere in the body, including beside neutral references.
    reference = r"(?:(?:https://github\.com/[\w.-]+/[\w.-]+/issues/)|(?:[\w.-]+/[\w.-]+)?#)[1-9][0-9]*"
    directives = re.findall(
        rf"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s+(?:issues?\s+)?({reference}(?:\s*(?:,|and)\s*{reference})*)",
        body, re.IGNORECASE,
    )
    closing = [re.search(r"([1-9][0-9]*)$", ref)[1] for directive in directives
               for ref in re.findall(reference, directive, re.IGNORECASE)]
    mentioned = all(re.search(rf"(?:#|/issues/){re.escape(issue.lstrip('#'))}\b", body) for issue in issues)
    return mentioned and closing == fixes, f"expected closing issues {fixes}; observed {closing}; all issues mentioned: {mentioned}"


def eval_zero(result: dict) -> list[dict]:
    skill_ok, skill_evidence = has_required_skill_shape()
    commit_ok, commit_evidence = has_commit_message_shape(
        result.get("commit_message", ""),
        result.get("commit_type", ""),
        result.get("subject", ""),
    )
    branch = result.get("branch", "")
    return [
        expectation("The rewritten skill keeps the standard anatomy headings.", skill_ok, skill_evidence),
        expectation("Returns a commit decision instead of a stop.", result.get("status") == "commit", result.get("status", "<missing>")),
        expectation(
            "Selects only src/invoice/export_csv.py.",
            result.get("selected_paths") == ["src/invoice/export_csv.py"],
            str(result.get("selected_paths")),
        ),
        expectation(
            "Creates a non-main feature branch using issue 123.",
            branch not in {"", "main", "master"} and re.match(r"^feat/123-[a-z0-9-]+$", branch) is not None,
            branch or "<missing branch>",
        ),
        expectation("Uses commit type feat.", result.get("commit_type") == "feat", result.get("commit_type", "<missing>")),
        expectation("Uses commit message shape with Summary, Rationale, Tests, and valid optional trailers.", commit_ok, commit_evidence),
        expectation("Uses the scenario issue and contributor trailers.", *expected_trailers(result, "single-file-on-main")),
        expectation(
            "Plans a push but no PR.",
            result.get("should_push") is True and result.get("should_create_pr") is False,
            json.dumps({"should_push": result.get("should_push"), "should_create_pr": result.get("should_create_pr")}),
        ),
    ]


def eval_one(result: dict, fixture_name: str) -> list[dict]:
    commit_ok, commit_evidence = has_commit_message_shape(
        result.get("commit_message", ""),
        result.get("commit_type", ""),
        result.get("subject", ""),
    )
    return [
        expectation("Returns a commit decision instead of a stop.", result.get("status") == "commit", result.get("status", "<missing>")),
        expectation(
            "Selects only the staged bugfix files and excludes unstaged README noise.",
            result.get("selected_paths") == ["src/rate_limit.py", "tests/test_rate_limit.py"],
            str(result.get("selected_paths")),
        ),
        expectation(
            "Keeps branch fix/rate-limit-backoff.",
            result.get("branch") == "fix/rate-limit-backoff",
            result.get("branch", "<missing branch>"),
        ),
        expectation("Uses commit type fix.", result.get("commit_type") == "fix", result.get("commit_type", "<missing>")),
        expectation("Uses commit message shape with Summary, Rationale, Tests, and valid optional trailers.", commit_ok, commit_evidence),
        expectation("Uses the scenario issue and contributor trailers.", *expected_trailers(result, fixture_name)),
        expectation(
            "Plans both push and PR creation.",
            result.get("should_push") is True and result.get("should_create_pr") is True,
            json.dumps({"should_push": result.get("should_push"), "should_create_pr": result.get("should_create_pr")}),
        ),
        expectation("Sets the PR title to the commit subject.", result.get("pr_title") == result.get("subject") and bool(result.get("subject")), str(result.get("pr_title"))),
        expectation("Uses the authorized PR issue intent.", *pr_issue_intent(result.get("pr_body"), fixture_name)),
    ]


def eval_two(result: dict) -> list[dict]:
    stop_reason = normalize(result.get("stop_reason", ""))
    next_action = normalize(result.get("next_action", ""))
    return [
        expectation("Returns a stop decision.", result.get("status") == "stop", result.get("status", "<missing>")),
        expectation(
            "Explains that the file scope is ambiguous.",
            "ambiguous" in stop_reason or "which files" in stop_reason or "top-level" in stop_reason,
            result.get("stop_reason", "<missing stop_reason>"),
        ),
        expectation(
            "Asks the user which files to commit next.",
            "which files" in next_action or "select" in next_action,
            result.get("next_action", "<missing next_action>"),
        ),
        expectation(
            "Does not plan a push or PR.",
            result.get("should_push") is False and result.get("should_create_pr") is False,
            json.dumps({"should_push": result.get("should_push"), "should_create_pr": result.get("should_create_pr")}),
        ),
    ]


def eval_three(result: dict) -> list[dict]:
    stop_reason = normalize(result.get("stop_reason", ""))
    next_action = normalize(result.get("next_action", ""))
    return [
        expectation("Returns a stop decision.", result.get("status") == "stop", result.get("status", "<missing>")),
        expectation(
            "Flags generated artifacts instead of committing them automatically.",
            "artifact" in stop_reason or "generated" in stop_reason or "screenshot" in stop_reason or "video" in stop_reason,
            result.get("stop_reason", "<missing stop_reason>"),
        ),
        expectation(
            "Asks for confirmation before versioning those artifacts.",
            "confirm" in next_action or "version" in next_action or "ask" in next_action,
            result.get("next_action", "<missing next_action>"),
        ),
        expectation(
            "Does not plan a push or PR.",
            result.get("should_push") is False and result.get("should_create_pr") is False,
            json.dumps({"should_push": result.get("should_push"), "should_create_pr": result.get("should_create_pr")}),
        ),
    ]


def eval_validation_workflow(run_dir: Path) -> list[dict]:
    try:
        events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text().splitlines()]
        fixture = json.loads((run_dir / "fixture.json").read_text())
        expected_coauthors = fixture.get("expected_coauthors", []) if isinstance(fixture, dict) else []
        if (not isinstance(expected_coauthors, list)
                or any(not isinstance(author, str) or not author.strip() for author in expected_coauthors)
                or len(set(expected_coauthors)) != len(expected_coauthors)):
            raise ValueError("fixture expected_coauthors must be unique nonempty identity strings")
        source_fixture = json.loads((Path(__file__).parent / "files/validation-before-commit/input.json").read_text())
        expected = {
            "draft": fixture.get("expected_draft", source_fixture.get("draft")),
            "after": fixture.get("expected_content", source_fixture.get("after")),
        }
        if not isinstance(expected, dict) or any(not isinstance(expected.get(key), str) for key in ("draft", "after")):
            raise ValueError("the source fixture needs the original draft and expected file content")
        if not events or any(not isinstance(event, dict) for event in events):
            raise ValueError("missing or malformed observation events")
        for event in events:
            if event.get("kind") not in ("validation", "commit") or not isinstance(event.get("message"), str):
                raise ValueError("each observation needs a known kind and string message")
            if event["kind"] == "validation" and (
                type(event.get("exit_code")) is not int or not isinstance(event.get("path"), str)
            ):
                raise ValueError("validation observations need an integer exit_code and string path")
            if event["kind"] == "validation" and "argv" in event and (
                not isinstance(event["argv"], list) or any(not isinstance(arg, str) for arg in event["argv"])
            ):
                raise ValueError("validation argv evidence must be a list of strings")
        if not isinstance(fixture, dict) or not isinstance(fixture.get("initial_head"), str):
            raise ValueError("fixture metadata needs the initial commit SHA")
        validations = [(index, event) for index, event in enumerate(events) if event.get("kind") == "validation"]
        commits = [(index, event) for index, event in enumerate(events) if event.get("kind") == "commit"]
        if not validations or not commits:
            raise ValueError("missing validator or commit observations")
        repo = run_dir / "repo"

        def git(*args):
            return subprocess.run(
                ["git", *args], cwd=repo, capture_output=True, text=True, check=True, timeout=10,
            ).stdout

        count = git("rev-list", "--count", f"{fixture['initial_head']}..HEAD").strip()
        paths = git("diff", "--name-only", fixture["initial_head"], "HEAD").splitlines()
        message = git("log", "-1", "--format=%B").rstrip("\n")
        first = validations[0][1]
        last_index, last = validations[-1]
        commit_index, commit = commits[0]
        root = run_dir.resolve()

        def contained(path: Path) -> bool:
            try:
                path.resolve().relative_to(root)
                return True
            except (OSError, ValueError):
                return False

        def validation_is_scoped(event: dict) -> bool:
            observed = Path(event["path"])
            if not contained(observed):
                return False
            argv = event.get("argv")
            if argv is None:
                return True
            if not argv:
                return False
            argument_path = Path(argv[0])
            if not argument_path.is_absolute():
                argument_path = run_dir / "repo" / argument_path
            return contained(argument_path) and argument_path.resolve() == observed.resolve()

        scoped_files = all(validation_is_scoped(event) for _, event in validations)
        final_message = last.get("message", "")
        expectations = [
            expectation("The initial malformed draft fails validation.",
                        first.get("exit_code") == 1 and first["message"] == expected["draft"]
                        and first["path"] == str((run_dir / "message.txt").resolve()),
                        json.dumps(first)),
            expectation("The repaired draft is revalidated successfully before committing.",
                        len(validations) >= 2 and scoped_files and last.get("exit_code") == 0 and last_index < commit_index,
                        json.dumps({"validations": validations, "commit_index": commit_index})),
            expectation("Exactly one commit follows validation and contains only the scoped change.",
                        len(commits) == 1 and count == "1" and paths == ["notes.txt"]
                        and git("show", "HEAD:notes.txt") == expected["after"] and git("status", "--porcelain") == "",
                        json.dumps({"attempts": len(commits), "commits": count, "paths": paths})),
            expectation("The committed message matches the validated content and has real body lines.",
                        final_message.rstrip("\n") == commit.get("message", "").rstrip("\n") == message
                        and "\u2028" not in message and all("\n\n" + heading + "\n- " in message for heading in ("Summary:", "Rationale:", "Tests:")),
                        message),
        ]
        if expected_coauthors:
            argv = last.get("argv")
            observed_coauthors = []
            if isinstance(argv, list) and all(isinstance(arg, str) for arg in argv):
                index = 0
                while index < len(argv):
                    if argv[index] == "--co-author":
                        if index + 1 >= len(argv):
                            observed_coauthors.append("<missing value>")
                            break
                        observed_coauthors.append(argv[index + 1])
                        index += 2
                    else:
                        index += 1
            actual_trailers = [line for line in message.splitlines() if line.startswith("Co-authored-by: ")]
            required_trailers = [f"Co-authored-by: {author}" for author in expected_coauthors]
            expectations.extend([
                expectation("The final validator invocation supplies each expected co-author exactly once.",
                            observed_coauthors == expected_coauthors,
                            json.dumps({"argv": argv, "observed_coauthors": observed_coauthors,
                                        "expected_coauthors": expected_coauthors})),
                expectation("The actual Git message contains each expected co-author trailer exactly once.",
                            all(actual_trailers.count(trailer) == 1 for trailer in required_trailers)
                            and len(actual_trailers) == len(expected_coauthors),
                            json.dumps({"actual_trailers": actual_trailers,
                                        "required_trailers": required_trailers})),
            ])
        return expectations
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        return [expectation("Observed workflow evidence is complete and readable.", False, str(error))]


def eval_attribution_workflow(run_dir: Path) -> list[dict]:
    try:
        events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text().splitlines()]
        fixture = json.loads((run_dir / "fixture.json").read_text())
        if not isinstance(events, list) or any(not isinstance(event, dict) for event in events):
            raise ValueError("event log must contain JSON objects")
        if not isinstance(fixture, dict):
            raise ValueError("fixture metadata must be a JSON object")
        expected_coauthors = fixture.get("expected_coauthors", [])
        if (not isinstance(expected_coauthors, list)
                or any(not isinstance(identity, str) or not identity.strip() for identity in expected_coauthors)
                or len(set(expected_coauthors)) != len(expected_coauthors)):
            raise ValueError("fixture expected_coauthors must be unique nonempty strings")
        validations = [(index, event) for index, event in enumerate(events) if event.get("kind") == "validation"]
        commits = [(index, event) for index, event in enumerate(events) if event.get("kind") == "commit"]
        if not validations or len(commits) != 1:
            raise ValueError("expected a validator observation and exactly one commit observation")
        repo = run_dir / "repo"
        run_root = run_dir.resolve()

        def contained(path: Path) -> bool:
            try:
                path.resolve().relative_to(run_root)
                return True
            except (OSError, ValueError):
                return False

        for _, event in validations:
            path = event.get("path")
            message = event.get("message")
            argv = event.get("argv")
            exit_code = event.get("exit_code")
            if not isinstance(path, str) or not path.strip():
                raise ValueError("validator observation needs a nonempty message path")
            if not isinstance(message, str):
                raise ValueError("validator observation needs the exact message text")
            if (not isinstance(argv, list) or not argv
                    or any(not isinstance(argument, str) for argument in argv)):
                raise ValueError("validator observation needs a nonempty string argument vector")
            if type(exit_code) is not int or exit_code not in (0, 1, 2):
                raise ValueError("validator observation needs an integer exit code")
            argument_path = Path(argv[0])
            if not argument_path.is_absolute():
                argument_path = repo / argument_path
            observed_path = Path(path)
            if (not contained(argument_path) or not contained(observed_path)
                    or argument_path.resolve() != observed_path.resolve()):
                raise ValueError("validator argv message path does not match its observed input path")

        if any(not isinstance(event.get("message"), str) for _, event in commits):
            raise ValueError("commit observation needs the actual message text")

        def git(*args):
            return subprocess.run(
                ["git", *args], cwd=repo, capture_output=True, text=True, check=True, timeout=10,
            ).stdout

        initial_head = fixture["initial_head"]
        count = git("rev-list", "--count", f"{initial_head}..HEAD").strip()
        paths = git("diff", "--name-only", initial_head, "HEAD").splitlines()
        message = git("log", "-1", "--format=%B").rstrip("\n")
        author = git("show", "-s", "--format=%an <%ae>", "HEAD").strip()
        committer = git("show", "-s", "--format=%cn <%ce>", "HEAD").strip()
        last_index, last = validations[-1]
        commit_index, commit = commits[0]
        final_message = last.get("message", "")
        argv = last.get("argv")
        observed_coauthors = []
        if isinstance(argv, list) and all(isinstance(arg, str) for arg in argv):
            cursor = 0
            while cursor < len(argv):
                if argv[cursor] == "--co-author":
                    if cursor + 1 == len(argv):
                        observed_coauthors.append("<missing value>")
                        break
                    observed_coauthors.append(argv[cursor + 1])
                    cursor += 2
                else:
                    cursor += 1
        actual_trailers = [line for line in message.splitlines() if line.startswith("Co-authored-by: ")]
        expected_trailers = [f"Co-authored-by: {identity}" for identity in expected_coauthors]
        expectations = [
            expectation("The agent's edit is the only committed change in one commit.",
                        count == "1" and paths == ["notes.txt"]
                        and git("show", "HEAD:notes.txt") == fixture["expected_content"]
                        and git("status", "--porcelain") == "",
                        json.dumps({"count": count, "paths": paths, "author": author, "committer": committer})),
            expectation("The final validator invocation supplies every expected co-author once.",
                        observed_coauthors == expected_coauthors and last.get("exit_code") == 0 and last_index < commit_index,
                        json.dumps({"argv": argv, "observed_coauthors": observed_coauthors,
                                    "expected_coauthors": expected_coauthors, "validation": last})),
            expectation("The actual Git message contains exactly the expected co-author trailers and matches validation.",
                        all(actual_trailers.count(trailer) == 1 for trailer in expected_trailers)
                        and len(actual_trailers) == len(expected_coauthors)
                        and final_message.rstrip("\n") == commit.get("message", "").rstrip("\n") == message,
                        json.dumps({"actual_trailers": actual_trailers,
                                    "expected_trailers": expected_trailers, "message": message})),
            expectation("The fixture Git author and committer identities remain unchanged.",
                        author == committer == "Workflow Fixture <fixture@example.com>",
                        json.dumps({"author": author, "committer": committer})),
        ]
        if fixture.get("repository_policy") is not None:
            policy_file = fixture.get("policy_file")
            policy_content = git("show", f"{initial_head}:{policy_file}")
            expectations.append(expectation("The repository policy was part of the fixture before the evaluated turn.",
                                             policy_content == fixture["repository_policy"], policy_content))
        return expectations
    except (OSError, RuntimeError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        return [expectation("Observed attribution workflow evidence is complete and readable.", False, str(error))]


def grade_expectations(eval_id: int, run_dir: Path) -> list[dict]:
    if eval_id in (4, 5):
        return eval_validation_workflow(run_dir)
    if eval_id in (6, 7, 8, 9, 10, 11, 12, 13, 14):
        return eval_attribution_workflow(run_dir)
    result = read_json(run_dir / "outputs" / "result.json")
    if not result:
        return [expectation("result.json exists and is valid JSON.", False, "missing or invalid outputs/result.json")]
    if eval_id == 0:
        return eval_zero(result)
    if eval_id == 1:
        return eval_one(result, "staged-bugfix-pr")
    if eval_id == 15:
        return eval_one(result, "staged-bugfix-pr-close")
    if eval_id == 2:
        return eval_two(result)
    if eval_id == 3:
        return eval_three(result)
    return [expectation(f"Unknown eval id {eval_id}.", False, f"Unsupported eval_id={eval_id}")]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Grade retained commit-skill evaluation artifacts without launching a provider.",
        allow_abbrev=False,
        epilog="Reads an iteration from the argument; JSON result on stdout, diagnostics on stderr. Exit 0 when graded (including assertion failures), 2 for invalid input or I/O errors. Example: python3 grade_benchmark.py /path/to/iteration-1",
    )
    parser.add_argument("iteration_dir", type=Path, help="existing iteration directory containing eval-* artifacts")
    args = parser.parse_args()
    iteration_dir = args.iteration_dir
    if not iteration_dir.is_dir():
        parser.error(f"iteration directory not found or not a directory: {iteration_dir}")
    written = []
    try:
        for eval_dir in sorted(iteration_dir.glob("eval-*")):
            metadata = read_json(eval_dir / "eval_metadata.json")
            eval_id = metadata.get("eval_id")
            for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
                for run_dir in sorted(config_dir.glob("run-*")):
                    expectations = grade_expectations(eval_id, run_dir)
                    grading = build_grading(run_dir, expectations)
                    target = run_dir / "grading.json"
                    target.write_text(json.dumps(grading, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                    written.append(str(target))
    except (OSError, UnicodeError) as exc:
        print(f"grade_benchmark: {exc}", file=sys.stderr)
        return 2
    if not written:
        print(f"grade_benchmark: no runs found in {iteration_dir}", file=sys.stderr)
        return 2
    try:
        print(json.dumps({"iteration_dir": str(iteration_dir.resolve()), "grading_files": written,
                          "count": len(written)}, ensure_ascii=False), flush=True)
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except BrokenPipeError:
            pass
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
