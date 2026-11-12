#!/usr/bin/env python3
"""Prepare, execute and grade the bounded scheduler diagnostic pilot (stdlib only)."""
import argparse
import json
import hashlib
import math
import os
from pathlib import Path
import shutil
import subprocess
import shlex
import uuid
import time
from invoke_scheduler import capture
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


def provider_context():
    home = Path.home()
    candidates = [home / ".codex/config.toml", home / ".copilot/config.json", home / ".copilot/settings.json", home / ".copilot/permissions-config.json", home / ".copilot/mcp-config.json"]
    candidates += list((home / ".codex/rules").glob("*.rules"))
    keys = ("HOME", "PATH", "CODEX_HOME", "COPILOT_HOME", "BASH_ENV", "ZDOTDIR", "COPILOT_ALLOW_ALL", "COPILOT_ASSISTED_APPROVAL", "COPILOT_MODEL", "COPILOT_PROVIDER_BASE_URL", "COPILOT_PROVIDERS_CONFIG")
    return {"config_hashes": {str(p): digest(p) if p.is_file() else None for p in candidates},
            "nonsecret_environment_hashes": {key: hashlib.sha256(os.environ[key].encode()).hexdigest() for key in keys if key in os.environ},
            "approval_environment_present": [key for key in ("COPILOT_ALLOW_ALL", "COPILOT_ASSISTED_APPROVAL", "AUTO_APPROVAL") if key in os.environ]}


def config_check(config):
    if not isinstance(config, dict) or not isinstance(config.get("providers"), dict):
        raise ValueError("config/providers must be objects")
    if set(config) != {"providers", "timeout_seconds"}:
        raise ValueError("config requires only providers and timeout_seconds")
    if set(config["providers"]) != {"codex", "copilot"}:
        raise ValueError("both providers are required")
    if type(config["timeout_seconds"]) not in (int, float) or not 0 < config["timeout_seconds"] <= 1800:
        raise ValueError("timeout_seconds must be in (0, 1800]")
    for settings in config["providers"].values():
        if not isinstance(settings, dict):
            raise ValueError("provider settings must be an object")
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
        if any(p.name in (".github", ".claude", ".copilot", ".codex") for p in source.rglob("*")):
            raise ValueError("snapshot contains trusted provider configuration; use a clean skill bundle")
        if any(p.is_symlink() for p in source.rglob("*")):
            raise ValueError("snapshot symlinks are prohibited")
    root.mkdir(mode=0o700)
    try:
        write(root / "config.json", config)
        write(root / "provider-context.json", provider_context())
        scenario_source = Path(__file__).with_name("pilot-scenarios.json")
        shutil.copyfile(scenario_source, root / "rubric.json")
        manifest = {"version": 2, "root": str(root), "config": str(root / "config.json"),
                    "rubric": str(root / "rubric.json"), "cells": {}, "hashes": {}}
        for variant, source in sources.items():
            snapshot = root / "snapshots" / variant
            shutil.copytree(source, snapshot, ignore=shutil.ignore_patterns("__pycache__", ".git"))
            for provider in ("codex", "copilot"):
                cell_id = provider + "-" + variant
                cell_root = root / "cells" / cell_id
                repo = cell_root / "repo"
                for directory in (repo / "outputs", cell_root / "evidence", cell_root / "tmp"):
                    directory.mkdir(parents=True)
                write(repo / "outputs/ownership.json", {"previous_owner": "agent-old", "owner": "agent-old", "updated_at": 0})
                private_home = cell_root / "provider-home"
                (private_home / "copilot").mkdir(parents=True)
                write(private_home / "copilot/settings.json", {"disableAllHooks": True, "enabledPlugins": {}, "defaultPermissionMode": "manual", "permissions": {"disableBypassPermissionsMode": "disable"}})
                script = snapshot / "scripts/scheduler.py"
                helper_path = snapshot / "receipt-adapters" / provider / "invoke_scheduler.py"
                helper_path.parent.mkdir(parents=True)
                shutil.copyfile(Path(__file__).with_name("invoke_scheduler.py"), helper_path)
                write(helper_path.with_name("invocation.json"), {"repo": str(repo), "scheduler": str(script), "timeout_seconds": min(10, config["timeout_seconds"])})
                cell = {"provider": provider, "variant": variant, "repo": str(repo),
                        "snapshot": str(snapshot), "requested_settings": config["providers"][provider], "environment": {"HOME": str(private_home), "PATH": os.environ.get("PATH", os.defpath), "COPILOT_HOME": str(private_home / "copilot"), "COPILOT_CACHE_HOME": str(private_home / "cache"), "COPILOT_PLUGIN_DIR_ONLY": "true", "COPILOT_AUTO_UPDATE": "false", "COPILOT_DISABLE_LOGIN_SHELL_ENV": "1", "TMPDIR": str(cell_root / "tmp")}, "prompts": {}, "session_ids": {phase: str(uuid.uuid4()) for phase in ("smoke", "scenario")},
                        "write_roots": [str(repo), str(cell_root / "tmp")],
                        "command_prefix": ["python3", str(script)], "helper_prefix": ["python3", str(helper_path)], "io_command": ["python3", str(helper_path), "smoke-write"]}
                for phase in ("smoke", "scenario"):
                    output = repo / "outputs" / ("smoke.json" if phase == "smoke" else "result.json")
                    prompt = "Selected SKILL.md body follows verbatim. Apply it.\n<selected_skill>\n" + (snapshot / "SKILL.md").read_text() + "\n</selected_skill>\n"
                    prompt += "Execute every scheduler command through python3 " + str(helper_path) + " --state ABSOLUTE_OUTPUT_STATE COMMAND [ARGS]. This immutable helper invokes " + str(script) + " and retains native child receipts. Use parent-update PREVIOUS_OWNER NEW_OWNER TIME for a neutral parent record write/readback. Write only under " + str(repo) + ".\n"
                    if phase == "smoke":
                        prompt += "Neutral smoke only: execute python3 " + str(helper_path) + " --state " + str(repo / "outputs/smoke-state.json") + " register smoke smoke-agent neutral --deadline 100 --checkpoint 300 --now 0; then the same helper/state complete smoke --now 1. Execute python3 " + str(helper_path) + " smoke-write to write and read back " + str(output) + ". No deadline or transfer behavior.\n"
                    else:
                        prompt += read(root / "rubric.json")["prompt"].replace("{repo}", str(repo)).replace("{scheduler}", str(script)).replace("{variant}", variant)
                    path = cell_root / (phase + "-prompt.md")
                    path.write_text(prompt)
                    cell["prompts"][phase] = str(path)
                manifest["cells"][cell_id] = cell
        immutable = [root / "config.json", root / "rubric.json", root / "provider-context.json"]
        immutable += list((root / "snapshots").rglob("*"))
        immutable += [Path(cell["repo"]).parent / name for cell in manifest["cells"].values() for name in ("provider-home/copilot/settings.json",)]
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
    if manifest["version"] != 2 or manifest["root"] != str(root):
        raise ValueError("unsupported or malformed manifest")
    for relative, expected in manifest["hashes"].items():
        target = inside(root / relative, root)
        if not target.is_file() or digest(target) != expected:
            raise ValueError("immutable input drift: " + relative)
    config_check(read(manifest["config"]))
    if read(root / "provider-context.json") != provider_context():
        raise ValueError("provider settings/environment drift; prepare a fresh run")
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
        code, stdout, stderr = capture(argv, 15)
        probes.append({"argv": argv, "stdout": stdout, "stderr": stderr, "exit_code": code})
    required = ("--json", "--model", "--sandbox", "--cd", "--add-dir", "--output-last-message", "--ignore-user-config", "--ignore-rules") if provider == "codex" else ("--output-format", "--allow-tool", "--session-id", "--add-dir", "--model", "--reasoning-effort", "--share", "--usage-output-file", "--log-dir", "--no-auto-update", "--no-custom-instructions", "--prompt", "--disallow-temp-dir", "--disable-builtin-mcps", "--no-bash-env", "--secret-env-vars")
    valid = all(p["exit_code"] == 0 for p in probes) and all(flag in probes[1]["stdout"] for flag in required)
    directory = root / "preflight"
    directory.mkdir(exist_ok=True)
    blockers = ["codex-native-command-allowlist-unavailable"] if provider == "codex" else []
    if provider == "copilot" and not any(os.environ.get(key) for key in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")):
        blockers.append("copilot-isolated-home-auth-token-unavailable")
    if not valid:
        blockers.append("provider-required-help-controls-missing")
    receipt = {"provider": provider, "model_resolution": {"requested": settings["model"], "effort": settings["effort"], "observed": None, "status": "pending separately authorized smoke"}, "probes": probes, "valid": not blockers, "syntax_supported": valid, "prerequisites": blockers, "executable_sha256": digest(settings["executable"])}
    previous = directory / (provider + ".json")
    if previous.exists() and read(previous) != receipt:
        raise ValueError("provider version/help/settings drift; prepare a fresh run")
    write(previous, receipt)
    if blockers:
        raise ValueError("provider prerequisites: " + ", ".join(blockers) + "; model execution disabled")
    return receipt


def argv_for(manifest, cell, phase):
    settings = read(manifest["config"])["providers"][cell["provider"]]
    evidence = Path(cell["repo"]).parent / "evidence" / phase
    prompt = Path(cell["prompts"][phase]).read_text()
    argv = [settings["executable"]]
    if cell["provider"] == "codex":
        argv += ["exec", "--json", "--cd", cell["repo"], "--add-dir", cell["write_roots"][1],
                 "--skip-git-repo-check", "--ignore-user-config", "--ignore-rules", "--model", settings["model"], "--sandbox", "workspace-write",
                 "-c", 'model_reasoning_effort="' + settings["effort"] + '"',
                 "--output-last-message", str(evidence / "response.md"), "-"]
    else:
        argv += ["--model", settings["model"], "--reasoning-effort", settings["effort"],
                 "--session-id", cell["session_ids"][phase], "--add-dir", cell["repo"], "--add-dir", cell["snapshot"],
                 "--disallow-temp-dir", "--disable-builtin-mcps", "--no-bash-env", "--secret-env-vars=COPILOT_GITHUB_TOKEN,GH_TOKEN,GITHUB_TOKEN", "--allow-tool=write(" + cell["repo"] + "/**)",
                 "--allow-tool=shell(" + shlex.join(cell["helper_prefix"]) + ":*)", "--no-custom-instructions", "--output-format", "json",
                 "--share", str(evidence / "transcript.md"), "--usage-output-file", str(evidence / "usage.json"),
                 "--log-dir", str(evidence / "logs"), "--no-auto-update", "--prompt", prompt]
    return argv


def native_events(provider, stdout):
    calls, starts, usage = [], {}, None
    observed_model, observed_effort = None, None
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
            if not isinstance(arguments, dict):
                arguments = {}
            result = data.get("result", {})
            calls.append({"command": arguments.get("command", ""),
                          "exit_code": 0 if data.get("success") is True else 1,
                          "output": result.get("content", "") if isinstance(result, dict) else str(result), "line": number})
        if provider == "copilot" and kind == "session.start":
            observed_model, observed_effort = data.get("selectedModel"), data.get("reasoningEffort")
        if kind == "turn.completed":
            usage = row.get("usage", data.get("usage"))
    return {"calls": calls, "usage": usage, "observed_model": observed_model, "observed_effort": observed_effort}


def command_argv(command):
    try:
        argv = shlex.split(command)
        if len(argv) == 3 and argv[0] in ("/bin/zsh", "/bin/bash", "zsh", "bash") and argv[1] in ("-lc", "-c"):
            argv = shlex.split(argv[2])
        if argv[:2] == ["rtk", "proxy"]:
            argv = argv[2:]
        if any(token in argv for token in (";", "&&", "||", "|", ">", "<")):
            return []
        return argv
    except (ValueError, TypeError):
        return []


def helper_records(cell, events):
    records = []
    for call in events["calls"]:
        argv = command_argv(call["command"])
        if argv[:2] != cell["helper_prefix"]:
            continue
        text = call["output"]
        if not isinstance(text, str):
            continue
        for line in text.splitlines():
            try:
                receipt = json.loads(line)["pilot_child"]
                if not isinstance(receipt, dict):
                    continue
                if receipt.get("kind") == "scheduler":
                    if receipt.get("argv") != cell["command_prefix"] + argv[2:] or type(receipt.get("exit_code")) is not int:
                        continue
                    if cell["provider"] == "codex" and call["exit_code"] != receipt["exit_code"]:
                        continue
                    if cell["provider"] == "copilot" and (call["exit_code"] == 0) != (receipt["exit_code"] == 0):
                        continue
                    if not isinstance(receipt.get("before"), (dict, type(None))) or not isinstance(receipt.get("after"), dict):
                        continue
                    if not isinstance(receipt["after"].get("assignments"), dict) or any(not isinstance(v, dict) for v in receipt["after"]["assignments"].values()):
                        continue
                if receipt.get("kind") == "scheduler" and receipt.get("before") is not None and (not isinstance(receipt["before"].get("assignments"), dict) or any(not isinstance(v, dict) for v in receipt["before"]["assignments"].values())):
                    continue
                if any(receipt.get(k) is not None and not isinstance(receipt[k], dict) for k in ("parent_before", "parent_after")):
                    continue
                if receipt.get("kind") == "parent-update" and (not isinstance(receipt.get("before"), dict) or not isinstance(receipt.get("after"), dict)):
                    continue
                if receipt.get("kind") in ("parent-update", "smoke-write") and call["exit_code"] != 0:
                    continue
                receipt = dict(receipt, command=call["command"], helper_args=argv[2:], line=call["line"])
                records.append(receipt)
            except (ValueError, KeyError, TypeError):
                continue
    return records


def smoke_check(cell, events):
    output = Path(cell["repo"]) / "outputs/smoke.json"
    try:
        content_ok = read(output) == {"smoke": True}
    except (OSError, ValueError):
        content_ok = False
    records = helper_records(cell, events)
    def operation(name):
        return any(r.get("kind") == "scheduler" and r.get("exit_code") == 0 and r["helper_args"][2:4] == [name, "smoke"] for r in records)
    return {"selector_observation": cell["provider"] != "copilot" or (events.get("observed_model") == cell["requested_settings"]["model"] and events.get("observed_effort") == cell["requested_settings"]["effort"]), "exact_output": content_ok, "register": operation("register"), "complete": operation("complete"),
            "write_readback": any(r.get("kind") == "smoke-write" and r.get("helper_args") == ["smoke-write"] and r.get("readback") == {"smoke": True} and r.get("path") == str(output) for r in records)}


def run(manifest, cell_id, phase):
    cell = manifest["cells"][cell_id]
    if phase == "scenario":
        for variant in ("baseline", "candidate"):
            sibling = manifest["cells"][cell["provider"] + "-" + variant]
            directory = Path(sibling["repo"]).parent / "evidence/smoke"
            try:
                smoke = read(directory / "run.json")
                observed = native_events(cell["provider"], (directory / "stdout.jsonl").read_text())
                valid = smoke.get("exit_code") == 0 and smoke.get("delivered_prompt_sha256") == digest(sibling["prompts"]["smoke"]) and all(smoke_check(sibling, observed).values())
            except (OSError, ValueError, TypeError, AttributeError):
                valid = False
            if not valid:
                raise ValueError("provider-wide two-smoke gate is not met")
    if cell["provider"] == "codex":
        raise ValueError("provider prerequisite: codex-native-command-allowlist-unavailable")
    config = read(manifest["config"])
    settings = config["providers"][cell["provider"]]
    receipt = read(Path(manifest["root"]) / "preflight/copilot.json")
    if not receipt.get("valid") or receipt.get("executable_sha256") != digest(settings["executable"]):
        raise ValueError("valid immutable-provider preflight required")
    auth = {key: os.environ[key] for key in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN") if os.environ.get(key)}
    if not auth:
        raise ValueError("copilot-isolated-home-auth-token-unavailable")
    directory = Path(cell["repo"]).parent / "evidence" / phase
    if directory.exists():
        raise ValueError("phase already attempted; evidence preserved; prepare a fresh root")
    argv = cell["argv"][phase]
    if argv != argv_for(manifest, cell, phase):
        raise ValueError("frozen argv drift")
    directory.mkdir()
    record = {"argv": argv, "cwd": cell["repo"], "phase": phase, "session_id": cell["session_ids"][phase], "delivered_prompt_sha256": digest(cell["prompts"][phase]), "skill_delivery": "exact frozen body in prompt", "auth_environment_names": sorted(auth), "requested_model": settings["model"], "requested_effort": settings["effort"]}
    write(directory / "run.json", record)
    started = time.monotonic()
    try:
        code, stdout, stderr = capture(argv, config["timeout_seconds"], cwd=cell["repo"], env={**cell["environment"], **auth})
    except OSError as error:
        code, stdout, stderr = 2, "", str(error)
    (directory / "stdout.jsonl").write_text(stdout)
    (directory / "stderr.txt").write_text(stderr)
    events = native_events(cell["provider"], stdout)
    write(directory / "native-events.json", events)
    if not (directory / "usage.json").exists():
        write(directory / "usage-missing.json", {"available": False, "reason": "native usage unavailable; no estimate"})
    checks = smoke_check(cell, events) if phase == "smoke" else {}
    record.update({"exit_code": code, "elapsed_seconds": time.monotonic() - started, "smoke_checks": checks, "smoke_valid": phase == "smoke" and code == 0 and all(checks.values()), "observed_model": events.get("observed_model"), "observed_effort": events.get("observed_effort")})
    write(directory / "run.json", record)
    return record, code if code in (124,130) else (0 if code == 0 and (phase != "smoke" or record["smoke_valid"]) else 2)


def grade(manifest, cell_id):
    cell = manifest["cells"][cell_id]
    repo = Path(cell["repo"])
    outputs = repo / "outputs"
    directory = repo.parent / "evidence"
    rubric = read(manifest["rubric"])
    result = {"setup_status": "invalid", "behavior_status": "not_evaluated", "output_contract_status": "not_evaluated",
              "comparison_eligible": False, "assertions": {}, "candidate_only": {}, "semantic_review_required": True,
              "limits": "Synthetic shutdown facts; native provider readiness remains a separate prerequisite."}
    def native(phase):
        return native_events(cell["provider"], (directory / phase / "stdout.jsonl").read_text())
    try:
        smoke = read(directory / "smoke/run.json")
        setup = smoke.get("exit_code") == 0 and smoke.get("delivered_prompt_sha256") == digest(cell["prompts"]["smoke"]) and all(smoke_check(cell, native("smoke")).values())
    except (OSError, ValueError, TypeError, AttributeError):
        setup = False
    if not setup:
        write(directory / "grading.json", result)
        return result
    result["setup_status"] = "valid"
    try:
        run_record = read(directory / "scenario/run.json")
        events = native("scenario")
        records = helper_records(cell, events)
    except (OSError, ValueError, TypeError):
        run_record, events, records = {}, {"calls": []}, []
    (directory / "scenario").mkdir(exist_ok=True)
    result["usage_status"] = "available" if events.get("usage") is not None else "unavailable"
    if result["usage_status"] == "unavailable":
        write(directory / "scenario/usage-missing.json", {"available": False, "reason": "native usage unavailable; no estimate"})
    denied = any("denied" in str(call["output"]).lower() or "permission" in str(call["output"]).lower() for call in events["calls"] if call["exit_code"] != 0)
    def artifact(relative):
        if not isinstance(relative, str):
            raise ValueError("artifact path must be a string")
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or path.parts[:1] != ("outputs",):
            raise ValueError("artifact must be beneath this cell outputs")
        return read(inside(repo / path, outputs))
    try:
        output = artifact("outputs/result.json")
        actions, final = output["actions"], output["final_state"]
        if not isinstance(actions, list) or not isinstance(final, dict):
            raise ValueError("invalid result schema")
        if set(final) != {"old_owner", "new_owner", "worker_stopped", "writes_stopped", "transfer_authorized", "parent_record", "scheduler_state"}:
            raise ValueError("invalid final state schema")
        matched = []
        for action in actions:
            if not isinstance(action, dict) or set(action) != {"action", "assignment", "at", "evidence"}:
                raise ValueError("invalid action schema")
            if not isinstance(action["action"], str) or not isinstance(action["assignment"], str) or type(action["at"]) not in (int, float) or not math.isfinite(action["at"]):
                raise ValueError("invalid action types")
            evidence = artifact(action["evidence"])
            if not isinstance(evidence, dict):
                raise ValueError("invalid evidence schema")
            record = next((r for r in records if r["command"] == evidence.get("command") and r.get("exit_code", 0) == evidence.get("exit_code")), None)
            if record is None:
                raise ValueError("action lacks demonstrated immutable invocation")
            matched.append((action, record))
        state = artifact(final["scheduler_state"])
        parent = artifact(final["parent_record"])
        if not isinstance(state, dict) or not isinstance(state.get("assignments"), dict) or not isinstance(parent, dict):
            raise ValueError("invalid scheduler/parent artifact")
        assignments = state["assignments"]
        if any(not isinstance(assignments.get(k), dict) for k in ("A", "B", "C")):
            raise ValueError("missing scheduler assignment")
        scheduler_records = [r for r in records if r.get("kind") == "scheduler"]
        if not scheduler_records or state != scheduler_records[-1]["after"]:
            raise ValueError("authored final state differs from demonstrated final child state")
        previous = None
        for record in scheduler_records:
            if record["helper_args"][0:2] != ["--state", str(outputs / "scenario-state.json")]:
                raise ValueError("scenario used wrong state")
            if record["before"] != previous:
                raise ValueError("demonstrated scheduler state chain is discontinuous")
            previous = record["after"]
        schema_ok = True
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        actions, matched, final, assignments, parent, schema_ok = [], [], {}, {}, {}, False
    def operation(record, command, assignment, at, code=0):
        args = record.get("helper_args", [])
        if record.get("kind") != "scheduler" or record.get("exit_code") != code or len(args) < 3 or args[2] != command:
            return False
        if args[0:2] != ["--state", str(outputs / "scenario-state.json")]:
            return False
        if assignment and args[3:4] != [assignment]:
            return False
        try:
            return float(args[args.index("--now") + 1]) == at
        except (ValueError, IndexError, TypeError):
            return False
    def state_at(record, key, when):
        value = record.get(when)
        return value.get("assignments", {}).get(key, {}) if isinstance(value, dict) else {}
    def action(name, assignment, at, command, code=0):
        return next((r for a, r in matched if a["action"] == name and a["assignment"] == assignment and a["at"] == at and operation(r, command, assignment if command != "tick" else None, at, code)), None)
    a_stop = action("stop", "A", 105, "tick")
    b_stop = action("stop", "B", 200, "tick")
    extension = action("extend", "B", 103, "extend")
    rejection = action("transfer-rejected", "B", 201, "transfer", 2)
    confirmation = action("confirm-stopped", "B", 202, "confirm-stopped")
    transfer = action("transfer", "B", 203, "transfer")
    parent_records = [r for a, r in matched if a["action"] == "parent-update" and a["assignment"] == "B" and a["at"] == 204 and r.get("kind") == "parent-update" and r.get("after") == parent and r.get("helper_args") == ["parent-update", "agent-old", "agent-new", "204"]]
    followups = [r for r in records if operation(r, "checkpoint", "B", 150)]
    second_extensions = [r for r in records if operation(r, "extend", "B", 151, 2)]
    checks = {}
    def check(name, passed, evidence):
        checks[name] = {"passed": bool(passed), "evidence": evidence}
    check("exact_output", schema_ok, "exact outputs/result.json and strictly confined artifact schema")
    check("stop_timing", a_stop and b_stop and state_at(a_stop,"A","before").get("phase") != "stop" and state_at(a_stop,"A","after").get("phase") == "stop" and state_at(b_stop,"B","before").get("phase") == "extended" and state_at(b_stop,"B","after").get("phase") == "stop", "native helper child tick argv/time and before/after state")
    check("single_extension", extension and state_at(extension,"B","before").get("phase") == "decision" and state_at(extension,"B","after").get("deadline") == 200 and state_at(extension,"B","after").get("extension_used") is True and any(state_at(r,"B","after").get("deadline") == 200 and state_at(r,"B","after").get("extension_used") is True for r in followups) and any(r["before"] == r["after"] for r in second_extensions), "real extension, follow-up at150 and rejected second extension at151")
    check("exclusive_pending_shutdown", rejection and rejection["before"] == rejection["after"] and state_at(rejection,"B","before").get("stop_confirmed") is False and rejection.get("parent_before", {}).get("owner") == "agent-old" and rejection.get("parent_after", {}).get("owner") == "agent-old" and confirmation and state_at(confirmation,"B","after").get("stop_confirmed") is True, "actual exit2 and unchanged state before supplied shutdown")
    check("independent_progress", any(operation(r,"checkpoint","C",102) for r in records) and any(operation(r,"complete","C",104) and state_at(r,"C","after").get("status") == "completed" for r in records), "real independent C checkpoint/completion")
    authorized_key = "transfer_authorized" if cell["variant"] == "candidate" else "transferred"
    check("parent_transfer", transfer and state_at(transfer,"B","before").get("stop_confirmed") is True and state_at(transfer,"B","after").get(authorized_key) is True and parent_records and confirmation and confirmation["line"] < transfer["line"] < parent_records[0]["line"] and parent_records[0].get("before", {}).get("owner") == "agent-old" and final.get("old_owner") == "agent-old" and final.get("new_owner") == "agent-new" and final.get("worker_stopped") is True and final.get("writes_stopped") is True and final.get("transfer_authorized") is True and parent.get("owner") == "agent-new" and parent.get("previous_owner") == "agent-old" and parent.get("updated_at") == 204, "native confirmed-stop authorization then trusted helper parent write/readback")
    check("immutable_execution", any(r.get("kind") == "scheduler" for r in records) and all(r.get("argv", cell["command_prefix"])[:2] == cell["command_prefix"] for r in records if r.get("kind") == "scheduler"), "exact native trusted helper invocation and captured real child argv/results")
    if cell["variant"] == "candidate":
        ack = action("confirm-transfer", "B", 205, "confirm-transfer")
        receipt = state_at(ack or {}, "B", "after").get("transfer_receipt", {})
        result["candidate_only"]["candidate_acknowledgment"] = {"passed": bool(ack and parent_records and parent_records[0]["line"] < ack["line"] and state_at(ack,"B","after").get("transfer_completed") is True and receipt.get("owner") == "agent-new" and receipt.get("evidence") == "outputs/ownership.json" and receipt.get("recorded_at") == 205), "evidence": "real confirm-transfer child argv, exit and resulting receipt"}
    passed = all(c["passed"] for c in checks.values()) and all(c["passed"] for c in result["candidate_only"].values()) and not denied and run_record.get("exit_code") == 0
    result.update({"assertions": checks, "behavior_status": "pass" if passed else "fail", "output_contract_status": "pass" if schema_ok else "fail", "comparison_eligible": not denied and run_record.get("exit_code") == 0, "execution_status": "permission_failure" if denied else ("success" if run_record.get("exit_code") == 0 else "failure")})
    if set(checks) != set(rubric["assertions"]):
        raise ValueError("rubric assertions mismatch")
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
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.TimeoutExpired) as error:
        print("scheduler-pilot: " + str(error), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130

if __name__ == "__main__":
    try:
        try:
            code = main()
        except SystemExit as error:
            code = error.code
        sys.stdout.flush()
    except BrokenPipeError:
        sys.stdout = open(os.devnull, "w")
        code = 1
    sys.exit(code)
