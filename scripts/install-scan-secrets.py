#!/usr/bin/env -S python3 -I -S -B
"""Install an isolated, provider-neutral checkpoint CLI without registration."""
from __future__ import annotations

import argparse
from contextlib import contextmanager, ExitStack
import ast
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import stat
import sys
import tempfile
import time
import unicodedata

VERSION = "1.0.0"
SCHEMA = "scan_secrets_install_v1"


class Failure(Exception):
    def __init__(self, reason, code=2):
        self.reason, self.code = reason, code


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Failure("invalid_arguments", 3)


def parser():
    common = Parser(add_help=False, allow_abbrev=False)
    for flag in ("--json", "--no-input", "--quiet", "--no-color"):
        common.add_argument(flag, action="store_true", default=argparse.SUPPRESS)
    root = Parser(prog="install-scan-secrets", parents=[common], allow_abbrev=False,
        description="Install explicit check/status commands. No PATH, Git or provider configuration changes.",
        epilog="Example: python3 -I -S -B scripts/install-scan-secrets.py install --dry-run. Invoke DESTINATION/scan-secrets on POSIX, or pwsh -NoProfile -File DESTINATION/scan-secrets.ps1 on Windows. Data remains in the documented platform data root outside the executable bundle.")
    root.add_argument("--version", action="version", version=f"install-scan-secrets {VERSION}; {SCHEMA}")
    actions = root.add_subparsers(dest="command")
    install = actions.add_parser("install", parents=[common], allow_abbrev=False, help="explicitly install or preflight the standalone runtime")
    install.add_argument("--destination", help="absolute private executable directory (default: platform user programs directory)")
    install.add_argument("--source-dir", default=str(Path(__file__).resolve().parent.parent), help="canonical source checkout")
    install.add_argument("--dry-run", action="store_true", help="validate exact source and destination without writes")
    help_command = actions.add_parser("help", allow_abbrev=False)
    help_command.add_argument("topic", nargs="?", choices=("install",))
    return root, install


def platform_roots():
    if os.name == "nt":
        data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
        executable = data / "Programs/scan-secrets"
    else:
        executable = Path.home() / ".local/lib/scan-secrets"
        data = Path(os.environ["XDG_DATA_HOME"]) if os.environ.get("XDG_DATA_HOME") else Path.home() / ("Library/Application Support" if sys.platform == "darwin" else ".local/share")
    return executable, data / "scan-secrets"


def absolute(path):
    path = Path(path)
    if not path.is_absolute():
        raise Failure("location_invalid", 3)
    # macOS system-owned aliases are the only accepted linked ancestors.
    for alias in (Path("/var"), Path("/tmp")) if sys.platform == "darwin" else ():
        if path.is_relative_to(alias):
            path = alias.resolve(strict=True) / path.relative_to(alias)
    if ".." in path.parts:
        raise Failure("location_invalid", 3)
    return path


def trusted_component(info):
    if info.st_uid not in {0, os.getuid()} or (info.st_mode & 0o022 and not (info.st_uid == 0 and info.st_mode & stat.S_ISVTX)):
        raise Failure("unsafe_destination")


def inspect_path(path, *, private=False, trusted=False):
    current = Path(path.anchor or ".")
    for component in (path.parts[1:] if path.anchor else path.parts):
        current /= component
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise Failure("unsafe_destination")
        if not stat.S_ISDIR(info.st_mode):
            raise Failure("unsafe_destination")
        if trusted and os.name != "nt":
            trusted_component(info)
        if current == path and private:
            if hasattr(os, "getuid") and (info.st_uid != os.getuid() or info.st_mode & 0o077):
                raise Failure("unsafe_destination")


def inspect_bundle(path, assets, destination):
    inspect_path(path, private=True, trusted=True)
    if not path.exists():
        return
    inventory = set()
    deadline = time.monotonic() + 10
    for parent, directories, files in os.walk(path, followlinks=False):
        for name in directories + files:
            entry = Path(parent) / name
            info = entry.lstat()
            inventory.add(str(entry.relative_to(path)).replace(os.sep, "/"))
            if len(inventory) > 64 or len(entry.relative_to(path).parts) > 5 or time.monotonic() > deadline:
                raise Failure("installation_inventory_invalid")
            if (stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400 or
                not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)) or
                (stat.S_ISREG(info.st_mode) and info.st_nlink != 1) or
                (hasattr(os, "getuid") and (info.st_uid != os.getuid() or info.st_mode & 0o077))):
                raise Failure("unsafe_destination")

    validate_owned(inventory, lambda name: bounded_read(path / name), assets, destination)


def bounded_read(path, *, reason="installation_ownership_invalid"):
    before = path.lstat()
    if stat.S_ISLNK(before.st_mode) or getattr(before, "st_file_attributes", 0) & 0x400:
        raise Failure(reason)
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        info = os.fstat(descriptor)
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > 1048576 or
            (before.st_dev, before.st_ino) != (info.st_dev, info.st_ino)):
            raise Failure(reason)
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            raw = stream.read(1048577)
        if len(raw) > 1048576 or len(raw) != info.st_size or os.fstat(descriptor).st_size != len(raw):
            raise Failure(reason)
        return raw
    finally:
        os.close(descriptor)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def runtime_asset_names(cli_bytes):
    """Read the declared closure as data, never by importing the runtime."""
    declarations = []
    for node in ast.parse(cli_bytes).body:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, (ast.AnnAssign, ast.AugAssign)) else []
        if any(isinstance(target, ast.Name) and target.id == "MODULES" for target in targets):
            declarations.append(node)
    if len(declarations) != 1 or not isinstance(declarations[0], ast.Assign) or len(declarations[0].targets) != 1:
        raise ValueError
    modules = ast.literal_eval(declarations[0].value)
    if (not isinstance(modules, tuple) or not modules or
        any(not isinstance(name, str) or not name.startswith("scan_") or not name.isidentifier() for name in modules) or
        len(set(modules)) != len(modules)):
        raise ValueError
    folded = {unicodedata.normalize("NFD", name).casefold() for name in modules}
    if len(folded) != len(modules) or {"scan_cli", "scan_status"}.intersection(folded):
        raise ValueError
    names = ("scripts/scan-secrets.py", "hooks/runtime/scan_cli.py", "hooks/runtime/scan_status.py", *(f"hooks/runtime/{name}.py" for name in modules))
    # Three directories, two launchers and one manifest share the reader cap.
    if len(names) + 6 > 64:
        raise ValueError
    return names


def validate_owned(inventory, read, assets, destination):
    try:
        raw = read("installation.json")
        if len(raw) > 32768:
            raise ValueError
        manifest = json.loads(raw, object_pairs_hook=unique_object)
        expected_keys = {"schema", "version", "interpreter", "entrypoint", "runtime", "data", "configuration", "files", "launchers"}
        if (not isinstance(manifest, dict) or set(manifest) != expected_keys or manifest["schema"] != SCHEMA or
            manifest["version"] != VERSION or manifest["configuration"] is not None or
            manifest["entrypoint"] != str(destination / "scripts/scan-secrets.py") or
            manifest["runtime"] != str(destination / "hooks/runtime") or
            any(not isinstance(manifest[key], str) or not Path(manifest[key]).is_absolute() for key in ("interpreter", "data")) or
            not isinstance(manifest["files"], dict) or not isinstance(manifest["launchers"], dict) or
            set(manifest["launchers"]) != {"scan-secrets", "scan-secrets.ps1"}):
            raise ValueError
        owned = {**manifest["files"], **manifest["launchers"]}
        if any(not isinstance(digest, str) or len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest) for digest in owned.values()):
            raise ValueError
        # Ownership describes the prior closure, independently of the desired
        # payload. Hash the protected declaration before parsing it as data.
        prior_cli = read("hooks/runtime/scan_cli.py")
        if hashlib.sha256(prior_cli).hexdigest() != manifest["files"].get("hooks/runtime/scan_cli.py"):
            raise ValueError
        if set(manifest["files"]) != set(runtime_asset_names(prior_cli)):
            raise ValueError
        launchers = bundle_payload(destination, {}, manifest["interpreter"], manifest["data"])
        if any(hashlib.sha256(launchers[name]).hexdigest() != digest for name, digest in manifest["launchers"].items()):
            raise ValueError
        expected = {*owned, "installation.json"}
        for name in list(expected):
            expected.update(str(parent).replace(os.sep, "/") for parent in Path(name).parents if str(parent) != ".")
        if inventory != expected:
            raise ValueError
        for name, digest in owned.items():
            if hashlib.sha256(read(name)).hexdigest() != digest:
                raise ValueError
    except (OSError, SyntaxError, ValueError, TypeError, KeyError):
        raise Failure("installation_ownership_invalid") from None


@contextmanager
def installation_parent(destination):
    """Hold every ancestor; all mutation names remain relative to this parent."""
    parent = destination.parent
    with ExitStack() as resources:
        original = os.open(".", os.O_RDONLY | os.O_DIRECTORY)
        resources.callback(os.close, original)
        resources.callback(os.fchdir, original)
        descriptor = os.open(parent.anchor, os.O_RDONLY | os.O_DIRECTORY)
        resources.callback(os.close, descriptor)
        trusted_component(os.fstat(descriptor))
        for component in parent.parts[1:]:
            try:
                child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            except FileNotFoundError:
                try:
                    os.mkdir(component, 0o700, dir_fd=descriptor)
                except FileExistsError:
                    pass
                child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            resources.callback(os.close, child)
            trusted_component(os.fstat(child))
            descriptor = child
        parent_info = os.fstat(descriptor)
        if parent_info.st_uid != os.getuid() or parent_info.st_mode & 0o022:
            raise Failure("unsafe_destination")
        os.fchdir(descriptor)
        yield Path(destination.name)


@contextmanager
def installer_lock(destination):
    path = destination.with_name(destination.name + ".install-lock")
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    except FileExistsError:
        descriptor = os.open(path, os.O_RDWR | getattr(os, "O_NOFOLLOW", 0))
    locked = False
    try:
        identity = os.fstat(descriptor)
        if not stat.S_ISREG(identity.st_mode) or identity.st_nlink != 1 or (hasattr(os, "getuid") and (identity.st_uid != os.getuid() or identity.st_mode & 0o077)):
            raise Failure("unsafe_destination")
        import fcntl
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Failure("installation_busy") from None
        locked = True
        yield
    finally:
        if locked:
            import fcntl
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def validate_native_api(raw):
    # Validate only the small shared handle contract; compatible optional
    # additions and implementation changes remain installable.
    contract = {
        "__init__": (("self", "resources"), (), 2),
        "information": (("self", "handle"), (), 2),
        "validate_name": (("self", "name"), (), 2),
        "open_handle": (("self", "name", "access"), ("directory", "create", "exclusive", "share_delete"), 2),
        "pin_root": (("self", "path"), ("access",), 2),
        "descend": (("self", "name"), ("create", "exclusive", "access"), 2),
        "stat": (("self", "name"), (), 2),
        "open": (("self", "name", "flags"), ("access", "normalize_readonly", "share_delete"), 3),
        "replace": (("self", "source", "destination"), (), 3),
        "remove": (("self", "name"), (), 2),
    }
    classes = [node for node in ast.parse(raw).body if isinstance(node, ast.ClassDef) and node.name == "WindowsDirectoryHandles"]
    if len(classes) != 1:
        raise ValueError
    methods = {node.name: node.args for node in classes[0].body if isinstance(node, ast.FunctionDef)}
    for name, (prefix, keywords, required) in contract.items():
        arguments = methods.get(name)
        if arguments is None:
            raise ValueError
        positional = tuple(argument.arg for argument in (*arguments.posonlyargs, *arguments.args))
        named = {argument.arg for argument in (*arguments.args, *arguments.kwonlyargs)}
        if (len(positional) < len(prefix) or not set(keywords).issubset(named) or
            len(positional) - len(arguments.defaults) > required or any(value is None for value in arguments.kw_defaults)):
            raise ValueError


def source_assets(source):
    try:
        cli = source / "hooks/runtime/scan_cli.py"
        cli_bytes = bounded_read(cli, reason="source_assets_invalid")
        names = runtime_asset_names(cli_bytes)
        assets = {}
        for name in names:
            path = source / name
            raw = cli_bytes if name == "hooks/runtime/scan_cli.py" else bounded_read(path, reason="source_assets_invalid")
            compile(raw, name, "exec")
            assets[name] = raw
        validate_native_api(assets["hooks/runtime/scan_native_file.py"])
        return assets
    except (OSError, SyntaxError, ValueError, StopIteration, TypeError, KeyError):
        raise Failure("source_assets_invalid") from None


def private_directory(path):
    path.mkdir(mode=0o700)


def write(path, raw, mode=0o600):
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    path.chmod(mode)


def verify_binding(binding):
    inspect_path(binding.parent, trusted=True)
    current, recorded = os.stat("."), binding.parent.stat()
    if (current.st_dev, current.st_ino) != (recorded.st_dev, recorded.st_ino):
        raise Failure("unsafe_destination")


def bundle_payload(binding, assets, interpreter, data):
    entry = binding / "scripts/scan-secrets.py"
    shell = "#!/bin/sh\nexec " + " ".join(shlex.quote(item) for item in (str(interpreter), "-I", "-S", "-B", str(entry))) + ' "$@"\n'
    quote = lambda value: "'" + str(value).replace("'", "''") + "'"
    powershell = "#!/usr/bin/env pwsh\n& " + quote(interpreter) + " -I -S -B " + quote(entry) + " @args\nexit $LASTEXITCODE\n"
    manifest = {"schema": SCHEMA, "version": VERSION, "interpreter": str(interpreter), "entrypoint": str(entry), "runtime": str(binding / "hooks/runtime"), "data": str(data), "configuration": None,
                "files": {name: hashlib.sha256(raw).hexdigest() for name, raw in assets.items()},
                "launchers": {"scan-secrets": hashlib.sha256(shell.encode()).hexdigest(), "scan-secrets.ps1": hashlib.sha256(powershell.encode()).hexdigest()}}
    return {**assets, "scan-secrets": shell.encode(), "scan-secrets.ps1": powershell.encode(),
            "installation.json": (json.dumps(manifest, sort_keys=True) + "\n").encode()}


def deploy(destination, assets, interpreter, data, binding):
    verify_binding(binding)
    previous = destination.with_name(destination.name + ".previous")
    # An interrupted promotion leaves either the old bundle or its complete backup.
    if previous.exists() and not destination.exists():
        os.replace(previous, destination)
    elif previous.exists():
        shutil.rmtree(previous)
    stage = Path(tempfile.mkdtemp(prefix=".scan-secrets-stage-", dir=destination.parent))
    try:
        for relative, raw in bundle_payload(binding, assets, interpreter, data).items():
            output = stage / relative
            for parent in reversed(output.relative_to(stage).parents):
                directory = stage / parent
                if not directory.exists():
                    private_directory(directory)
            write(output, raw, 0o700 if relative in {"scan-secrets", "scan-secrets.ps1"} else 0o600)
        verify_binding(binding)
        if destination.exists():
            os.replace(destination, previous)
        try:
            os.replace(stage, destination)
        except BaseException:
            if previous.exists():
                os.replace(previous, destination)
            raise
        if previous.exists():
            shutil.rmtree(previous)
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def main(argv):
    json_mode = "--json" in argv
    try:
        root, install = parser()
        args = root.parse_args(argv)
        if args.command is None or args.command == "help":
            (install if getattr(args, "topic", None) == "install" else root).print_help()
            return 0
        default, data = platform_roots()
        destination = absolute(args.destination or default)
        data = absolute(data)
        if data == destination or data.is_relative_to(destination) or destination.is_relative_to(data):
            raise Failure("locations_overlap", 3)
        assets = source_assets(Path(args.source_dir))
        interpreter = Path(sys.executable).resolve(strict=True)
        inspect_path(data)
        # Capture installer support even on POSIX: either platform must fail exact-asset preflight.
        try:
            support = Path(args.source_dir) / "scripts/scan_install_windows.py"
            support_bytes = bounded_read(support, reason="source_assets_invalid")
            compile(support_bytes, "scan_install_windows.py", "exec")
        except (OSError, ValueError, SyntaxError):
            raise Failure("source_assets_invalid") from None
        if os.name == "nt":
            namespace = {}
            exec(compile(support_bytes, "scan_install_windows.py", "exec"), namespace)
            namespace["install"](destination, assets, bundle_payload(destination, assets, interpreter, data),
                validate_owned, Failure, dry_run=args.dry_run)
        else:
            if destination.parent.exists():
                parent_info = destination.parent.stat()
                if parent_info.st_uid != os.getuid() or parent_info.st_mode & 0o022:
                    raise Failure("unsafe_destination")
            inspect_bundle(destination, assets, destination)
            inspect_bundle(destination.with_name(destination.name + ".previous"), assets, destination)
            if not args.dry_run:
                with installation_parent(destination) as local:
                    with installer_lock(local):
                        inspect_bundle(local, assets, destination)
                        inspect_bundle(local.with_name(local.name + ".previous"), assets, destination)
                        deploy(local, assets, interpreter, data, destination)
        value = {"schema": SCHEMA, "version": VERSION, "outcome": "validated" if args.dry_run else "installed", "destination": str(destination), "interpreter": str(interpreter), "data": str(data), "asset_count": len(assets)}
        if json_mode:
            print(json.dumps(value, separators=(",", ":")))
        elif not getattr(args, "quiet", False):
            print(f"scan-secrets: {value['outcome']}; {destination}")
        return 0
    except KeyboardInterrupt:
        reason, code = "cancelled", 130
    except Failure as failure:
        reason, code = failure.reason, failure.code
    except Exception:
        reason, code = "installation_failed", 2
    recovery = "Run install-scan-secrets help install; restore exact source assets or repair the private destination, then rerun explicit install. An interrupted promotion retains the previous complete bundle in the sibling .previous directory; rerun install to recover. The sibling .install-lock is a stable owner-only advisory lock; process termination releases it, so leave the file in place."
    value = {"schema": SCHEMA, "version": VERSION, "outcome": "invalid" if code == 3 else "incomplete", "reason": reason, "phase": "installation", "recovery": recovery}
    if json_mode:
        print(json.dumps(value, separators=(",", ":")))
    else:
        print(f"scan-secrets installer: {reason}. {recovery}", file=sys.stderr)
    return code


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except BrokenPipeError:
        os._exit(2)
