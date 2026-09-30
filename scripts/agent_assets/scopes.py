"""Explicit installation layouts and exact private Git excludes."""

from dataclasses import dataclass
from pathlib import Path
import os
import sys
import subprocess
import tempfile

from .sources import AssetError, git


@dataclass(frozen=True)
class Layout:
    scope: str = "repo"
    mode: str = "team"
    codex_home: str | None = None

    @property
    def records(self):
        prefix = ".agent-assets/local" if self.mode == "local" else ".agent-assets"
        return (prefix + "/selection.json", prefix + "/lock.json")

    def state(self, root, name):
        if self.scope == "user":
            return root / ".agent-assets/state" / name
        return Path(git(root, "rev-parse", "--path-format=absolute", "--git-path", name).decode().strip())

    def exclude(self, root):
        return self.state(root, "info/exclude").as_posix()


def target(args):
    override = args.codex_home
    if not override and args.scope == "user" and (not args.home or Path(args.home).expanduser().resolve() == Path.home().resolve()):
        override = os.environ.get("CODEX_HOME")
    layout = Layout(args.scope, args.mode, str(absolute_path(override)) if override else None)
    if override and layout.scope != "user":
        raise AssetError("ASSET_SELECTION_INVALID", "--codex-home requires --scope user.")
    if layout.scope == "user":
        if args.repo or layout.mode != "team":
            raise AssetError("ASSET_SELECTION_INVALID", "Personal scope cannot use --repo or --mode local.")
        root = absolute_path(args.home or Path.home())
        from .core import inspect_destination
        inspect_destination(Path("/"), (root / ".agent-assets-home-check").as_posix())
        if not root.is_dir():
            raise AssetError("ASSET_SELECTION_INVALID", "Personal home must be an existing directory.")
        return root.resolve(), layout
    if args.home:
        raise AssetError("ASSET_SELECTION_INVALID", "--home requires --scope user.")
    return Path(git(Path(args.repo or "."), "rev-parse", "--show-toplevel").decode().strip()).resolve(), layout


def private_preflight(root, paths):
    if not paths:
        return
    tracked = git(root, "ls-files", "-z", "--", *paths)
    if tracked:
        raise AssetError("ASSET_LOCAL_TRACKED_CONFLICT", "Private installation would change or hide tracked paths; use team mode or reconcile native configuration explicitly.", 1)


def other_records(root, layout):
    from .core import inspect_destination, read_records, authenticate_ownership
    if layout.scope != "repo":
        return None, []
    other = Layout(mode="local" if layout.mode == "team" else "team")
    for name in other.records:
        inspect_destination(root, name)
    if not any((root / name).exists() for name in other.records):
        return None, list(other.records)
    pair = read_records(*(root / name for name in other.records))
    if pair[0]["scope"] != other.scope or pair[0]["mode"] != other.mode:
        raise AssetError("ASSET_RECORD_INVALID", "Scope records are stored in the wrong layout.")
    authenticate_ownership(pair)
    return pair, [*other.records, *(item["destination"] for item in pair[1]["items"])]


def shared_item(path, data, mode, spec, other):
    from .sources import digest
    if other is None:
        return None
    item = next((item for item in other[1]["items"] if item["destination"] == path), None)
    if item is None:
        return None
    if item["baseline_digest"] != digest(data) or item["mode"] != mode or item.get("entries") != spec.get("configuration"):
        raise AssetError("ASSET_CONFLICT", "Other scope requires different bytes or entries: " + path, 1)
    return item


def exclude_line(path):
    # Escape Git wildcards, spaces, and comment/negation syntax literally.
    return ("/" + "".join("\\" + char if char in "\\*?[] !#" else char for char in path) + "\n").encode()


def plan_excludes(root, layout, paths, existing):
    from .core import inspect_destination
    path = layout.exclude(root)
    inspect_destination(root, path)
    target = Path(path)
    data = target.read_bytes() if target.exists() else b""
    old = existing[1].get("excludes", []) if existing else []
    # Only exact recorded lines are owned; arbitrary text and other worktrees'
    # identical lines remain untouched. Retain entries rather than pruning
    # shared excludes, since Git's info/exclude is common to linked worktrees.
    if any(data.count(exclude_line(name)) != 1 for name in old):
        raise AssetError("ASSET_CONFLICT", "Managed private exclude was changed; restore the exact rule before updating.", 1)
    result = data
    owned = list(old)
    for name in sorted(set(paths)):
        line = exclude_line(name)
        if line not in result.splitlines(keepends=True):
            if result and not result.endswith(b"\n"):
                result += b"\n"
            result += line
            owned.append(name)
    effective_excludes(root, paths, proposed=result)
    return path, result, sorted(set(owned) & set(paths))


def effective_excludes(root, paths, *, proposed=None):
    """Ask Git to resolve ignore precedence without filters or index refresh."""
    from .core import inspect_destination
    paths = sorted(set(paths))
    if not paths:
        return
    def check(directory):
        result = subprocess.run(["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C", str(directory),
                                 "check-ignore", "--no-index", "--verbose", "--non-matching", "-z", "--stdin"],
                                input=b"".join(os.fsencode(path) + b"\0" for path in paths), capture_output=True, timeout=60)
        fields = result.stdout.split(b"\0")
        matches = {os.fsdecode(fields[index + 3]): fields[index + 2] for index in range(0, len(fields) - 1, 4)}
        if result.returncode not in (0, 1) or any(not matches.get(path) or matches[path].startswith(b"!") for path in paths):
            raise AssetError("ASSET_LOCAL_IGNORE_CONFLICT", "Effective Git ignore rules expose private paths; reconcile negated or higher-precedence rules before installation.", 1)
    if proposed is None:
        check(root)
        return
    # Every required path has an exact info/exclude rule, so lower-priority
    # global excludes cannot change its result. Copy only relevant .gitignore
    # policy, preserving directory structure, into a disposable Git mirror.
    with tempfile.TemporaryDirectory(prefix="agent-assets-ignore-") as temporary:
        mirror = Path(temporary)
        git(mirror, "init", "-q")
        (mirror / ".git/info/exclude").write_bytes(proposed)
        parents = {parent for path in paths for parent in Path(path).parents}
        for parent in sorted(parents):
            (mirror / parent).mkdir(parents=True, exist_ok=True)
            relative = (parent / ".gitignore").as_posix()
            inspect_destination(root, relative)
            if (root / relative).exists():
                (mirror / relative).write_bytes((root / relative).read_bytes())
        # Match repository case policy rather than relying on the mirror's
        # filesystem default. Do not copy arbitrary repository configuration.
        for entry in git(root, "config", "--null", "--list").split(b"\0"):
            key, _, value = entry.partition(b"\n")
            if key == b"core.ignorecase":
                git(mirror, "config", "core.ignorecase", value.decode())
        check(mirror)


def verify_excludes(root, layout, selection, lock):
    from .core import inspect_destination
    path = layout.exclude(root)
    inspect_destination(root, path)
    data = Path(path).read_bytes() if Path(path).exists() else b""
    required = [*layout.records, *(item["destination"] for item in lock["items"] if "borrowed_from" not in item)]
    if any(exclude_line(name) not in data.splitlines(keepends=True) for name in required):
        raise AssetError("ASSET_CONFLICT", "A required exact private exclude is missing.", 1)
    if git(root, "ls-files", "-z", "--", *required):
        raise AssetError("ASSET_LOCAL_TRACKED_CONFLICT", "Private nonborrowed paths are tracked; exact excludes cannot hide tracked files.", 1)
    effective_excludes(root, required)


def check_shared_excludes(root):
    # Git resolves info/exclude to the common directory. Never remove a shared
    # rule while another worktree has private records that might require it.
    for field in git(root, "worktree", "list", "--porcelain", "-z").split(b"\0"):
        if not field.startswith(b"worktree "):
            continue
        worktree = Path(os.fsdecode(field[9:])).resolve()
        if worktree == root:
            continue
        if any((worktree / name).exists() or (worktree / name).is_symlink() for name in Layout(mode="local").records):
            raise AssetError("ASSET_CONFLICT", "Cannot promote private files while another worktree has local records sharing Git excludes; reconcile that worktree explicitly first.", 1)


def validate_layout(selection, layout):
    if (selection["scope"], selection["mode"], selection.get("codex_home")) != (layout.scope, layout.mode, layout.codex_home):
        raise AssetError("ASSET_RECORD_INVALID", "Recorded scope or Codex override differs from explicit authority; pass the same --scope, --mode and --codex-home (or CODEX_HOME in that home).")


def promote(root, layout, other, files, installation_id, *, explicit, existing):
    """Make explicit team selection visible and turn local requirements into borrowers."""
    from copy import deepcopy
    from .sources import canonical
    if layout.scope != "repo" or layout.mode != "team" or other is None:
        return {}
    overlap = {item["destination"] for item in other[1]["items"]} & set(files)
    promoted = {path for path in overlap if next(item for item in other[1]["items"] if item["destination"] == path).get("borrowed_from") != installation_id}
    old_paths = {item["destination"] for item in existing[1]["items"]} if existing else set()
    released = {item["destination"] for item in other[1]["items"] if item["destination"] in old_paths - set(files)
                and item.get("borrowed_from") == installation_id
                and not git(root, "ls-files", "-z", "--", item["destination"])}
    if not promoted and not released:
        return {}
    if promoted and not explicit:
        raise AssetError("ASSET_CONFLICT", "Promoting local files requires an explicit install selection.", 1)
    if promoted:
        check_shared_excludes(root)
    local = Layout(mode="local")
    lock = deepcopy(other[1])
    exclude, data, _ = plan_excludes(root, local, [], other)
    for path in promoted:
        if path in lock.get("excludes", []):
            data = data.replace(exclude_line(path), b"")
            lock["excludes"].remove(path)
        for item in lock["items"]:
            if item["destination"] == path:
                item["borrowed_from"] = installation_id
    for item in lock["items"]:
        if item["destination"] in released:
            item.pop("borrowed_from", None)
            line = exclude_line(item["destination"])
            if line not in data.splitlines(keepends=True):
                data += (b"\n" if data and not data.endswith(b"\n") else b"") + line
                lock.setdefault("excludes", []).append(item["destination"])
    lock["excludes"] = sorted(lock.get("excludes", []))
    effective_excludes(root, [*local.records, *(item["destination"] for item in lock["items"] if "borrowed_from" not in item)], proposed=data)
    return {local.records[1]: (canonical(lock) + b"\n", 0o644),
            exclude: (data, Path(exclude).stat().st_mode & 0o777)}


def absolute_path(value):
    path = Path(value).expanduser().absolute()
    if sys.platform == "darwin" and path.parts[1:2] in (("var",), ("tmp",)):
        path = Path("/private") / path.relative_to("/")
    return path
