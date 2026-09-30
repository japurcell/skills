"""Native registrations and trusted read-only verification of generated hooks."""

import importlib
import sys
from pathlib import Path

from .sources import AssetError, canonical, digest
from .configuration import PATHS

COMMAND_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOTS = {"codex": ".codex/hooks/", "copilot": ".copilot/hooks/scripts/", "gemini": ".gemini/hooks/scripts/"}
RUNTIME_ROOTS = {"codex": ".codex/hooks/agent-assets/", "copilot": ".github/hooks/agent-assets/", "gemini": ".gemini/hooks/agent-assets/"}
SUPPORTED = {"hook:required-skills", "hook:tool-guard", "hook:scan-secrets"}


def verify_generated(snapshot, selected_paths, *, freshness=True):
    # Acquired Python is only compared as bytes, never imported or executed.
    if str(COMMAND_ROOT) not in sys.path:
        sys.path.insert(0, str(COMMAND_ROOT))
    from hooks.manifest import targets
    from hooks.providers import PROVIDERS
    selected = [target for target in targets() if str(target.output_path) in selected_paths]
    inputs = []
    compatibility = {"hooks/__init__.py", "hooks/families/__init__.py", "hooks/manifest.py", "hooks/providers.py", "scripts/generate-hooks.py"}
    compatibility.update("hooks/families/" + target.family + ".py" for target in selected)
    if any(target.family in {"tool_guard", "scan_secrets"} for target in selected):
        compatibility.add("hooks/families/allowlist.py")
    for path in sorted(compatibility):
        data, executable = snapshot.read(path)
        if freshness and data != (COMMAND_ROOT / path).read_bytes():
            raise AssetError("ASSET_RENDERER_UNAVAILABLE", "Unsupported hook generation inputs at " + path + "; use a compatible command checkout. Acquired generator code is never executed.", 1)
        inputs.append({"path": path, "type": "file", "executable": executable, "digest": digest(data)})
    for target in selected:
        if not freshness:
            continue
        family = importlib.import_module("hooks.families." + target.family)
        expected = family.render(PROVIDERS[target.provider], target).encode("utf-8")
        actual, executable = snapshot.read(str(target.output_path))
        if actual != expected or not executable:
            raise AssetError("ASSET_SOURCE_STALE", "Stale generated hook: " + str(target.output_path) + "; run python3 scripts/generate-hooks.py --write in a compatible source checkout and commit it.", 1)
    if set(selected_paths) - {str(target.output_path) for target in selected}:
        raise AssetError("ASSET_RENDERER_UNAVAILABLE", "Hook source is unsupported by this command checkout's generated manifest.", 1)
    return inputs


def registration(provider, hook):
    root = RUNTIME_ROOTS[provider]
    posix = 'python3 -B "$(git rev-parse --show-toplevel)/' + root + 'repository-launcher.py" ' + hook
    # This fixed Python bootstrap avoids interpolating any target path into shell
    # source. It works with Gemini's single command field and Windows cmd.exe.
    bootstrap = ("import subprocess,sys;from pathlib import Path;"
                 "root=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],text=True).strip());"
                 "sys.exit(subprocess.call([sys.executable,'-B',str(root/'" + root + "repository-launcher.py'),'" + hook + "']))")
    portable = 'python -B -c "' + bootstrap + '"'
    if provider == "copilot":
        entry = {"type": "command", "bash": posix, "powershell": portable, "timeoutSec": 30}
        event = "sessionStart" if hook == "required-skills" else "agentStop" if hook == "scan-secrets-end" else "preToolUse"
        return {event: [entry]}
    entry = {"type": "command", "command": posix, "timeout": 30 if provider == "codex" else 30000}
    if provider == "codex":
        entry["commandWindows"] = portable.replace("python -B", "py -3 -B", 1)
        if hook == "required-skills":
            entry["additionalContextLimit"] = 8000
        event = "SessionStart" if hook == "required-skills" else "Stop" if hook == "scan-secrets-end" else "PreToolUse"
        group = {"hooks": [entry]}
        if event != "Stop":
            group["matcher"] = "startup|resume|clear|compact" if hook == "required-skills" else "Bash|apply_patch|Edit|Write"
        return {event: [group]}
    entry["command"] = portable
    entry["name"] = "agent-assets-" + hook
    event = "SessionStart" if hook == "required-skills" else "SessionEnd" if hook == "scan-secrets-end" else "BeforeTool"
    group = {"hooks": [entry]}
    if event == "BeforeTool":
        group["matcher"] = "*"
    return {event: [group]}


def render_hooks(snapshot, catalog, assets, clients, installation_id, *, freshness=True):
    hooks = [asset for asset in assets if asset.startswith("hook:")]
    if not hooks:
        return {}, []
    selected_paths = {spec["path"] for asset in hooks for spec in catalog["assets"][asset]["source_paths"]}
    inputs = verify_generated(snapshot, selected_paths, freshness=freshness)
    files = {}
    for provider in clients:
        owners, events = [], {}
        for asset_id in hooks:
            if asset_id not in SUPPORTED:
                raise AssetError("ASSET_RENDERER_UNAVAILABLE", "Unsupported maintained hook: " + asset_id, 1)
            owners.append(asset_id)
            declared = {spec["path"] for spec in catalog["assets"][asset_id]["source_paths"]}
            handler = "skill-context-injector.py" if provider == "gemini" and asset_id == "hook:required-skills" else "load-required-skills.py" if asset_id == "hook:required-skills" else asset_id.split(":")[1] + ".py"
            required = {SOURCE_ROOTS[provider] + name for name in (handler, "helpers/common.py", "helpers/audit.py", "helpers/runtime_config.py", "repository-launcher.py")}
            if provider in {"copilot", "gemini"}:
                required.add(SOURCE_ROOTS[provider] + "helpers/observability.py")
            if not required.issubset(declared):
                raise AssetError("ASSET_RENDERER_UNAVAILABLE", "Hook lacks required runtime dependencies: " + asset_id, 1)
            for spec in catalog["assets"][asset_id]["source_paths"]:
                if not spec["path"].startswith(SOURCE_ROOTS[provider]):
                    continue
                destination = RUNTIME_ROOTS[provider] + spec["path"].removeprefix(SOURCE_ROOTS[provider])
                data, executable = snapshot.read(spec["path"])
                previous = files.get(destination)
                if previous and (previous[0], previous[1], previous[3]) != (data, 0o755 if executable else 0o644, spec):
                    raise AssetError("ASSET_CATALOG_INVALID", "Conflicting declared hook output: " + destination)
                files[destination] = (data, 0o755 if executable else 0o644, sorted(set([asset_id, *(previous[2] if previous else [])])), spec)
            for event, entries in registration(provider, asset_id.split(":")[1]).items():
                events.setdefault(event, []).extend(entries)
            if asset_id == "hook:scan-secrets":
                for event, entries in registration(provider, "scan-secrets-end").items():
                    events.setdefault(event, []).extend(entries)
        runtime = {"schema_version": 1, "provider": provider, "installation_id": installation_id,
                   "skills": "../../../.agents/skills", "references": "../../../.agents/references",
                   "required_skill_files": [dependency.split(":")[1] + "/SKILL.md" for dependency in catalog["assets"].get("hook:required-skills", {}).get("requires", []) if dependency.startswith("skill:")] if "hook:required-skills" in hooks else []}
        spec = {"content": "text", "line_endings": "lf"}
        files[RUNTIME_ROOTS[provider] + "runtime.json"] = (canonical(runtime) + b"\n", 0o644, sorted(owners), spec)
        config = {"hooks": events}
        if provider == "copilot":
            config["version"] = 1
        files[PATHS[provider]] = (canonical(config) + b"\n", 0o644, sorted(owners), {**spec, "configuration": config})
    return files, inputs
