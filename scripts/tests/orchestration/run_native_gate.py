"""Prepare a Copilot model-gate fixture locally. Live execution can spend model tokens."""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import uuid

from grade_native_gate import grade_native_gate


ROOT = Path(__file__).resolve().parents[3]
PROMPTS = {
    "delegate": "Complete Assignment.md using the project-local delegate-to-subagents caller. Allowed project commands are route38 --input route-request.json, policy38 and scheduler38; invoke aliases directly without rtk or python prefixes. Return a short outcome.",
    "execplan": "Complete Assignment.md using the project-local execplan-implement caller. Allowed project commands are route38 --input route-request.json and policy38; invoke aliases directly without rtk or python prefixes. Return a short outcome.",
}
TASK = ("Use the required project worker `check-total` to calculate 17 + 25 + 31. "
        "Keep the coordination record current. Return only the integer result.\n")
ROUTER_REQUEST = {"task": {"work": "bounded"}}


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    return sha256_bytes(Path(path).read_bytes())


def write_json(path, value, *, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = os.O_WRONLY | os.O_CREAT | (os.O_EXCL if exclusive else os.O_TRUNC)
    fd = os.open(path, mode, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write("\n")


def write_private(path, text, executable=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(0o700 if executable else 0o600)


def resolve_router(router_script, router_catalog):
    script = Path(router_script).resolve(strict=True)
    catalog = Path(router_catalog).resolve(strict=True)
    if script.name != "route.py" or catalog.name != "catalog.json":
        raise ValueError("router inputs must be a real route.py and catalog.json")
    return script, catalog


def load_policy(policy_project):
    github = Path(policy_project).resolve(strict=True)
    hooks = github / "hooks"
    agents = github / "agents"
    files = {
        "gate": hooks / "gate.json",
        "hook": hooks / "check-worker.py",
        "worker_policy": hooks / "worker-models.json",
        "worker_agent": agents / "check-total.agent.md",
    }
    if any(not path.is_file() for path in files.values()):
        raise ValueError("policy source must contain the calibrated hook, worker-models.json, and check-total agent")
    policy = json.loads(files["worker_policy"].read_text(encoding="utf-8"))
    if policy != {"check-total": ["claude-haiku-5.5"]}:
        raise ValueError("worker policy differs from the B1 calibrated restriction")
    return github, files, policy


def _route_launcher():
    return '''#!/usr/bin/env python3
import os, sys
from pathlib import Path
base = Path(__file__).resolve().parent
os.environ["P0_REAL_ROUTER_SCRIPT"] = str(base.parent / ".harness/frozen-router/scripts/route.py")
sys.path.insert(0, str(base))
from route_capture import main
raise SystemExit(main())
'''


def _policy_launcher(policy_file, capture_file):
    return f'''#!/usr/bin/env python3
from datetime import datetime, timezone
import hashlib, json, os, sys
from pathlib import Path
policy_path = Path({str(policy_file)!r})
data = policy_path.read_bytes()
digest = hashlib.sha256(data).hexdigest()
record = {{"timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "sha256": digest}}
target = Path({str(capture_file)!r})
fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
with os.fdopen(fd, "a", encoding="utf-8") as stream:
    stream.write(json.dumps(record, sort_keys=True) + "\\n")
sys.stdout.write(data.decode("utf-8"))
'''


def _scheduler_launcher(real_scheduler, project):
    return f'''#!/usr/bin/env python3
import os, sys
from pathlib import Path
args = sys.argv[1:]
if "--now" in args:
    sys.exit("live scheduler does not accept test-clock overrides")
try:
    state = Path(args[args.index("--state") + 1]).resolve()
except (ValueError, IndexError):
    sys.exit("use --state scheduler.json")
if state != (Path({str(project)!r}) / "scheduler.json").resolve():
    sys.exit("use --state scheduler.json")
os.execv(sys.executable, [sys.executable, {str(real_scheduler)!r}, *args])
'''


def prepare(args):
    run_dir = args.run_dir.resolve()
    if run_dir.exists():
        raise ValueError("run directory must be fresh and absent")
    skill_names = {"delegate": "delegate-to-subagents", "execplan": "execplan-implement"}
    caller_file = (args.caller_skill_file or ROOT / "skills/default" / skill_names[args.caller] / "SKILL.md").resolve(strict=True)
    router_file = (args.router_skill_file or ROOT / "skills/default/subagent-model-router/SKILL.md").resolve(strict=True)
    router_script, router_catalog = resolve_router(
        args.router_script or ROOT / "skills/default/subagent-model-router/scripts/route.py",
        args.router_catalog or ROOT / "skills/default/subagent-model-router/reference/catalog.json")
    policy_project = args.policy_project or ROOT / "scripts/tests/orchestration/native_gate_fixture/.github"
    github, policy_files, policy = load_policy(policy_project)
    scheduler_source = args.scheduler_script.resolve(strict=True) if args.scheduler_script else ROOT / "skills/default/delegate-to-subagents/scripts/scheduler.py"
    if args.caller == "delegate" and not scheduler_source.is_file():
        raise ValueError("delegate runner needs the pinned scheduler script")

    os.umask(0o077)
    run_dir.mkdir(parents=True, mode=0o700)
    project = run_dir / "project"
    private = run_dir / "private"
    logs = private / "logs"
    for directory in (project, private, logs):
        directory.mkdir(parents=True, mode=0o700)
    assignment_id = "p0-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]

    caller_name = skill_names[args.caller]
    copy_targets = [
        (caller_file, project / ".github/skills" / caller_name / "SKILL.md"),
        (caller_file, project / "skills/default" / caller_name / "SKILL.md"),
        (router_file, project / ".github/skills/subagent-model-router/SKILL.md"),
        (router_file, project / "skills/default/subagent-model-router/SKILL.md"),
        (router_script, project / ".harness/frozen-router/scripts/route.py"),
        (router_catalog, project / ".harness/frozen-router/reference/catalog.json"),
    ]
    for source, target in copy_targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        target.chmod(0o700 if target.name == "route38" else 0o600)
    (project / "bin").mkdir(parents=True, exist_ok=True)
    route38 = project / "bin/route38"
    capture_source = Path(__file__).with_name("route_capture.py")
    shutil.copyfile(capture_source, project / "bin/route_capture.py")
    (project / "bin/route_capture.py").chmod(0o600)
    write_private(route38, _route_launcher(), executable=True)
    for key, source in policy_files.items():
        target = project / ".github" / ("hooks" if key != "worker_agent" else "agents") / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        target.chmod(0o600)

    write_private(project / "bin/policy38", _policy_launcher(project / ".github/hooks/worker-models.json", private / "policy-observations.jsonl"), executable=True)

    source_hashes = {
        "caller": sha256_file(caller_file), "router_skill": sha256_file(router_file),
        "router_script": sha256_file(router_script), "router_catalog": sha256_file(router_catalog),
        "route_executable": sha256_file(route38),
        "gate": sha256_file(policy_files["gate"]), "hook": sha256_file(policy_files["hook"]),
        "worker_policy": sha256_file(policy_files["worker_policy"]),
        "worker_agent": sha256_file(policy_files["worker_agent"]),
    }
    if args.caller == "delegate":
        scheduler_target = project / ".harness/frozen-scheduler.py"
        shutil.copyfile(scheduler_source, scheduler_target)
        scheduler_target.chmod(0o600)
        source_hashes["scheduler"] = sha256_file(scheduler_source)
        write_private(project / "bin/scheduler38", _scheduler_launcher(scheduler_target, project), executable=True)

    (project / "route-request.json").write_text(json.dumps(ROUTER_REQUEST, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    (project / "Assignment.md").write_text(TASK, encoding="utf-8")
    (project / "assignment-id.txt").write_text(assignment_id + "\n", encoding="utf-8")
    (project / ".harness/coordination.md").write_text(
        "Coordination record location: `coordination.json`. Record shape: `.harness/coordination.schema.json`. "
        "Assignment identifier: `assignment-id.txt`. Project caller and router instructions are in their local "
        "skill files. Available router command: `route38 --input route-request.json`. Worker policy location: "
        "`.github/hooks/worker-models.json`; available policy reader: `policy38`.\n",
        encoding="utf-8")
    (project / ".github/copilot-instructions.md").write_text(
        "Project-local caller and router skills are at `.github/skills/`. Additional input locations and "
        "commands are listed in `.harness/coordination.md`. Worker policy is at "
        "`.github/hooks/worker-models.json`; the reader command is `policy38`. The required profile is "
        "`.github/agents/check-total.agent.md`; local router is `route38 --input route-request.json`. "
        "Coordination record is `coordination.json` and its format is `.harness/coordination.schema.json`.\n",
        encoding="utf-8")
    before_fields = ["recorded_at", "assignment_id", "router_argv", "router_request", "router_output", "intended_child_controls", "parent_controls"]
    after_fields = before_fields + ["actual_args", "worker_id", "observed_worker_model", "blocker", "override_fallback"]
    schema = {"type": "object", "required": ["before", "after"], "additionalProperties": False,
              "properties": {name: {"type": "object", "required": fields, "additionalProperties": False,
                                    "properties": {key: {} for key in fields}}
                             for name, fields in (("before", before_fields), ("after", after_fields))}}
    write_json(project / ".harness/coordination.schema.json", schema)

    parent_flags = ["--trust-folder", "--no-ask-user", "--no-auto-update", "--disable-builtin-mcps",
                    "--no-color", "--model", args.parent_model, "--output-format", "json"]
    allow_tools = [f"write({project}/**)", "shell(policy38:*)", "shell(route38:*)"]
    if args.caller == "delegate":
        scheduler = project / "bin/scheduler38"
        scheduler_source_copy = project / ".harness/frozen-scheduler.py"
        shutil.copyfile(scheduler_source, scheduler_source_copy)
        scheduler_source_copy.chmod(0o600)
        write_private(scheduler, _scheduler_launcher(scheduler_source_copy, project), executable=True)
        allow_tools.append("shell(scheduler38:*)")
    prompt = PROMPTS[args.caller]
    prompt_sha = sha256_bytes(prompt.encode())
    manifest = {
        "schema_version": 1, "assignment_id": assignment_id, "caller": args.caller,
        "source_hashes": source_hashes, "worker_policy": policy,
        "parent_model": args.parent_model, "parent_effort": None,
        "host_parent_effort_argument": "omitted", "host_cli": args.copilot,
        "timeout_seconds": args.timeout_seconds, "expected_answer": 73,
        "prompt_sha256": prompt_sha, "intended_controls": {
            "parent_model": args.parent_model,
            "parent_effort": None,
        },
    }
    write_json(private / "manifest.json", manifest, exclusive=True)
    write_private(private / "copilot-prompt.txt", prompt)
    write_json(private / "copilot-flags.json", {"flags": parent_flags, "allow_tools": allow_tools}, exclusive=True)
    argv = [args.copilot, *parent_flags, "--log-dir", str(logs), "--usage-output-file", str(private / "usage.json")]
    for pattern in allow_tools:
        argv += ["--allow-tool", pattern]
    argv += ["-p", prompt]
    write_json(private / "argv.json", argv, exclusive=True)
    return {"run_dir": run_dir, "project": project, "private": private, "logs": logs,
            "manifest": manifest, "argv": argv, "caller_file": caller_file, "router_file": router_file,
            "route_executable": route38}


def load_actor_records(project):
    """Load the records written by the native actor; never infer them from host events."""
    path = Path(project) / "coordination.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, None
    if not isinstance(value, dict):
        return None, None
    return value.get("before"), value.get("after")


def _kill(proc):
    if os.name == "nt":
        proc.terminate()
        return
    os.killpg(proc.pid, signal.SIGTERM)
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)


def run_prepared(prepared, args):
    version = subprocess.run([args.copilot, "--version"], capture_output=True, text=True, timeout=15, check=False)
    manifest = prepared["manifest"]
    manifest["host_cli_version"] = version.stdout.strip() if version.returncode == 0 else None
    manifest["host_cli_version_exit"] = version.returncode
    manifest["started_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    manifest["deadline"] = (datetime.now(timezone.utc) + timedelta(seconds=args.timeout_seconds)).isoformat().replace("+00:00", "Z")
    write_json(prepared["private"] / "manifest.json", manifest)
    env = os.environ.copy()
    env["PATH"] = str(prepared["project"] / "bin") + os.pathsep + env.get("PATH", "")
    env["P0_ROUTER_LOG"] = str(prepared["private"] / "router-events.jsonl")
    with (prepared["private"] / "events.jsonl").open("x", encoding="utf-8") as stdout, \
         (prepared["private"] / "stderr.txt").open("x", encoding="utf-8") as stderr:
        proc = subprocess.Popen(prepared["argv"], cwd=prepared["project"], env=env,
                                 stdout=stdout, stderr=stderr, start_new_session=(os.name != "nt"))
        try:
            exit_code = proc.wait(timeout=args.timeout_seconds)
        except subprocess.TimeoutExpired:
            _kill(proc)
            exit_code = 124
    manifest["finished_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    manifest["native_exit_code"] = exit_code
    write_json(prepared["private"] / "manifest.json", manifest)
    event_path = prepared["private"] / "events.jsonl"
    events = []
    if event_path.is_file():
        for line in event_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    before, after = load_actor_records(prepared["project"])
    router_log = prepared["private"] / "router-events.jsonl"
    router_records = []
    if router_log.is_file():
        for line in router_log.read_text(encoding="utf-8").splitlines():
            try:
                router_records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    policy_path = prepared["private"] / "policy-observations.jsonl"
    policy_records = []
    if policy_path.is_file():
        try:
            policy_records = [json.loads(line) for line in policy_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        except json.JSONDecodeError:
            policy_records = []
    verdict = grade_native_gate(events, manifest, router_records, before, after, policy_records)
    write_json(prepared["private"] / "verdict.json", verdict)
    print(json.dumps({"status": verdict["status"], "behavior_failures": verdict["behavior_failures"],
                      "record_failures": verdict["record_failures"], "unavailable": verdict["unavailable"],
                      "shareable_result": str(prepared["private"] / "verdict.json")}, sort_keys=True))
    return {"pass": 0, "fail": 1, "unavailable": 2}[verdict["status"]]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--caller", choices=("delegate", "execplan"), required=True)
    parser.add_argument("--caller-skill-file", type=Path, help="full rendered local caller SKILL.md; defaults to this checkout")
    parser.add_argument("--router-skill-file", type=Path, help="full rendered local router SKILL.md; defaults to this checkout")
    parser.add_argument("--router-script", type=Path, help="frozen real router route.py; defaults to this checkout")
    parser.add_argument("--router-catalog", type=Path, help="frozen real router catalog.json; defaults to this checkout")
    parser.add_argument("--policy-project", type=Path, help="calibrated .github hook fixture; defaults to the bundled fixture")
    parser.add_argument("--run-dir", type=Path, required=True, help="new private output directory; must not exist")
    parser.add_argument("--scheduler-script", type=Path, help="frozen scheduler source; required for delegate, defaults to this checkout")
    parser.add_argument("--copilot", default="copilot", help="Copilot CLI executable from the existing provider-managed environment")
    parser.add_argument("--parent-model", default="gpt-6-luna")
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument("--allow-model-calls", action="store_true", help="launch Copilot and allow token usage")
    args = parser.parse_args(argv)
    if args.timeout_seconds < 1:
        parser.error("--timeout-seconds must be positive")
    try:
        prepared = prepare(args)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"native gate setup failed: {error}", file=sys.stderr)
        return 2
    if not args.allow_model_calls:
        print(json.dumps({"status": "prepared", "project": str(prepared["project"]),
                          "private_evidence": str(prepared["private"]),
                          "native_session_started": False}, sort_keys=True))
        return 0
    return run_prepared(prepared, args)


if __name__ == "__main__":
    raise SystemExit(main())
