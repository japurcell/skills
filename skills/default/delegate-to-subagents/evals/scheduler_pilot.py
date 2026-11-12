#!/usr/bin/env python3
"""Prepare, execute and grade the bounded scheduler diagnostic pilot (stdlib only)."""
import argparse
import ast
import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import signal
import shlex
import time
import uuid
import sys


def parser():
    p = argparse.ArgumentParser(description=__doc__, allow_abbrev=False,
        epilog="JSON stdout; diagnostics stderr; stdin unused. Exit 0 success (including graded behavioral failure), 2 invalid setup, 124 timeout, 130 interruption.")
    sub = p.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare")
    for name in ("run-root", "baseline", "candidate", "config"):
        prepare.add_argument("--" + name, required=True)
    preflight = sub.add_parser("preflight")
    preflight.add_argument("--manifest", required=True)
    preflight.add_argument("--provider", choices=("codex", "copilot"), required=True)
    for name in ("run", "grade"):
        command = sub.add_parser(name)
        command.add_argument("--manifest", required=True)
        command.add_argument("--cell", required=True)
        if name == "run":
            command.add_argument("--phase", choices=("smoke", "scenario"), required=True)
    return p


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inside(path, root):
    path = Path(path)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("path escapes private run root: " + str(path))
    current = path
    while current != root:
        if current.is_symlink():
            raise ValueError("symlink path is not allowed: " + str(path))
        current = current.parent
    return path


def config_check(config):
    if set(config) != {"providers", "timeout_seconds"}:
        raise ValueError("config requires only providers and timeout_seconds")
    if set(config["providers"]) != {"codex", "copilot"}:
        raise ValueError("both providers are required")
    if type(config["timeout_seconds"]) not in (int, float) or not 0 < config["timeout_seconds"] <= 1800:
        raise ValueError("timeout_seconds must be in (0, 1800]")
    for settings in config["providers"].values():
        if set(settings) != {"executable", "model", "effort"}:
            raise ValueError("provider settings require executable, model, effort; arbitrary flags prohibited")
        for key, value in settings.items():
            if not isinstance(value, str) or not value.strip() or value.startswith("-"):
                raise ValueError("invalid provider setting: " + key)
        executable = Path(settings["executable"])
        if not executable.is_absolute() or not executable.is_file() or not os.access(executable, os.X_OK):
            raise ValueError("provider executable must be an absolute executable file")


def prepare(args):
    root = Path(args.run_root).absolute()
    if root.exists() or root.is_symlink():
        raise ValueError("run root must be fresh and private")
    if root.parent.resolve() != root.parent:
        root = root.parent.resolve() / root.name
    config = read(args.config)
    config_check(config)
    sources = {name: Path(getattr(args, name)).resolve() for name in ("baseline", "candidate")}
    for source in sources.values():
        if not (source / "SKILL.md").is_file() or not (source / "scripts/scheduler.py").is_file():
            raise ValueError("snapshot needs SKILL.md and scripts/scheduler.py")
        if any(p.is_symlink() for p in source.rglob("*")):
            raise ValueError("snapshot symlinks are prohibited")
    root.mkdir(mode=0o700)
    try:
        write(root / "config.json", config)
        helper = root / "io_fixture.py"
        helper.write_text("import json, pathlib, sys\np = pathlib.Path(sys.argv[1]) / 'outputs/smoke.json'\np.write_text(json.dumps({'smoke': True}))\nprint(p.read_text())\n")
        scenario_source = Path(__file__).with_name("pilot-scenarios.json")
        shutil.copyfile(scenario_source, root / "rubric.json")
        manifest = {"version": 1, "root": str(root), "config": str(root / "config.json"),
                    "rubric": str(root / "rubric.json"), "cells": {}, "hashes": {}}
        for variant, source in sources.items():
            snapshot = root / "snapshots" / variant
            shutil.copytree(source, snapshot, ignore=shutil.ignore_patterns("__pycache__", ".git"))
            shutil.copyfile(helper, snapshot / "io_fixture.py")
            for provider in ("codex", "copilot"):
                cell_id = provider + "-" + variant
                cell_root = root / "cells" / cell_id
                repo = cell_root / "repo"
                for directory in (repo / "outputs", cell_root / "evidence", cell_root / "tmp"):
                    directory.mkdir(parents=True)
                script = snapshot / "scripts/scheduler.py"
                cell = {"provider": provider, "variant": variant, "repo": str(repo),
                        "snapshot": str(snapshot), "prompts": {}, "session_ids": {phase: str(uuid.uuid4()) for phase in ("smoke", "scenario")},
                        "write_roots": [str(repo), str(cell_root / "tmp")],
                        "command_prefix": ["python3", str(script)], "io_command": ["python3", str(snapshot / "io_fixture.py"), str(repo)]}
                for phase in ("smoke", "scenario"):
                    output = repo / "outputs" / ("smoke.json" if phase == "smoke" else "result.json")
                    prompt = "Selected SKILL.md body follows verbatim. Apply it.\n<selected_skill>\n" + (snapshot / "SKILL.md").read_text() + "\n</selected_skill>\n"
                    prompt += "Use only the immutable scheduler " + str(script) + ". Write only under " + str(repo) + ".\n"
                    if phase == "smoke":
                        prompt += "Neutral smoke only: run python3 " + str(script) + " --state " + str(repo / "smoke-state.json") + " register smoke smoke-agent neutral --deadline 100 --checkpoint 300 --now 0; then complete smoke at 1 using that state. Write {\"smoke\": true} to " + str(output) + " and read it back by executing python3 " + str(snapshot / "io_fixture.py") + " " + str(repo) + ". Do not exercise deadline/transfer behavior.\n"
                    else:
                        prompt += read(root / "rubric.json")["prompt"].replace("{repo}", str(repo)).replace("{scheduler}", str(script)).replace("{variant}", variant)
                    path = cell_root / (phase + "-prompt.md")
                    path.write_text(prompt)
                    cell["prompts"][phase] = str(path)
                manifest["cells"][cell_id] = cell
        immutable = [root / "config.json", root / "rubric.json", helper]
        immutable += list((root / "snapshots").rglob("*"))
        immutable += [Path(path) for cell in manifest["cells"].values() for path in cell["prompts"].values()]
        for path in immutable:
            if path.is_file():
                manifest["hashes"][str(path.relative_to(root))] = digest(path)
                path.chmod(0o400)
        for cell in manifest["cells"].values():
            cell["argv"] = {phase: argv_for(manifest, cell, phase) for phase in ("smoke", "scenario")}
        write(root / "manifest.json", manifest)
        write(root / "manifest.sha256.json", {"sha256": digest(root / "manifest.json")})
        return {"manifest": str(root / "manifest.json"), "cells": list(manifest["cells"])}
    except Exception as error:
        write(root / "preparation-error.json", {"error": str(error)})
        raise


def load_manifest(path):
    path = Path(path).resolve()
    root = path.parent
    if root.is_symlink() or root.stat().st_mode & 0o077:
        raise ValueError("run root must be private (0700) and physical")
    if read(root / "manifest.sha256.json") != {"sha256": digest(path)}:
        raise ValueError("manifest drift detected")
    manifest = read(path)
    if manifest["version"] != 1 or manifest["root"] != str(root):
        raise ValueError("unsupported or malformed manifest")
    for relative, expected in manifest["hashes"].items():
        target = inside(root / relative, root)
        if not target.is_file() or digest(target) != expected:
            raise ValueError("immutable input drift: " + relative)
    config_check(read(manifest["config"]))
    for cell in manifest["cells"].values():
        for location in (cell["repo"], cell["snapshot"], *cell["prompts"].values(), *cell["write_roots"]):
            inside(location, root)
        for output in ("smoke.json", "result.json"):
            inside(Path(cell["repo"]) / "outputs" / output, root)
    return manifest


def preflight(manifest, provider):
    root = Path(manifest["root"])
    settings = read(manifest["config"])["providers"][provider]
    probes = []
    for flag in ("--version", "--help"):
        argv = [settings["executable"]] + (["exec", flag] if provider == "codex" and flag == "--help" else [flag])
        result = subprocess.run(argv, capture_output=True, text=True, timeout=15, stdin=subprocess.DEVNULL)
        probes.append({"argv": argv, "stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode})
    required = ("--json", "--model", "--sandbox", "--cd", "--add-dir", "--output-last-message") if provider == "codex" else ("--output-format", "--allow-tool", "--session-id", "--add-dir", "--model", "--reasoning-effort", "--share", "--usage-output-file", "--log-dir", "--no-auto-update", "--no-custom-instructions", "--prompt")
    valid = all(p["exit_code"] == 0 for p in probes) and all(flag in probes[1]["stdout"] for flag in required)
    directory = root / "preflight"
    directory.mkdir(exist_ok=True)
    receipt = {"provider": provider, "probes": probes, "valid": valid, "executable_sha256": digest(settings["executable"])}
    previous = directory / (provider + ".json")
    if previous.exists() and read(previous) != receipt:
        raise ValueError("provider version/help/settings drift; prepare a fresh run")
    write(previous, receipt)
    if not valid:
        raise ValueError("provider prerequisites missing; inspect preflight evidence")
    return receipt


def argv_for(manifest, cell, phase):
    settings = read(manifest["config"])["providers"][cell["provider"]]
    evidence = Path(cell["repo"]).parent / "evidence" / phase
    prompt = Path(cell["prompts"][phase]).read_text()
    argv = [settings["executable"]]
    if cell["provider"] == "codex":
        argv += ["exec", "--json", "--cd", cell["repo"], "--add-dir", cell["write_roots"][1],
                 "--skip-git-repo-check", "--model", settings["model"], "--sandbox", "workspace-write",
                 "-c", 'model_reasoning_effort="' + settings["effort"] + '"',
                 "--output-last-message", str(evidence / "response.md"), "-"]
    else:
        argv += ["--model", settings["model"], "--reasoning-effort", settings["effort"],
                 "--session-id", cell["session_ids"][phase], "--add-dir", cell["repo"], "--add-dir", cell["snapshot"],
                 "--allow-tool=write(" + cell["repo"] + ")",
                 "--allow-tool=shell(python3 " + str(Path(cell["snapshot"]) / "scripts/scheduler.py") + ":*)",
                 "--allow-tool=shell(" + shlex.join(cell["io_command"]) + ")", "--no-custom-instructions", "--output-format", "json",
                 "--share", str(evidence / "transcript.md"), "--usage-output-file", str(evidence / "usage.json"),
                 "--log-dir", str(evidence / "logs"), "--no-auto-update", "--prompt", prompt]
    return argv


def native_events(provider, stdout):
    calls, starts, usage = [], {}, None
    for number, line in enumerate(stdout.splitlines(), 1):
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if not isinstance(row, dict):
            continue
        kind, data = row.get("type"), row.get("data", {})
        if not isinstance(data, dict):
            data = {}
        item = row.get("item", {})
        if provider == "codex" and kind == "item.completed" and isinstance(item, dict) and item.get("type") == "command_execution":
            calls.append({"command": item.get("command", ""), "exit_code": item.get("exit_code"),
                          "output": item.get("aggregated_output", ""), "line": number})
        if provider == "copilot" and kind == "tool.execution_start":
            starts[data.get("toolCallId")] = data.get("arguments", {})
        if provider == "copilot" and kind == "tool.execution_complete":
            arguments = starts.pop(data.get("toolCallId"), {})
            result = data.get("result", {})
            calls.append({"command": arguments.get("command", ""),
                          "exit_code": 0 if data.get("success") is True else 1,
                          "output": str(result), "line": number})
        if kind == "turn.completed":
            usage = row.get("usage", data.get("usage"))
    return {"calls": calls, "usage": usage}


def executed(call, prefix):
    if call["exit_code"] != 0 or not isinstance(call["command"], str):
        return False
    try:
        argv = shlex.split(call["command"])
    except ValueError:
        return False
    if argv[:2] == ["rtk", "proxy"]:
        argv = argv[2:]
    if argv[:len(prefix[:2])] == prefix[:2] and all(token in argv for token in prefix[2:]):
        return not any(token in argv for token in (";", "&&", "||", "|"))
    # A wrapper is evidence only when its literal subprocess argv is retained and
    # check=True propagates a child failure into the native execution exit.
    code = argv[2] if argv[:2] == ["python3", "-c"] and len(argv) == 3 else None
    if code is None:
        return False
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if not isinstance(node.func.value, ast.Name) or node.func.value.id != "subprocess" or node.func.attr != "run":
                continue
            if not any(keyword.arg == "check" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True for keyword in node.keywords):
                continue
            child = ast.literal_eval(node.args[0])
            if isinstance(child, list) and child[:2] == prefix[:2] and all(token in child for token in prefix[2:]):
                return True
    except (ValueError, SyntaxError, IndexError):
        pass
    return False


def smoke_check(cell, events):
    output = Path(cell["repo"]) / "outputs/smoke.json"
    try:
        content_ok = read(output) == {"smoke": True}
    except (OSError, ValueError):
        content_ok = False
    calls = events["calls"]
    scheduler_calls = [call for call in calls if executed(call, cell["command_prefix"])]
    checks = {"exact_output": content_ok,
              "register": any("register" in call["command"] and "smoke" in call["command"] for call in scheduler_calls),
              "complete": any("complete" in call["command"] and "smoke" in call["command"] for call in scheduler_calls),
              "write_readback": any(executed(call, cell["io_command"]) for call in calls)}
    return checks


def stop(process):
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        return process.communicate(timeout=1)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return process.communicate(timeout=2)


def run(manifest, cell_id, phase):
    cell = manifest["cells"][cell_id]
    root = Path(manifest["root"])
    preflight_path = root / "preflight" / (cell["provider"] + ".json")
    receipt = read(preflight_path)
    settings = read(manifest["config"])["providers"][cell["provider"]]
    if not receipt["valid"] or receipt["executable_sha256"] != digest(settings["executable"]):
        raise ValueError("preflight absent or provider executable drift")
    directory = Path(cell["repo"]).parent / "evidence" / phase
    if directory.exists():
        raise ValueError("phase already attempted; evidence is preserved, prepare a fresh run")
    if phase == "scenario":
        smoke = read(directory.parent / "smoke/run.json")
        if not smoke.get("smoke_valid"):
            raise ValueError("successful smoke required before scenario")
    directory.mkdir()
    argv = cell["argv"][phase]
    if argv != argv_for(manifest, cell, phase):
        raise ValueError("frozen argv drift")
    prompt = Path(cell["prompts"][phase]).read_text()
    started = time.monotonic()
    record = {"argv": argv, "cwd": cell["repo"], "phase": phase,
              "session_id": cell["session_ids"][phase], "delivered_prompt_sha256": digest(cell["prompts"][phase]),
              "skill_delivery": "exact body embedded in frozen prompt", "write_roots": cell["write_roots"]}
    write(directory / "run.json", record)
    env = os.environ.copy()
    env["TMPDIR"] = str(Path(cell["repo"]).parent / "tmp")
    process = None
    code, stdout, stderr = 2, "", ""
    try:
        process = subprocess.Popen(argv, cwd=cell["repo"], env=env,
             stdin=subprocess.PIPE if cell["provider"] == "codex" else subprocess.DEVNULL,
             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
        try:
            stdout, stderr = process.communicate(prompt if cell["provider"] == "codex" else None,
                                                 timeout=read(manifest["config"])["timeout_seconds"])
            code = process.returncode
        except subprocess.TimeoutExpired:
            stdout, stderr = stop(process)
            code = 124
        except KeyboardInterrupt:
            stdout, stderr = stop(process)
            code = 130
    except OSError as error:
        stderr = str(error)
    (directory / "stdout.jsonl").write_text(stdout)
    (directory / "stderr.txt").write_text(stderr)
    events = native_events(cell["provider"], stdout)
    write(directory / "native-events.json", events)
    if events["usage"] is not None:
        write(directory / "usage.json", events["usage"])
    if not (directory / "usage.json").exists():
        write(directory / "usage-missing.json", {"available": False, "reason": "provider usage unavailable; no estimate"})
    checks = smoke_check(cell, events) if phase == "smoke" else {}
    record.update({"exit_code": code, "elapsed_seconds": time.monotonic() - started,
                   "smoke_checks": checks, "smoke_valid": phase == "smoke" and code == 0 and all(checks.values())})
    write(directory / "run.json", record)
    return record, code if code in (124, 130) else (0 if code == 0 and (phase != "smoke" or record["smoke_valid"]) else 2)


def grade(manifest, cell_id):
    cell = manifest["cells"][cell_id]
    repo = Path(cell["repo"])
    root = Path(manifest["root"])
    directory = repo.parent / "evidence"
    rubric = read(manifest["rubric"])
    checks = {}
    def check(name, passed, evidence):
        checks[name] = {"passed": bool(passed), "evidence": evidence}
    try:
        smoke = read(directory / "smoke/run.json")
        setup = smoke.get("smoke_valid") is True and smoke.get("delivered_prompt_sha256") == digest(cell["prompts"]["smoke"]) and all(smoke_check(cell, native_events(cell["provider"], (directory / "smoke/stdout.jsonl").read_text())).values())
    except (OSError, ValueError):
        setup = False
    result = {"setup_status": "valid" if setup else "invalid", "behavior_status": "not_evaluated",
              "output_contract_status": "not_evaluated", "comparison_eligible": False,
              "assertions": checks, "candidate_only": {}, "semantic_review_required": True,
              "limits": "Synthetic shutdown facts; deterministic checks require authored-file and native-event review."}
    if setup:
        try:
            run_record = read(directory / "scenario/run.json")
            events = native_events(cell["provider"], (directory / "scenario/stdout.jsonl").read_text())
        except (OSError, ValueError):
            run_record, events = {}, {"calls": []}
        denied = any(call["exit_code"] != 0 and ("denied" in call["output"].lower() or "permission" in call["output"].lower()) for call in events["calls"])
        result["execution_status"] = "permission_failure" if denied else ("success" if run_record.get("exit_code") == 0 else "failure")
        try:
            output = read(inside(repo / "outputs/result.json", root))
            actions = output["actions"]
            final = output["final_state"]
            if not isinstance(actions, list) or not isinstance(final, dict):
                raise ValueError("invalid result shape")
            for action in actions:
                if not isinstance(action, dict) or set(action) != {"action", "assignment", "at", "evidence"}:
                    raise ValueError("invalid action schema")
                if not isinstance(action["at"], (int, float)) or isinstance(action["at"], bool):
                    raise ValueError("invalid action time")
                relative = Path(action["evidence"])
                if relative.is_absolute() or not relative.parts or relative.parts[0] != "outputs":
                    raise ValueError("action evidence must be under outputs")
                evidence = read(inside(repo / relative, root))
                if not isinstance(evidence, dict):
                    raise ValueError("action evidence must be JSON object")
                observed = next((call for call in events["calls"] if call["command"] == evidence.get("command") and call["exit_code"] == evidence.get("exit_code")), None)
                expected_exit = 2 if action["action"] == "transfer-rejected" else 0
                if observed is None or observed["exit_code"] != expected_exit:
                    raise ValueError("action evidence lacks the required native execution result")
            paths = {}
            for key in ("parent_record", "scheduler_state"):
                relative = Path(final[key])
                if relative.is_absolute() or not relative.parts or relative.parts[0] != "outputs":
                    raise ValueError("final evidence must be under outputs")
                paths[key] = read(inside(repo / relative, root))
            state = paths["scheduler_state"]["assignments"]
            parent = paths["parent_record"]
            schema_ok = all(key in final for key in ("old_owner", "new_owner", "worker_stopped", "writes_stopped", "transfer_authorized"))
        except (OSError, ValueError, KeyError, TypeError):
            actions, final, state, parent, schema_ok = [], {}, {}, {}, False
        def action(name, assignment, at):
            return any(a.get("action") == name and a.get("assignment") == assignment and a.get("at") == at for a in actions)
        a, b, c = (state.get(key, {}) for key in ("A", "B", "C"))
        check("exact_output", schema_ok, "repo/outputs/result.json and referenced JSON artifacts")
        check("stop_timing", action("stop", "A", 105) and action("stop", "B", 200) and a.get("phase") == "stop" and b.get("phase") == "stop", "stop actions and final scheduler state")
        check("single_extension", action("extend", "B", 103) and b.get("extension_used") is True and b.get("deadline") == 200 and sum(a.get("action") == "extend" and a.get("assignment") == "B" for a in actions) == 1, "B deadline 200, extension flag, one extension action")
        check("exclusive_pending_shutdown", action("transfer-rejected", "B", 201) and action("confirm-stopped", "B", 202) and parent.get("previous_owner") == "agent-old", "rejected transfer before supplied shutdown facts")
        check("independent_progress", c.get("status") == "completed" and any(executed(call, cell["command_prefix"] + ["complete", "C"]) for call in events["calls"]), "C completed and successful native command")
        authorized = b.get("transfer_authorized") is True if cell["variant"] == "candidate" else b.get("transferred") is True
        check("parent_transfer", final.get("old_owner") == "agent-old" and final.get("new_owner") == "agent-new" and final.get("worker_stopped") is True and final.get("writes_stopped") is True and final.get("transfer_authorized") is True and b.get("stop_confirmed") is True and authorized and parent.get("owner") == "agent-new" and parent.get("updated_at") == 204 and action("parent-update", "B", 204), "authored parent ownership record plus scheduler stop/authorization state")
        check("immutable_execution", any(executed(call, cell["command_prefix"]) for call in events["calls"]), "native successful execution at frozen scheduler path")
        if cell["variant"] == "candidate":
            receipt = b.get("transfer_receipt", {})
            result["candidate_only"]["candidate_acknowledgment"] = {"passed": b.get("transfer_completed") is True and receipt.get("owner") == "agent-new" and receipt.get("evidence") == "outputs/ownership.json" and action("confirm-transfer", "B", 205) and any(executed(call, cell["command_prefix"] + ["confirm-transfer", "B"]) for call in events["calls"]), "evidence": "scheduler receipt and native confirm-transfer command"}
        passed = all(item["passed"] for item in checks.values()) and all(item["passed"] for item in result["candidate_only"].values()) and not denied and run_record.get("exit_code") == 0
        result.update({"behavior_status": "pass" if passed else "fail", "output_contract_status": "pass" if schema_ok else "fail", "comparison_eligible": not denied and run_record.get("exit_code") == 0})
    if set(checks) and set(checks) != set(rubric["assertions"]):
        raise ValueError("rubric assertions do not match grader contract")
    write(directory / "grading.json", result)
    return result


def main():
    args = parser().parse_args()
    try:
        if args.command == "prepare":
            result = prepare(args)
        else:
            manifest = load_manifest(args.manifest)
            if args.command == "preflight":
                result = preflight(manifest, args.provider)
            else:
                if args.command == "run":
                    result, code = run(manifest, args.cell, args.phase)
                    print(json.dumps(result))
                    return code
                result = grade(manifest, args.cell)
        print(json.dumps(result))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print("scheduler-pilot: " + str(error), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130

if __name__ == "__main__":
    sys.exit(main())
