#!/usr/bin/env python3
"""D0 laboratory experiment. Never install this prototype in a user repository.

This deliberately separate artifact exercises real Git/LFS and the maintained
matcher. It is not the production CLI, installer, audit, or security boundary.
"""
from __future__ import annotations

import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import resource
import runpy
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

ZERO = "0" * 40
GIT = shutil.which("git")


def clean_env(home):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k not in {"PYTHONPATH", "PYTHONHOME", "SCAN_MODE", "SKIP_SECRETS_SCAN", "SECRETS_ALLOWLIST"}}
    env.update(HOME=str(home), USERPROFILE=str(home), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0", GIT_ASKPASS="", GIT_NO_LAZY_FETCH="1", GIT_NO_REPLACE_OBJECTS="1", XDG_CONFIG_HOME=str(home / ".config"))
    return env


def command(args, *, cwd, env, data=None, expected=0, timeout=60):
    result = subprocess.run(args, cwd=cwd, env=env, input=data, capture_output=True, timeout=timeout)
    if expected is not None and result.returncode != expected:
        raise AssertionError(f"process exit {result.returncode}, expected {expected}: {args!r}\n{result.stderr.decode(errors='replace')[:2000]}")
    return result


def git(repo, env, *args, **kwargs):
    return command([GIT, "--no-replace-objects", "-c", "user.name=D0 fixture", "-c", "user.email=d0@example.invalid", "-c", "commit.gpgsign=false", *args], cwd=repo, env=env, **kwargs)


def emit(value):
    print(json.dumps(value, sort_keys=True))


def gate(config_path, remote, url):
    cfg = json.loads(Path(config_path).read_bytes())
    repo = Path.cwd()
    env = clean_env(Path(cfg["home"]))
    if cfg.get("lfs_binary"):
        env["PATH"] = str(Path(cfg["lfs_binary"]).parent) + os.pathsep + env["PATH"]
    os.environ.clear()
    os.environ.update(env)
    scanner = runpy.run_path(str(Path(cfg["source"]) / ".codex/hooks/scan-secrets.py"))
    scanner_globals = scanner["scan_line_events"].__globals__
    scanner_globals.update(MAX_GIT_OUTPUT_BYTES=cfg.get("max_capture_bytes", 512 * 1024 * 1024), MAX_TOTAL_BYTES=cfg.get("max_candidate_bytes", 256 * 1024 * 1024), MAX_SCAN_SECONDS=cfg.get("max_seconds", 120))
    started = time.monotonic()
    metrics = dict(logical_candidate_bytes=0, distinct_acquired_bytes=0, objects=0,
                   path_occurrences=0, capture_bytes=0, temp_peak_bytes=0,
                   enumeration_seconds=0, acquisition_seconds=0, matching_seconds=0)
    result = dict(schema="d0-prototype-v1", outcome="incomplete", metrics=metrics)
    raw = sys.stdin.buffer.read(1024 * 1024 + 1)
    result["transaction_sha256"] = hashlib.sha256(remote.encode() + b"\0" + url.encode() + b"\0" + raw).hexdigest()
    result["stdin_sha256"] = hashlib.sha256(raw).hexdigest()
    result["remote_arguments"] = [remote, url]
    root = Path(cfg["invocation_root"]) if cfg.get("invocation_root") else Path(tempfile.mkdtemp(prefix="d0-invocation-", dir=cfg["scratch"]))
    root.chmod(0o700)

    def check_time():
        if time.monotonic() - started > cfg.get("max_seconds", 120):
            raise ValueError("deadline")

    def checked(*args, optional=False, input_bytes=None):
        check_time()
        with scanner["capture_git"](["--no-replace-objects", *args], cwd=repo, deadline=started+cfg.get("max_seconds", 120), allow_nonzero=optional, input_bytes=input_bytes) as capture:
            if capture is None:
                return None
            metrics["temp_peak_bytes"] = max(metrics["temp_peak_bytes"], metrics["distinct_acquired_bytes"] + capture.size)
            output = b"".join(capture.chunks())
        metrics["capture_bytes"] += len(output)
        if metrics["capture_bytes"] > cfg.get("max_capture_bytes", 512 * 1024 * 1024):
            raise ValueError("capture_limit")
        return output

    try:
        if len(raw) > 1024 * 1024 or (raw and not raw.endswith(b"\n")):
            raise ValueError("transaction_framing")
        tuples = []
        for record in raw.splitlines():
            fields = record.split(b" ")
            if len(fields) != 4 or not all(fields) or not all(re.fullmatch(b"[0-9a-f]{40}", fields[i]) for i in (1, 3)):
                raise ValueError("transaction_record")
            tuples.append([field.decode() for field in fields])
        if len(tuples) > 4096:
            raise ValueError("record_limit")
        result["tuples"] = tuples
        if (repo / ".git/shallow").exists() or (repo / ".git/info/grafts").exists():
            raise ValueError("unsupported_history")
        positives = sorted({row[1] for row in tuples if row[1] != ZERO})
        negatives = []
        enum_start = time.monotonic()
        for row in tuples:
            old = row[3]
            if old != ZERO:
                graph = checked("rev-list", "--objects", "--no-object-names", old, optional=True)
                if graph is not None:
                    # Verify every referenced object exists before subtraction.
                    verify = checked("cat-file", "--batch-check", input_bytes=graph, optional=True)
                    if verify is not None and b" missing\n" not in verify:
                        negatives.append(old)
        revisions = "\n".join(positives + ["^" + oid for oid in sorted(set(negatives))]) + "\n"
        ids = b""
        if positives:
            with scanner["capture_git"](["--no-replace-objects", "rev-list", "--objects", "--no-object-names", "--stdin"], cwd=repo, deadline=started+cfg.get("max_seconds",120), input_bytes=revisions.encode()) as capture:
                ids = b"".join(capture.chunks())
                metrics["capture_bytes"] += capture.size
        metrics["enumeration_seconds"] = time.monotonic() - enum_start
        object_ids = list(dict.fromkeys(ids.decode().splitlines()))
        if len(object_ids) > cfg.get("max_objects", 100000):
            raise ValueError("object_limit")
        metrics["objects"] = len(object_ids)
        objects = {}
        acquisition = time.monotonic()
        for oid in object_ids:
            typ = checked("cat-file", "-t", oid).decode().strip()
            if typ not in {"blob", "tree", "commit", "tag"}:
                raise ValueError("object_type")
            dest = root / oid
            with scanner["capture_git"](["--no-replace-objects", "cat-file", typ, oid], cwd=repo, deadline=started+cfg.get("max_seconds",120)) as capture:
                metrics["capture_bytes"] += capture.size
                metrics["temp_peak_bytes"] = max(metrics["temp_peak_bytes"], metrics["distinct_acquired_bytes"] + 2*capture.size)
                metrics["distinct_acquired_bytes"] += capture.size
                if metrics["distinct_acquired_bytes"] > cfg.get("max_candidate_bytes", 256 * 1024 * 1024):
                    raise ValueError("candidate_limit")
                with dest.open("xb") as output:
                    dest.chmod(0o600)
                    for chunk in capture.chunks():
                        output.write(chunk)
            objects[oid] = (typ, dest)
        metrics["acquisition_seconds"] = time.monotonic() - acquisition
        report = scanner["StreamReport"]()
        matching = time.monotonic()
        lfs = []
        for oid, (typ, path) in objects.items():
            if typ == "tree":
                continue
            content = path.read_bytes()
            if typ != "blob":
                metrics["logical_candidate_bytes"] += len(content)
            scanner["scan_line_events"](oid, scanner["full_line_events"]((content[i:i + 65536] for i in range(0, len(content), 65536)), "binary", check_time), report, lambda _: False, scanner["redact_match"], check_time)
            if typ == "blob" and content.startswith(b"version https://git-lfs.github.com/spec/v1"):
                pointer = re.fullmatch(rb"version https://git-lfs.github.com/spec/v1\noid sha256:([a-f0-9]{64})\nsize ([0-9]{1,12})\n", content)
                if not pointer:
                    raise ValueError("lfs_pointer_invalid")
                lfs.append((pointer[1].decode(), int(pointer[2])))
        # Inspect every relevant tree occurrence. Object bytes are acquired once.
        covered_blobs = set()
        for oid, (typ, path) in objects.items():
            if typ != "commit":
                continue
            records = checked("ls-tree", "-r", "-z", oid).split(b"\0")
            for record in records:
                if not record:
                    continue
                header, name = record.split(b"\t", 1)
                mode, kind, blob = header.split(b" ")
                if kind != b"blob":
                    raise ValueError("unsupported_tree_entry")
                metrics["path_occurrences"] += 1
                label = os.fsdecode(name)
                if scanner["is_credential_path"](label):
                    report.record_findings(1, [("credential_path", "critical", "[redacted path]", 1, "[SENSITIVE PATH]")])
                if blob.decode() not in objects:
                    continue
                covered_blobs.add(blob.decode())
                metrics["logical_candidate_bytes"] += objects[blob.decode()][1].stat().st_size
        for oid, (typ, path) in objects.items():
            if typ == "blob" and oid not in covered_blobs:
                metrics["logical_candidate_bytes"] += path.stat().st_size
        for oid, size in sorted(set(lfs)):
            source = repo / ".git/lfs/objects" / oid[:2] / oid[2:4] / oid
            metrics["distinct_acquired_bytes"] += size
            metrics["logical_candidate_bytes"] += size
            if metrics["distinct_acquired_bytes"] > cfg.get("max_candidate_bytes", 256 * 1024 * 1024):
                raise ValueError("candidate_limit")
            target = root / "lfs/objects" / oid[:2] / oid[2:4] / oid
            target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            candidate = (scanner["CANDIDATE_WORKTREE"], str(source.relative_to(repo)))
            budget = scanner["ScanBudget"](started+cfg.get("max_seconds",120))
            with scanner["snapshot_source"](repo, [candidate], budget) as snapshots:
                with snapshots.acquire(candidate) as snapshot:
                    if snapshot is None or snapshot.byte_count != size:
                        raise ValueError("lfs_payload_size")
                    digest = hashlib.sha256()
                    with target.open("xb") as output:
                        target.chmod(0o600)
                        for chunk in snapshot.chunks():
                            digest.update(chunk)
                            output.write(chunk)
                    if digest.hexdigest() != oid:
                        raise ValueError("lfs_payload_digest")
                    scanner["scan_line_events"](oid, scanner["full_line_events"](snapshot.chunks(), snapshot.classification, check_time), report, lambda _: False, scanner["redact_match"], check_time)
            target.chmod(0o400)
        if metrics["logical_candidate_bytes"] > cfg.get("max_candidate_bytes", 256 * 1024 * 1024):
            raise ValueError("logical_candidate_limit")
        metrics["matching_seconds"] = time.monotonic() - matching
        metrics["temp_peak_bytes"] = max(metrics["temp_peak_bytes"], sum(path.stat().st_size for path in root.rglob("*") if path.is_file()) + max((size for _, size in lfs), default=0))
        if metrics["temp_peak_bytes"] > cfg.get("max_temp_bytes", 512 * 1024 * 1024):
            raise ValueError("temp_limit")
        if report.processed:
            result.update(outcome="findings", findings=report.processed)
            return 1
        handoff = root / "handoff.json"
        handoff.write_text(json.dumps({"transaction_sha256": result["transaction_sha256"], "objects": lfs}))
        handoff.chmod(0o600)
        result["outcome"] = "clean"
        return 0
    except KeyboardInterrupt:
        result["reason"] = "interrupted"
        return 130
    except (ValueError, OSError, AssertionError, subprocess.TimeoutExpired, scanner["ScanFailure"]) as error:
        result["reason"] = type(error).__name__
        if isinstance(error, scanner["ScanFailure"]):
            result["diagnostic"] = error.diagnostic()
        return 2
    finally:
        if not cfg.get("invocation_root"):
            shutil.rmtree(root)
        result["scanner_pid"] = os.getpid()
        metrics["elapsed_seconds"] = time.monotonic() - started
        metrics["peak_self_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        metrics["peak_child_rss_bytes"] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        Path(cfg["result"]).write_text(json.dumps(result, sort_keys=True))


def dispatch(config_path, remote, url):
    """Parent owns temporary state across the scanner and real upload process."""
    cfg = json.loads(Path(config_path).read_bytes())
    repo = Path.cwd()
    env = clean_env(Path(cfg["home"]))
    if cfg.get("lfs_binary"):
        env["PATH"] = str(Path(cfg["lfs_binary"]).parent) + os.pathsep + env["PATH"]
    root = Path(tempfile.mkdtemp(prefix="d0-invocation-", dir=cfg["scratch"]))
    root.chmod(0o700)
    raw = sys.stdin.buffer.read(1024 * 1024 + 1)
    transaction_id = hashlib.sha256(remote.encode() + b"\0" + url.encode() + b"\0" + raw).hexdigest()
    scan_config = root / "scan-config.json"
    scan_config.write_text(json.dumps({**cfg, "invocation_root": str(root)}))
    scan_config.chmod(0o600)
    result = dict(outcome="incomplete", metrics={})
    started = time.monotonic()
    def check_time():
        if time.monotonic() - started > cfg.get("max_seconds", 120):
            raise ValueError("deadline")
    try:
        scan = command([sys.executable, "-I", "-S", "-B", str(Path(__file__).resolve()), "gate", "--config", str(scan_config), remote, url], cwd=repo, env=env, data=raw, expected=None, timeout=cfg.get("max_seconds",120)+2)
        result = json.loads(Path(cfg["result"]).read_bytes())
        if scan.returncode:
            return scan.returncode
        if result.get("schema") != "d0-prototype-v1" or result.get("outcome") != "clean" or result.get("transaction_sha256") != transaction_id:
            raise ValueError("handoff_result")
        details = root.stat()
        if details.st_uid != os.getuid() or details.st_mode & 0o777 != 0o700:
            raise ValueError("handoff_owner")
        handoff = root / "handoff.json"
        manifest = json.loads(handoff.read_bytes())
        lfs = manifest["objects"]
        # Test-only intervention models source-store mutation after acquisition.
        if cfg.get("mutate_original"):
            for oid, size in lfs:
                source = repo / ".git/lfs/objects" / oid[:2] / oid[2:4] / oid
                source.write_bytes(b"X" * size)
        if cfg.get("alter_handoff"):
            for oid, size in lfs:
                (root / "lfs/objects" / oid[:2] / oid[2:4] / oid).unlink()
        if cfg.get("corrupt_handoff"):
            for oid, size in lfs:
                target = root / "lfs/objects" / oid[:2] / oid[2:4] / oid
                target.chmod(0o600)
                target.write_bytes(b"Y" * size)
        if cfg.get("pause_before_upload"):
            Path(cfg["pause_before_upload"]).write_text(str(root))
            while True:
                check_time()
                time.sleep(.01)
        # Verify invocation handoff just before consumption, never reuse it.
        if json.loads(handoff.read_bytes())["transaction_sha256"] != result["transaction_sha256"]:
            raise ValueError("handoff_identity")
        for oid, size in lfs:
            data = (root / "lfs/objects" / oid[:2] / oid[2:4] / oid).read_bytes()
            if len(data) != size or hashlib.sha256(data).hexdigest() != oid:
                raise ValueError("handoff_payload")
        for downstream in cfg.get("downstream", []):
            proc = command([downstream, remote, url], cwd=repo, env=env, data=raw, expected=None)
            if proc.returncode:
                result.update(outcome="incomplete", reason="downstream_failed")
                return 2
        if lfs:
            lfs_result = git(repo, env, "-c", "lfs.storage=" + str(root / "lfs"), "-c", "lfs.url=" + cfg["lfs_url"], "-c", "lfs.basictransfersonly=true", "-c", "lfs.concurrenttransfers=1", "-c", "lfs.transfer.maxretries=0", "-c", "lfs.dialtimeout=2", "-c", "lfs.activitytimeout=2", "lfs", "pre-push", remote, url, data=raw, expected=None)
            if lfs_result.returncode:
                result.update(outcome="incomplete", reason="uploader_failed")
                return 2
        result["dispatcher_pid"] = os.getpid()
        result["scanner_dispatcher_handoff"] = result["scanner_pid"] != os.getpid()
        return 0
    except KeyboardInterrupt:
        result.update(outcome="incomplete", reason="interrupted")
        return 130
    except (ValueError, OSError, AssertionError, subprocess.TimeoutExpired) as error:
        result.update(outcome="incomplete", reason=type(error).__name__)
        return 2
    finally:
        shutil.rmtree(root)
        result["dispatch_elapsed_seconds"] = time.monotonic() - started
        result["dispatcher_peak_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        result["dispatcher_children_peak_rss_bytes"] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        Path(cfg["result"]).write_text(json.dumps(result, sort_keys=True))


class Lab:
    def __init__(self, workspace, source):
        self.root = Path(workspace).resolve()
        self.source = Path(source).resolve()
        self.home = self.root / "home"
        self.home.mkdir(exist_ok=True)
        self.env = clean_env(self.home)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        git(self.repo, self.env, "init", "-q", "-b", "main")
        git(self.repo, self.env, "config", "gc.auto", "0")
        git(self.repo, self.env, "config", "maintenance.auto", "false")
        self.remote = self.root / "remote.git"
        git(self.repo, self.env, "init", "--bare", "-q", str(self.remote))
        git(self.remote, self.env, "config", "gc.auto", "0")
        git(self.remote, self.env, "config", "maintenance.auto", "false")
        git(self.repo, self.env, "remote", "add", "origin", str(self.remote))
        self.scratch = self.root / "scratch"
        self.scratch.mkdir()
        self.cfg = dict(home=str(self.home), source=str(self.source), scratch=str(self.scratch), result=str(self.root / "result.json"))
        self.config = self.root / "config.json"
        self.save()
        hook = self.repo / ".git/hooks/pre-push"
        import shlex
        hook.write_text("#!/bin/sh\nexec " + shlex.join([sys.executable, "-I", "-S", "-B", str(Path(__file__).resolve()), "dispatch", "--config", str(self.config)]) + ' "$@"\n')
        hook.chmod(0o755)

    def save(self):
        self.config.write_text(json.dumps(self.cfg))
        self.config.chmod(0o600)

    def commit(self, name, data, message="fixture"):
        (self.repo / name).write_bytes(data)
        git(self.repo, self.env, "add", "--", name)
        git(self.repo, self.env, "commit", "-qm", message)
        return git(self.repo, self.env, "rev-parse", "HEAD").stdout.decode().strip()

    def push(self, *refs, expect=True):
        proc = git(self.repo, self.env, "push", "origin", *refs, expected=None, timeout=180)
        if (proc.returncode == 0) != expect:
            raise AssertionError(proc.stderr.decode())
        data = Path(self.cfg["result"]).read_bytes()
        result = json.loads(data)
        result.update(result_file_bytes=len(data), git_stdout_bytes=len(proc.stdout), git_stderr_bytes=len(proc.stderr))
        return result


def transaction(lab):
    base = lab.commit("safe", b"safe\n")
    lab.push("main")
    git(lab.repo, lab.env, "checkout", "-qb", "topic")
    topic = lab.commit("topic", b"non HEAD selected\n")
    git(lab.repo, lab.env, "checkout", "-q", "main")
    git(lab.repo, lab.env, "tag", "-a", "v1", "-m", "safe annotated message", topic)
    logs = []
    for number in (1, 2):
        hook = lab.root / f"preserved-{number}"
        target = lab.root / f"stdin-{number}"
        hook.write_text(f"#!/bin/sh\ncat > '{target}'\nprintf '{number}\\n' >> '{lab.root / 'order'}'\nprintf '%s\\n' \"$@\" > '{lab.root / f'args-{number}'}'\n")
        hook.chmod(0o755)
        logs.append(str(hook))
    lab.cfg["downstream"] = logs
    lab.save()
    result = lab.push(topic + ":refs/heads/explicit", "topic", "refs/tags/v1")
    assert (lab.root / "order").read_text() == "1\n2\n"
    assert (lab.root / "stdin-1").read_bytes() == (lab.root / "stdin-2").read_bytes()
    assert (lab.root / "args-1").read_bytes() == (lab.root / "args-2").read_bytes()
    delivered = git(lab.remote, lab.env, "rev-parse", "refs/heads/explicit").stdout.decode().strip()
    assert delivered == topic
    # Git freezes the requested OID before pre-push. A preserved hook can move
    # the local ref without changing which requested OID Git transfers.
    mover = lab.root / "move-ref"
    mover.write_text(f"#!/bin/sh\ncat >/dev/null\n'{GIT}' update-ref refs/heads/topic {base}\n")
    mover.chmod(0o755)
    lab.cfg["downstream"] = [str(mover)]
    lab.save()
    moving = lab.push("topic:refs/heads/moved-during-hook")
    assert git(lab.remote, lab.env, "rev-parse", "refs/heads/moved-during-hook").stdout.decode().strip() == topic
    lab.cfg["downstream"] = []
    lab.save()
    lab.push("+" + base + ":refs/heads/explicit", ":refs/heads/topic")
    # A removed secret in an intermediate commit must still reject publication.
    lab.commit("control", b"ghp_" + b"A" * 32 + b"FAKE\n")
    lab.commit("control", b"repaired latest tree\n")
    rejected = lab.push("main:refs/heads/unsafe-history", expect=False)
    assert rejected["outcome"] == "findings"
    assert git(lab.remote, lab.env, "show-ref", "--verify", "refs/heads/unsafe-history", expected=None).returncode != 0
    # Normal Git replacement masks the secret blob; the proof ignores it.
    secret = git(lab.repo, lab.env, "rev-parse", "HEAD~:control").stdout.decode().strip()
    safe = git(lab.repo, lab.env, "hash-object", "-w", "--stdin", data=b"masked\n").stdout.decode().strip()
    git(lab.repo, lab.env, "replace", secret, safe)
    assert git(lab.repo, lab.env, "cat-file", "blob", secret).stdout.startswith(b"ghp_")
    replaced = lab.push("main:refs/heads/replaced", expect=False)
    assert replaced["outcome"] == "findings"
    return dict(delivered_oid_matches=delivered == topic, earlier_secret_rejected=True,
                replacement_resisted=True, preserved_order=True, stdin_replay_identical=True,
                non_head_explicit_oid=True, multi_ref=True, new_ref=True, forced_update=True,
                deletion=True, annotated_tag=True, ref_movement_did_not_change_delivery=True,
                measured_transaction=result, moving_transaction=moving)


class Endpoint:
    def __init__(self):
        self.uploads = []
        self.batches = 0
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                if self.path.endswith("/locks/verify"):
                    data = b'{"ours":[],"theirs":[],"next_cursor":""}'
                    self.send_response(200)
                    self.send_header("Content-Type", "application/vnd.git-lfs+json")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                outer.batches += 1
                objects = [dict(oid=obj["oid"], size=obj["size"], actions=dict(upload=dict(href=outer.url + "/upload/" + obj["oid"]))) for obj in body["objects"]]
                data = json.dumps(dict(transfer="basic", objects=objects)).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.git-lfs+json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_PUT(self):
                data = self.rfile.read(int(self.headers["Content-Length"]))
                outer.uploads.append((self.path.rsplit("/", 1)[1], data))
                self.send_response(200)
                self.send_header("Content-Length", "0")
                self.end_headers()

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = "http://127.0.0.1:" + str(self.server.server_port)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()


def lfs_case(lab, binary):
    endpoint = Endpoint()
    try:
        lab.cfg.update(lfs_binary=binary, lfs_url=endpoint.url, mutate_original=True)
        lab.save()
        lab.env["PATH"] = str(Path(binary).parent) + os.pathsep + lab.env["PATH"]
        gate_bytes = (lab.repo / ".git/hooks/pre-push").read_bytes()
        git(lab.repo, lab.env, "lfs", "install", "--local", "--force")
        standard = (lab.repo / ".git/hooks/pre-push").read_bytes()
        assert b'git lfs pre-push "$@"' in standard
        standard_hash = hashlib.sha256(standard).hexdigest()
        (lab.repo / ".git/hooks/pre-push").write_bytes(gate_bytes)
        def payload(data, name="payload.bin"):
            oid = hashlib.sha256(data).hexdigest()
            store = lab.repo / ".git/lfs/objects" / oid[:2] / oid[2:4] / oid
            store.parent.mkdir(parents=True, exist_ok=True)
            store.write_bytes(data)
            lab.commit(name, f"version https://git-lfs.github.com/spec/v1\noid sha256:{oid}\nsize {len(data)}\n".encode())
            return oid, store

        original = (b"\x00safe verified LFS bytes\xff\n" * 4096)
        oid, store = payload(original)
        result = lab.push("main")
        assert endpoint.uploads == [(oid, original)]
        assert store.read_bytes() != original
        assert not list(lab.scratch.iterdir())
        store.write_bytes(original)
        before = len(endpoint.uploads)
        before_batches = endpoint.batches
        lab.cfg.update(alter_handoff=False, corrupt_handoff=True, mutate_original=False)
        lab.save()
        corrupted = lab.push("main:refs/heads/corrupted-handoff", expect=False)
        assert corrupted["outcome"] == "incomplete"
        assert len(endpoint.uploads) == before and endpoint.batches == before_batches
        lab.cfg.update(corrupt_handoff=False)
        lab.save()
        store.unlink()
        missing = lab.push("main:refs/heads/missing-payload", expect=False)
        assert missing["outcome"] == "incomplete"
        store.write_bytes(b"X" * len(original))
        invalid = lab.push("main:refs/heads/corrupt-payload", expect=False)
        assert invalid["outcome"] == "incomplete"
        store.write_bytes(original)
        assert len(endpoint.uploads) == before and endpoint.batches == before_batches
        # Restore source before testing a second transaction.
        store.write_bytes(original)
        before = len(endpoint.uploads)
        before_batches = endpoint.batches
        payload(b"\0safe prefix\n" + b"ghp_" + b"A" * 32 + b"FAKE\n", "unsafe.bin")
        rejected = lab.push("main:refs/heads/unsafe-lfs", expect=False)
        assert rejected["outcome"] == "findings"
        assert len(endpoint.uploads) == before and endpoint.batches == before_batches
        # Reset unpublished unsafe commit, then remove the invocation copy.
        git(lab.repo, lab.env, "reset", "--hard", "HEAD~")
        lab.cfg.update(alter_handoff=True, mutate_original=False)
        lab.save()
        altered = lab.push("main:refs/heads/altered-handoff", expect=False)
        assert altered["outcome"] == "incomplete"
        assert len(endpoint.uploads) == before and endpoint.batches == before_batches
        assert not list(lab.scratch.iterdir())
        # A pause after acquisition gives a deterministic cancellation boundary.
        marker = lab.root / "paused"
        lab.cfg.update(alter_handoff=False, pause_before_upload=str(marker))
        lab.save()
        process = subprocess.Popen([GIT, "push", "origin", "main:refs/heads/canceled"], cwd=lab.repo, env=lab.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        deadline = time.monotonic() + 10
        while not marker.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(.01)
        assert marker.exists(), "did not reach acquired handoff"
        cancel_start = time.monotonic()
        os.killpg(process.pid, signal.SIGINT)
        process.communicate(timeout=3)
        cancellation = time.monotonic() - cancel_start
        assert process.returncode != 0 and not list(lab.scratch.iterdir())
        assert len(endpoint.uploads) == before and endpoint.batches == before_batches
        assert git(lab.remote, lab.env, "show-ref", "--verify", "refs/heads/canceled", expected=None).returncode != 0
        return dict(delivered_snapshot_matches=True, original_store_mutated=True, scanner_dispatcher_handoff=result["scanner_dispatcher_handoff"], standard_lfs_hook_sha256=standard_hash,
                    upload_objects=len(endpoint.uploads), upload_bytes=sum(len(data) for _, data in endpoint.uploads),
                    rejected_payload_transfers=len(endpoint.uploads) - before, rejected_batch_requests=endpoint.batches - before_batches,
                    altered_handoff_rejected=True, cancellation_seconds=cancellation,
                    cancellation_temp_removed=True, canceled_ref_absent=True, clean=result, rejected=rejected, altered=altered, corrupted=corrupted, missing=missing, invalid=invalid)
    finally:
        endpoint.close()


def capacity_control(lab):
    data = b"\x00" + b"A" * (1024 * 1024 - 1)
    for number in range(24):
        (lab.repo / f"repeat-{number:03}.bin").write_bytes(data)
    git(lab.repo, lab.env, "add", "--all")
    git(lab.repo, lab.env, "commit", "-qm", "repeated binary content")
    clean = lab.push("main")
    assert clean["metrics"]["path_occurrences"] == 24
    assert clean["metrics"]["logical_candidate_bytes"] > 24 * 1024 * 1024
    assert clean["metrics"]["distinct_acquired_bytes"] < 2 * 1024 * 1024
    lab.commit("zz-late", b"ghp_" + b"A" * 32 + b"FAKE\n")
    finding = lab.push("main:refs/heads/late", expect=False)
    assert finding["outcome"] == "findings"
    git(lab.repo, lab.env, "reset", "--hard", "HEAD~")
    lab.cfg["max_candidate_bytes"] = 24 * 1024 * 1024
    lab.save()
    over = lab.push("main:refs/heads/over-limit", expect=False)
    assert over["outcome"] == "incomplete"
    return dict(late_control_detected=True, over_limit_incomplete=True, clean=clean, finding=finding, over_limit=over)


def large_control(lab):
    data = b"\0" * (64 * 1024 * 1024)
    lab.commit("large.bin", data)
    clean = lab.push("main")
    lab.commit("large.bin", data + b"ghp_" + b"A" * 32 + b"FAKE\n")
    rejected = lab.push("main:refs/heads/embedded-late", expect=False)
    assert rejected["outcome"] == "findings"
    return dict(embedded_late_secret_detected=True, clean=clean, rejected=rejected)


def path_control(lab):
    initial = lab.commit("safe.txt", b"ordinary shared bytes\n")
    lab.push("main")
    git(lab.repo, lab.env, "mv", "safe.txt", "credentials")
    git(lab.repo, lab.env, "commit", "-qm", "same object at sensitive path")
    rejected = lab.push("main", expect=False)
    assert rejected["outcome"] == "findings"
    assert git(lab.remote, lab.env, "rev-parse", "refs/heads/main").stdout.decode().strip() == initial
    return dict(reused_blob_sensitive_path_rejected=True, remote_ref_unchanged=True, rejected=rejected)


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("gate", "dispatch"):
        p = sub.add_parser(name, allow_abbrev=False)
        p.add_argument("--config", required=True)
        p.add_argument("remote")
        p.add_argument("url")
    p = sub.add_parser("experiment", allow_abbrev=False)
    p.add_argument("--source", required=True)
    p.add_argument("--workspace", required=True)
    p.add_argument("--case", choices=["transaction", "lfs", "capacity-control", "large-control", "path-control"], required=True)
    p.add_argument("--lfs")
    args = parser.parse_args()
    if args.action in {"gate", "dispatch"}:
        return (gate if args.action == "gate" else dispatch)(args.config, args.remote, args.url)
    lab = Lab(args.workspace, args.source)
    emit({"transaction": lambda: transaction(lab), "lfs": lambda: lfs_case(lab, args.lfs), "capacity-control": lambda: capacity_control(lab), "large-control": lambda: large_control(lab), "path-control": lambda: path_control(lab)}[args.case]())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
