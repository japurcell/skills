"""Synchronous scan-before-upload dispatch for an explicitly bound Git action.

The binding is an installation input, not a saved scan receipt. Every action
gets a new parent-owned directory, scanner process, audit, and verified handoff.
Only the pinned basic-HTTP uploader sees private verified payload copies.
"""
from __future__ import annotations

import contextlib
import hashlib
import os
from pathlib import Path
import re
import secrets
import stat
import sys
import tempfile
import time
from urllib.parse import urlsplit

from .scan_budget import DEFAULTS, load_budget
from .scan_gate import repository_identity, validate_result
from .scan_git import capture_git
from .scan_private import Directory, encoded, decoded
from .scan_repository import ProtectedRepository
from .scan_transaction import capture_transaction
from .scan_types import ScanContext, ScanLimits, ScanFailure, ScanSecurityError, ScanLimitExceeded

SCHEMA = "scan_secrets_dispatch_v1"
BINDING_KEYS = {"schema_version", "build", "repository_identity", "budget_file", "interpreter", "data_directory", "downstream_seconds", "endpoint", "lfs", "steps", "remote", "url"}


def binding(repository, args, build):
    with repository.open_selected(Path(os.path.abspath(args.binding))) as descriptor:
        info = os.fstat(descriptor)
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1:
            raise ValueError()
        raw = repository.read(Path(args.binding), descriptor=descriptor, maximum=131072)
    value = decoded(raw)
    if (type(value) is not dict or value.keys() != BINDING_KEYS or type(value["schema_version"]) is not int
            or value["schema_version"] != 1 or value["build"] != build
            or value["repository_identity"] != repository_identity(repository)
            or value["interpreter"] != str(Path(sys.executable).resolve())
            or type(value["data_directory"]) is not str or not Path(value["data_directory"]).is_absolute()
            or Path(value["data_directory"]).name != "scan-secrets"
            or (value["budget_file"] is not None and (type(value["budget_file"]) is not str or not Path(value["budget_file"]).is_absolute()))
            or [value["remote"], value["url"]] != args.destination
            or type(value["downstream_seconds"]) is not int or not 1 <= value["downstream_seconds"] <= 600
            or type(value["steps"]) is not list or len(value["steps"]) > 32):
        raise ValueError()
    lfs_steps = 0
    for step in value["steps"]:
        if step == {"kind": "lfs"}:
            lfs_steps += 1
        elif (type(step) is not dict or step.keys() != {"kind", "path", "sha256"} or step["kind"] != "hook"
              or type(step["path"]) is not str or not Path(step["path"]).is_absolute()
              or type(step["sha256"]) is not str or re.fullmatch(r"[0-9a-f]{64}", step["sha256"]) is None):
            raise ValueError()
    if lfs_steps > 1:
        raise ValueError()
    if lfs_steps:
        lfs = value["lfs"]
        if (type(lfs) is not dict or lfs.keys() != {"path", "sha256", "version"} or lfs["version"] != "3.8.0"
                or type(lfs["path"]) is not str or not Path(lfs["path"]).is_absolute()
                or type(lfs["sha256"]) is not str or re.fullmatch(r"[0-9a-f]{64}", lfs["sha256"]) is None):
            raise ValueError()
        if (type(value["endpoint"]) is not str or len(value["endpoint"]) > 8192
                or any(ord(c) <= 32 or c in '"\\' for c in value["endpoint"])):
            raise ValueError()
        endpoint = urlsplit(value["endpoint"])
        if (endpoint.scheme not in {"http", "https"} or not endpoint.hostname or endpoint.username or endpoint.password
                or endpoint.query or endpoint.fragment or (endpoint.scheme == "http" and endpoint.hostname != "127.0.0.1")):
            raise ValueError()
    elif value["lfs"] is not None or value["endpoint"] is not None:
        raise ValueError()
    return value, hashlib.sha256(raw).hexdigest()


def scan_request(path, repository, transaction, build, budget_identity, *, resources=None):
    if os.name != "posix":
        raise ScanSecurityError("dispatch_platform_unsupported", "repository")
    directory = Directory(path, repository.context, repository.resources if resources is None else resources)
    request = decoded(directory.read("request.json"))
    expected = dict(schema_version=1, build=build, policy="publication_v1", budget_identity=budget_identity,
        repository_identity=repository_identity(repository), transaction_identity=transaction.identity,
        destination_identity=transaction.destination_identity)
    if (type(request) is not dict or request.keys() != expected.keys() | {"nonce", "binding_identity"}
            or any(type(request[key]) is not type(value) or request[key] != value for key, value in expected.items())
            or any(type(request[key]) is not str or re.fullmatch(r"[0-9a-f]{64}", request[key]) is None
                   for key in ("nonce", "binding_identity"))):
        raise ScanSecurityError("handoff_invalid", "repository")
    payloads = directory.child("payloads")
    return directory, payloads, request


def write_handoff(directory, request, records):
    raw = encoded(dict(schema_version=1, request=request, objects=records))
    directory.write("handoff.json", raw)
    return hashlib.sha256(raw).hexdigest()


def verified_handoff(directory, request, result):
    raw = directory.read("handoff.json", maximum=4096 + result["counts"]["lfs_objects"] * 256)
    if hashlib.sha256(raw).hexdigest() != result["lfs_handoff_identity"]:
        raise ValueError()
    value = decoded(raw)
    if type(value) is not dict or value.keys() != {"schema_version", "request", "objects"} or type(value["schema_version"]) is not int or value["schema_version"] != 1 or value["request"] != request:
        raise ValueError()
    records = value["objects"]
    if type(records) is not list or len(records) != result["counts"]["lfs_objects"]:
        raise ValueError()
    source = directory.child("payloads")
    verified = directory.child("upload", create=True)
    store = verified.child("objects", create=True)
    seen = set()
    first_seen = set()
    second_seen = set()
    size = 0
    for item in records:
        if (type(item) is not dict or item.keys() != {"oid", "size", "path"}
                or type(item["oid"]) is not str or re.fullmatch(r"[0-9a-f]{64}", item["oid"]) is None
                or item["oid"] in seen or type(item["size"]) is not int or not 0 <= item["size"] < 2**63
                or item["path"] != "payloads/" + item["oid"]):
            raise ValueError()
        seen.add(item["oid"])
        size += item["size"]
        with source.open(item["oid"]) as (handle, info):
            if info.st_size != item["size"]:
                raise ValueError()
            prefix, suffix = item["oid"][:2], item["oid"][2:4]
            with store.child(prefix, create=prefix not in first_seen) as first:
                with first.child(suffix, create=(prefix, suffix) not in second_seen) as second:
                    _, copied = second.copy(item["oid"], handle, item["oid"], maximum=item["size"])
                    if copied != item["size"]:
                        raise ValueError()
            first_seen.add(prefix)
            second_seen.add((prefix, suffix))
    if size != result["counts"]["lfs_payload_bytes"]:
        raise ValueError()
    return verified, sorted(seen)


def verify_upload(directory, oids, records):
    expected = {item["oid"]: item["size"] for item in records}
    objects = directory.child("objects")
    for oid in oids:
        with objects.child(oid[:2]) as first:
            with first.child(oid[2:4]) as second:
                with second.open(oid) as (handle, info):
                    if info.st_size != expected[oid]:
                        raise ValueError()
                    digest = hashlib.sha256()
                    while True:
                        directory.context.check_deadline()
                        chunk = handle.read(65536)
                        if not chunk:
                            break
                        directory.context.charge_capture(len(chunk))
                        digest.update(chunk)
                    if digest.hexdigest() != oid:
                        raise ValueError()


def git_value(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def process(context, executable, args, *, cwd, environment, raw):
    with capture_git(context, args, cwd=cwd, executable=str(executable), environment=environment,
                     input_bytes=raw, allow_nonzero=True, command_seconds=context.limits.max_seconds,
                     deadline=context.deadline) as result:
        # Captured hook/uploader output is deliberately never replayed: an
        # arbitrary hook can print payloads, URLs, credentials or terminal codes.
        return result.exit_code


def copy_tool(repository, directory, name, path, digest, *, maximum=None):
    maximum = repository.context.limits.max_capture_bytes if maximum is None else maximum
    with repository.open_selected(Path(path)) as descriptor:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > maximum:
            raise ValueError()
        with os.fdopen(os.dup(descriptor), "rb") as handle:
            result, size = directory.copy(name, handle, digest, maximum=maximum, mode=0o500)
        after = os.fstat(descriptor)
        if (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError()
    return result


def terminal_failure(value, code, reason, phase, recovery, diagnostic=None):
    # Cleanup may interrupt a return after the value was marked successful.
    # Always replace all terminal fields together, retaining transmitted counts.
    value.update(outcome="incomplete", exit_code=code, reason=reason, phase=phase,
                 recovery=recovery, diagnostic=diagnostic)
    return value, code


def run(args, *, build, entry):
    value = dict(schema=SCHEMA, outcome="incomplete", reason="dispatch_unavailable", phase="initialization", uploaded_objects=0, completed_steps=0, exit_code=2,
                 recovery="Restore the current installation binding and rerun the explicit Git action.")
    try:
        if os.name != "posix":
            raise ScanSecurityError("dispatch_platform_unsupported", "repository")
        if len(args.destination) != 2 or any(not item or len(os.fsencode(item)) > 8192 or any(c in item for c in "\r\n\0") for item in args.destination):
            value.update(outcome="invalid", reason="destination_invalid", exit_code=3)
            return value, 3
        # Preparation and scanner execution have a finite inspection deadline.
        # Downstream steps share a separate explicit wall-clock deadline.
        context = ScanContext(ScanLimits(**DEFAULTS["publication"], max_capture_total_bytes=DEFAULTS["publication"]["max_capture_bytes"]))
        with contextlib.ExitStack() as resources:
            repository = resources.enter_context(ProtectedRepository(context, args.repo, publication=True, executable=getattr(args, "git", None)))
            value["phase"] = "binding"
            try:
                configured, binding_identity = binding(repository, args, build)
            except (ValueError, TypeError):
                value.update(outcome="invalid", reason="binding_invalid", phase="configuration", exit_code=3)
                return value, 3
            root = Path(tempfile.mkdtemp(prefix="scan-dispatch-"))
            directory = Directory(root, context, resources)
            resources.callback(directory.cleanup)
            directory.child("payloads", create=True)
            if configured["budget_file"] is not None:
                budget_source = Path(configured["budget_file"])
                with repository.open_selected(budget_source) as descriptor:
                    info = os.fstat(descriptor)
                    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1
                            or stat.S_IMODE(info.st_mode) & 0o022):
                        value.update(outcome="invalid", reason="budget_untrusted", phase="configuration", exit_code=3,
                            recovery="Use a single-link ordinary budget file owned by the invoking user, without group or other write permission, and retry.")
                        return value, 3
                    budget_raw = repository.read(budget_source, descriptor=descriptor, maximum=65536)
            else:
                budget_raw = encoded(dict(schema_version=1, **DEFAULTS))
            # Private staging and capture/deadline failures are infrastructure,
            # outside the narrow invalid-document parsing boundary.
            budget_path = directory.write("budget.json", budget_raw)
            try:
                limits, budget_identity = load_budget(str(budget_path), profile="publication")
            except (ValueError, TypeError):
                value.update(outcome="invalid", reason="budget_invalid", phase="configuration", exit_code=3,
                    recovery="Repair the owner-selected schema-1 budget file with complete finite profiles and retry; reinstalling is unnecessary.")
                return value, 3
            context.limits = ScanLimits(**limits, max_capture_total_bytes=limits["max_capture_bytes"])
            context.deadline = context.started + limits["max_seconds"]
            transaction = capture_transaction(repository.object_format, *args.destination, context)
            request = dict(schema_version=1, build=build, policy="publication_v1", budget_identity=budget_identity,
                repository_identity=repository_identity(repository), transaction_identity=transaction.identity,
                destination_identity=transaction.destination_identity, nonce=secrets.token_hex(32), binding_identity=binding_identity)
            directory.write("request.json", encoded(request))
            value.update(build=build, policy_version="publication_v1", budget_identity=budget_identity,
                transaction_identity=transaction.identity, destination_identity=transaction.destination_identity)
            value["phase"] = "inspection"
            scanner_environment = os.environ.copy()
            scanner_environment["XDG_DATA_HOME"] = str(Path(configured["data_directory"]).parent)
            parent_scan_temp = context.temp_bytes + len(transaction.raw)
            with capture_git(context, ["-I", "-S", "-B", str(entry), "gate", "pre-push", "--repo", str(repository.root), "--json",
                    *(["--git", args.git] if getattr(args, "git", None) else []), "--remote", args.destination[0], "--url", args.destination[1], "--budget-file", str(budget_path), "--invocation", str(root)],
                    cwd=repository.root, executable=sys.executable, environment=scanner_environment, input_bytes=transaction.raw,
                    allow_nonzero=True, command_seconds=limits["max_seconds"], deadline=context.deadline) as scan:
                raw = b"".join(scan.chunks())
                result = validate_result(raw, scan.exit_code, action="pre-push", build=build,
                    repository_identity=request["repository_identity"], budget_identity=budget_identity,
                    transaction_identity=transaction.identity, destination_identity=transaction.destination_identity)
                value.update(inspection_counts=result["counts"], security_outcome=result["security_outcome"])
                if scan.exit_code:
                    value.update(outcome=result["outcome"], coverage_complete=result["coverage_complete"],
                        reason=result["reason"], phase=result["phase"], recovery=result["recovery"], diagnostic=result["diagnostic"],
                        audit_outcome=result["audit_outcome"], status_outcome=result["status_outcome"],
                        security_outcome=result["security_outcome"], counts=result["counts"], findings=result["findings"], exit_code=scan.exit_code)
                    return value, scan.exit_code
            # Reconcile the scanner process's actual captures into this
            # invocation's aggregate budget before any downstream work.
            context.charge_capture(result["counts"]["capture_bytes"])
            composed_peak = parent_scan_temp + result["counts"]["temp_peak_bytes"] + len(raw)
            if composed_peak > limits["max_temp_bytes"]:
                raise ScanLimitExceeded("temporary_bytes_limit", "repository", measured=composed_peak, limit=limits["max_temp_bytes"])
            context.temp_peak_bytes = max(context.temp_peak_bytes, composed_peak)
            value["phase"] = "handoff"
            context.charge_temp(result["counts"]["lfs_payload_bytes"])
            context.charge_temp(len(directory.read("handoff.json", maximum=4096 + result["counts"]["lfs_objects"] * 256)))
            verified, oids = verified_handoff(directory, request, result)
            if oids and (sys.platform != "darwin" or repository.object_format != "sha1" or {"kind": "lfs"} not in configured["steps"]):
                raise ScanSecurityError("lfs_unsupported", "repository")
            # Every pinned hook/tool is captured and verified before any
            # upload-capable step is allowed to start.
            tools = directory.child("tools", create=True)
            commands = []
            for index, step in enumerate(configured["steps"]):
                if step["kind"] == "hook":
                    copy_tool(repository, tools, str(index), step["path"], step["sha256"])
                    commands.append(Path(step["path"]))
                else:
                    commands.append(None)
            uploader = copy_tool(repository, tools, "git-lfs", configured["lfs"]["path"], configured["lfs"]["sha256"]) if oids else None
            environment = None
            if oids:
                private = directory.child("uploader.git", create=True)
                private.child("objects", create=True)
                private.child("refs", create=True)
                private.write("HEAD", b"ref: refs/heads/unborn\n")
                # No source config/index/HEAD/.lfsconfig or custom transfer agent is
                # imported into this empty uploader repository.
                config = ("[core]\nrepositoryformatversion = 0\nbare = true\n"
                    "[remote \"fixture\"]\nurl = " + git_value(configured["endpoint"]) + "\n"
                    "[lfs]\nurl = " + git_value(configured["endpoint"]) + "\nstorage = " + git_value(str(verified.path)) + "\n"
                    "basictransfersonly = true\nconcurrenttransfers = 1\nallowincompletepush = false\n"
                    "dialtimeout = 5\ntlstimeout = 5\nactivitytimeout = 5\n"
                    "[lfs \"transfer\"]\nmaxretries = 1\nmaxretrydelay = 0\nmaxretrytime = 1\n")
                private.write("config", config.encode())
                environment = repository.environment.copy()
                environment = {key: item for key, item in environment.items() if not key.startswith("GIT_")}
                environment.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull,
                    GIT_TERMINAL_PROMPT="0", GIT_ASKPASS="", GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1",
                    GIT_DIR=str(private.path), GIT_COMMON_DIR=str(private.path), GIT_WORK_TREE=str(root),
                    GIT_INDEX_FILE=str(private.path / "unused-index"), GIT_OPTIONAL_LOCKS="0")
            # Account retained files in the shared finite downstream temporary
            # ceiling; inspection/capture has its own already enforced budget.
            downstream = ScanContext(ScanLimits(**{**limits, "max_seconds": configured["downstream_seconds"]}, max_capture_total_bytes=limits["max_capture_bytes"]))
            downstream.charge_temp(context.temp_bytes)
            downstream.capture_bytes = context.capture_bytes
            if uploader is not None:
                with capture_git(downstream, ["version"], cwd=root, executable=str(uploader), environment=environment,
                                 command_seconds=5, deadline=downstream.deadline) as version:
                    if version.size > 256 or not b"".join(version.chunks()).startswith(b"git-lfs/3.8.0 "):
                        raise ScanSecurityError("lfs_unsupported", "repository")
            value["phase"] = "downstream"
            directory.validate()
            for step, command in zip(configured["steps"], commands):
                downstream.check_deadline()
                if step["kind"] == "lfs":
                    if not oids:
                        continue
                    # Prior hooks have completed and have no surviving process
                    # group. Recheck the exact current handoff and upload bytes
                    # before the only controlled uploader is allowed to start.
                    latest_raw = directory.read("handoff.json", maximum=4096 + result["counts"]["lfs_objects"] * 256)
                    latest = decoded(latest_raw)
                    if latest["request"] != request or hashlib.sha256(latest_raw).hexdigest() != result["lfs_handoff_identity"]:
                        raise ValueError()
                    source = directory.child("payloads")
                    for item in latest["objects"]:
                        with source.open(item["oid"]) as (handle, info):
                            if info.st_size != item["size"]:
                                raise ValueError()
                            digest = hashlib.sha256()
                            while True:
                                chunk = handle.read(65536)
                                if not chunk:
                                    break
                                downstream.check_deadline()
                                downstream.charge_capture(len(chunk))
                                digest.update(chunk)
                            if digest.hexdigest() != item["oid"]:
                                raise ValueError()
                    verified.context = downstream
                    verify_upload(verified, oids, latest["objects"])
                    directory.validate()
                    if private.read("config", maximum=32768) != config.encode():
                        raise ValueError()
                    with tools.open("git-lfs") as (handle, info):
                        digest = hashlib.sha256()
                        while True:
                            downstream.check_deadline()
                            chunk = handle.read(65536)
                            if not chunk:
                                break
                            downstream.charge_capture(len(chunk))
                            digest.update(chunk)
                        if digest.hexdigest() != configured["lfs"]["sha256"]:
                            raise ValueError()
                    code = process(downstream, uploader, ["push", "--object-id", "--stdin", "fixture"], cwd=root,
                        environment=environment, raw=("\n".join(oids) + "\n").encode())
                    if not code:
                        value["uploaded_objects"] = len(oids)
                else:
                    # Empty transactions perform no upload-capable downstream work.
                    if not transaction.records:
                        continue
                    with repository.open_selected(command) as descriptor:
                        with os.fdopen(os.dup(descriptor), "rb") as handle:
                            digest = hashlib.sha256()
                            while True:
                                downstream.check_deadline()
                                chunk = handle.read(65536)
                                if not chunk:
                                    break
                                downstream.charge_capture(len(chunk))
                                digest.update(chunk)
                            if digest.hexdigest() != step["sha256"]:
                                raise ValueError()
                        code = process(downstream, command, args.destination, cwd=repository.root,
                            environment=os.environ.copy(), raw=transaction.raw)
                if code:
                    value.update(reason="downstream_failed", exit_code=code if code > 0 else 128 - code)
                    return value, value["exit_code"]
                value["completed_steps"] += 1
            value.update(outcome="complete_clean", reason="clean", phase="complete", exit_code=0, recovery="No action required.",
                inspection_counts=result["counts"], dispatcher_capture_bytes=downstream.capture_bytes,
                dispatcher_temp_peak_reserved_bytes=max(context.temp_peak_bytes, downstream.temp_peak_bytes))
            return value, 0
    except KeyboardInterrupt:
        return terminal_failure(value, 130, "cancelled", "cancellation", "Rerun the explicit Git action when ready.")
    except ScanFailure as exc:
        return terminal_failure(value, 2, exc.cause, "cleanup" if exc.capture_step == "cleanup" else exc.operation,
                                exc.detail(), exc.diagnostic())
    except Exception:
        return terminal_failure(value, 2, "dispatch_validation_failed", "cleanup" if value["phase"] == "complete" else "dispatch",
                                "Repair the current binding, runtime or private storage and retry the explicit Git action.")
