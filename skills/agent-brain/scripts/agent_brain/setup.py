"""Read-only reviewed plans and journaled, reversible managed activation."""
from __future__ import annotations

from contextlib import closing, ExitStack
import copy
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid

from .config import load_config
from .history import exclusive, replace_content, revision, sync_directory, validate_size
from .lifecycle import actual_binding, read_json
from .software import command, validate_software
from .state import LifecycleError, StateStore, digest, local_path, write_private

LOCAL = ".agents/context/activation-local.json"
EXPECTED = ".agents/context/expected-runtime.json"
INDEX = ".agents/context/native-registrations.json"
PRIVATE_DIRECTORIES = (".agents/context/setup-history", ".agents/context/setup-backups", ".agents/context/registrations")
PRIVATE_FILES = (LOCAL, EXPECTED, INDEX, ".agents/context/setup.lock", ".agents/context/publication.lock",
    ".agents/context/setup-fixture-barrier.json", ".agents/context/setup-fixture-reached", ".agents/context/setup-fixture-release")


def ignore_literal(name):
    if any(ord(character) < 32 or ord(character) == 127 for character in name):
        raise LifecycleError("SETUP_CONFLICT", "private operational paths contain unsupported control characters; select a literal safe runtime path")
    return "".join("\\" + character if character in "\\*?[]!# " else character for character in name)


def validate_private_paths(root, config, config_name):
    """Refuse to hide portable ownership or leave tracked private records exposed."""
    directories = (config.state_dir, *PRIVATE_DIRECTORIES)
    ignore_literal(config.state_dir)
    portable = [config_name, config.history_dir, config.candidate_dir]
    portable.extend(owner.path for owner in config.knowledge_roots)
    portable.extend(unit.path for unit in config.mapped_units)
    if config.source_ingestion["enabled"]:
        portable.extend(config.source_ingestion[field] for field in ("engine_path", "bridge_path")
            if not Path(config.source_ingestion[field]).is_absolute())
    for private in directories:
        for name in portable:
            if Path(private).is_relative_to(Path(name)) or Path(name).is_relative_to(Path(private)):
                raise LifecycleError("SETUP_CONFLICT", "private operational directories overlap portable knowledge, configuration or history; select a separate runtime path")
    if any(Path(config.state_dir).is_relative_to(Path(name)) or Path(name).is_relative_to(Path(config.state_dir))
            for name in PRIVATE_DIRECTORIES):
        raise LifecycleError("SETUP_CONFLICT", "runtime directory overlaps reserved private setup storage")
    if any(name in PRIVATE_FILES or name.startswith(".agents/context/.agent-brain-") for name in portable):
        raise LifecycleError("SETUP_CONFLICT", "portable configuration or guidance occupies a private operational path")
    text(root, ".agents/context/.gitignore")
    if local_path(root, config.state_dir).is_dir():
        text(root, config.state_dir + "/.gitignore")
    checked = subprocess.run(["git", "--literal-pathspecs", "ls-files", "-z", "--", *directories, *PRIVATE_FILES],
        cwd=root, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=2)
    if checked.returncode:
        raise LifecycleError("SETUP_UNSUPPORTED", "cannot check private operational Git ownership before effects")
    if checked.stdout:
        raise LifecycleError("SETUP_CONFLICT", "private operational artifacts are already tracked; explicitly remove them from the index before setup, without deleting recoverable data")


def append_private_ignore(root, name, lines):
    """Append only privacy rules; never replace or reorder unrelated ignore bytes."""
    path = local_path(root, name)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(descriptor, "r+b") as stream:
        if os.fstat(stream.fileno()).st_size > 8 * 1024 * 1024:
            raise LifecycleError("SETUP_CONFLICT", "private ignore marker is too large; preserve it and review its rules")
        before = stream.read(8 * 1024 * 1024 + 1)
        before.decode("utf-8")
        block = ("\n".join(lines) + "\n").encode()
        if not before.endswith(block):
            stream.write((b"\n" if before else b"") + block)
            stream.flush()
            os.fsync(stream.fileno())
    sync_directory(path.parent)


def protect_private_state(root, config, config_name, *, runtime):
    """Persistent nonsemantic privacy precedes the first operational write/intent."""
    validate_private_paths(root, config, config_name)
    relative = Path(config.state_dir).relative_to(".agents/context").as_posix()
    lines = ["/.gitignore", "/.agent-brain-*", "/" + ignore_literal(relative) + "/"]
    lines.extend("/" + Path(name).name + "/" for name in PRIVATE_DIRECTORIES)
    lines.extend("/" + Path(name).name for name in PRIVATE_FILES)
    append_private_ignore(root, ".agents/context/.gitignore", lines)
    if runtime or local_path(root, config.state_dir).is_dir():
        append_private_ignore(root, config.state_dir + "/.gitignore", ["*"])
    probes = [*PRIVATE_FILES, ".agents/context/.agent-brain-privacy-probe",
        *(name + "/privacy-probe" for name in PRIVATE_DIRECTORIES), config.state_dir + "/brain.sqlite3"]
    checked = subprocess.run(["git", "check-ignore", "--no-index", "-z", "--stdin"], cwd=root,
        input=("\0".join(probes) + "\0").encode(), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=2)
    if checked.returncode or set(checked.stdout.decode().rstrip("\0").split("\0")) != set(probes):
        raise LifecycleError("SETUP_CONFLICT", "Git ignore rules do not protect every private operational path; preserve state and repair local privacy rules before setup")


def text(root: Path, name: str) -> str | None:
    path = local_path(root, name)
    if not path.exists():
        return None
    if not path.is_file() or path.stat().st_size > 8 * 1024 * 1024:
        raise LifecycleError("SETUP_INVALID", "setup input must be a bounded regular UTF-8 file")
    return path.read_bytes().decode("utf-8")


def encoded(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def checked_local(root):
    raw = text(root, LOCAL)
    if raw is None:
        return None
    result = read_json(raw)
    if set(result) != {"schema_version", "status", "repository_id", "worktree_root", "journal_path", "managed", "selectors", "integrations", "software", "shell", "binding_revision", "prior_integrations"} or result["schema_version"] != 1 or result["worktree_root"] != str(root):
        raise LifecycleError("SETUP_STATE_UNAVAILABLE", "managed activation identity is malformed or relocated; preserve it")
    return result


def fresh_configuration(root):
    identity = uuid.uuid5(uuid.NAMESPACE_URL, "agent-brain:" + str(root))
    roots = []
    units = []
    startup = []
    additions = {}
    for name in ("AGENTS.md", ".agents/memory/INDEX.md", ".agents/memory/ARCHITECTURE.md", ".agents/memory/CONVENTIONS.md"):
        if text(root, name) is not None:
            unit = str(uuid.uuid5(identity, name))
            roots.append({"path": name, "ownership": "read_only", "type": "file"})
            units.append({"id": unit, "path": name, "selector": {"type": "document"}, "kind": "policy", "status": "established",
                "applies": {"paths": ["**"]}})
            startup.append({"id": unit, "loading_mode": "whole"})
    # This is a routing artifact, with no invented lesson or second knowledge base.
    if not units:
        name = ".agents/context/map.md"
        unit = str(uuid.uuid5(identity, name))
        additions[name] = "# Repository knowledge map\n\nMap existing authoritative guidance in config.json before relying on it. No learned knowledge has been recorded.\n"
        roots.append({"path": name, "ownership": "read_only", "type": "file"})
        units.append({"id": unit, "path": name, "selector": {"type": "document"}, "kind": "policy", "status": "established",
            "applies": {"paths": ["**"]}})
        startup.append({"id": unit, "loading_mode": "whole"})
    for name in (".agents/instructions", ".agents/memory"):
        roots.append({"path": name, "ownership": "agent_brain"})
    return {"schema_version": 1, "repository_id": str(identity), "knowledge_roots": roots,
        "mapped_units": units, "startup": startup, "providers": {}}, additions


def current_software():
    bundle = Path(__file__).resolve().parents[2]
    manifest = bundle / "software.json"
    if not manifest.is_file():
        return {}
    value = read_json(manifest.read_bytes().decode("utf-8"))
    pin = {name: value[name] for name in ("bundle_path", "core_version", "adapter_version", "schema_version")}
    pin["manifest_revision"] = hashlib.sha256(manifest.read_bytes()).hexdigest()
    validate_software(pin)
    return pin


def remove_owned(document, event, entry):
    values = document.get("hooks", {}).get(event, [])
    if not isinstance(values, list) or values.count(entry) != 1:
        raise LifecycleError("SETUP_CONFLICT", "a managed handler was changed or removed; preserve the unexpected configuration and review it")
    values.remove(entry)
    if not values:
        del document["hooks"][event]


def registration_entries(support, selector, shell, interpreter):
    provider = support["provider"]
    adapter = support["adapter_path"]
    entries = []
    for event in support["native_events"]:
        argv = [interpreter, adapter, "--registration", selector, "--event", event]
        if provider == "copilot":
            entry = {"type": "command", "bash": command(argv), "powershell": command(argv, "powershell"),
                "timeoutSec": support["native_deadline_seconds"]}
        else:
            entry = {"hooks": [{"type": "command", "command": command(argv, shell),
                "timeout": support["native_deadline_seconds"] * (1000 if provider == "gemini" else 1)}]}
        entries.append((event, entry))
    return entries


def plan(root: Path, config_name: str, *, deactivate=False, shell=None) -> dict:
    repository, worktree = actual_binding(root)
    base_config = text(root, config_name)
    desired = read_json(base_config) if base_config is not None else fresh_configuration(root)[0]
    changes = {} if base_config is not None else fresh_configuration(root)[1]
    load_config(root / config_name, source=encoded(desired).encode())
    previous = checked_local(root)
    if previous and previous["status"] not in ("active", "disabled"):
        raise LifecycleError("SETUP_INCOMPLETE", "an interrupted activation must be rolled back before a new plan", exit_code=1)
    if previous and previous["repository_id"] != desired["repository_id"]:
        raise LifecycleError("SETUP_CONFLICT", "configuration and managed activation repository identities differ")
    shell = shell or (previous or {}).get("shell") or ("powershell" if os.name == "nt" else "posix")
    software = current_software()
    if desired.get("software") and desired["software"] != software:
        # Only explicit same-schema inventory updates are currently supported.
        old = validate_software(desired["software"])
        if not software or desired["software"]["core_version"] != software["core_version"] or desired["software"]["adapter_version"] != software["adapter_version"] or desired["software"]["schema_version"] != software["schema_version"]:
            raise LifecycleError("MIGRATION_UNSUPPORTED", "no explicit migration supports this version change or downgrade; restore the prior bundle before effects")
    if software:
        desired["software"] = software
    if deactivate:
        for provider in desired.get("providers", {}).values():
            provider["enabled"] = False
    config = load_config(root / config_name, source=encoded(desired).encode())
    validate_private_paths(root, config, config_name)
    documents = {}
    for owned in (previous or {}).get("managed", []):
        name = owned["path"]
        if name not in documents:
            documents[name] = read_json(text(root, name) or "{}")
        remove_owned(documents[name], owned["event"], owned["entry"])
    inputs = {config_name: revision(base_config)}
    prerequisites = [{"name": "runtime", "status": "ready" if sys.version_info >= (3, 12) and sqlite3.sqlite_version_info >= (3, 15, 2) else "unsupported"}]
    destination = local_path(root, config.state_dir)
    prerequisites.append({"name": "state destination", "status": "unsupported" if destination.exists() and not destination.is_dir() else "ready"})
    prerequisites.append({"name": "private operational protection", "status": "ready"})
    integrations = []
    managed = []
    selectors = []
    for integration_id, provider in sorted(config.providers.items()):
        if not provider["enabled"]:
            continue
        try:
            if provider["kind"] != "native":
                raise LifecycleError("NATIVE_UNSUPPORTED", "setup enables only exact native certification paths")
            from .native import support_record
            support = support_record(config, root, provider)
            if not software or support["bundle_path"] != software["bundle_path"]:
                raise LifecycleError("SOFTWARE_UNAVAILABLE", "certification must bind this exact installed immutable bundle")
            inputs[provider["support_record"]] = revision(text(root, provider["support_record"]))
            for name in ("permissions", "lifecycle_config"):
                inputs[support[name]["path"]] = revision(text(root, support[name]["path"]))
            if support["status"] == "certified":
                inputs[support["evidence"]["path"]] = revision(text(root, support["evidence"]["path"]))
            token = hashlib.sha256(integration_id.encode()).hexdigest()[:24]
            selector = f".agents/context/registrations/{token}.json"
            value = {"schema_version": 1, "integration_id": integration_id, "config_path": config_name,
                "bundle_path": support["bundle_path"], "provider": support["provider"],
                "provider_version": support["provider_version"], "entry_mode": support["entry_mode"]}
            changes[selector] = encoded(value)
            selectors.append(selector)
            name = {"copilot": ".github/hooks/agent-brain.json", "codex": ".codex/hooks.json", "gemini": ".gemini/settings.json"}[support["provider"]]
            if name not in documents:
                documents[name] = read_json(text(root, name) or ("{\"version\":1,\"hooks\":{}}" if support["provider"] == "copilot" else "{}"))
            hooks = documents[name].setdefault("hooks", {})
            if not isinstance(hooks, dict):
                raise LifecycleError("SETUP_INVALID", "existing provider hooks must be a JSON object")
            interpreter = validate_software(software)["interpreter"]["executable"]
            for event, entry in registration_entries(support, selector, shell, interpreter):
                values = hooks.setdefault(event, [])
                if not isinstance(values, list):
                    raise LifecycleError("SETUP_INVALID", "existing provider event hooks must be arrays")
                if entry not in values:
                    values.append(entry)
                managed.append({"path": name, "event": event, "entry": entry})
            integrations.append(value)
            prerequisites.append({"name": integration_id, "status": "ready", "certification": support["status"]})
        except (LifecycleError, OSError, ValueError, KeyError) as exc:
            prerequisites.append({"name": integration_id, "status": "unsupported", "cause": str(exc),
                "next_action": "Supply matching observed native certification, or disable this integration. Offline fixtures are confined to disposable Git repositories."})
    for name, document in documents.items():
        changes[name] = encoded(document)
    for name in (previous or {}).get("selectors", []):
        if name not in selectors:
            changes[name] = None
    activation = "active" if integrations else "disabled"
    changes[config_name] = encoded(desired)
    binding_revision = revision(encoded(desired))
    prior_integrations = []
    if previous and previous["status"] == "active" and not deactivate:
        old_plan = checked_journal(root, previous["journal_path"])["plan"]
        old_configuration = old_plan["configuration"]
        semantic = lambda value: {key: item for key, item in value.items() if key not in ("software", "providers")}
        if semantic(old_configuration) == semantic(desired) and all(desired.get("providers", {}).get(key) == item
                for key, item in old_configuration.get("providers", {}).items() if item["enabled"]):
            binding_revision = previous["binding_revision"]
            prior_integrations = list(previous["prior_integrations"])
            for item in previous["integrations"]:
                if item not in integrations and item not in prior_integrations:
                    prior_integrations.append(item)
    ignored = text(root, ".gitignore") or ""
    for name in (config.state_dir + "/", *PRIVATE_FILES, *(name + "/" for name in PRIVATE_DIRECTORIES)):
        line = "/" + ignore_literal(name)
        if line not in ignored.splitlines():
            ignored += ("\n" if ignored and not ignored.endswith("\n") else "") + line + "\n"
    changes[".gitignore"] = ignored
    if integrations or previous:
        changes[INDEX] = encoded({"schema_version": 1, "integrations": integrations})
    if base_config is not None:
        from .knowledge import load_knowledge
        knowledge = load_knowledge(config, repository_root=root)
        if knowledge.issues:
            raise LifecycleError("SETUP_KNOWLEDGE_INVALID", "repair the mapped knowledge and required references before activation")
    for owner in config.knowledge_roots:
        directory = local_path(root, owner.path)
        paths = [directory] if owner.type == "file" else sorted(directory.rglob("*.md"))
        for path in paths:
            name = path.relative_to(root).as_posix()
            inputs[name] = revision(text(root, name))
    # Include existing activation identity and every written before-image.
    inputs[LOCAL] = revision(text(root, LOCAL))
    inputs[EXPECTED] = revision(text(root, EXPECTED))
    changes = [{"path": name, "before": text(root, name), "after": content,
        "before_revision": revision(text(root, name)), "after_revision": revision(content)} for name, content in changes.items()
        if text(root, name) != content]
    value = {"schema_version": 1, "command": "setup", "operation_status": "ok", "repository_root": repository,
        "worktree_root": worktree, "config_path": config_name, "configuration": desired, "software": software,
        "inputs": inputs, "changes": changes, "prerequisites": prerequisites, "activation": activation,
        "deactivate": deactivate, "shell": shell, "managed": managed, "selectors": selectors, "integrations": integrations,
        "binding_revision": binding_revision, "prior_integrations": prior_integrations}
    value["id"] = digest(value)
    validate_size(value)
    return value


def read_plan(path: Path) -> dict:
    from .software import checked_absolute
    checked_absolute(path.absolute())
    if path.stat().st_size > 8 * 1024 * 1024:
        raise LifecycleError("SETUP_INVALID", "reviewed plan is oversized")
    value = read_json(path.read_bytes().decode("utf-8"))
    if value.get("schema_version") != 1 or value.get("id") != digest({key: item for key, item in value.items() if key != "id"}):
        raise LifecycleError("SETUP_INVALID", "reviewed plan schema or integrity is invalid")
    return value


def journal_path(value):
    return ".agents/context/setup-history/" + value["id"] + ".json"


def save_journal(root, path, journal):
    validate_size(journal)
    journal["integrity"] = digest({key: value for key, value in journal.items() if key != "integrity"})
    target = local_path(root, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    write_private(target, journal)
    sync_directory(target.parent)


def checked_journal(root, path):
    result = read_json(text(root, path) or "{}")
    if result.get("schema_version") != 1 or result.get("integrity") != digest({key: value for key, value in result.items() if key != "integrity"}):
        raise LifecycleError("SETUP_HISTORY_UNAVAILABLE", "managed journal is missing or corrupt; preserve recoverable state")
    try:
        value = result["plan"]
        if (value["id"] != digest({key: item for key, item in value.items() if key != "id"})
                or path != journal_path(value) or value["worktree_root"] != str(root)
                or result["status"] not in ("preparing", "applying", "applied", "rolling_back", "rolled_back")
                or len(result["changes"]) != len(value["changes"]) + 1
                or result["changes"][:-1] != value["changes"]):
            raise ValueError("journal no longer represents its exact reviewed plan")
        local = result["changes"][-1]
        expected = {"schema_version": 1, "status": value["activation"], "repository_id": value["configuration"]["repository_id"],
            "worktree_root": value["worktree_root"], "journal_path": path, "managed": value["managed"],
            "selectors": value["selectors"], "integrations": value["integrations"], "software": value["software"],
            "shell": value["shell"], "binding_revision": value["binding_revision"], "prior_integrations": value["prior_integrations"]}
        if local["path"] != LOCAL or local["after"] != encoded(expected) or local["before_revision"] != value["inputs"][LOCAL]:
            raise ValueError("journal activation identity differs")
        for item in result["changes"]:
            local_path(root, item["path"])
            if item["before_revision"] != revision(item["before"]) or item["after_revision"] != revision(item["after"]):
                raise ValueError("journal before/inverse bytes differ")
    except (ValueError, KeyError, TypeError) as exc:
        raise LifecycleError("SETUP_HISTORY_UNAVAILABLE", "managed journal effects or reviewed identity are corrupt; preserve recoverable state") from exc
    return result


def lock_store(root):
    # Setup serialization for configurations which have no initialized runtime.
    store = StateStore(root, ".agents/context")
    store.directory.mkdir(parents=True, exist_ok=True)
    return store


def sqlite_backup(store, root, path):
    store.read()
    target = local_path(root, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    until = time.monotonic() + 2
    def progress(status, remaining, total):
        if time.monotonic() > until:
            raise LifecycleError("STATE_CONTENDED", "bounded backup time was exhausted; preserve the prior state and retry", exit_code=1)
    with closing(store._connect(readonly=True)) as source, closing(sqlite3.connect(target, isolation_level=None)) as destination:
        source.backup(destination, pages=64, sleep=0.01, progress=progress)
    os.chmod(target, 0o600)


def apply(root, value):
    repository, worktree = actual_binding(root)
    if (value["repository_root"], value["worktree_root"]) != (repository, worktree):
        raise LifecycleError("SETUP_STALE", "reviewed plan belongs to another repository or worktree")
    path = journal_path(value)
    existing = text(root, path)
    if existing is not None:
        journal = checked_journal(root, path)
        if journal["status"] == "applied" and all(text(root, item["path"]) == item["after"] for item in journal["changes"]):
            changed = {item["path"] for item in journal["changes"]} | {LOCAL, EXPECTED}
            if any(revision(text(root, name)) != expected for name, expected in value["inputs"].items() if name not in changed):
                raise LifecycleError("SETUP_STALE", "a certification or knowledge input changed after the reviewed apply")
            config = load_config(root / value["config_path"])
            if config.software:
                validate_software(config.software)
            protect_private_state(root, config, value["config_path"], runtime=False)
            if value["activation"] == "active":
                StateStore(root, config.state_dir).read()
                from .native import support_record
                for provider in config.providers.values():
                    if provider["enabled"]:
                        support_record(config, root, provider)
            return {"schema_version": 1, "operation_status": "ok", "command": "setup", "activation": value["activation"], "journal_path": path, "idempotent": True}
        raise LifecycleError("SETUP_INCOMPLETE", "the reviewed plan has interrupted or changed effects; use its exact rollback journal", exit_code=1)
    if any(item["status"] != "ready" for item in value["prerequisites"]):
        raise LifecycleError("SETUP_UNSUPPORTED", "a prerequisite or exact certification is unavailable; disable that integration or supply matching evidence")
    for name, expected in value["inputs"].items():
        if revision(text(root, name)) != expected:
            raise LifecycleError("SETUP_STALE", "a reviewed configuration, knowledge, certification or activation input changed")
    if plan(root, value["config_path"], deactivate=value["deactivate"], shell=value["shell"]) != value:
        raise LifecycleError("SETUP_STALE", "reviewed exact setup effects or software prerequisites changed")
    config = load_config(root / value["config_path"], source=encoded(value["configuration"]).encode())
    store = StateStore(root, config.state_dir)
    if store.path.exists() or store.marker.exists() or text(root, EXPECTED) is not None and not value["deactivate"]:
        store.read()
    protect_private_state(root, config, value["config_path"], runtime=value["activation"] == "active")
    with ExitStack() as locks:
        setup_store = lock_store(root)
        locks.enter_context(exclusive(setup_store))
        store.remaining_contention = setup_store.remaining_contention
        if store.directory.is_dir() or value["activation"] == "active":
            store.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            locks.enter_context(exclusive(store))
        for name, expected in value["inputs"].items():
            if revision(text(root, name)) != expected:
                raise LifecycleError("SETUP_STALE", "a reviewed configuration, knowledge, certification or activation input changed")
        current = plan(root, value["config_path"], deactivate=value["deactivate"], shell=value["shell"])
        if current != value:
            raise LifecycleError("SETUP_STALE", "reviewed exact setup effects or software prerequisites changed")
        if store.path.exists() or store.marker.exists() or text(root, EXPECTED) is not None and not value["deactivate"]:
            store.read()
        journal = {"schema_version": 1, "status": "preparing", "plan": value, "changes": copy.deepcopy(value["changes"]), "backup_path": None}
        local = {"schema_version": 1, "status": "applying", "repository_id": config.repository_id,
            "worktree_root": worktree, "journal_path": path, "managed": value["managed"], "selectors": value["selectors"],
            "integrations": value["integrations"], "software": value["software"], "shell": value["shell"],
            "binding_revision": value["binding_revision"], "prior_integrations": value["prior_integrations"]}
        local_after = encoded(local | {"status": "active" if value["activation"] == "active" else "disabled"})
        journal["changes"].append({"path": LOCAL, "before": text(root, LOCAL), "after": local_after,
            "before_revision": revision(text(root, LOCAL)), "after_revision": revision(local_after)})
        save_journal(root, path, journal)
        replace_content(local_path(root, LOCAL), encoded(local))
        if store.path.exists():
            journal["backup_path"] = ".agents/context/setup-backups/" + value["id"] + ".sqlite3"
            sqlite_backup(store, root, journal["backup_path"])
            save_journal(root, path, journal)
        # Explicit supported migration: schema 1 to schema 1 preserves every live record.
        if value["activation"] == "active" and not store.path.exists():
            if text(root, EXPECTED) is not None:
                raise LifecycleError("STATE_UNAVAILABLE", "expected runtime was deleted; restore its backup, never initialize a replacement", exit_code=1)
            expected = {"schema_version": 1, "repository_id": config.repository_id, "repository_root": repository,
                "worktree_root": worktree, "state_dir": config.state_dir, "worktree_id": None, "status": "initializing"}
            replace_content(local_path(root, EXPECTED), encoded(expected))
            store.initialize(config.repository_id, repository, initial_setup=True)
            expected.update(worktree_id=store.read()["worktree_id"], status="expected")
            replace_content(local_path(root, EXPECTED), encoded(expected))
        # Configuration and hooks precede selectors; incomplete local identity denies every adapter.
        ordered = sorted(value["changes"], key=lambda item: (item["path"] in value["selectors"] or item["path"] == INDEX, item["path"]))
        journal["status"] = "applying"
        save_journal(root, path, journal)
        for item in ordered:
            if text(root, item["path"]) != item["before"]:
                raise LifecycleError("SETUP_CONFLICT", "an unexpected edit appeared during apply; preserve it and roll back only exact owned effects", exit_code=1)
            replace_content(local_path(root, item["path"]), item["after"])
            journal["applied_path"] = item["path"]
            save_journal(root, path, journal)
            barrier(root, value, item["path"])
        if value["deactivate"] and store.path.exists():
            state = store.read()
            def revoke(record):
                record["invocations"] = {}
                record["owner"] = None
                record["ownership_generation"] += 1
                record.pop("native_foreground", None)
                record.pop("native_output", None)
            store.change(state["revision"], revoke)
        journal["status"] = "applied"
        save_journal(root, path, journal)
        replace_content(local_path(root, LOCAL), local_after)
    return {"schema_version": 1, "operation_status": "ok", "command": "setup", "activation": value["activation"], "journal_path": path, "idempotent": False}


def barrier(root, value, name):
    # Fixture-only process fault controls never become native authority.
    if value["integrations"] and all(item["certification"] == "offline_fixture" for item in value["prerequisites"] if "certification" in item):
        path = local_path(root, ".agents/context/setup-fixture-barrier.json")
        if path.is_file():
            control = read_json(path.read_text(encoding="utf-8"))
            if control.get("after") == name:
                replace_content(local_path(root, ".agents/context/setup-fixture-reached"), "reached\n")
                while not local_path(root, ".agents/context/setup-fixture-release").exists():
                    time.sleep(0.02)


def rollback(root, path):
    journal = checked_journal(root, path)
    value = journal["plan"]
    if value["worktree_root"] != str(root):
        raise LifecycleError("SETUP_STALE", "rollback belongs to another worktree")
    config = load_config(root / value["config_path"], source=encoded(value["configuration"]).encode())
    store = StateStore(root, config.state_dir)
    protect_private_state(root, config, value["config_path"], runtime=False)
    with ExitStack() as locks:
        setup_store = lock_store(root)
        locks.enter_context(exclusive(setup_store))
        store.remaining_contention = setup_store.remaining_contention
        if store.directory.is_dir():
            locks.enter_context(exclusive(store))
        if journal["status"] == "rolled_back":
            return {"schema_version": 1, "operation_status": "ok", "command": "setup", "activation": "disabled", "journal_path": path}
        # Check the complete inverse set before the first effect.
        for item in journal["changes"]:
            actual = text(root, item["path"])
            if actual not in (item["before"], item["after"]):
                if item["path"] == LOCAL and checked_local(root)["journal_path"] == path:
                    continue
                raise LifecycleError("SETUP_CONFLICT", "unexpected edits prevent an exact inverse; preserve them and review owned registrations")
        local = checked_local(root)
        if local and local["journal_path"] != path:
            raise LifecycleError("SETUP_CONFLICT", "a later activation owns the current registrations")
        if local:
            replace_content(local_path(root, LOCAL), encoded(local | {"status": "rolling_back"}))
        journal["status"] = "rolling_back"
        save_journal(root, path, journal)
        for item in reversed(journal["changes"]):
            if item["path"] != LOCAL and text(root, item["path"]) == item["after"]:
                replace_content(local_path(root, item["path"]), item["before"])
        # Revoke rather than restoring stale live authority; pending/history survive.
        if store.path.exists():
            state = store.read()
            def revoke(record):
                record["owner"] = None
                record["invocations"] = {}
                record["ownership_generation"] += 1
                record.pop("native_foreground", None)
                record.pop("native_output", None)
            store.change(state["revision"], revoke)
        item = next(item for item in journal["changes"] if item["path"] == LOCAL)
        replace_content(local_path(root, LOCAL), item["before"])
        journal["status"] = "rolled_back"
        save_journal(root, path, journal)
    return {"schema_version": 1, "operation_status": "ok", "command": "setup", "activation": "disabled", "journal_path": path}


def run(arguments, root):
    name = arguments.config or ".agents/context/config.json"
    selected = Path(name)
    if selected.is_absolute():
        name = selected.relative_to(root).as_posix()
    local_path(root, name)
    if arguments.rollback:
        if arguments.apply or arguments.plan or arguments.deactivate:
            raise LifecycleError("USAGE_INVALID", "rollback takes only an exact managed journal path")
        path = Path(arguments.rollback)
        return rollback(root, path.relative_to(root).as_posix() if path.is_absolute() else path.as_posix())
    if arguments.apply:
        if not arguments.plan:
            raise LifecycleError("USAGE_INVALID", "setup --apply requires --plan PATH for the reviewed exact plan")
        return apply(root, read_plan(Path(arguments.plan)))
    if arguments.plan:
        raise LifecycleError("USAGE_INVALID", "--plan is an apply input; redirect setup --json to save a reviewed plan")
    return plan(root, name, deactivate=arguments.deactivate, shell=arguments.shell)
