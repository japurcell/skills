"""Read immutable Git content without modifying the source checkout."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import urlsplit


class AssetError(Exception):
    def __init__(self, code: str, message: str, exit_code: int = 2):
        super().__init__(message)
        self.code = code
        self.exit_code = exit_code


def git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C", str(repo), *args], capture_output=True, stdin=subprocess.DEVNULL,
                            timeout=60, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    if result.returncode:
        raise AssetError("ASSET_SOURCE_ERROR", "Git acquisition failed; check the source and requested revision.")
    return result.stdout


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(data: bytes, code: str):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result
    try:
        return json.loads(data, object_pairs_hook=unique,
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite number")))
    except (ValueError, UnicodeError):
        raise AssetError(code, "Expected unambiguous UTF-8 JSON; repair malformed or duplicate-key data.") from None


@contextmanager
def acquire(source: str, branch: str | None, revision: str | None):
    if any(value and (value.startswith("-") or any(ord(c) < 32 for c in value)) for value in (branch, revision)):
        raise AssetError("ASSET_SOURCE_INVALID", "Requested Git reference must be a name or commit, without options/control characters.")
    if not Path(source).expanduser().is_dir():
        url = urlsplit(source)
        scp = re.fullmatch(r"[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+:[^\s]+", source)
        if (url.scheme not in ("https", "ssh", "file") and not scp) or url.password or url.query or url.fragment or (
            url.username and url.scheme != "ssh"
        ) or any(ord(c) < 32 for c in source):
            raise AssetError("ASSET_SOURCE_INVALID", "Use a credential-free HTTPS/SSH Git URL or an existing local repository.")
    with tempfile.TemporaryDirectory(prefix="agent-assets-source-") as temporary:
        local = Path(source).expanduser()
        if local.is_dir():
            repo = local.resolve()
            branch = branch or (None if revision else git(repo, "symbolic-ref", "--short", "HEAD").decode().strip())
            location, kind = str(repo), "local"
        else:
            repo = Path(temporary) / "repo.git"
            result = subprocess.run(["git", "-c", "protocol.ext.allow=never", "clone", "--bare", "--", source, str(repo)],
                                    capture_output=True, stdin=subprocess.DEVNULL, timeout=60,
                                    env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
            if result.returncode:
                raise AssetError("ASSET_SOURCE_ERROR", "Cannot acquire the Git source; check URL and credentials.")
            branch = branch or (None if revision else git(repo, "symbolic-ref", "--short", "HEAD").decode().strip())
            location, kind = source, "git"
        ref = revision or f"refs/heads/{branch}"
        commit = git(repo, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}").decode().strip()
        policy = {"kind": "revision" if revision else "branch", "value": revision or branch}
        yield Snapshot(repo, commit, {"location": location, "kind": kind, "policy": policy})


class Snapshot:
    def __init__(self, repo: Path, commit: str, source: dict):
        self.repo, self.commit, self.source = repo, commit, source
        self.tree = {}
        for entry in git(repo, "ls-tree", "-rz", "--full-tree", commit).split(b"\0"):
            if entry:
                metadata, path = entry.split(b"\t", 1)
                mode, kind, oid = metadata.decode().split()
                self.tree[path.decode("utf-8")] = (mode, kind, oid)

    def read(self, path: str) -> tuple[bytes, bool]:
        entry = self.tree.get(path)
        if not entry or entry[0] not in ("100644", "100755") or entry[1] != "blob":
            raise AssetError("ASSET_SOURCE_INVALID", f"Expected a committed regular file: {path}")
        return git(self.repo, "cat-file", "blob", entry[2]), entry[0] == "100755"

    def catalog(self):
        data, _ = self.read("distribution/catalog.json")
        catalog = read_json(data, "ASSET_CATALOG_INVALID")
        if not isinstance(catalog, dict) or type(catalog.get("schema_version")) is not int or catalog["schema_version"] != 1 or not isinstance(catalog.get("assets"), dict):
            raise AssetError("ASSET_CATALOG_INVALID", "Unsupported catalog schema; use a compatible command checkout.")
        return catalog, data
