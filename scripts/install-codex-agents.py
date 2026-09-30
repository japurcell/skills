#!/usr/bin/env python3

"""Convert canonical Markdown agents into managed personal Codex TOML agents."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


MANIFEST_NAME = ".skills-repo-agents.json"
LOCK_NAME = ".skills-repo-agents.lock"
TEST_FAILURE_ENVIRONMENT = "CODEX_AGENT_TEST_FAIL_AFTER_REPLACEMENTS"


# Conversion is read-only with respect to its command/source checkout.
sys.dont_write_bytecode = True
from canonical_agents import (InstallError, AgentDefinition, parse_agent_bytes,
                              validate_agent_collisions, render_agent)


@dataclass(frozen=True)
class ManifestEntry:
    source: str
    output: str
    name: str


@dataclass(frozen=True)
class Manifest:
    entries: tuple[ManifestEntry, ...]


@dataclass(frozen=True)
class InstallPlan:
    destination: Path
    agents: tuple[AgentDefinition, ...]
    rendered: dict[str, bytes]
    replacements: tuple[str, ...]
    stale_outputs: tuple[str, ...]
    installed: int
    updated: int
    unchanged: int


@dataclass(frozen=True)
class InstallSummary:
    installed: int
    updated: int
    unchanged: int
    removed: int


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, type=Path, help="Flat Markdown agent source directory.")
    parser.add_argument("--destination-dir", required=True, type=Path, help="Personal Codex agent directory.")
    return parser.parse_args(argv)


def require_directory(path: Path, label: str, *, must_exist: bool) -> None:
    try:
        details = path.lstat()
    except FileNotFoundError:
        if must_exist:
            raise InstallError(f"{label} does not exist: {path}") from None
        return
    except OSError as exc:
        raise InstallError(f"Unable to inspect {label}: {path}: {exc}") from exc
    if stat.S_ISLNK(details.st_mode):
        raise InstallError(f"{label} must not be a symbolic link: {path}")
    if not stat.S_ISDIR(details.st_mode):
        raise InstallError(f"{label} must be a directory: {path}")


def parse_agent(path: Path) -> AgentDefinition:
    try:
        details = path.lstat()
    except OSError as exc:
        raise InstallError(f"Unable to inspect source agent: {path}: {exc}") from exc
    if stat.S_ISLNK(details.st_mode):
        raise InstallError(f"Source agent must not be a symbolic link: {path}")
    if not stat.S_ISREG(details.st_mode):
        raise InstallError(f"Source agent must be a regular file: {path}")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise InstallError(f"Unable to read source agent: {path}: {exc}") from exc
    return parse_agent_bytes(raw, path)


def discover_sources(source_dir: Path) -> list[AgentDefinition]:
    require_directory(source_dir, "Source directory", must_exist=True)
    try:
        entries = list(source_dir.iterdir())
    except OSError as exc:
        raise InstallError(f"Unable to list source directory: {source_dir}: {exc}") from exc
    agents: list[AgentDefinition] = []
    for entry in sorted(entries, key=lambda candidate: (candidate.name.casefold(), candidate.name)):
        if entry.suffix.casefold() != ".md":
            continue
        agents.append(parse_agent(entry))
    validate_agent_collisions(agents, source_dir)
    return agents



def validate_manifest_entry(value: object, destination: Path) -> ManifestEntry:
    if not isinstance(value, dict) or set(value) != {"source", "output", "name"}:
        raise InstallError(f"Malformed managed-agent manifest: {destination / MANIFEST_NAME}")
    source, output, name = (value["source"], value["output"], value["name"])
    if not all(isinstance(item, str) and item for item in (source, output, name)):
        raise InstallError(f"Malformed managed-agent manifest: {destination / MANIFEST_NAME}")
    if Path(source).name != source or Path(output).name != output or not source.casefold().endswith(".md") or not output.casefold().endswith(".toml"):
        raise InstallError(f"Unsafe managed-agent manifest path: {destination / MANIFEST_NAME}")
    return ManifestEntry(source, output, name)


def read_manifest(destination_dir: Path) -> Manifest:
    manifest_path = destination_dir / MANIFEST_NAME
    try:
        details = manifest_path.lstat()
    except FileNotFoundError:
        return Manifest(())
    except OSError as exc:
        raise InstallError(f"Unable to inspect managed-agent manifest: {manifest_path}: {exc}") from exc
    if stat.S_ISLNK(details.st_mode):
        raise InstallError(f"Managed-agent manifest must not be a symbolic link: {manifest_path}")
    if not stat.S_ISREG(details.st_mode):
        raise InstallError(f"Managed-agent manifest must be a regular file: {manifest_path}")
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallError(f"Malformed managed-agent manifest: {manifest_path}") from exc
    if not isinstance(data, dict) or set(data) != {"version", "agents"} or data["version"] != 1 or not isinstance(data["agents"], list):
        raise InstallError(f"Malformed managed-agent manifest: {manifest_path}")
    entries = tuple(validate_manifest_entry(entry, destination_dir) for entry in data["agents"])
    outputs: set[str] = set()
    names: set[str] = set()
    for entry in entries:
        if entry.output.casefold() in outputs or entry.name.casefold() in names:
            raise InstallError(f"Malformed managed-agent manifest: {manifest_path}")
        outputs.add(entry.output.casefold())
        names.add(entry.name.casefold())
    return Manifest(entries)


def inspect_unmanaged_agents(destination_dir: Path, managed_outputs: set[str]) -> dict[str, Path]:
    unmanaged: dict[str, Path] = {}
    if not destination_dir.exists():
        return unmanaged
    for path in destination_dir.rglob("*"):
        if path == destination_dir / MANIFEST_NAME or path == destination_dir / LOCK_NAME:
            continue
        if path.name.startswith(".skills-repo-agents-"):
            continue
        if path.suffix.casefold() != ".toml":
            continue
        try:
            details = path.lstat()
        except OSError as exc:
            raise InstallError(f"Unable to inspect destination agent: {path}: {exc}") from exc
        if stat.S_ISLNK(details.st_mode):
            raise InstallError(f"Destination agent must not be a symbolic link: {path}")
        if not stat.S_ISREG(details.st_mode):
            raise InstallError(f"Destination agent must be a regular file: {path}")
        relative = path.relative_to(destination_dir).as_posix()
        if relative in managed_outputs:
            continue
        try:
            parsed = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
            raise InstallError(f"Malformed unmanaged Codex agent: {path}") from exc
        name = parsed.get("name")
        if not isinstance(name, str) or not name:
            raise InstallError(f"Unmanaged Codex agent requires a name: {path}")
        key = name.casefold()
        if key in unmanaged:
            raise InstallError(f"Case-folded duplicate unmanaged Codex agent name {name!r}: {unmanaged[key]} and {path}")
        unmanaged[key] = path
    return unmanaged



def path_is_regular_or_missing(path: Path, label: str) -> bool:
    try:
        details = path.lstat()
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise InstallError(f"Unable to inspect {label}: {path}: {exc}") from exc
    if stat.S_ISLNK(details.st_mode):
        raise InstallError(f"{label} must not be a symbolic link: {path}")
    if not stat.S_ISREG(details.st_mode):
        raise InstallError(f"{label} must be a regular file: {path}")
    return True


def build_install_plan(source_dir: Path, destination_dir: Path) -> InstallPlan:
    agents = discover_sources(source_dir)
    require_directory(destination_dir, "Destination directory", must_exist=False)
    destination_exists = destination_dir.exists()
    if not destination_exists:
        manifest = Manifest(())
        unmanaged: dict[str, Path] = {}
    else:
        manifest = read_manifest(destination_dir)
        managed_outputs = {entry.output for entry in manifest.entries}
        unmanaged = inspect_unmanaged_agents(destination_dir, managed_outputs)
    lock_path = destination_dir / LOCK_NAME
    try:
        lock_details = lock_path.lstat()
    except FileNotFoundError:
        lock_details = None
    except OSError as exc:
        raise InstallError(f"Unable to inspect installation lock: {lock_path}: {exc}") from exc
    if lock_details is not None:
        if stat.S_ISLNK(lock_details.st_mode):
            raise InstallError(f"Installation lock must not be a symbolic link: {lock_path}")
        raise InstallError(f"Codex agent installation is already active: {lock_path}")

    managed_output_keys = {entry.output.casefold() for entry in manifest.entries}
    managed_by_output_key = {entry.output.casefold(): entry for entry in manifest.entries}
    rendered = {agent.output: render_agent(agent) for agent in agents}
    replacements: list[str] = []
    installed = updated = unchanged = 0
    for agent in agents:
        output_path = destination_dir / agent.output
        output_key = agent.output.casefold()
        previous_entry = managed_by_output_key.get(output_key)
        if previous_entry is not None and previous_entry.output != agent.output:
            raise InstallError(
                "Case-folded managed output differs from generated output: "
                f"{destination_dir / previous_entry.output} and {output_path}"
            )
        if output_key not in managed_output_keys:
            conflict = next((path for path in destination_dir.glob("*") if path.name.casefold() == output_key), None) if destination_exists else None
            if conflict is not None:
                raise InstallError(f"Unmanaged destination path collides with generated agent: {conflict}")
        if agent.name.casefold() in unmanaged:
            raise InstallError(f"Unmanaged Codex agent name collides with generated agent {agent.name!r}: {unmanaged[agent.name.casefold()]}")
        exists = path_is_regular_or_missing(output_path, "Managed destination agent") if destination_exists else False
        if not exists:
            installed += 1
            replacements.append(agent.output)
        elif output_path.read_bytes() == rendered[agent.output]:
            unchanged += 1
        else:
            updated += 1
            replacements.append(agent.output)
    stale_outputs = tuple(entry.output for entry in manifest.entries if entry.output not in rendered)
    for output in stale_outputs:
        path_is_regular_or_missing(destination_dir / output, "Managed destination agent")
    return InstallPlan(destination_dir, tuple(agents), rendered, tuple(replacements), stale_outputs, installed, updated, unchanged)


def fsync_directory(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def set_owner_only_mode(descriptor: int) -> None:
    if hasattr(os, "fchmod"):
        os.fchmod(descriptor, 0o600)


def write_file(path: Path, content: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        set_owner_only_mode(descriptor)
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        if descriptor != -1:
            os.close(descriptor)


def manifest_bytes(agents: tuple[AgentDefinition, ...]) -> bytes:
    data = {
        "version": 1,
        "agents": [
            {"source": agent.source, "output": agent.output, "name": agent.name}
            for agent in agents
        ],
    }
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def create_lock(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise InstallError(f"Codex agent installation is already active: {path}") from exc
    try:
        set_owner_only_mode(descriptor)
        os.write(descriptor, f"pid={os.getpid()}\n".encode("ascii"))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def restore_paths(destination: Path, backups: Path, affected: tuple[str, ...]) -> None:
    for name in affected:
        original = destination / name
        backup = backups / name
        if backup.exists():
            os.replace(backup, original)
        else:
            try:
                original.unlink()
            except FileNotFoundError:
                pass
    fsync_directory(destination)


def apply_install_plan(plan: InstallPlan) -> InstallSummary:
    destination = plan.destination
    destination.mkdir(parents=True, exist_ok=True)
    require_directory(destination, "Destination directory", must_exist=True)
    lock_path = destination / LOCK_NAME
    transaction: Path | None = None
    created_lock = False
    affected = tuple(dict.fromkeys((*plan.replacements, *plan.stale_outputs, MANIFEST_NAME)))
    try:
        create_lock(lock_path)
        created_lock = True
        transaction = Path(tempfile.mkdtemp(prefix=".skills-repo-agents-", dir=destination))
        staged = transaction / "staged"
        backups = transaction / "backups"
        staged.mkdir()
        backups.mkdir()
        for name in affected:
            path = destination / name
            if path.exists():
                write_file(backups / name, path.read_bytes())
        for output in plan.replacements:
            write_file(staged / output, plan.rendered[output])
        write_file(staged / MANIFEST_NAME, manifest_bytes(plan.agents))
        fsync_directory(staged)
        replacements_done = 0
        for output in plan.replacements:
            os.replace(staged / output, destination / output)
            fsync_directory(destination)
            replacements_done += 1
            failure_after = os.environ.get(TEST_FAILURE_ENVIRONMENT)
            if failure_after and replacements_done >= int(failure_after):
                raise OSError("injected apply failure")
        for output in plan.stale_outputs:
            try:
                (destination / output).unlink()
            except FileNotFoundError:
                pass
        fsync_directory(destination)
        os.replace(staged / MANIFEST_NAME, destination / MANIFEST_NAME)
        fsync_directory(destination)
        return InstallSummary(plan.installed, plan.updated, plan.unchanged, len(plan.stale_outputs))
    except (OSError, ValueError) as exc:
        if transaction is not None:
            try:
                restore_paths(destination, transaction / "backups", affected)
            except OSError as rollback_error:
                raise InstallError(f"Codex agent installation failed and rollback also failed: {rollback_error}") from exc
        raise InstallError(f"Codex agent installation failed: {exc}") from exc
    finally:
        if transaction is not None:
            shutil.rmtree(transaction, ignore_errors=True)
        if created_lock:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass
        fsync_directory(destination)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parse_arguments(argv)
    try:
        plan = build_install_plan(arguments.source_dir, arguments.destination_dir)
        summary = apply_install_plan(plan)
    except InstallError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(
        "Codex agents: "
        f"{summary.installed} installed, {summary.updated} updated, "
        f"{summary.unchanged} unchanged, {summary.removed} removed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
