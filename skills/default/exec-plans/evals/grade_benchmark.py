#!/usr/bin/env python3
"""Deterministic behavioral checks for the exec-plans skill evals."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path


REQUIRED_SECTIONS = (
    "purpose",
    "progress",
    "surprises & discoveries",
    "decision log",
    "outcomes & retrospective",
    "context and orientation",
    "plan of work",
    "concrete steps",
    "validation and acceptance",
)
STALE_JSON_CLAIMS = (
    r"the current cli does not implement json output",
    r"the cli currently prints only text",
    r"the json option does not exist yet",
    r"only the original text command currently works",
    r"json acceptance is unmet",
)
REPORT_SOURCE = Path(__file__).resolve().parent / "files" / "resume-plan" / "project" / "src" / "report_cli.py"
RECOVERY_SOURCE = Path(__file__).resolve().parent / "files" / "preserve-recovery" / "project" / "src" / "guardian.py"


def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def normalize(text):
    return " ".join(text.lower().split())


def compact(text):
    return re.sub(r"\s+", "", text.lower())


def expectation(label, passed, evidence):
    return {"text": label, "passed": bool(passed), "evidence": evidence}


def heading_blocks(text):
    lines = text.splitlines()
    starts = []
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if match:
            starts.append((index, len(match.group(1)), match.group(2).strip()))
    blocks = []
    for offset, (start, level, title) in enumerate(starts):
        end = len(lines)
        for next_start, next_level, _ in starts[offset + 1 :]:
            if next_level <= level:
                end = next_start
                break
        blocks.append({"level": level, "title": title, "body": "\n".join(lines[start + 1 : end])})
    return blocks


def find_block(text, aliases):
    aliases = tuple(alias.lower() for alias in aliases)
    for block in heading_blocks(text):
        title = block["title"].lower().strip()
        if any(title == alias or title.startswith(alias + " ") or title.startswith(alias + "/") for alias in aliases):
            return block
    return None


def has_required_sections(text):
    titles = {block["title"].lower().strip() for block in heading_blocks(text)}
    return all(any(title == required or title.startswith(required + " ") or title.startswith(required + "/") for title in titles) for required in REQUIRED_SECTIONS)


def active_and_historical(text):
    active = []
    historical = []
    in_history = False
    history_level = 0
    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if match:
            level = len(match.group(1))
            title = match.group(2).lower()
            if in_history and level <= history_level:
                in_history = False
            if re.search(r"histor|archive|superseded", title):
                in_history = True
                history_level = level
                historical.append(line)
                continue
        (historical if in_history else active).append(line)
    return "\n".join(active), "\n".join(historical)


def progress_items(text):
    items = {}
    for line in text.splitlines():
        match = re.match(r"^\s*-\s*\[([ xX])\].*?\[milestone-(\d+)\]", line)
        if match:
            milestone_id = int(match.group(2))
            items.setdefault(milestone_id, []).append(match.group(1).lower() == "x")
    return items


def milestone_states(text):
    states = {}
    for block in heading_blocks(text):
        match = re.match(r"milestone\s+(\d+)\b", block["title"], re.IGNORECASE)
        if not match:
            continue
        milestone_id = int(match.group(1))
        status = re.search(r"^Status:\s*(done|in progress|open)\s*$", block["body"], re.IGNORECASE | re.MULTILINE)
        acceptance = re.search(r"^Acceptance:\s*(met|not met)\s*$", block["body"], re.IGNORECASE | re.MULTILINE)
        states[milestone_id] = {
            "status": status.group(1).lower() if status else "",
            "acceptance": acceptance.group(1).lower() if acceptance else "",
        }
    return states


def milestone_sync(text):
    states = milestone_states(text)
    items = progress_items(text)
    if not states or set(states) != set(items):
        return False, f"milestones={sorted(states)}, progress={sorted(items)}"
    for milestone_id, state in states.items():
        checked = all(items[milestone_id])
        if state["status"] == "done":
            if not checked or state["acceptance"] != "met":
                return False, f"milestone-{milestone_id} is done without a checked, accepted progress entry"
        elif checked or state["acceptance"] == "met":
            return False, f"milestone-{milestone_id} is open/in progress but marked complete"
        elif not state["status"] or not state["acceptance"]:
            return False, f"milestone-{milestone_id} is missing an explicit state"
    return True, f"{len(states)} milestone states match their progress entries"


def expected_states(text, expected):
    states = milestone_states(text)
    items = progress_items(text)
    if not text.strip() or not expected:
        return False, "plan or expected milestones are missing"
    for milestone_id, expected_status in expected.items():
        state = states.get(milestone_id)
        progress = items.get(milestone_id, [])
        if not state or not progress:
            return False, f"milestone-{milestone_id} or its progress entry is missing"
        expected_checked = expected_status == "done"
        if state["status"] != expected_status or all(progress) != expected_checked:
            return False, f"milestone-{milestone_id}: status={state['status']}, checked={progress}"
        if expected_status == "done" and state["acceptance"] != "met":
            return False, f"milestone-{milestone_id} is done but acceptance is {state['acceptance']}"
        if expected_status != "done" and state["acceptance"] == "met":
            return False, f"milestone-{milestone_id} is unfinished but acceptance is marked met"
    return True, f"expected milestone states match: {expected}"


def common_plan_checks(text):
    present = bool(text.strip())
    return [
        expectation("The plan is present with the required novice-facing sections.", present and has_required_sections(text), "required sections present" if present and has_required_sections(text) else "plan missing or one or more required sections missing"),
        expectation("Milestone states match their progress entries.", present and milestone_sync(text)[0], milestone_sync(text)[1] if present else "plan is missing"),
    ]


def run_tests(project, source_dir):
    test_files = list((project / "tests").glob("test*.py")) if project.exists() else []
    if not project.is_dir() or not test_files:
        return False, "project or test files are missing"
    env = os.environ.copy()
    if source_dir:
        env["PYTHONPATH"] = str(project / source_dir)
    command = [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
    try:
        result = subprocess.run(command, cwd=project, env=env, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as error:
        return False, f"test command failed to start or timed out: {error}"
    output = (result.stdout + result.stderr).strip()
    count_match = re.search(r"Ran\s+(\d+)\s+tests?", output)
    passed = result.returncode == 0 and count_match is not None and int(count_match.group(1)) > 0
    return passed, output or f"test exit={result.returncode}; no tests reported"


def run_command(project, *args):
    command = [sys.executable, *args]
    try:
        return subprocess.run(command, cwd=project, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None


def grade_create(run_dir):
    plan = read_text(run_dir / "outputs" / "ExecPlan.md")
    active, _ = active_and_historical(plan)
    checks = common_plan_checks(plan)
    path_and_commands = all(token in active for token in ("src/report_cli.py", "src/summary.py", "python3 -m unittest discover -s tests"))
    checks.append(expectation("The plan names the actual project files and test command.", bool(plan.strip()) and path_and_commands, "project paths and test command found" if path_and_commands else "plan or concrete project paths/command missing"))
    validation = find_block(active, ("validation and acceptance",))
    validation_text = validation["body"] if validation else ""
    contract_compact = compact(active)
    observable = (
        bool(validation_text.strip())
        and "python3src/report_cli.py" in contract_compact
        and "count=3total=31" in contract_compact
        and "--formatjson" in contract_compact
        and re.search(r'\bcount["`]*\s*:\s*3\b(?!\.)', active, re.IGNORECASE)
        and re.search(r'\btotal["`]*\s*:\s*31\b(?!\.)', active, re.IGNORECASE)
        and ("default" in active.lower() or "omitting" in active.lower() or "no-option" in active.lower())
        and "text" in active.lower()
    )
    checks.append(expectation("Acceptance gives exact text and JSON outputs and preserves the default.", bool(plan.strip()) and observable, validation_text or "validation section missing"))
    states = milestone_states(plan)
    unfinished = any(state["status"] in {"open", "in progress"} and state["acceptance"] != "met" for state in states.values())
    checks.append(expectation("The new plan leaves its unstarted milestone open with unchecked progress.", bool(plan.strip()) and unfinished and milestone_sync(plan)[0], milestone_sync(plan)[1] if plan.strip() else "plan is missing"))
    return checks


def report_cli_checks(project):
    script = project / "src" / "report_cli.py"
    if not script.is_file():
        return False, "outputs/project/src/report_cli.py is missing"
    default = run_command(project, "src/report_cli.py")
    json_full = run_command(project, "src/report_cli.py", "--json")
    json_limited = run_command(project, "src/report_cli.py", "--json", "--limit", "2")
    negative = run_command(project, "src/report_cli.py", "--limit", "-1")
    if None in (default, json_full, json_limited, negative):
        return False, "a direct CLI command failed to start or timed out"
    try:
        full_value = json.loads(json_full.stdout)
        limited_value = json.loads(json_limited.stdout)
    except json.JSONDecodeError as error:
        return False, f"JSON output is invalid: {error}"
    passed = (
        default.returncode == 0
        and default.stdout.strip() == "count=3 total=31"
        and json_full.returncode == 0
        and full_value == {"count": 3, "total": 31}
        and json_limited.returncode == 0
        and limited_value == {"count": 2, "total": 18}
        and negative.returncode != 0
    )
    return passed, f"text={default.stdout.strip()!r}; json={full_value!r}; limited={limited_value!r}; negative_exit={negative.returncode}"


def linked_history_is_retained(plan_path, plan_text):
    history = find_block(plan_text, ("historical records", "historical run records", "earlier run history"))
    if not history:
        return False, "a clearly titled historical section is missing"
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", history["body"])
    for target in links:
        relative = Path(target.split("#", 1)[0])
        archive_path = (plan_path.parent / relative).resolve()
        if relative.is_absolute() or archive_path == plan_path.resolve() or archive_path.parent != plan_path.parent.resolve():
            continue
        archive = read_text(archive_path)
        evidence = compact(archive)
        has_date = "2026-09-30" in evidence
        has_command = "python3-munittestdiscover-stests" in evidence
        has_count = "2tests" in evidence or "twotests" in evidence
        has_json = '{"count":3,"total":31}' in evidence
        if archive and has_date and has_command and has_count and has_json:
            return True, f"{relative} exists and retains the date, test count, command, and JSON result"
        if archive:
            return False, f"{relative} exists but is missing unique dated test evidence"
    return False, "the historical link is missing, points back to the active plan, or has no retained sibling file"


def grade_resume(run_dir):
    project = run_dir / "outputs" / "project"
    plan_path = project / "ExecPlan.md"
    plan = read_text(plan_path)
    active, _ = active_and_historical(plan)
    checks = common_plan_checks(plan)
    state_ok, state_evidence = expected_states(plan, {1: "done", 2: "done", 3: "open"})
    checks.append(expectation("Milestones 1 and 2 are complete with matching progress entries.", bool(plan.strip()) and state_ok, state_evidence))
    no_stale = bool(plan.strip()) and has_required_sections(active) and not any(re.search(pattern, active, re.IGNORECASE) for pattern in STALE_JSON_CLAIMS)
    checks.append(expectation("No superseded JSON claim remains in active instructions.", no_stale, "active sections contain no known stale JSON claim" if no_stale else "plan missing, active sections incomplete, or a known stale JSON claim remains"))
    concrete = find_block(active, ("concrete steps",))
    stale_steps = []
    if concrete:
        completed_level = None
        for line in concrete["body"].splitlines():
            heading = re.match(r"^(#{1,6})\s+(.+)", line)
            if heading:
                level = len(heading.group(1))
                if completed_level is not None and level <= completed_level:
                    completed_level = None
                if re.search(r"\b(?:completed|finished|historical)\b", heading.group(2), re.IGNORECASE):
                    completed_level = level
                continue
            if completed_level is not None:
                continue
            line = re.sub(r"^\s*(?:\d+\.|[-*])\s+", "", line).strip()
            if re.match(r"(?:completed|done|historical|previously completed)\s*:", line, re.IGNORECASE) or re.search(r"\((?:completed|done|historical)\)\s*$", line, re.IGNORECASE):
                continue
            for sentence in re.split(r"(?<=[.!?;])\s+", line):
                if re.match(r"(?:add|update|write|document)\s+(?:verified\s+)?(?:readme|documentation|(?:command|usage)\s+examples)\b", sentence, re.IGNORECASE):
                    continue
                if re.search(
                    r"^(?:(?:then|next)[,:]?\s+)?(?:add|create|write|implement|update|change|modify|extend|edit|introduce)\b"
                    r"[^.\n]{0,180}(?:(?:cli|command.line|behavior)\s+(?:tests?|coverage)|argument\s+parsing|row\s+selection|--(?:json|limit)\b|src/report_cli|tests/test[_-](?:cli|report))",
                    sentence, re.IGNORECASE,
                ):
                    stale_steps.append(sentence)
    steps_current = bool(plan.strip()) and concrete is not None and not stale_steps
    checks.append(expectation("Completed implementation work is not left as current Concrete Steps.", steps_current, "concrete steps contain no current instruction to repeat completed CLI implementation" if steps_current else "; ".join(stale_steps) or "active concrete steps missing"))
    history_ok, history_evidence = linked_history_is_retained(plan_path, plan) if plan.strip() else (False, "plan is missing")
    checks.append(expectation("The linked historical archive exists and preserves the unique dated test evidence.", history_ok, history_evidence))
    tests_ok, tests_evidence = run_tests(project, "src")
    checks.append(expectation("The supplied project test suite passes after the second checkpoint.", tests_ok, tests_evidence))
    cli_ok, cli_evidence = report_cli_checks(project)
    checks.append(expectation("CLI behavior preserves defaults and validates the row limit.", cli_ok, cli_evidence))
    validation = find_block(active, ("validation and acceptance",))
    validation_compact = compact(validation["body"] if validation else "")
    plan_evidence = (
        all(token in compact(active) for token in ("--json", "--limit"))
        and "count=3total=31" in compact(active)
        and re.search(r'\bcount["`]*\s*[:=]\s*2\b(?!\.)', active, re.IGNORECASE)
        and re.search(r'\btotal["`]*\s*[:=]\s*18\b(?!\.)', active, re.IGNORECASE)
        and "json" in validation_compact
        and "limit" in validation_compact
        and re.search(r"\b(?:passed|passes|verified|accepted)\b", validation["body"] if validation else "", re.IGNORECASE)
    )
    checks.append(expectation("The active acceptance records the verified JSON and row-limit outcomes.", bool(plan.strip()) and plan_evidence, "current command outcomes found" if plan_evidence else "current validation outcomes are incomplete"))
    return checks


def recovery_source_unchanged(project):
    output_source = project / "src" / "guardian.py"
    if not output_source.is_file() or not RECOVERY_SOURCE.is_file():
        return False, "output or canonical fixture source is missing"
    try:
        unchanged = output_source.read_bytes() == RECOVERY_SOURCE.read_bytes()
    except OSError as error:
        return False, str(error)
    return unchanged, "source matches the supplied completed implementation" if unchanged else "source differs from the supplied completed implementation"


def claims_current_external_proof(active):
    sentences = re.split(r"[.;\n]|\b(?:but|while|whereas)\b", active, flags=re.IGNORECASE)
    for sentence in sentences:
        prefix = ""
        for clause in re.split(r",|\band\b", sentence, flags=re.IGNORECASE):
            text = normalize(clause)
            subject = re.search(r"\b(?:staged(?: device)?|external) validation\b|\b(?:release[- ]?)?owner approval\b", text)
            completion = re.search(r"\b(?:passed|verified|succeeded|completed|granted)\b|(?<!-)\bapproved\b|\b(?:is|are|was|were) (?:now )?complete\b|\b(?:has|have) been (?:run|performed|supplied|recorded)\b", text)
            negated_or_required = re.search(r"\b(?:not|no|never|pending|unverified|unconfirmed|requires?|until|must|should)\b", text)
            # A condition can govern both sides of "until approval and validation are complete".
            conditional = subject and (
                re.search(r"\b(?:until|before|if)\b", prefix + text[:subject.start()])
                or re.search(r"\bonly after\b", text[:subject.start()])
            )
            denied_list = (
                text.startswith("or ")
                and re.search(r"\bno\b", prefix)
                and not re.search(r"\b(?:passed|verified|succeeded|completed|approved|granted|run|ran|performed|supplied|recorded)\b", prefix)
            )
            if subject and completion and not negated_or_required and not conditional and not denied_list:
                return True
            prefix += text + " "
    return False


def grade_recovery(run_dir):
    project = run_dir / "outputs" / "project"
    plan = read_text(project / "ExecPlan.md")
    active, _ = active_and_historical(plan)
    checks = common_plan_checks(plan)
    state_ok, state_evidence = expected_states(plan, {1: "done", 2: "done", 3: "open"})
    checks.append(expectation("Code milestones are complete and owner validation remains an open milestone.", bool(plan.strip()) and state_ok, state_evidence))
    owner_text = normalize(re.sub(r"(?<=\w)-(?=\w)", " ", active))
    actor = r"(?:agent|(?:current\s+)?contributor)"
    agent_restricted = (
        re.search(r"\b" + actor + r"(?:\s+\w+){0,5}\s+(?:must not|is not authorized|does not execute rollback)\b", owner_text)
        or re.search(r"\b(?:this|the) plan does not authorize an? agent(?: or device owner)? to (?:run (?:that|the) command|execute rollback)\b", owner_text)
    )
    unsafe_agent_permission = re.search(
        r"\b" + actor + r"(?:\s+\w+){0,5}\s+(?:may|can|should|must|is authorized to)\s+"
        r"(?:(?:execute|run|perform)\s+(?:the\s+)?(?:rollback|recovery|deployment|external validation)|"
        r"deploy|rollback|rotate\s+(?:a\s+|the\s+)?production\s+key|contact\s+(?:an?\s+|the\s+)?owner)\b",
        owner_text,
    )
    owner_ok = (
        bool(plan.strip())
        and "release owner" in owner_text
        and "device owner" in owner_text
        and agent_restricted
        and not unsafe_agent_permission
        and "approval" in owner_text
    )
    checks.append(expectation("Owner-action limits are stated in active plan sections.", owner_ok, "active sections name both owners, approval, and an agent restriction" if owner_ok else "active owner roles, approval, or agent restriction missing"))
    recovery_section = find_block(active, ("idempotence and recovery", "recovery and authorization", "recovery"))
    recovery_text = compact(active)
    failure_trigger = re.search(r"\b(?:failed staged(?: device)? validation|staged(?: device)? validation fails)\b", owner_text)
    owner_only = re.search(r"\b(?:only the release owner|release owner is the only person|must be run by the release owner)\b", owner_text)
    recovery_ok = (
        bool(plan.strip())
        and recovery_section is not None
        and "src/guardian.pyrollback--snapshot<snapshot-path>--target<target-path>" in recovery_text
        and "30days" in recovery_text
        and failure_trigger
        and owner_only
        and agent_restricted
        and not unsafe_agent_permission
        and "approval" in owner_text
    )
    checks.append(expectation("Recovery instructions remain in the active plan with the owner-only command.", recovery_ok, recovery_section["body"].strip() if recovery_section else "active recovery section missing"))
    active_validation = find_block(active, ("validation and acceptance",))
    validation_text = normalize(re.sub(r"(?<=\w)-(?=\w)", " ", active_validation["body"])) if active_validation else ""
    no_external_proof = (
        re.search(r"\b(?:has|have) not been (?:performed|run|supplied|recorded)\b", validation_text)
        or re.search(r"\bno (?:staged|external)(?:\s+\w+){0,8}\s+(?:has been run|was run|was performed|is included|has been supplied)\b", validation_text)
    )
    pending = (
        bool(plan.strip())
        and active_validation is not None
        and re.search(r"\b(?:pending|incomplete|remain open)\b", validation_text)
        and no_external_proof
        and "device owner" in validation_text
        and "release owner" in validation_text
        and not claims_current_external_proof(active)
    )
    checks.append(expectation("External owner approval and staged validation remain pending.", pending, active_validation["body"].strip() if active_validation else "active validation section missing"))
    tests_ok, tests_evidence = run_tests(project, "src")
    checks.append(expectation("The unchanged local recovery implementation passes its supplied tests.", tests_ok, tests_evidence))
    unchanged, source_evidence = recovery_source_unchanged(project)
    checks.append(expectation("The supplied completed source is unchanged.", unchanged, source_evidence))
    active_outcomes = find_block(active, ("outcomes & retrospective",))
    outcome_text = active_outcomes["body"].lower() if active_outcomes else ""
    completed_code = (
        "code is complete" in outcome_text
        or re.search(r"\bsnapshot and restore(?:\s+\w+){0,3}\s+(?:implemented|complete)\b", outcome_text)
        or re.search(r"\bcode milestone(?: and (?:local )?verification milestone)? (?:is|are) complete\b", outcome_text)
    )
    not_closed = (
        bool(plan.strip())
        and active_outcomes is not None
        and completed_code
        and re.search(r"\brelease[^.\n]*\b(?:pending|open)\b", outcome_text)
        and not re.search(r"(?:release|plan|overall work) is complete", outcome_text)
    )
    checks.append(expectation("The plan records completed code without claiming release completion.", not_closed, active_outcomes["body"].strip() if active_outcomes else "active outcomes section missing"))
    return checks


def grade_eval(eval_name, run_dir):
    graders = {
        "create-self-contained-plan": grade_create,
        "resume-stale-plan-two-checkpoints": grade_resume,
        "preserve-owner-recovery-after-code": grade_recovery,
    }
    if eval_name not in graders:
        return [expectation("Known eval scenario.", False, f"unknown eval name: {eval_name}")]
    return graders[eval_name](run_dir)


def load_timing(run_dir):
    path = run_dir / "timing.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def build_grading(run_dir, expectations, timing):
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    transcript = read_text(run_dir / "transcript.md")
    outputs = run_dir / "outputs"
    output_chars = sum(len(read_text(path)) for path in outputs.rglob("*") if path.is_file()) if outputs.exists() else 0
    duration = timing.get("total_duration_seconds", 0.0)
    return {
        "expectations": expectations,
        "summary": {"passed": passed, "failed": total - passed, "total": total, "pass_rate": round(passed / total, 2) if total else 0.0},
        "execution_metrics": {"tool_calls": {}, "total_tool_calls": 0, "total_steps": 0, "errors_encountered": 0, "output_chars": output_chars, "transcript_chars": len(transcript)},
        "timing": {"executor_duration_seconds": duration, "grader_duration_seconds": 0.0, "total_duration_seconds": duration},
        "claims": [],
        "user_notes_summary": {"uncertainties": [], "needs_review": [], "workarounds": []},
        "eval_feedback": {"suggestions": [], "overall": "No evaluator suggestions."},
    }


def grade_iteration(iteration_dir):
    for eval_dir in sorted(path for path in iteration_dir.glob("eval-*") if path.is_dir()):
        metadata_path = eval_dir / "eval_metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        eval_name = metadata["eval_name"]
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            for run_dir in sorted(path for path in config_dir.glob("run-*") if path.is_dir()):
                result = build_grading(run_dir, grade_eval(eval_name, run_dir), load_timing(run_dir))
                (run_dir / "grading.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("Usage: python3 evals/grade_benchmark.py <iteration-dir>")
        return 1
    iteration_dir = Path(argv[0])
    if not iteration_dir.is_dir():
        print(f"Iteration directory not found: {iteration_dir}")
        return 1
    try:
        grade_iteration(iteration_dir)
    except (OSError, KeyError, json.JSONDecodeError) as error:
        print(f"Could not grade iteration {iteration_dir}: {error}")
        return 1
    print(f"Wrote grading.json files in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
