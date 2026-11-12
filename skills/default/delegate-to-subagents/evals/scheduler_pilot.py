#!/usr/bin/env python3
"""Prepare, execute and grade the bounded scheduler diagnostic pilot (stdlib only)."""
import argparse
import json
import hashlib
import math
import re
import datetime
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
from urllib.parse import urlsplit, unquote


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
    keys = ("HOME", "PATH", "CODEX_HOME", "COPILOT_HOME", "COPILOT_ALLOW_ALL", "COPILOT_ASSISTED_APPROVAL", "AUTO_APPROVAL")
    return {"nonsecret_environment_hashes": {
        key: hashlib.sha256(os.environ[key].encode()).hexdigest()
        for key in keys if key in os.environ}}


def native_auth(settings):
    return settings.get("authentication", {}).get("mode", "process-token") == "native-existing-login"


def copilot_controls(cell):
    settings = cell["requested_settings"]
    return ["--no-auto-update", "--disable-builtin-mcps", "--no-custom-instructions", "--available-tools", "bash", "apply_patch", "--model", settings["model"], "--reasoning-effort", settings["effort"], "--disallow-temp-dir", "--sync-session=off"]


def copilot_status(cell):
    """Bounded no-session Content-Length RPC, retaining status/catalog fields only."""
    argv = [cell["requested_settings"]["executable"], "--headless", "--stdio", "--log-level", "none", *copilot_controls(cell)]
    child = subprocess.Popen(argv, cwd=cell["repo"], env=cell["environment"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, start_new_session=True)
    selector = selectors.DefaultSelector()
    selector.register(child.stdout, selectors.EVENT_READ)
    pending, received, results = b"", 0, []
    deadline = time.monotonic() + 10
    requests = [{"jsonrpc": "2.0", "id": i, "method": method, "params": {}} for i, method in enumerate(("status.get", "auth.getStatus", "models.list"), 1)]
    try:
        for request in requests:
            payload = json.dumps(request).encode()
            child.stdin.write(("Content-Length: " + str(len(payload)) + "\r\n\r\n").encode() + payload)
            child.stdin.flush()
            while time.monotonic() < deadline:
                if b"\r\n\r\n" in pending:
                    header, body = pending.split(b"\r\n\r\n", 1)
                    if not header.startswith(b"Content-Length: ") or b"\r\n" in header:
                        raise ValueError("unsupported Copilot RPC framing")
                    length = header.removeprefix(b"Content-Length: ")
                    if not length.isdigit():
                        raise ValueError("invalid Copilot RPC length")
                    size = int(length)
                    if not 0 < size <= 1048576:
                        raise ValueError("Copilot RPC size bound")
                    if len(body) >= size:
                        row = json.loads(body[:size]); pending = body[size:]
                        if not isinstance(row, dict) or type(row.get("id")) is not int or row.get("id") != request["id"] or "error" in row or "method" in row or row.get("jsonrpc", "2.0") != "2.0" or not isinstance(row.get("result"), dict):
                            raise ValueError("unexpected Copilot RPC reply")
                        results.append(row["result"])
                        break
                if not selector.select(max(0, deadline - time.monotonic())):
                    raise ValueError("Copilot status timeout")
                chunk = os.read(child.stdout.fileno(), 65536)
                if not chunk:
                    raise ValueError("Copilot status EOF")
                received += len(chunk); pending += chunk
                if received > 1048576:
                    raise ValueError("Copilot RPC size bound")
            else:
                raise ValueError("Copilot status timeout")
        if pending or (selector.select(0) and os.read(child.stdout.fileno(), 65536)):
            raise ValueError("unexpected trailing Copilot RPC bytes")
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
    status, auth, catalog = results
    if status.get("version") != "1.0.109" or status.get("protocolVersion") != 3:
        raise ValueError("unsupported Copilot native status version/protocol")
    if auth.get("isAuthenticated") is not True or auth.get("authType") != "user":
        raise ValueError("native-existing-login unavailable in invoking environment")
    settings = cell["requested_settings"]
    matches = [row for row in catalog.get("models", []) if isinstance(row, dict) and row.get("id") == settings["model"]]
    if len(matches) != 1 or not isinstance(matches[0].get("supportedReasoningEfforts"), list) or settings["effort"] not in matches[0]["supportedReasoningEfforts"]:
        raise ValueError("native catalog lacks exact model/effort")
    return {"argv": argv, "requests": requests, "version": status["version"], "protocolVersion": 3, "isAuthenticated": True, "authType": "user", "login_present": bool(auth.get("login")), "host_present": bool(auth.get("host")), "catalog": {"id": settings["model"], "effort_supported": settings["effort"]}}


def config_check(config):
    if not isinstance(config, dict) or not isinstance(config.get("providers"), dict):
        raise ValueError("config/providers must be objects")
    if set(config) != {"providers", "timeout_seconds"}:
        raise ValueError("config requires only providers and timeout_seconds")
    if set(config["providers"]) != {"codex", "copilot"}:
        raise ValueError("both providers are required")
    if type(config["timeout_seconds"]) not in (int, float) or not 0 < config["timeout_seconds"] <= 600:
        raise ValueError("timeout_seconds must be in (0, 600]")
    for provider, settings in config["providers"].items():
        if not isinstance(settings, dict):
            raise ValueError("provider settings must be an object")
        if set(settings) - {"executable", "model", "effort", "authentication"} or not {"executable", "model", "effort"} <= set(settings):
            raise ValueError("provider settings require executable, model, effort; arbitrary flags prohibited")
        if "authentication" in settings and settings["authentication"] not in (({"mode": "private"}, {"mode": "native-existing-login"}) if provider == "codex" else ({"mode": "process-token"}, {"mode": "native-existing-login"})):
            raise ValueError("invalid " + provider + " authentication mode")
        for key in ("executable", "model", "effort"):
            value = settings[key]
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
                helper_path = snapshot / "receipt-adapters" / provider / "invoke-scheduler"
                helper_path.parent.mkdir(parents=True)
                helper_source = Path(__file__).with_name("invoke_scheduler.py").read_text()
                interpreter = str(Path(shutil.which("python3", path=os.environ.get("PATH", os.defpath))).resolve())
                helper_path.write_text("#!" + interpreter + "\n" + helper_source.split("\n", 1)[1])
                helper_path.chmod(0o500)
                write(helper_path.with_name("invocation.json"), {"repo": str(repo), "scheduler": str(script), "timeout_seconds": min(10, config["timeout_seconds"])})
                cell = {"provider": provider, "variant": variant, "repo": str(repo),
                        "snapshot": str(snapshot), "requested_settings": config["providers"][provider], "environment": {"HOME": str(private_home), "CODEX_HOME": str(private_home / ".codex"), "PATH": os.environ.get("PATH", os.defpath), "COPILOT_HOME": str(private_home / "copilot"), "COPILOT_CACHE_HOME": str(private_home / "cache"), "COPILOT_PLUGIN_DIR_ONLY": "true", "COPILOT_AUTO_UPDATE": "false", "COPILOT_DISABLE_LOGIN_SHELL_ENV": "1", "TMPDIR": str(cell_root / "tmp")}, "prompts": {}, "session_ids": {phase: str(uuid.uuid4()) for phase in (("smoke", "scenario") if variant == "baseline" else ("scenario",))},
                        "write_roots": [str(repo), str(cell_root / "tmp")],
                        "command_prefix": ["python3", str(script)], "helper_prefix": [str(helper_path)], "io_command": [str(helper_path), "smoke-write"]}
                executable = Path(config["providers"][provider]["executable"]).resolve()
                python = Path(shutil.which("python3", path=cell["environment"]["PATH"])).resolve()
                cell["executable_identity"] = {"path": str(executable), "sha256": digest(executable)}
                cell["python_identity"] = {"path": str(python), "sha256": digest(python)}
                cell["safe_config"] = {"model": config["providers"][provider]["model"], "model_reasoning_effort": config["providers"][provider]["effort"], "sandbox_mode": "workspace-write", "approval_policy": "never", "sandbox_workspace_write": {"writable_roots": cell["write_roots"], "network_access": False, "exclude_tmpdir_env_var": True, "exclude_slash_tmp": True}}
                cell["tool_restrictions"] = {"enumeration": "unavailable", "qualification": "requires observed native phase evidence"}
                cell["authentication"] = {"mode": "process-token", "source": "supported process token names"}
                if provider == "copilot" and native_auth(cell["requested_settings"]):
                    if os.environ.get("BASH_ENV") or any(os.environ.get(key) for key in ("COPILOT_ALLOW_ALL", "COPILOT_ASSISTED_APPROVAL", "AUTO_APPROVAL", "COPILOT_PROVIDER_BASE_URL", "COPILOT_PROVIDERS_CONFIG")):
                        raise ValueError("unsafe inherited Copilot behavior environment")
                    cell["environment"].update({"HOME": str(Path.home().resolve()), "COPILOT_HOME": str(Path(os.environ.get("COPILOT_HOME", str(Path.home() / ".copilot"))).resolve())})
                    cell["environment"].pop("CODEX_HOME", None)
                    cell["environment"].pop("COPILOT_CACHE_HOME", None)
                    cell["authentication"] = {"mode": "native-existing-login", "HOME": cell["environment"]["HOME"], "COPILOT_HOME": cell["environment"]["COPILOT_HOME"], "source": "provider-owned existing native login; no credential copy"}
                    cell["copilot_repo_settings"] = {"disableAllHooks": True, "enabledPlugins": {}, "defaultPermissionMode": "manual", "memory": False, "ide": {"autoConnect": False}}
                    override = repo / ".github/copilot/settings.json"
                    override.parent.mkdir(parents=True)
                    write(override, cell["copilot_repo_settings"])
                if provider == "codex" and native_auth(cell["requested_settings"]):
                    codex_native_prepare(cell)
                for phase in (("smoke", "scenario") if variant == "baseline" else ("scenario",)):
                    output = repo / "outputs" / ("smoke.json" if phase == "smoke" else "result.json")
                    prompt = "Selected SKILL.md body follows verbatim. Apply it.\n<selected_skill>\n" + (snapshot / "SKILL.md").read_text() + "\n</selected_skill>\n"
                    if provider == "codex":
                        prompt += "All shell tool calls require login=false and tty=false.\n"
                    prefix = shlex.join(cell["helper_prefix"])
                    state = repo / "outputs" / ("smoke-state.json" if phase == "smoke" else "scenario-state.json")
                    prompt += "The frozen helper is directly executable. Invoke it exactly as printed, without prepending Python or another interpreter. Run each helper invocation in its own shell tool call; do not combine it with another command or a script wrapper. Execute every scheduler command through " + prefix + " --state " + str(state) + " COMMAND [ARGS]. This immutable helper invokes " + str(script) + " and retains native child receipts. Use " + prefix + " parent-update PREVIOUS_OWNER NEW_OWNER TIME for a neutral parent record write/readback. Write only under " + str(repo) + ".\n"
                    if phase == "smoke":
                        prompt += "Neutral smoke only: execute " + prefix + " --state " + str(repo / "outputs/smoke-state.json") + " register smoke smoke-agent neutral --deadline 100 --checkpoint 300 --now 0. Then the same helper/state complete smoke --now 1. Execute " + prefix + " smoke-write to write and read back " + str(output) + ". No deadline or transfer behavior.\n"
                    else:
                        prompt += read(root / "rubric.json")["prompt"].replace("{repo}", str(repo)).replace("{scheduler}", str(script)).replace("{variant}", variant)
                    path = cell_root / (phase + "-prompt.md")
                    path.write_text(prompt)
                    cell["prompts"][phase] = str(path)
                manifest["cells"][cell_id] = cell
        immutable = [root / "config.json", root / "rubric.json", root / "provider-context.json"]
        immutable += list((root / "snapshots").rglob("*"))
        immutable += [Path(cell["repo"]).parent / name for cell in manifest["cells"].values() for name in ("provider-home/copilot/settings.json",)]
        immutable += [Path(cell["repo"]) / ".github/copilot/settings.json" for cell in manifest["cells"].values() if "copilot_repo_settings" in cell]
        immutable += [Path(path) for cell in manifest["cells"].values() for path in cell["prompts"].values()]
        for path in immutable:
            if path.is_file():
                manifest["hashes"][str(path.relative_to(root))] = digest(path)
                path.chmod(0o500 if path.name == "invoke-scheduler" else 0o400)
        for cell in manifest["cells"].values():
            cell["argv"] = {phase: argv_for(manifest, cell, phase) for phase in cell["prompts"]}
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
            if cell["provider"] == "codex" and native_auth(cell["requested_settings"]):
                auth = cell["authentication"]
                if auth["HOME"] != str(Path.home().resolve()) or auth["CODEX_HOME"] != str(Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).resolve()):
                    raise ValueError("native Codex authentication path drift")
                shell = inside(cell["shell_home"], root)
                if shell.is_symlink() or not shell.is_dir() or list(shell.iterdir()) or shell.stat().st_mode & 0o222:
                    raise ValueError("native Codex shell startup directory drift")
            private = Path(cell["environment"]["HOME"]) / ".codex"
            if cell["provider"] == "codex" and not native_auth(cell["requested_settings"]) and (cell["environment"].get("CODEX_HOME") != str(private) or not inside(private, root).is_dir()):
                raise ValueError("private CODEX_HOME required")
        if Path(cell["helper_prefix"][0]).stat().st_mode & 0o777 != 0o500:
            raise ValueError("helper executable mode drift")
        for location in (cell["repo"], cell["snapshot"], *cell["prompts"].values(), *cell["write_roots"]):
            inside(location, root)
        for output in ("smoke.json", "result.json"):
            inside(Path(cell["repo"]) / "outputs" / output, root)
    return manifest


def codex_config_args(cell):
    def toml(value):
        if isinstance(value, dict):
            return "{" + ",".join(json.dumps(k) + "=" + toml(v) for k, v in value.items()) + "}"
        if isinstance(value, list):
            return "[" + ",".join(toml(v) for v in value) + "]"
        return json.dumps(value)
    return [part for key, value in cell["safe_config"].items()
            for part in ("-c", key + "=" + toml(value))]


def codex_native_prepare(cell):
    home = str(Path.home().resolve())
    codex_home = str(Path(os.environ.get("CODEX_HOME", str(Path(home) / ".codex"))).resolve())
    cell["environment"].update(HOME=home, CODEX_HOME=codex_home)
    cell["authentication"] = {"mode": "native-existing-login", "HOME": home, "CODEX_HOME": codex_home, "source": "provider-owned existing native login"}
    shell = Path(cell["repo"]).parent / "control/shell-home"
    shell.mkdir(parents=True, mode=0o500)
    shell.chmod(0o500)
    cell["shell_home"] = str(shell)
    settings = cell["requested_settings"]
    if (settings["model"], settings["effort"]) != ("gpt-6.1-sol", "medium"):
        raise ValueError("native Codex requires exact Sol/medium selector")
    code, stdout, stderr = capture([settings["executable"], "--version"], 3, cwd=cell["repo"], env=cell["environment"])
    if code or stdout.strip() != "codex-cli 0.167.1":
        raise ValueError("unsupported native Codex version")
    cell["native_version"] = stdout.strip()
    cell["safe_config"].update({"model_provider": "openai", "instructions": "", "developer_instructions": "", "project_doc_max_bytes": 0, "web_search": "disabled", "notify": [], "allow_login_shell": False, "skills": {"bundled": {"enabled": False}, "include_instructions": False}, "features": {key: False for key in ("hooks", "apps", "plugins", "memories", "multi_agent", "browser_use", "computer_use")}, "shell_environment_policy": {"inherit": "none", "set": {"PATH": str(Path(cell["python_identity"]["path"]).parent) + ":/usr/bin:/bin", "HOME": str(shell), "ZDOTDIR": str(shell)}}})


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
                code, stdout, stderr = capture([settings["executable"], "login", "status"], 3, cwd=cell["repo"], env=cell["environment"])
                authenticated = code == 0 and (stdout + stderr).strip() in ("Logged in using ChatGPT", "Logged in using an API key")
                discovery[cell_id] = {"authentication": {"present": authenticated}}
                if not authenticated:
                    blockers.append(cell_id + ":authentication-unavailable")
            except (OSError, ValueError, KeyError, TypeError) as error:
                blockers.append(cell_id + ":authentication-invalid:" + str(error))
    elif native_auth(settings):
        for cell_id, cell in cells.items():
            try:
                discovery[cell_id] = copilot_status(cell)
            except (OSError, ValueError, KeyError, TypeError) as error:
                blockers.append(cell_id + ":native-existing-login-preflight:" + str(error))
    elif not any(os.environ.get(key) for key in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")):
        blockers.append("copilot-isolated-home-auth-token-unavailable")
    if provider == "copilot" and native_auth(settings) and not all(flag in probes[1]["stdout"] for flag in ("--available-tools", "--sync-session", "--trust-folder")):
        blockers.append("native-Copilot-required-controls-missing")
    receipt = {"schema_version": 1, "provider": provider, "manifest_sha256": digest(root / "manifest.json"), "cells": discovery, "model_resolution": {"requested": settings["model"], "effort": settings["effort"], "observed": None, "status": "pending observed phase"}, "probes": probes, "valid": not blockers, "syntax_supported": syntax, "setup_ready": not blockers, "smoke_ready": not blockers, "scenario_ready": not blockers, "prerequisites": blockers, "executable_sha256": digest(settings["executable"])}
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
                 "--skip-git-repo-check", "--model", settings["model"], "--sandbox", "workspace-write",
                 *codex_config_args(cell),
                 "--output-last-message", str(evidence / "response.md"), "-"]
    else:
        argv += ["--model", settings["model"], "--reasoning-effort", settings["effort"],
                 "--new-session-id" if native_auth(settings) else "--session-id", cell["session_ids"][phase], "--add-dir", cell["repo"], "--add-dir", cell["snapshot"],
                 "--disallow-temp-dir", "--disable-builtin-mcps", "--no-bash-env", "--secret-env-vars=COPILOT_GITHUB_TOKEN,GH_TOKEN,GITHUB_TOKEN", "--allow-tool=write(" + cell["repo"] + "/**)",
                 "--allow-tool=shell(" + shlex.join(cell["helper_prefix"]) + ":*)", "--no-custom-instructions", "--output-format", "json",
                 "--share", str(evidence / "transcript.md"), "--usage-output-file", str(evidence / "usage.json"),
                 "--log-dir", str(evidence / "logs"), "--no-auto-update", "--prompt", prompt]
    if cell["provider"] == "copilot" and native_auth(settings):
        argv.remove("--no-bash-env")
        argv += ["--available-tools", "bash", "apply_patch", "--sync-session=off", "--trust-folder"]
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
            if kind in ("session.start", "tool.execution_start", "tool.execution_complete") and not isinstance(data, dict):
                raise ValueError("required event data object missing")
            normalized.append({"line": number, "event": row})
            if provider == "copilot" and kind == "session.start":
                if session is not None:
                    errors.append("duplicate-session")
                if data.get("alreadyInUse") is True:
                    errors.append("session-already-in-use")
                session, model, effort = data.get("sessionId"), data.get("selectedModel"), data.get("reasoningEffort")
                session_cwd = data.get("context", {}).get("cwd")
                if not isinstance(session, str) or not session:
                    errors.append("session-identity-missing")
                continue
            if provider == "codex" and kind == "thread.started":
                if session is not None or not isinstance(row.get("thread_id"), str) or not row["thread_id"]:
                    errors.append("duplicate-or-missing-thread")
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
                native_exit = None
                if start.get("toolName") == "bash":
                    execution = data.get("shellExecution", {})
                    if isinstance(execution, dict) and "exitCode" in execution:
                        if type(execution["exitCode"]) is int:
                            native_exit = execution["exitCode"]
                        else:
                            errors.append("native-shell-exit-mismatch")
                    footer = re.search(r"(?:^|\n)<shellId: ([^\s>]+) completed with exit code (-?[0-9]+)>\s*$", result.get("content", ""))
                    shell = result.get("structuredContent", {})
                    if footer:
                        if not isinstance(shell, dict) or shell.get("shellId") != footer[1] or (native_exit is not None and native_exit != int(footer[2])):
                            errors.append("native-shell-exit-mismatch")
                            native_exit = None
                        else:
                            native_exit = int(footer[2])
                calls.append({"id": key, "tool_type": start.get("toolName"), "turn_id": start.get("turnId"), "command": arguments.get("command", "") if isinstance(arguments, dict) else "", "patch": arguments if isinstance(arguments, str) else None, "file_edits": data.get("fileEdits"), "success": data.get("success"), "native_exit_code": native_exit, "exit_code_source": "native-shell-completion" if start.get("toolName") == "bash" else "native-tool-success", "exit_code": native_exit if start.get("toolName") == "bash" else (0 if data.get("success") is True else 1), "output": result.get("content", ""), "start_line": start_line, "line": number})
                continue
            if provider == "codex" and kind in ("item.started", "item.completed"):
                item = row.get("item", {})
                key = item.get("id")
                if kind == "item.started" and item.get("type") in ("command_execution", "file_change") and starts:
                    errors.append("overlapping-native-items")
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
                elif item.get("type") == "file_change":
                    if kind == "item.started":
                        if not isinstance(key, str) or not key or key in seen or item.get("status") != "in_progress":
                            errors.append("duplicate-or-invalid-file-change-start")
                        starts[key] = (item, number)
                        seen.add(key)
                    else:
                        start, start_line = starts.pop(key, ({}, None))
                        if not start or start.get("type") != "file_change" or start.get("changes") != item.get("changes") or item.get("status") != "completed":
                            errors.append("unmatched-or-failed-file-change")
                        calls.append({"id": key, "tool_type": "apply_patch", "command": "", "exit_code": None, "output": "", "file_changes": item.get("changes"), "patch_status": item.get("status"), "start_line": start_line, "line": number})
                continue
            if kind == "turn.completed":
                usage = row.get("usage", data.get("usage") if isinstance(data, dict) else None)
            # Observational events do not establish execution evidence.
        except (ValueError, TypeError, AttributeError) as error:
            errors.append("malformed-native-line:" + str(number))
    if starts:
        errors.append("missing-tool-completion")
    return {"calls": calls, "usage": usage, "observed_model": model, "observed_effort": effort, "session_id": session, "session_cwd": session_cwd, "normalized": normalized, "invalid_reasons": errors}


def local_path(value):
    if not isinstance(value, str):
        raise ValueError("missing cwd")
    if value.startswith("file:"):
        uri = urlsplit(value)
        if uri.netloc not in ("", "localhost") or uri.query or uri.fragment:
            raise ValueError("nonlocal cwd URI")
        value = unquote(uri.path)
    path = Path(value)
    if not path.is_absolute():
        raise ValueError("cwd must be absolute")
    return str(path.resolve())


def codex_companion(cell, events, raw, started_at):
    """Use the exact session rollout only for session, selector and cwd identity."""
    rows = [json.loads(line) for line in raw.splitlines()]
    metadata = [row for row in rows if row.get("type") == "session_meta"]
    contexts = [row["payload"] for row in rows if row.get("type") == "turn_context"]
    if len(metadata) != 1 or not contexts:
        raise ValueError("missing fresh Codex session metadata or turn context")
    meta = metadata[0]["payload"]
    session = events.get("session_id")
    if not session or meta.get("id") != session or local_path(meta.get("cwd")) != cell["repo"] or meta.get("originator") != "codex_exec" or meta.get("model_provider") != "openai":
        raise ValueError("Codex session identity mismatch")
    instant = datetime.datetime.fromisoformat(metadata[0]["timestamp"].replace("Z", "+00:00"))
    if instant.tzinfo is None or not started_at - 2 <= instant.timestamp() <= time.time() + 2:
        raise ValueError("stale Codex session")
    model, effort = cell["requested_settings"]["model"], cell["requested_settings"]["effort"]
    if any(local_path(context.get("cwd")) != cell["repo"] or context.get("model") != model or context.get("effort") != effort for context in contexts):
        raise ValueError("Codex selector or cwd mismatch")
    return {"session_id": session, "model": model, "effort": effort, "cwd": cell["repo"], "rollout_sha256": hashlib.sha256(raw).hexdigest()}


def phase_events(manifest, cell_id, phase, collect=False):
    cell = manifest["cells"][cell_id]
    directory = Path(cell["repo"]).parent / "evidence" / phase
    events = native_events(cell["provider"], (directory / "stdout.jsonl").read_text())
    if cell["provider"] != "codex" or not native_auth(cell["requested_settings"]):
        return events
    attempt = read(directory / "attempt.json")
    path = directory / "codex-context.json"
    raw_path = directory / "codex-rollout.jsonl"
    if collect:
        session = events.get("session_id")
        if not isinstance(session, str) or not re.fullmatch(r"[A-Za-z0-9-]+", session):
            raise ValueError("invalid Codex session ID")
        provider_root = Path(cell["environment"]["CODEX_HOME"]) / "sessions"
        matches = list(provider_root.rglob("*" + session + ".jsonl"))
        if len(matches) != 1:
            raise ValueError("exact Codex session rollout unavailable")
        source = matches[0]
        if source.is_symlink() or source.resolve() != source or not source.is_file() or source.stat().st_nlink != 1 or source.stat().st_size > 8388608:
            raise ValueError("unsafe Codex rollout file")
        raw_path.write_bytes(source.read_bytes())
    raw = raw_path.read_bytes()
    if not raw or not raw.endswith(b"\n") or len(raw) > 8388608:
        raise ValueError("truncated or oversized Codex rollout")
    projection = codex_companion(cell, events, raw, attempt["started_at"])
    for sibling in manifest["cells"].values():
        for other_phase in sibling["prompts"]:
            other = Path(sibling["repo"]).parent / "evidence" / other_phase / "run.json"
            if sibling["provider"] == "codex" and other.exists() and other != directory / "run.json" and read(other).get("session_id") == events["session_id"]:
                raise ValueError("Codex session replay across phases")
    if collect:
        write(path, projection)
    elif read(path) != projection:
        raise ValueError("Codex context evidence drift")
    events.update(observed_model=projection["model"], observed_effort=projection["effort"], session_cwd=projection["cwd"])
    for call in events["calls"]:
        call["raw_command"] = call["command"]
        call["command"] = shlex.join(command_argv(call["command"]))
    return events


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


def helper_arguments(cell, command):
    """Recognize the frozen executable and the observed pinned Codex Python form."""
    argv = command_argv(command)
    helper = cell["helper_prefix"][0]
    if argv[:1] == [helper]:
        return argv[1:]
    if cell["provider"] != "codex" or len(argv) < 2 or argv[1] != helper:
        return None
    python = cell["python_identity"]
    if argv[0] not in ("python3", python["path"]):
        return None
    shell_path = cell["safe_config"].get("shell_environment_policy", {}).get("set", {}).get("PATH")
    resolved = shutil.which("python3", path=shell_path) if shell_path else None
    if not resolved or str(Path(resolved).resolve()) != python["path"] or digest(resolved) != python["sha256"]:
        return None
    return argv[2:]


def receipt_claims(output):
    for candidate in output.splitlines():
        try:
            claim = json.loads(candidate)
        except ValueError:
            continue
        if isinstance(claim, dict) and "pilot_child" in claim:
            yield claim["pilot_child"]


def helper_inspection(cell, arguments, call):
    claims = list(receipt_claims(str(call["output"])))
    if arguments == ["--help"]:
        return call["exit_code"] == 0 and not claims
    if not arguments or arguments[:1] != ["--state"] or len(arguments) < 3:
        return False
    states = [str(Path(cell["repo"]) / "outputs" / name) for name in ("smoke-state.json", "scenario-state.json")]
    if arguments[1] not in states:
        return False
    if arguments[2:] == ["--help"]:
        return call["exit_code"] == 2 and not claims
    if arguments[2:] != ["register", "--help"] or call["exit_code"] != 0 or len(claims) != 1:
        return False
    receipt = claims[0]
    return (isinstance(receipt, dict) and receipt.get("kind") == "scheduler"
            and receipt.get("argv") == cell["command_prefix"] + arguments
            and receipt.get("exit_code") == 0 and receipt.get("before") == receipt.get("after")
            and receipt.get("parent_before") == receipt.get("parent_after")
            and receipt.get("stderr") == "" and str(receipt.get("stdout", "")).startswith("usage:"))


def helper_records(cell, events):
    records = []
    for call in events["calls"]:
        arguments = helper_arguments(cell, call["command"])
        if arguments is None or helper_inspection(cell, arguments, call):
            continue
        text = call["output"]
        if not isinstance(text, str):
            continue
        for receipt in receipt_claims(text):
            try:
                if not isinstance(receipt, dict):
                    continue
                if receipt.get("kind") == "scheduler":
                    if receipt.get("argv") != cell["command_prefix"] + arguments or type(receipt.get("exit_code")) is not int:
                        continue
                    if call["exit_code"] != receipt["exit_code"]:
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
                receipt = dict(receipt, command=call["command"], helper_args=arguments, line=call["line"])
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
    return {"selector_observation": (events.get("observed_model") == cell["requested_settings"]["model"] and events.get("observed_effort") == cell["requested_settings"]["effort"]), "exact_output": content_ok, "register": registered and linked, "complete": completed and linked,
            "write_readback": linked and any(r.get("kind") == "smoke-write" and r.get("helper_args") == ["smoke-write"] and r.get("readback") == {"smoke": True} and r.get("path") == str(output) for r in records)}


def json_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def atomic_receipt(path, value):
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("x") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")
    os.replace(temporary, path)


def phase_bindings(manifest, cell_id, phase):
    cell = manifest["cells"][cell_id]
    root = Path(manifest["root"])
    preflight_path = inside(root / ("preflight/" + cell["provider"] + ".json"), root)
    preflight_receipt = read(preflight_path)
    if preflight_receipt.get("provider") != cell["provider"] or preflight_receipt.get("manifest_sha256") != digest(root / "manifest.json") or not preflight_receipt.get("setup_ready"):
        raise ValueError("valid bound provider preflight required")
    snapshot = Path(cell["snapshot"])
    return {"schema_version": 1, "authentication": cell["authentication"], "provider": cell["provider"], "cell": cell_id, "variant": cell["variant"], "phase": phase,
            "root": manifest["root"], "cwd": cell["repo"], "manifest_sha256": digest(root / "manifest.json"),
            "approved_payload_sha256": json_digest({"manifest_sha256": digest(root / "manifest.json"), "preflight_sha256": digest(preflight_path)}), "caller_sources": manifest["caller_sources"],
            "selected_sources": {"skill": digest(snapshot / "SKILL.md"), "scheduler": digest(snapshot / "scripts/scheduler.py"), "helper": digest(cell["helper_prefix"][0])},
            "executable": cell["executable_identity"], "python": cell["python_identity"], "provider_version": preflight_receipt["probes"][0]["stdout"].strip(),
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
        if record.get("started_at") != attempt.get("started_at"):
            errors.append("attempt-time-drift")
        if not record.get("attempt_id") or record.get("attempt_id") != attempt.get("attempt_id"):
            errors.append("attempt-identity-mismatch")
        raw_path = inside(directory / "stdout.jsonl", root)
        stderr_path = inside(directory / "stderr.txt", root)
        if record.get("raw_stdout") != str(raw_path) or record.get("raw_stderr") != str(stderr_path) or record.get("native_events") != str(directory / "native-events.json"):
            errors.append("raw-evidence-reference-mismatch")
        if record.get("raw_stdout_sha256") != digest(raw_path) or record.get("raw_stderr_sha256") != digest(stderr_path):
            errors.append("raw-evidence-drift")
        events = phase_events(manifest, cell_id, phase)
        if cell["provider"] == "codex" and native_auth(cell["requested_settings"]) and record.get("codex_context_sha256") != digest(directory / "codex-context.json"):
            errors.append("Codex-context-receipt-drift")
        if record.get("native_events_sha256") != digest(inside(directory / "native-events.json", root)) or read(directory / "native-events.json") != events:
            errors.append("parsed-evidence-drift")
        errors.extend(events["invalid_reasons"])
        if cell["provider"] == "copilot" and bindings["provider_version"].splitlines()[0] != "GitHub Copilot CLI 1.0.109.":
            errors.append("native-parser-version-unsupported")
        if events.get("observed_model") != cell["requested_settings"]["model"] or events.get("observed_effort") != cell["requested_settings"]["effort"]:
            errors.append("observed-selector-missing-or-wrong")
        if cell["provider"] == "copilot" and events.get("session_id") != cell["session_ids"][phase]:
            errors.append("native-session-mismatch")
        if cell["provider"] == "copilot" and local_path(events.get("session_cwd")) != cell["repo"]:
            errors.append("native-cwd-mismatch")
        if record.get("observed_model") != events.get("observed_model") or record.get("observed_effort") != events.get("observed_effort"):
            errors.append("receipt-selector-mismatch")
        if type(record.get("exit_code")) is not int or record.get("exit_code") != 0:
            errors.append("provider-exit-failure")
        if record.get("session_id") != events.get("session_id"):
            errors.append("receipt-session-mismatch")
        receipt_commands = set()
        for call in events["calls"]:
            arguments = helper_arguments(cell, call["command"])
            if arguments is None:
                continue
            if helper_inspection(cell, arguments, call):
                continue
            receipts = helper_records(cell, {"calls": [call]})
            if len(receipts) != 1:
                errors.append("missing-real-child-receipt")
            elif call["exit_code"] != 0 and receipts[0].get("exit_code") != 2:
                errors.append("unexpected-native-tool-rejection")
            if call["command"] in receipt_commands:
                errors.append("duplicate-helper-execution")
            receipt_commands.add(call["command"])
            if "permission denied" in str(call["output"]).lower():
                errors.append("unexpected-permission-denial")
        if phase == "smoke":
            checks = smoke_check(cell, events)
            errors.extend("smoke:" + key for key, value in checks.items() if not value)
        else:
            try:
                outputs = Path(cell["repo"]) / "outputs"
                state_path = inside(outputs / "scenario-state.json", outputs)
                output = read(inside(outputs / "result.json", outputs))
                reference = Path(output["final_state"]["scheduler_state"])
                if reference.is_absolute() or ".." in reference.parts or inside(Path(cell["repo"]) / reference, outputs).resolve() != state_path.resolve():
                    raise ValueError("final state must reference canonical scheduler state")
                records = [r for r in helper_records(cell, events) if r.get("kind") == "scheduler"]
                if not records:
                    raise ValueError("missing required scheduler execution")
                previous = None
                for receipt in records:
                    if receipt["helper_args"][:2] != ["--state", str(state_path)] or receipt["before"] != previous:
                        raise ValueError("inconsistent canonical scheduler state chain")
                    previous = receipt["after"]
                if read(state_path) != previous:
                    raise ValueError("canonical state differs from final child readback")
            except (OSError, ValueError, KeyError, TypeError, AttributeError):
                errors.append("scenario-state-or-output-invalid")
    except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError) as error:
        errors.append("phase-evidence-unavailable:" + str(error))
    return {"valid": not errors, "invalid_reasons": sorted(set(errors)), "checks": checks, "events": events}


def run(manifest, cell_id, phase):
    cell = manifest["cells"][cell_id]
    bindings = phase_bindings(manifest, cell_id, phase)
    if cell["argv"][phase] != argv_for(manifest, cell, phase):
        raise ValueError("frozen argv drift")
    if cell["provider"] == "codex":
        if native_auth(cell["requested_settings"]):
            code, stdout, stderr = capture([cell["requested_settings"]["executable"], "login", "status"], 3, cwd=cell["repo"], env=cell["environment"])
            if code or (stdout + stderr).strip() not in ("Logged in using ChatGPT", "Logged in using an API key"):
                raise ValueError("native Codex authentication unavailable")
    if cell["provider"] == "copilot" and native_auth(cell["requested_settings"]):
        copilot_status(cell)
    auth = {key: os.environ[key] for key in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN") if os.environ.get(key)} if cell["provider"] == "copilot" and not native_auth(cell["requested_settings"]) else {}
    if cell["provider"] == "copilot" and not native_auth(cell["requested_settings"]) and not auth:
        raise ValueError("copilot-isolated-home-auth-token-unavailable")
    directory = Path(cell["repo"]).parent / "evidence" / phase
    directory.mkdir()  # Exclusive phase attempt, including failed/partial attempts.
    provider_lock = Path(manifest["root"]) / (cell["provider"] + "-phase-active")
    provider_descriptor = os.open(provider_lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    os.close(provider_descriptor)
    lock = directory.parent / "phase-active"
    descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    os.close(descriptor)
    record = {**bindings, "attempt_id": str(uuid.uuid4()), "started_at": time.time(), "auth_environment_names": sorted(auth), "authentication_source": cell["authentication"]["source"] if cell["provider"] == "copilot" or native_auth(cell["requested_settings"]) else "private-CODEX_HOME-status"}
    atomic_receipt(directory / "attempt.json", record)
    started = time.monotonic()
    config = read(manifest["config"])
    try:
        try:
            code, stdout, stderr = capture(bindings["argv"], config["timeout_seconds"], cwd=cell["repo"], env={**cell["environment"], **auth}, text_input=Path(cell["prompts"][phase]).read_text() if cell["provider"] == "codex" else None)
        except OSError as error:
            code, stdout, stderr = 2, "", str(error)
        provider_elapsed = time.monotonic() - started
        (directory / "stdout.jsonl").write_text(stdout)
        (directory / "stderr.txt").write_text(stderr)
        events = native_events(cell["provider"], stdout)
        if cell["provider"] == "codex" and native_auth(cell["requested_settings"]):
            try:
                events = phase_events(manifest, cell_id, phase, collect=True)
                record["codex_context_sha256"] = digest(directory / "codex-context.json")
            except (OSError, ValueError, KeyError, TypeError) as error:
                events["invalid_reasons"].append("Codex-context-invalid:" + str(error))
        write(directory / "native-events.json", events)
        try:
            provider_usage = read(directory / "usage.json")
        except (OSError, ValueError):
            provider_usage = events.get("usage")
        record["provider_usage"] = provider_usage
        if provider_usage is None:
            write(directory / "usage-missing.json", {"available": False, "reason": "native usage unavailable; no estimate"})
        record.update({"exit_code": code, "elapsed_seconds": time.monotonic() - started, "provider_execution_seconds": provider_elapsed, "evidence_collection_seconds": time.monotonic() - started - provider_elapsed, "session_id": events.get("session_id"), "turn_ids": sorted({call.get("turn_id") for call in events["calls"] if call.get("turn_id")}), "observed_model": events.get("observed_model"), "observed_effort": events.get("observed_effort"), "raw_stdout": str(directory / "stdout.jsonl"), "raw_stdout_sha256": digest(directory / "stdout.jsonl"), "raw_stderr": str(directory / "stderr.txt"), "raw_stderr_sha256": digest(directory / "stderr.txt"), "native_events": str(directory / "native-events.json"), "native_events_sha256": digest(directory / "native-events.json")})
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
        return phase_events(manifest, cell_id, phase)
    scenario_validation = validate_phase(manifest, cell_id, "scenario")
    qualified = scenario_validation["valid"]
    result["invalid_reasons"] = scenario_validation["invalid_reasons"]
    try:
        result["diagnostic_smoke_checks"] = smoke_check(manifest["cells"][cell["provider"] + "-baseline"], phase_events(manifest, cell["provider"] + "-baseline", "smoke"))
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
    result["provider_usage"] = run_record.get("provider_usage", events.get("usage"))
    result["usage_status"] = "available" if result["provider_usage"] is not None else "unavailable"
    if result["usage_status"] == "unavailable" and (directory / "scenario").exists():
        write(directory / "scenario/usage-missing.json", {"available": False, "reason": "native usage unavailable; no estimate"})
    denied = any("denied" in str(call["output"]).lower() or "permission" in str(call["output"]).lower() for call in events["calls"] if call["exit_code"] != 0)
    required_denial = "unexpected-permission-denial" in scenario_validation["invalid_reasons"]
    result["permission_denial_observed"] = denied
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
        used_actions = set()
        used_batch_members = set()
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
            if action["action"] == "request-checkpoints":
                args = record.get("helper_args", [])
                events = json.loads(record.get("stdout", "{}")).get("events", [])
                members = [event for event in events if event.get("assignment") == action["assignment"] and event.get("type") == "deadline_expired" and event.get("host_action") == "request status by the checkpoint deadline"]
                member = (record["command"], action["assignment"], "deadline_expired")
                if record.get("kind") != "scheduler" or record.get("exit_code") != 0 or args[2:] != ["tick", "--now", "100"] or action["at"] != 100 or len(members) != 1 or member in used_batch_members:
                    raise ValueError("unverified or duplicated batch action member")
                used_batch_members.add(member)
            else:
                if record["command"] in used_actions:
                    raise ValueError("duplicated action receipt")
                used_actions.add(record["command"])
            matched.append((action, record))
        state = artifact(final["scheduler_state"])
        canonical_state = outputs / "scenario-state.json"
        if inside(repo / final["scheduler_state"], outputs).resolve() != canonical_state.resolve() or state != artifact("outputs/scenario-state.json"):
            raise ValueError("scheduler state must bind canonical output")
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
    passed = all(c["passed"] for c in checks.values()) and all(c["passed"] for c in result["candidate_only"].values()) and chronological and run_record.get("exit_code") == 0
    result.update({"assertions": checks, "behavior_status": "pass" if passed else "fail", "output_contract_status": "pass" if schema_ok else "fail", "comparison_eligible": run_record.get("exit_code") == 0, "execution_status": "permission_failure" if required_denial else ("success" if run_record.get("exit_code") == 0 else "failure")})
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
