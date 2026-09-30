"""Repository skill discovery paths established by the distribution research."""

from pathlib import Path
import tomllib
from canonical_agents import InstallError, parse_agent_bytes, render_agent, validate_agent_collisions
from .sources import AssetError

# Official path evidence and precedence are recorded in
# docs/agent-asset-distribution/research/{codex-copilot,claude-gemini,portable-methods}/findings.md.
SKILL_ROOTS = {
    "codex": ".agents/skills", "copilot": ".agents/skills", "gemini": ".agents/skills",
    "claude": ".claude/skills", "cursor": ".agents/skills", "opencode": ".agents/skills",
}
CLIENTS = tuple(SKILL_ROOTS)
SKILLS_ONLY = {"claude", "cursor", "opencode"}


def skill_roots(clients):
    return sorted({SKILL_ROOTS[client] for client in clients})


def render_agents(snapshot, catalog, assets, clients):
    definitions, files = [], {}
    for asset_id in assets:
        if not asset_id.startswith("agent:"):
            continue
        asset = catalog["assets"][asset_id]
        if len(asset["source_paths"]) != 1:
            raise AssetError("ASSET_RENDERER_UNAVAILABLE", "Agent needs one canonical source: " + asset_id, 1)
        spec = asset["source_paths"][0]
        raw, executable = snapshot.read(spec["path"])
        try:
            agent = parse_agent_bytes(raw, Path(spec["path"]))
            definitions.append(agent)
            validate_agent_collisions(definitions, Path("agents"))
            for client in clients:
                path = {"codex": ".codex/agents/" + agent.output,
                        "copilot": ".github/agents/" + Path(agent.source).stem + ".agent.md",
                        "gemini": ".gemini/agents/" + agent.source}[client]
                data = render_agent(agent) if client == "codex" else raw.replace(b"\r\n", b"\n")
                files[path] = (data, 0o644, [asset_id], {**spec, "line_endings": "lf"})
        except InstallError as error:
            raise AssetError("ASSET_CATALOG_INVALID", str(error)) from None
    return files


def preflight_agents(root, files, existing, inspect):
    desired = {path: tomllib.loads(value[0].decode("utf-8"))["name"].casefold()
               for path, value in files.items() if path.startswith(".codex/agents/")}
    if not desired:
        return []
    inspect(root, ".codex/agents/.agent-assets-preflight")
    directory = root / ".codex/agents"
    old_paths = {item["destination"] for item in existing[1]["items"]} if existing else set()
    inspected, seen = [], {}
    for target in sorted(directory.iterdir() if directory.exists() else []):
        if target.suffix.casefold() != ".toml":
            continue
        path = target.relative_to(root).as_posix()
        inspect(root, path)
        inspected.append(path)
        if path in old_paths:
            continue
        try:
            value = tomllib.loads(target.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError) as error:
            raise AssetError("ASSET_CONFIG_INVALID", "Invalid unmanaged Codex agent TOML: " + path) from error
        name = value.get("name")
        if not isinstance(name, str) or not name.strip():
            raise AssetError("ASSET_CONFIG_INVALID", "Unmanaged Codex agent has no valid name: " + path)
        folded = name.casefold()
        if folded in seen or folded in desired.values() or path.casefold() in {p.casefold() for p in desired}:
            raise AssetError("ASSET_CONFLICT", "Unmanaged Codex agent name/path collision: " + path, 1)
        seen[folded] = path
    return inspected
