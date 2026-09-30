"""Side-effect-free strict canonical agent parsing and Codex serialization."""
from __future__ import annotations
import json
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

RESERVED_NAMES = frozenset({"default", "worker", "explorer"})

class InstallError(ValueError):
    """Invalid canonical agent definition."""

@dataclass(frozen=True)
class AgentDefinition:
    source: str
    output: str
    name: str
    description: str
    instructions: str


def parse_scalar(value: str, path: Path, field: str) -> str:
    if not value or value.strip() != value:
        raise InstallError(f"Invalid {field} in {path}: value must be nonempty single-line text")
    if value.startswith(("[", "{", "|", ">", "&", "*", "!")):
        raise InstallError(f"Unsupported YAML form for {field} in {path}")
    if value.startswith('"'):
        if len(value) < 2 or value[-1] != '"':
            raise InstallError(f"Invalid quoted {field} in {path}")
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise InstallError(f"Invalid quoted {field} in {path}") from exc
        if not isinstance(parsed, str) or not parsed or "\n" in parsed or "\r" in parsed:
            raise InstallError(f"Invalid quoted {field} in {path}")
        return parsed
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise InstallError(f"Invalid quoted {field} in {path}")
        parsed = value[1:-1]
        if parsed.replace("''", "").find("'") != -1:
            raise InstallError(f"Invalid quoted {field} in {path}")
        return parsed.replace("''", "'")
    if "\t" in value:
        raise InstallError(f"Unsupported YAML form for {field} in {path}")
    return value


def parse_agent_bytes(raw: bytes, path: Path) -> AgentDefinition:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise InstallError(f"Source agent must not have a UTF-8 BOM: {path}")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InstallError(f"Source agent is not valid UTF-8: {path}") from exc

    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---" or lines[0] not in {"---\n", "---\r\n", "---"}:
        raise InstallError(f"Source agent must begin with an exact frontmatter delimiter: {path}")
    closing_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.rstrip("\r\n") == "---" and line in {"---\n", "---\r\n", "---"}:
            closing_index = index
            break
    if closing_index is None:
        raise InstallError(f"Source agent has no closing frontmatter delimiter: {path}")

    metadata: dict[str, str] = {}
    for line in lines[1:closing_index]:
        content = line.rstrip("\r\n")
        if not content or content.startswith((" ", "\t")) or ": " not in content:
            raise InstallError(f"Unsupported frontmatter line in {path}: {content!r}")
        field, value = content.split(": ", 1)
        if field not in {"name", "description"}:
            raise InstallError(f"Unknown frontmatter field {field!r} in {path}")
        if field in metadata:
            raise InstallError(f"Duplicate frontmatter field {field!r} in {path}")
        metadata[field] = parse_scalar(value, path, field)
    if set(metadata) != {"name", "description"}:
        raise InstallError(f"Source agent requires exactly name and description: {path}")

    body = "".join(lines[closing_index + 1 :])
    if not body.strip():
        raise InstallError(f"Source agent body must not be empty: {path}")
    name = metadata["name"]
    if name.casefold() in RESERVED_NAMES:
        raise InstallError(f"Source agent uses reserved Codex agent name {name!r}: {path}")
    source = path.name
    return AgentDefinition(source, f"{path.stem}.toml", name, metadata["description"], body)


def validate_agent_collisions(agents: Sequence[AgentDefinition], source_dir: Path) -> None:
    names: dict[str, Path] = {}
    outputs: dict[str, Path] = {}
    for agent in agents:
        name_key = agent.name.casefold()
        output_key = agent.output.casefold()
        if name_key in names:
            raise InstallError(f"Case-folded duplicate agent name {agent.name!r}: {names[name_key]} and {source_dir / agent.source}")
        if output_key in outputs:
            raise InstallError(f"Case-folded duplicate output {agent.output!r}: {outputs[output_key]} and {source_dir / agent.source}")
        names[name_key] = source_dir / agent.source
        outputs[output_key] = source_dir / agent.source


def render_agent(agent: AgentDefinition) -> bytes:
    rendered = (
        f"# Generated from agents/{agent.source} by scripts/install-codex-agents.py. Do not edit.\n"
        f"name = {json.dumps(agent.name, ensure_ascii=False)}\n"
        f"description = {json.dumps(agent.description, ensure_ascii=False)}\n"
        f"developer_instructions = {json.dumps(agent.instructions, ensure_ascii=False)}\n"
    ).encode("utf-8")
    try:
        decoded = tomllib.loads(rendered.decode("utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise InstallError(f"Internal error rendering {agent.source} as TOML") from exc
    if decoded != {"name": agent.name, "description": agent.description, "developer_instructions": agent.instructions}:
        raise InstallError(f"Internal error validating rendered TOML for {agent.source}")
    return rendered
