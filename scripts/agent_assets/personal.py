"""Personal native paths and immutable legacy registration rendering."""

from copy import deepcopy
from pathlib import Path

from . import configuration
from .sources import AssetError, canonical, digest
from .hook_rendering import RUNTIME_ROOTS, SOURCE_ROOTS


CONFIGS = {"codex": ".codex/hooks.json", "copilot": ".copilot/hooks/hooks.json", "gemini": ".gemini/settings.json"}
TEMPLATES = {"codex": ".codex/global-hooks.json", "copilot": ".copilot/hooks/hooks.json", "gemini": ".gemini/global-settings.json"}


def render(files, snapshot, assets, clients, *, codex_home=None):
    result, inputs = {}, []
    for path, value in files.items():
        if path in configuration.PATHS.values() or any(path.startswith(prefix) for prefix in RUNTIME_ROOTS.values()):
            continue
        if path.startswith(".github/agents/"):
            path = path.replace(".github/agents/", ".copilot/agents/", 1).removesuffix(".agent.md") + ".md"
        if codex_home and path.startswith(".codex/agents/"):
            path = (Path(codex_home) / "agents" / Path(path).name).as_posix()
        result[path] = value
    hooks = sorted(asset for asset in assets if asset.startswith("hook:"))
    if not hooks:
        return result, inputs
    for provider in clients:
        selected = set()
        for asset in hooks:
            name = asset.split(":")[1]
            selected.add("skill-context-injector.py" if name == "required-skills" and provider == "gemini" else "load-required-skills.py" if name == "required-skills" else name + ".py")
        for path, value in files.items():
            if path.startswith(RUNTIME_ROOTS[provider]) and not path.endswith(("/runtime.json", "/repository-launcher.py")):
                result[SOURCE_ROOTS[provider] + path.removeprefix(RUNTIME_ROOTS[provider])] = value
        template = TEMPLATES[provider]
        raw, executable = snapshot.read(template)
        inputs.append({"path": template, "type": "file", "executable": executable, "digest": digest(raw)})
        value = configuration.parse(raw)
        events = {}
        for event, entries in value.get("hooks", {}).items():
            for entry in entries:
                handlers = [entry] if provider == "copilot" else entry.get("hooks", [])
                kept = [deepcopy(handler) for handler in handlers if any(
                    name in command for name in selected for command in configuration.commands(handler))]
                if kept:
                    events.setdefault(event, []).extend(kept if provider == "copilot" else [{**deepcopy(entry), "hooks": kept}])
        if not events:
            raise AssetError("ASSET_RENDERER_UNAVAILABLE", "Personal template lacks selected hook registrations.", 1)
        config = {"hooks": events}
        if provider == "copilot":
            config["version"] = 1
        result[CONFIGS[provider]] = (canonical(config) + b"\n", 0o600, hooks,
                                    {"content": "text", "line_endings": "lf", "configuration": config})
    return result, inputs
