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
import selectors
import signal


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
    if type(config["timeout_seconds"]) not in (int, float) or not 0 < config["timeout_seconds"] <= 600:
        raise ValueError("timeout_seconds must be in (0, 600]")
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


def source_identity(path):
    path = Path(path).resolve()
    code, stdout, stderr = capture(["git", "-C", str(path if path.is_dir() else path.parent), "rev-parse", "HEAD"], 3)
    return {"path": str(path), "revision": stdout.strip() if code == 0 else None}


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
        control_dir = root / "control"
        control_dir.mkdir()
        policy_script = control_dir / "policy_hook.py"
        shutil.copyfile(Path(__file__).with_name("policy_hook.py"), policy_script)
        scenario_source = Path(__file__).with_name("pilot-scenarios.json")
        shutil.copyfile(scenario_source, root / "rubric.json")
        manifest = {"version": 3, "root": str(root), "config": str(root / "config.json"),
                    "rubric": str(root / "rubric.json"), "cells": {}, "hashes": {},
                    "qualification_contract": "observed-run-pending",
                    "caller_identity": source_identity(__file__),
                    "selected_sources": {name: source_identity(source) for name, source in sources.items()},
                    "caller_sources": {str(Path(__file__).resolve()): digest(__file__), str(Path(__file__).with_name("invoke_scheduler.py").resolve()): digest(Path(__file__).with_name("invoke_scheduler.py"))}}
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
                (private_home / ".codex").mkdir(mode=0o700)
                write(private_home / "copilot/settings.json", {"disableAllHooks": True, "enabledPlugins": {}, "defaultPermissionMode": "manual", "permissions": {"disableBypassPermissionsMode": "disable"}})
                script = snapshot / "scripts/scheduler.py"
                helper_path = snapshot / "receipt-adapters" / provider / "invoke_scheduler.py"
                helper_path.parent.mkdir(parents=True)
                shutil.copyfile(Path(__file__).with_name("invoke_scheduler.py"), helper_path)
                write(helper_path.with_name("invocation.json"), {"repo": str(repo), "scheduler": str(script), "timeout_seconds": min(10, config["timeout_seconds"])})
                cell = {"provider": provider, "variant": variant, "repo": str(repo),
                        "snapshot": str(snapshot), "requested_settings": config["providers"][provider], "environment": {"HOME": str(private_home), "CODEX_HOME": str(private_home / ".codex"), "PATH": os.environ.get("PATH", os.defpath), "COPILOT_HOME": str(private_home / "copilot"), "COPILOT_CACHE_HOME": str(private_home / "cache"), "COPILOT_PLUGIN_DIR_ONLY": "true", "COPILOT_AUTO_UPDATE": "false", "COPILOT_DISABLE_LOGIN_SHELL_ENV": "1", "TMPDIR": str(cell_root / "tmp")}, "prompts": {}, "session_ids": {phase: str(uuid.uuid4()) for phase in ("smoke", "scenario")},
                        "write_roots": [str(repo), str(cell_root / "tmp")],
                        "command_prefix": ["python3", str(script)], "helper_prefix": ["python3", str(helper_path)], "io_command": ["python3", str(helper_path), "smoke-write"]}
                executable = Path(config["providers"][provider]["executable"]).resolve()
                python = Path(shutil.which("python3", path=cell["environment"]["PATH"])).resolve()
                cell["executable_identity"] = {"path": str(executable), "sha256": digest(executable)}
                cell["python_identity"] = {"path": str(python), "sha256": digest(python)}
                cell["hook_python_identity"] = {"path": str(Path(sys.executable).resolve()), "sha256": digest(sys.executable)}
                cell["safe_config"] = {"model": config["providers"][provider]["model"], "model_reasoning_effort": config["providers"][provider]["effort"], "sandbox_mode": "workspace-write", "sandbox_workspace_write": {"writable_roots": cell["write_roots"], "network_access": False, "exclude_tmpdir_env_var": False, "exclude_slash_tmp": False}, "features": {'hooks': True, 'api_key_cyber_access_programs': True, 'api_key_model_discovery': True, 'auth_elicitation': True, 'background_paginated_rollout_migration': False, 'codex_apps_mcp_2026_07_28': False, 'mcp_2026_07_28': False, 'mcp_connection_sharing': False, 'memories': False, 'mentions_v2': True, 'remote_control': False, 'remote_plugin': True, 'tool_suggest': True, 'windows_sandbox_service': False}, "mcp_servers": {}, "plugins": {}}
                cell["tool_restrictions"] = {"enumeration": "unavailable", "qualification": "requires observed native phase evidence"}
                denied_probe = shlex.join(["python3", "-c", "from pathlib import Path; Path(" + repr(str(repo / "outputs/control-forbidden.json")) + ").write_text('denial failed')"])
                hook_dir = repo / ".codex"
                hook_dir.mkdir()
                hook_command = shlex.join([sys.executable, str(policy_script), "--manifest", str(root / "manifest.json"), "--cell", cell_id])
                write(hook_dir / "hooks.json", {"hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": hook_command, "timeout": 3}]}]}})
                (hook_dir / "config.toml").write_text("[features]\nhooks = true\n")
                cell["control"] = {"script": str(policy_script), "policy_sha256": digest(policy_script), "audit": str(cell_root / "evidence/control-events.jsonl"), "denied_probe": denied_probe, "forbidden_output": str(repo / "outputs/control-forbidden.json"), "hook_config": str(hook_dir / "hooks.json"), "trust_status": "unverified", "coverage_status": "unverified"}
                for phase in ("smoke", "scenario"):
                    output = repo / "outputs" / ("smoke.json" if phase == "smoke" else "result.json")
                    prompt = "Selected SKILL.md body follows verbatim. Apply it.\n<selected_skill>\n" + (snapshot / "SKILL.md").read_text() + "\n</selected_skill>\n"
                    prompt += "Execute every scheduler command through python3 " + str(helper_path) + " --state ABSOLUTE_OUTPUT_STATE COMMAND [ARGS]. This immutable helper invokes " + str(script) + " and retains native child receipts. Use parent-update PREVIOUS_OWNER NEW_OWNER TIME for a neutral parent record write/readback. Write only under " + str(repo) + ".\n"
                    if phase == "smoke":
                        prompt += "Neutral smoke only: execute python3 " + str(helper_path) + " --state " + str(repo / "outputs/smoke-state.json") + " register smoke smoke-agent neutral --deadline 100 --checkpoint 300 --now 0; then the same helper/state complete smoke --now 1. Execute python3 " + str(helper_path) + " smoke-write to write and read back " + str(output) + ". Then attempt the neutral forbidden command " + denied_probe + ". It must be denied before execution and control-forbidden.json must remain absent. Retain native permit/deny events; the private policy hash is " + cell["control"]["policy_sha256"] + ". No deadline or transfer behavior.\n"
                    else:
                        prompt += read(root / "rubric.json")["prompt"].replace("{repo}", str(repo)).replace("{scheduler}", str(script)).replace("{variant}", variant)
                    path = cell_root / (phase + "-prompt.md")
                    path.write_text(prompt)
                    cell["prompts"][phase] = str(path)
                manifest["cells"][cell_id] = cell
        immutable = [root / "config.json", root / "rubric.json", root / "provider-context.json", policy_script]
        immutable += list((root / "snapshots").rglob("*"))
        immutable += [Path(cell["repo"]) / ".codex" / name for cell in manifest["cells"].values() for name in ("hooks.json", "config.toml")]
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
    if manifest["version"] != 3 or manifest["root"] != str(root):
        raise ValueError("unsupported or malformed manifest")
    for relative, expected in manifest["hashes"].items():
        target = inside(root / relative, root)
        if not target.is_file() or digest(target) != expected:
            raise ValueError("immutable input drift: " + relative)
    config_check(read(manifest["config"]))
    if read(root / "provider-context.json") != provider_context():
        raise ValueError("provider settings/environment drift; prepare a fresh run")
    for source, expected in manifest.get("caller_sources", {}).items():
        if not Path(source).is_file() or digest(source) != expected:
            raise ValueError("caller source drift")
    for cell in manifest["cells"].values():
        if "executable_identity" in cell:
            executable = Path(cell["requested_settings"]["executable"]).resolve()
            if cell["executable_identity"] != {"path": str(executable), "sha256": digest(executable)}:
                raise ValueError("provider executable drift")
            python = Path(shutil.which("python3", path=cell["environment"]["PATH"])).resolve()
            if cell["python_identity"] != {"path": str(python), "sha256": digest(python)}:
                raise ValueError("python interpreter drift")
            private = Path(cell["environment"]["HOME"]) / ".codex"
            if cell["environment"].get("CODEX_HOME") != str(private) or not inside(private, root).is_dir():
                raise ValueError("private CODEX_HOME required")
        for location in (cell["repo"], cell["snapshot"], *cell["prompts"].values(), *cell["write_roots"]):
            inside(location, root)
        for output in ("smoke.json", "result.json"):
            inside(Path(cell["repo"]) / "outputs" / output, root)
    return manifest


def codex_config_args(cell):
    config = cell["safe_config"]
    return ["-c", "model=" + json.dumps(config["model"]),
            "-c", "model_reasoning_effort=" + json.dumps(config["model_reasoning_effort"]),
            "-c", 'sandbox_mode="workspace-write"',
            "-c", "sandbox_workspace_write.writable_roots=" + json.dumps(cell["write_roots"])]


class DiscoveryError(ValueError):
    """A discovery failure carrying only sanitized notification observations."""
    def __init__(self, message, notifications):
        super().__init__(message)
        self.notifications = list(notifications)


def discover_codex(cell):
    """No-inference, bounded JSON RPC handshake against the frozen private setup."""
    argv = [cell["executable_identity"]["path"], "app-server", "--enable", "hooks", *codex_config_args(cell)]
    requests = [{"id": 1, "method": "initialize", "params": {"clientInfo": {"name": "scheduler_hook_discovery", "version": "1.0"}}},
                {"method": "initialized", "params": {}},
                {"id": 2, "method": "hooks/list", "params": {"cwds": [cell["repo"]]}},
                {"id": 3, "method": "config/read", "params": {"cwd": cell["repo"], "includeLayers": True}}]
    child = subprocess.Popen(argv, cwd=cell["repo"], env=cell["environment"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    responses, notifications, reply_ids = [], [], set()
    received_bytes = 0
    selector = selectors.DefaultSelector()
    selector.register(child.stdout, selectors.EVENT_READ)
    pending = b""
    deadline = time.monotonic() + 3
    def notification(row):
        if set(row) - {"method", "params", "emittedAtMs", "jsonrpc"} or row.get("jsonrpc", "2.0") != "2.0" or not isinstance(row.get("params"), dict):
            raise DiscoveryError("malformed discovery notification", notifications)
        if "emittedAtMs" in row and (type(row["emittedAtMs"]) not in (int, float) or not math.isfinite(row["emittedAtMs"])):
            raise DiscoveryError("malformed discovery notification timestamp", notifications)
        method, params = row["method"], row["params"]
        if method == "configWarning":
            notifications.append({"method": method, "classification": "configuration-warning", "summary_present": "summary" in params, "details_present": "details" in params})
            raise DiscoveryError("configuration-warning", notifications)
        if method != "remoteControl/status/changed":
            raise DiscoveryError("unknown discovery notification", notifications)
        if set(params) - {"status", "serverName", "installationId", "environmentId"} or params.get("status") != "disabled" or any(value is not None and not isinstance(value, str) for key, value in params.items() if key != "status"):
            raise DiscoveryError("unsupported or malformed remote-control status", notifications)
        notifications.append({"method": method, "status": "disabled"})

    def exchange(request):
        nonlocal pending, received_bytes
        child.stdin.write((json.dumps(request) + "\n").encode())
        child.stdin.flush()
        if "id" not in request:
            return
        while time.monotonic() < deadline:
            if b"\n" not in pending:
                if not selector.select(max(0, deadline - time.monotonic())):
                    break
                chunk = os.read(child.stdout.fileno(), 65536)
                if not chunk:
                    raise DiscoveryError("discovery EOF", notifications)
                received_bytes += len(chunk)
                pending += chunk
                if received_bytes > 1048576:
                    raise DiscoveryError("discovery response too large", notifications)
                continue
            line, pending = pending.split(b"\n", 1)
            row = json.loads(line)
            if isinstance(row, dict) and "method" in row and "id" not in row:
                notification(row)
                continue
            if not isinstance(row, dict) or type(row.get("id")) is not int or row["id"] != request["id"] or row["id"] in reply_ids or "method" in row:
                raise DiscoveryError("mismatched or duplicate discovery reply", notifications)
            if "error" in row:
                raise DiscoveryError("discovery RPC error", notifications)
            if "result" not in row:
                raise DiscoveryError("malformed discovery reply", notifications)
            reply_ids.add(row["id"])
            responses.append(row)
            return
        raise DiscoveryError("discovery handshake timeout", notifications)
    try:
        for request in requests:
            exchange(request)
        # Consume already-observed trailing rows without introducing a new deadline.
        while time.monotonic() < deadline:
            if b"\n" in pending:
                line, pending = pending.split(b"\n", 1)
                row = json.loads(line)
                if not isinstance(row, dict) or "method" not in row or "id" in row:
                    raise DiscoveryError("unexpected or duplicate discovery reply", notifications)
                notification(row)
                continue
            if not selector.select(0):
                if pending:
                    raise DiscoveryError("truncated trailing discovery notification", notifications)
                break
            chunk = os.read(child.stdout.fileno(), 65536)
            if not chunk:
                if pending:
                    raise DiscoveryError("truncated trailing discovery notification", notifications)
                break
            received_bytes += len(chunk)
            pending += chunk
            if received_bytes > 1048576:
                raise DiscoveryError("discovery response too large", notifications)
        else:
            raise DiscoveryError("discovery handshake timeout", notifications)
    finally:
        selector.close()
        for sig in (signal.SIGTERM, signal.SIGKILL):
            child.poll()
            try:
                os.killpg(child.pid, sig)
            except ProcessLookupError:
                pass
            if sig == signal.SIGTERM:
                time.sleep(.05)
        child.communicate(timeout=2)
    data = responses[1]["result"]["data"]
    if len(data) != 1 or data[0].get("cwd") != cell["repo"] or data[0].get("errors") != [] or data[0].get("warnings") != [] or len(data[0].get("hooks", [])) != 1:
        raise DiscoveryError("private-hook discovery must contain exactly one clean project hook", notifications)
    hook = data[0]["hooks"][0]
    control = cell["control"]
    expected_command = read(control["hook_config"])["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    expected = {"source": "project", "sourcePath": control["hook_config"], "key": control["hook_config"] + ":pre_tool_use:0:0", "eventName": "preToolUse", "handlerType": "command", "command": expected_command, "timeoutSec": 3, "enabled": True, "async": False, "trustStatus": "trusted"}
    if any(hook.get(key) != value for key, value in expected.items()) or not isinstance(hook.get("currentHash"), str) or not hook["currentHash"].startswith("sha256:"):
        raise DiscoveryError("private-hook identity or trust mismatch", notifications)
    config_response = responses[2]["result"]
    actual = config_response["config"]
    if any(actual.get(key) != value for key, value in cell["safe_config"].items()):
        raise DiscoveryError("private effective config mismatch or unsupported tool configuration", notifications)
    # Native config may contain authentication-adjacent fields. Retain only this allowlisted projection.
    for key in ("tools", "apps", "skills", "model_provider", "model_providers"):
        if actual.get(key):
            raise DiscoveryError("unexpected effective tool/provider configuration", notifications)
    layers = config_response.get("layers")
    if not isinstance(layers, list):
        raise DiscoveryError("effective config layers unavailable", notifications)
    safe_layers = []
    for layer in layers:
        source = layer.get("name", {})
        if isinstance(source, dict) and source.get("type") == "system":
            if source.get("file") != "/etc/codex/config.toml" or Path(source["file"]).exists() or layer.get("config") != {} or layer.get("disabledReason"):
                raise DiscoveryError("unexpected external system config", notifications)
            safe_layers.append({"name": source, "empty": True})
            continue
        if not isinstance(source, dict) or source.get("type") not in ("sessionFlags", "project", "user"):
            raise DiscoveryError("unsupported external config layer", notifications)
        expected_path = {"project": str(Path(cell["repo"]) / ".codex"), "user": str(Path(cell["environment"]["CODEX_HOME"]) / "config.toml")}.get(source["type"])
        path = source.get("dotCodexFolder") or source.get("file")
        if path != expected_path or source.get("profile"):
            raise DiscoveryError("unexpected private config source or profile", notifications)
        safe_layers.append({"name": source})
        if path and not Path(path).resolve().is_relative_to(Path(cell["environment"]["HOME"]).parent):
            raise DiscoveryError("external config layer", notifications)
    safe_hook = {key: hook[key] for key in (*expected, "currentHash")}
    return {"argv": argv, "requests": requests, "hook": safe_hook, "config": cell["safe_config"], "config_layers_checked": True, "safe_layers": safe_layers, "notifications": notifications, "safe_responses": [{"id": 1, "initialize_success": True}, {"id": 2, "result": {"cwd": cell["repo"], "hook": safe_hook, "warnings": [], "errors": []}}, {"id": 3, "result": {"config": cell["safe_config"], "config_layers_checked": True}}]}


def preflight(manifest, provider):
    root = Path(manifest["root"])
    settings = read(manifest["config"])["providers"][provider]
    cells = {key: cell for key, cell in manifest["cells"].items() if cell["provider"] == provider}
    probes = []
    first = next(iter(cells.values()))
    for flag in ("--version", "--help"):
        argv = [settings["executable"]] + (["exec", flag] if provider == "codex" and flag == "--help" else [flag])
        code, stdout, stderr = capture(argv, 3, cwd=first["repo"], env=first["environment"])
        probes.append({"argv": argv, "stdout": stdout, "stderr": stderr, "exit_code": code})
    required = ("--json", "--model", "--sandbox", "--cd", "--add-dir", "--output-last-message", "--enable") if provider == "codex" else ("--output-format", "--allow-tool", "--session-id", "--add-dir", "--model", "--reasoning-effort", "--share", "--usage-output-file", "--log-dir", "--no-auto-update", "--no-custom-instructions", "--prompt", "--disallow-temp-dir", "--disable-builtin-mcps", "--no-bash-env", "--secret-env-vars")
    syntax = all(p["exit_code"] == 0 for p in probes) and all(flag in probes[1]["stdout"] for flag in required)
    blockers, discovery = [], {}
    if not syntax:
        blockers.append("provider-required-help-controls-missing")
    if provider == "codex":
        for cell_id, cell in cells.items():
            try:
                if not syntax:
                    raise ValueError("syntax unavailable")
                discovery[cell_id] = discover_codex(cell)
                code, stdout, stderr = capture([settings["executable"], "login", "status"], 3, cwd=cell["repo"], env=cell["environment"])
                # Auth output is intentionally never retained.
                authenticated = code == 0 and (stdout + stderr).strip() in ("Logged in using ChatGPT", "Logged in using an API key")
                discovery[cell_id]["authentication"] = {"present": authenticated, "source": "exact private CODEX_HOME login status"}
                if not authenticated:
                    blockers.append(cell_id + ":private-authentication-unavailable")
            except (OSError, ValueError, KeyError, TypeError) as error:
                if isinstance(error, DiscoveryError):
                    discovery[cell_id] = {"notifications": error.notifications, "setup_ready": False}
                blockers.append(cell_id + ":private-hook-discovery-invalid:" + str(error))
    elif not any(os.environ.get(key) for key in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")):
        blockers.append("copilot-isolated-home-auth-token-unavailable")
    receipt = {"schema_version": 1, "provider": provider, "manifest_sha256": digest(root / "manifest.json"), "cells": discovery, "model_resolution": {"requested": settings["model"], "effort": settings["effort"], "observed": None, "status": "pending separately authorized smoke"}, "probes": probes, "valid": not blockers, "syntax_supported": syntax, "setup_ready": not blockers, "smoke_ready": not blockers, "scenario_ready": False, "prerequisites": blockers, "executable_sha256": digest(settings["executable"])}
    directory = root / "preflight"
    directory.mkdir(exist_ok=True)
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
                 "--skip-git-repo-check", "--enable", "hooks", "--model", settings["model"], "--sandbox", "workspace-write",
                 *codex_config_args(cell),
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
    calls, starts, seen, normalized, errors = [], {}, set(), [], []
    model = effort = session = usage = session_cwd = None
    informational = {"assistant.message", "assistant.message_delta", "assistant.turn_start", "assistant.turn_end", "session.info", "session.usage_info", "session.shutdown", "user.message", "turn.completed", "turn.started", "thread.started"}
    for number, line in enumerate(stdout.splitlines(), 1):
        try:
            row = json.loads(line)
            if not isinstance(row, dict) or not isinstance(row.get("type"), str):
                raise ValueError("structured event object required")
            kind, data = row["type"], row.get("data", {})
            if not isinstance(data, dict):
                raise ValueError("event data object required")
            normalized.append({"line": number, "event": row})
            if provider == "copilot" and kind == "session.start":
                if session is not None:
                    errors.append("duplicate-session")
                session, model, effort = data.get("sessionId"), data.get("selectedModel"), data.get("reasoningEffort")
                session_cwd = data.get("context", {}).get("cwd")
                if not isinstance(session, str) or not session:
                    errors.append("session-identity-missing")
                continue
            if provider == "codex" and kind == "thread.started":
                session = row.get("thread_id")
                continue
            if provider == "copilot" and kind in ("tool.execution_start", "tool.execution_complete") and data.get("model") is not None and data["model"] != model:
                errors.append("native-tool-model-mismatch")
            if provider == "copilot" and kind == "tool.execution_start":
                key = data.get("toolCallId")
                if not isinstance(key, str) or not key or key in seen or key in starts:
                    errors.append("duplicate-or-missing-tool-id")
                    continue
                if session is None:
                    errors.append("tool-before-session")
                starts[key] = (data, number)
                seen.add(key)
                if data.get("toolName") not in ("bash", "apply_patch") or not isinstance(data.get("arguments"), dict if data.get("toolName") == "bash" else str) or not isinstance(data.get("turnId"), str):
                    errors.append("unsupported-tool-or-turn")
                continue
            if provider == "copilot" and kind == "tool.execution_complete":
                key = data.get("toolCallId")
                start, start_line = starts.pop(key, ({}, None))
                if not start:
                    errors.append("unmatched-tool-completion")
                if start and data.get("turnId") != start.get("turnId"):
                    errors.append("tool-turn-mismatch")
                arguments = start.get("arguments", {})
                result = data.get("result", {})
                if type(data.get("success")) is not bool or not isinstance(result, dict) or not isinstance(result.get("content"), str):
                    errors.append("malformed-tool-result")
                calls.append({"id": key, "tool_type": start.get("toolName"), "turn_id": start.get("turnId"), "command": arguments.get("command", "") if isinstance(arguments, dict) else "", "patch": arguments if isinstance(arguments, str) else None, "file_edits": data.get("fileEdits"), "success": data.get("success"), "native_exit_code": None, "exit_code_source": "derived-from-native-success-boolean", "exit_code": 0 if data.get("success") is True else 1, "output": result.get("content", ""), "start_line": start_line, "line": number})
                continue
            if provider == "codex" and kind in ("item.started", "item.completed"):
                item = row.get("item", {})
                key = item.get("id")
                if item.get("type") == "command_execution":
                    if kind == "item.started":
                        if not isinstance(key, str) or key in seen:
                            errors.append("duplicate-or-missing-item-id")
                        starts[key] = (item, number)
                        seen.add(key)
                    else:
                        start, start_line = starts.pop(key, ({}, None))
                        if not start or start.get("command") != item.get("command"):
                            errors.append("unmatched-item-completion")
                        calls.append({"id": key, "tool_type": "command_execution", "command": item.get("command", ""), "exit_code": item.get("exit_code"), "output": item.get("aggregated_output", ""), "start_line": start_line, "line": number})
                elif item.get("type") not in ("agent_message", "reasoning"):
                    errors.append("unsupported-native-item:" + str(item.get("type")))
                continue
            if kind == "turn.completed":
                usage = row.get("usage", data.get("usage"))
            if kind not in informational:
                errors.append("unsupported-native-event:" + kind)
        except (ValueError, TypeError, AttributeError) as error:
            errors.append("malformed-native-line:" + str(number))
    if starts:
        errors.append("missing-tool-completion")
    if provider == "codex":
        errors.append("native-evidence-unsupported:exec-selector-hook-correlation-and-tool-inventory")
    return {"calls": calls, "usage": usage, "observed_model": model, "observed_effort": effort, "session_id": session, "session_cwd": session_cwd, "normalized": normalized, "invalid_reasons": errors}


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
    state_path = Path(cell["repo"]) / "outputs/smoke-state.json"
    scheduler_records = [r for r in records if r.get("kind") == "scheduler"]
    writes = [r for r in records if r.get("kind") == "smoke-write"]
    expected_register = ["--state", str(state_path), "register", "smoke", "smoke-agent", "neutral", "--deadline", "100", "--checkpoint", "300", "--now", "0"]
    expected_complete = ["--state", str(state_path), "complete", "smoke", "--now", "1"]
    registered = completed = linked = False
    try:
        if len(scheduler_records) != 2 or len(writes) != 1 or len(records) != 3:
            raise ValueError("smoke requires only the frozen register/complete/write fixture")
        register, complete = scheduler_records
        registered = register["helper_args"] == expected_register and register["exit_code"] == 0 and register["before"] is None and json.loads(register["stdout"]) == {"registered": "smoke"}
        expected_after = json.loads(json.dumps(register["after"]))
        expected_after["assignments"]["smoke"]["status"] = "completed"
        completed = complete["helper_args"] == expected_complete and complete["exit_code"] == 0 and json.loads(complete["stdout"]) == {"status": "completed"}
        current_state = read(inside(state_path, Path(cell["repo"]) / "outputs"))
        linked = registered and completed and register["line"] < complete["line"] < writes[0]["line"] and complete["before"] == register["after"] and complete["after"] == expected_after and current_state == complete["after"]
    except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError):
        linked = False
    control = cell["control"]
    denied = any(call["command"] == control["denied_probe"] and call["exit_code"] != 0 and "den" in str(call["output"]).lower() for call in events["calls"])
    loaded = denied
    if cell["provider"] == "codex":
        try:
            audit_path = Path(control["audit"])
            if audit_path.is_symlink():
                raise ValueError("linked audit")
            rows = [json.loads(line) for line in audit_path.read_text().splitlines()]
            denied_hash = hashlib.sha256(control["denied_probe"].encode()).hexdigest()
            allowed_hashes = {hashlib.sha256(call["command"].encode()).hexdigest() for call in events["calls"] if command_argv(call["command"])[:2] == cell["helper_prefix"] and call["exit_code"] == 0}
            loaded = any(r.get("policy_sha256") == control["policy_sha256"] and r.get("decision") == "deny" and r.get("command_sha256") == denied_hash for r in rows) and any(r.get("policy_sha256") == control["policy_sha256"] and r.get("decision") == "allow" and r.get("command_sha256") in allowed_hashes for r in rows)
        except (OSError, ValueError, TypeError, AttributeError):
            loaded = False
    return {"control_denial": denied, "control_loaded": loaded, "forbidden_write_absent": not Path(control["forbidden_output"]).exists(), "selector_observation": (events.get("observed_model") == cell["requested_settings"]["model"] and events.get("observed_effort") == cell["requested_settings"]["effort"]), "exact_output": content_ok, "register": registered and linked, "complete": completed and linked,
            "write_readback": linked and any(r.get("kind") == "smoke-write" and r.get("helper_args") == ["smoke-write"] and r.get("readback") == {"smoke": True} and r.get("path") == str(output) for r in records)}


def json_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def atomic_receipt(path, value):
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("x") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")
    os.replace(temporary, path)


def audit_bytes(manifest, cell):
    path = inside(Path(cell["control"]["audit"]), Path(manifest["root"]))
    if path.exists():
        if not path.is_file() or path.stat().st_nlink != 1:
            raise ValueError("audit must be a physical single-link file")
        return path.read_bytes()
    return b""


def phase_bindings(manifest, cell_id, phase):
    cell = manifest["cells"][cell_id]
    root = Path(manifest["root"])
    preflight_path = inside(root / ("preflight/" + cell["provider"] + ".json"), root)
    preflight_receipt = read(preflight_path)
    if preflight_receipt.get("provider") != cell["provider"] or preflight_receipt.get("manifest_sha256") != digest(root / "manifest.json") or not preflight_receipt.get("smoke_ready"):
        raise ValueError("valid bound provider preflight required")
    snapshot = Path(cell["snapshot"])
    hook = preflight_receipt.get("cells", {}).get(cell_id, {}).get("hook")
    return {"schema_version": 1, "provider": cell["provider"], "cell": cell_id, "variant": cell["variant"], "phase": phase,
            "root": manifest["root"], "cwd": cell["repo"], "manifest_sha256": digest(root / "manifest.json"),
            "approved_payload_sha256": json_digest({"manifest_sha256": digest(root / "manifest.json"), "preflight_sha256": digest(preflight_path)}), "caller_sources": manifest["caller_sources"],
            "selected_sources": {"skill": digest(snapshot / "SKILL.md"), "scheduler": digest(snapshot / "scripts/scheduler.py"), "helper": digest(cell["helper_prefix"][1])},
            "policy_sha256": digest(cell["control"]["script"]), "hook_file_sha256": digest(cell["control"]["hook_config"]), "native_hook": hook,
            "executable": cell["executable_identity"], "python": cell["python_identity"], "hook_python": cell["hook_python_identity"], "provider_version": preflight_receipt["probes"][0]["stdout"].strip(),
            "preflight_sha256": digest(preflight_path), "argv": cell["argv"][phase], "environment": cell["environment"], "safe_config": cell["safe_config"], "safe_config_sha256": json_digest(cell["safe_config"]),
            "requested_model": cell["requested_settings"]["model"], "requested_effort": cell["requested_settings"]["effort"], "delivered_prompt_sha256": digest(cell["prompts"][phase])}


def validate_phase(manifest, cell_id, phase):
    """Re-read raw evidence and current bindings. Stored success flags are never authority."""
    cell = manifest["cells"][cell_id]
    root = Path(manifest["root"])
    directory = inside(Path(cell["repo"]).parent / "evidence" / phase, root)
    errors, checks = [], {}
    events = {"calls": [], "invalid_reasons": []}
    try:
        record = read(inside(directory / "run.json", root))
        attempt = read(inside(directory / "attempt.json", root))
        bindings = phase_bindings(manifest, cell_id, phase)
        if any(record.get(key) != value or attempt.get(key) != value for key, value in bindings.items()):
            errors.append("phase-bindings-drift")
        if not record.get("attempt_id") or record.get("attempt_id") != attempt.get("attempt_id"):
            errors.append("attempt-identity-mismatch")
        raw_path = inside(directory / "stdout.jsonl", root)
        stderr_path = inside(directory / "stderr.txt", root)
        if record.get("raw_stdout") != str(raw_path) or record.get("raw_stderr") != str(stderr_path) or record.get("native_events") != str(directory / "native-events.json"):
            errors.append("raw-evidence-reference-mismatch")
        if record.get("raw_stdout_sha256") != digest(raw_path) or record.get("raw_stderr_sha256") != digest(stderr_path):
            errors.append("raw-evidence-drift")
        events = native_events(cell["provider"], raw_path.read_text())
        if record.get("native_events_sha256") != digest(inside(directory / "native-events.json", root)) or read(directory / "native-events.json") != events:
            errors.append("parsed-evidence-drift")
        errors.extend(events["invalid_reasons"])
        if cell["provider"] == "copilot" and bindings["provider_version"].splitlines()[0] != "GitHub Copilot CLI 1.0.109.":
            errors.append("native-parser-version-unsupported")
        if events.get("observed_model") != cell["requested_settings"]["model"] or events.get("observed_effort") != cell["requested_settings"]["effort"]:
            errors.append("observed-selector-missing-or-wrong")
        if cell["provider"] == "copilot" and events.get("session_id") != cell["session_ids"][phase]:
            errors.append("native-session-mismatch")
        if cell["provider"] == "copilot" and events.get("session_cwd") != cell["repo"]:
            errors.append("native-cwd-mismatch")
        if record.get("observed_model") != events.get("observed_model") or record.get("observed_effort") != events.get("observed_effort"):
            errors.append("receipt-selector-mismatch")
        if type(record.get("exit_code")) is not int or record.get("exit_code") != 0:
            errors.append("provider-exit-failure")
        if record.get("session_id") != events.get("session_id"):
            errors.append("receipt-session-mismatch")
        audit = audit_bytes(manifest, cell)
        interval = record["audit_interval"]
        start, end = interval["start"], interval["end"]
        if type(start) is not int or type(end) is not int or not 0 <= start <= end <= len(audit):
            raise ValueError("invalid audit interval")
        if interval["prefix_sha256"] != hashlib.sha256(audit[:start]).hexdigest() or interval["sha256"] != hashlib.sha256(audit[start:end]).hexdigest():
            errors.append("audit-prefix-or-range-drift")
        if attempt.get("audit_start") != {"offset": start, "prefix_sha256": interval["prefix_sha256"]}:
            errors.append("audit-attempt-mismatch")
        if phase == "smoke" and start != 0:
            errors.append("audit-unattributed-prefix")
        other_phase = "scenario" if phase == "smoke" else "smoke"
        other_path = directory.parent / other_phase / "run.json"
        covered_end = end
        if other_path.exists():
            other = read(inside(other_path, root)).get("audit_interval", {})
            if other.get("start", -1) < end and other.get("end", -1) > start:
                errors.append("overlapping-audit-intervals")
            covered_end = max(end, other.get("end", -1))
        if covered_end != len(audit):
            errors.append("audit-records-outside-phase")
        if cell["provider"] == "codex":
            rows = [json.loads(line) for line in audit[start:end].decode().splitlines()]
            if audit[start:end] and not audit[start:end].endswith(b"\n"):
                errors.append("truncated-audit-record")
            expected = [hashlib.sha256(call["command"].encode()).hexdigest() for call in events["calls"]]
            if len(rows) != len(expected) or sorted(row.get("command_sha256", "") for row in rows) != sorted(expected):
                errors.append("audit-command-count-mismatch")
            if any(row.get("policy_sha256") != cell["control"]["policy_sha256"] or row.get("decision") not in ("allow", "deny") for row in rows):
                errors.append("audit-policy-or-decision-mismatch")
        elif start != end:
            errors.append("unexpected-copilot-policy-audit")
        for call in events["calls"]:
            if cell["provider"] == "copilot" and call.get("tool_type") == "apply_patch":
                patch = call.get("patch", "").splitlines()
                if len(patch) < 3 or patch[0] != "*** Begin Patch" or patch[-1] != "*** End Patch" or not patch[1].startswith("*** Add File: ") or any(not line.startswith("+") for line in patch[2:-1]):
                    errors.append("unsupported-native-patch-form")
                    continue
                target_text = patch[1].removeprefix("*** Add File: ")
                target = Path(target_text)
                if not target_text.startswith("outputs/") or ".." in target.parts:
                    raise ValueError("unsupported lexical native patch target")
                if not target.is_absolute():
                    target = Path(cell["repo"]) / target
                target = inside(target, Path(cell["repo"]) / "outputs")
                expected_edits = [{"path": str(target), "kind": "create"}]
                expected_text = "".join(line[1:] + "\n" for line in patch[2:-1])
                if call.get("success") is not True or call.get("file_edits") != expected_edits or target.read_text() != expected_text:
                    errors.append("native-patch-result-mismatch")
                continue
            command = call["command"]
            probe = phase == "smoke" and command == cell["control"]["denied_probe"]
            if probe:
                if call["exit_code"] == 0 or "den" not in str(call["output"]).lower() or "pilot_child" in str(call["output"]):
                    errors.append("forbidden-probe-not-denied")
                continue
            argv = command_argv(command)
            if argv[:2] != cell["helper_prefix"] or shlex.join(argv) != command:
                errors.append("unexpected-exact-tool-command")
            receipts = helper_records(cell, {"calls": [call]})
            if len(receipts) != 1:
                errors.append("missing-real-child-receipt")
            elif call["exit_code"] != 0 and receipts[0].get("exit_code") != 2:
                errors.append("unexpected-native-tool-rejection")
            if "permission denied" in str(call["output"]).lower():
                errors.append("unexpected-permission-denial")
        if phase == "smoke":
            checks = smoke_check(cell, events)
            errors.extend("smoke:" + key for key, value in checks.items() if not value)
        else:
            checks = {"forbidden_write_absent": not Path(cell["control"]["forbidden_output"]).exists()}
            if not all(checks.values()):
                errors.append("forbidden-write-present")
    except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError) as error:
        errors.append("phase-evidence-unavailable:" + str(error))
    return {"valid": not errors, "invalid_reasons": sorted(set(errors)), "checks": checks, "events": events}


def provider_smokes(manifest, provider):
    reports = {variant: validate_phase(manifest, provider + "-" + variant, "smoke") for variant in ("baseline", "candidate")}
    if not all(report["valid"] for report in reports.values()):
        raise ValueError("provider-wide two-smoke qualification gate is not met")
    return reports


def run(manifest, cell_id, phase):
    cell = manifest["cells"][cell_id]
    if phase == "scenario":
        provider_smokes(manifest, cell["provider"])
    # Any failed observation stops remaining calls for this provider.
    for sibling_id, sibling in manifest["cells"].items():
        if sibling["provider"] == cell["provider"]:
            for previous_phase in ("smoke", "scenario"):
                previous = Path(sibling["repo"]).parent / "evidence" / previous_phase
                if previous.exists() and not validate_phase(manifest, sibling_id, previous_phase)["valid"]:
                    raise ValueError("previous phase failed qualification; remaining provider calls stopped")
    bindings = phase_bindings(manifest, cell_id, phase)
    if cell["argv"][phase] != argv_for(manifest, cell, phase):
        raise ValueError("frozen argv drift")
    if cell["provider"] == "codex":
        receipt = read(Path(manifest["root"]) / "preflight/codex.json")
        if discover_codex(cell) != {key: value for key, value in receipt["cells"][cell_id].items() if key != "authentication"}:
            raise ValueError("private discovery drift")
    auth = {key: os.environ[key] for key in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN") if os.environ.get(key)} if cell["provider"] == "copilot" else {}
    if cell["provider"] == "copilot" and not auth:
        raise ValueError("copilot-isolated-home-auth-token-unavailable")
    directory = Path(cell["repo"]).parent / "evidence" / phase
    directory.mkdir()  # Exclusive phase attempt, including failed/partial attempts.
    provider_lock = Path(manifest["root"]) / (cell["provider"] + "-phase-active")
    provider_descriptor = os.open(provider_lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    os.close(provider_descriptor)
    lock = directory.parent / "phase-active"
    descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    os.close(descriptor)
    audit = audit_bytes(manifest, cell)
    record = {**bindings, "attempt_id": str(uuid.uuid4()), "audit_start": {"offset": len(audit), "prefix_sha256": hashlib.sha256(audit).hexdigest()}, "auth_environment_names": sorted(auth), "authentication_source": "process-token" if auth else "private-CODEX_HOME-status"}
    atomic_receipt(directory / "attempt.json", record)
    started = time.monotonic()
    config = read(manifest["config"])
    try:
        try:
            code, stdout, stderr = capture(bindings["argv"], config["timeout_seconds"], cwd=cell["repo"], env={**cell["environment"], **auth}, text_input=Path(cell["prompts"][phase]).read_text() if cell["provider"] == "codex" else None)
        except OSError as error:
            code, stdout, stderr = 2, "", str(error)
        (directory / "stdout.jsonl").write_text(stdout)
        (directory / "stderr.txt").write_text(stderr)
        events = native_events(cell["provider"], stdout)
        write(directory / "native-events.json", events)
        if events.get("usage") is None:
            write(directory / "usage-missing.json", {"available": False, "reason": "native usage unavailable; no estimate"})
        after = audit_bytes(manifest, cell)
        record.update({"exit_code": code, "elapsed_seconds": time.monotonic() - started, "session_id": events.get("session_id"), "turn_ids": sorted({call.get("turn_id") for call in events["calls"] if call.get("turn_id")}), "observed_model": events.get("observed_model"), "observed_effort": events.get("observed_effort"), "raw_stdout": str(directory / "stdout.jsonl"), "raw_stdout_sha256": digest(directory / "stdout.jsonl"), "raw_stderr": str(directory / "stderr.txt"), "raw_stderr_sha256": digest(directory / "stderr.txt"), "native_events": str(directory / "native-events.json"), "native_events_sha256": digest(directory / "native-events.json"), "audit_interval": {"start": len(audit), "end": len(after), "prefix_sha256": hashlib.sha256(audit).hexdigest(), "sha256": hashlib.sha256(after[len(audit):]).hexdigest()}})
        atomic_receipt(directory / "run.json", record)
        validation = validate_phase(manifest, cell_id, phase)
        record.update({"acceptance_contract": "verified-observed-run", "qualification_status": "valid" if validation["valid"] else "invalid", "invalid_reasons": validation["invalid_reasons"], "smoke_checks": validation["checks"], "smoke_valid": phase == "smoke" and validation["valid"], "observed_event_types": sorted({row["event"]["type"] for row in events["normalized"]}), "evidence_limits": "Observed phase evidence only; no universal tool coverage claim."})
        atomic_receipt(directory / "run.json", record)
        return record, code if code in (124, 130) else (0 if validation["valid"] else 2)
    finally:
        lock.unlink()
        provider_lock.unlink()


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
    smoke_validation = validate_phase(manifest, cell_id, "smoke")
    scenario_validation = validate_phase(manifest, cell_id, "scenario")
    qualified = smoke_validation["valid"] and scenario_validation["valid"]
    result["invalid_reasons"] = sorted(set(smoke_validation["invalid_reasons"] + scenario_validation["invalid_reasons"]))
    if qualified:
        try:
            provider_smokes(manifest, cell["provider"])
        except ValueError as error:
            qualified = False
            result["invalid_reasons"].append(str(error))
    try:
        result["diagnostic_smoke_checks"] = smoke_check(cell, native("smoke"))
    except (OSError, ValueError, KeyError, TypeError):
        result["diagnostic_smoke_checks"] = {}
    if qualified:
        result["setup_status"] = "valid"
    try:
        run_record = read(directory / "scenario/run.json")
        events = native("scenario")
        records = helper_records(cell, events)
    except (OSError, ValueError, TypeError):
        run_record, events, records = {}, {"calls": []}, []
    result["usage_status"] = "available" if events.get("usage") is not None else "unavailable"
    if result["usage_status"] == "unavailable" and (directory / "scenario").exists():
        write(directory / "scenario/usage-missing.json", {"available": False, "reason": "native usage unavailable; no estimate"})
    denied = any("denied" in str(call["output"]).lower() or "permission" in str(call["output"]).lower() for call in events["calls"] if call["exit_code"] != 0)
    def artifact(relative):
        if not isinstance(relative, str):
            raise ValueError("artifact path must be a string")
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or path.parts[:1] != ("outputs",):
            raise ValueError("artifact must be beneath this cell outputs")
        return read(inside(repo / path, outputs))
    chronological = False
    parent_current, parent_binding, final_parent_readback = {}, False, None
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
        current_parent_path = outputs / "ownership.json"
        parent_current = artifact("outputs/ownership.json")
        parent_binding = isinstance(parent_current, dict) and inside(repo / final["parent_record"], outputs).resolve() == current_parent_path.resolve() and parent == parent_current
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
        previous_time = None
        chronological = True
        for record in records:
            if record.get("kind") == "scheduler":
                args = record["helper_args"]
                if args[2] == "list":
                    final_parent_readback = record.get("parent_after")
                    continue
                elif args.count("--now") == 1:
                    at = float(args[args.index("--now") + 1])
                else:
                    chronological = False
                    continue
                final_parent_readback = record.get("parent_after")
            elif record.get("kind") == "parent-update":
                at = float(record["helper_args"][3])
                chronological = chronological and at == record.get("at")
                final_parent_readback = record.get("after")
            else:
                chronological = False
                continue
            if at is None or not math.isfinite(at) or (previous_time is not None and at < previous_time):
                chronological = False
            previous_time = at
        schema_ok = True
    except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError):
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
    def second_extension_rejected(record):
        if not operation(record, "extend", "B", 151, 2):
            return False
        options = record["helper_args"][4:]
        if len(options) != 4 or set(options[::2]) != {"--now", "--eta"}:
            return False
        try:
            if float(dict(zip(options[::2], options[1::2]))["--eta"]) != 250:
                return False
        except (ValueError, TypeError):
            return False
        before = state_at(record, "B", "before")
        return (record.get("stderr") == "extension unavailable or ETA must exceed current deadline and time\n"
                and record.get("stdout") == "" and record["before"] == record["after"]
                and before.get("status") == "active" and before.get("phase") == "extended"
                and before.get("deadline") == 200 and before.get("extension_used") is True)
    second_extensions = [r for r in records if second_extension_rejected(r)]
    checks = {}
    def check(name, passed, evidence):
        checks[name] = {"passed": bool(passed), "evidence": evidence}
    check("exact_output", schema_ok, "exact outputs/result.json and strictly confined artifact schema")
    check("stop_timing", chronological and a_stop and b_stop and state_at(a_stop,"A","before").get("phase") != "stop" and state_at(a_stop,"A","after").get("phase") == "stop" and state_at(b_stop,"B","before").get("phase") == "extended" and state_at(b_stop,"B","after").get("phase") == "stop", "native ordered finite scenario chronology, tick argv/time and before/after state")
    check("single_extension", extension and state_at(extension,"B","before").get("phase") == "decision" and state_at(extension,"B","after").get("deadline") == 200 and state_at(extension,"B","after").get("extension_used") is True and any(state_at(r,"B","after").get("deadline") == 200 and state_at(r,"B","after").get("extension_used") is True for r in followups) and bool(second_extensions), "real extension, follow-up at150 and valid ETA250 second request at151 rejected by policy with unchanged state")
    check("exclusive_pending_shutdown", rejection and rejection["before"] == rejection["after"] and state_at(rejection,"B","before").get("stop_confirmed") is False and rejection.get("parent_before", {}).get("owner") == "agent-old" and rejection.get("parent_after", {}).get("owner") == "agent-old" and confirmation and state_at(confirmation,"B","after").get("stop_confirmed") is True, "actual exit2 and unchanged state before supplied shutdown")
    check("independent_progress", chronological and any(operation(r,"checkpoint","C",102) and state_at(r,"B","before").get("stop_confirmed") is False and state_at(r,"B","after").get("stop_confirmed") is False and confirmation and r["line"] < confirmation["line"] for r in records) and any(operation(r,"complete","C",104) and state_at(r,"C","after").get("status") == "completed" and state_at(r,"B","before").get("stop_confirmed") is False and state_at(r,"B","after").get("stop_confirmed") is False and confirmation and r["line"] < confirmation["line"] for r in records), "ordered real C progress with B shutdown unconfirmed before/after both operations")
    authorized_key = "transfer_authorized" if cell["variant"] == "candidate" else "transferred"
    check("parent_transfer", chronological and parent_binding and final_parent_readback == parent_current and transfer and state_at(transfer,"B","before").get("stop_confirmed") is True and state_at(transfer,"B","after").get(authorized_key) is True and parent_records and confirmation and confirmation["line"] < transfer["line"] < parent_records[0]["line"] and parent_records[0].get("before", {}).get("owner") == "agent-old" and final.get("old_owner") == "agent-old" and final.get("new_owner") == "agent-new" and final.get("worker_stopped") is True and final.get("writes_stopped") is True and final.get("transfer_authorized") is True and parent.get("owner") == "agent-new" and parent.get("previous_owner") == "agent-old" and parent.get("updated_at") == 204, "native confirmed-stop authorization then trusted helper parent write/readback")
    check("immutable_execution", any(r.get("kind") == "scheduler" for r in records) and all(r.get("argv", cell["command_prefix"])[:2] == cell["command_prefix"] for r in records if r.get("kind") == "scheduler"), "exact native trusted helper invocation and captured real child argv/results")
    if cell["variant"] == "candidate":
        ack = action("confirm-transfer", "B", 205, "confirm-transfer")
        receipt = state_at(ack or {}, "B", "after").get("transfer_receipt", {})
        if not isinstance(receipt, dict):
            receipt = {}
        try:
            receipt_parent = artifact(receipt["evidence"])
            acknowledgment_bound = parent_binding and inside(repo / receipt["evidence"], outputs).resolve() == (outputs / "ownership.json").resolve() and receipt_parent == parent_current == final_parent_readback and ack.get("parent_after") == parent_current and receipt.get("owner") == parent_current.get("owner")
        except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError):
            acknowledgment_bound = False
        if ack and not acknowledgment_bound:
            checks["parent_transfer"]["passed"] = False
        result["candidate_only"]["candidate_acknowledgment"] = {"passed": bool(ack and chronological and acknowledgment_bound and parent_records and parent_records[0]["line"] < ack["line"] and state_at(ack,"B","after").get("transfer_completed") is True and receipt.get("owner") == "agent-new" and receipt.get("recorded_at") == 205), "evidence": "real acknowledgment receipt resolves to the same current parent target and final native readback"}
    passed = all(c["passed"] for c in checks.values()) and all(c["passed"] for c in result["candidate_only"].values()) and chronological and not denied and run_record.get("exit_code") == 0
    result.update({"assertions": checks, "behavior_status": "pass" if passed else "fail", "output_contract_status": "pass" if schema_ok else "fail", "comparison_eligible": not denied and run_record.get("exit_code") == 0, "execution_status": "permission_failure" if denied else ("success" if run_record.get("exit_code") == 0 else "failure")})
    if not qualified:
        result.update({"setup_status": "invalid", "behavior_status": "not_evaluated", "comparison_eligible": False, "assertions_are_diagnostic": True})
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
