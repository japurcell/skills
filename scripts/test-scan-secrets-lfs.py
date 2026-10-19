#!/usr/bin/env python3
"""Verified LFS publication through isolated processes and real Git pushes."""
from pathlib import Path
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts/scan-secrets.py"
GIT = shutil.which("git")


class RecordingEndpoint:
    def __init__(self):
        self.batches = []
        self.request_paths = []
        self.payloads = {}
        self.received_bytes = 0
        self.active = threading.Event()
        self.release = threading.Event()
        self.stall = False
        endpoint = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                raw = self.rfile.read(int(self.headers["Content-Length"]))
                value = json.loads(raw)
                endpoint.batches.append(value)
                endpoint.request_paths.append(self.path)
                objects = [{**item, "actions": {"upload": {"href": endpoint.url + "/upload/" + item["oid"]}}}
                           for item in value["objects"]]
                result = json.dumps({"transfer": "basic", "objects": objects}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.git-lfs+json")
                self.send_header("Content-Length", str(len(result)))
                self.end_headers()
                self.wfile.write(result)

            def do_PUT(self):
                length = int(self.headers["Content-Length"])
                initial = self.rfile.read(min(65536, length))
                endpoint.received_bytes += len(initial)
                endpoint.active.set()
                if endpoint.stall:
                    endpoint.release.wait(20)
                remaining = self.rfile.read(length - len(initial))
                endpoint.received_bytes += len(remaining)
                raw = initial + remaining
                endpoint.payloads[self.path.rsplit("/", 1)[-1]] = raw
                self.send_response(200)
                self.send_header("Content-Length", "0")
                self.end_headers()

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = "http://127.0.0.1:" + str(self.server.server_port)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def close(self):
        self.release.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


class LFSTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="lfs-gate-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.entry = CLI
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SCAN_", "PYTHON"))}
        self.env.update(HOME=str(self.base / "home"), USERPROFILE=str(self.base / "home"),
            LOCALAPPDATA=str(self.base / "data"),
            XDG_DATA_HOME=str(self.base / "data"), XDG_CONFIG_HOME=str(self.base / "config"),
            GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", TMPDIR=str(self.base / "tmp"))
        (self.base / "tmp").mkdir()
        self.git("init", "--quiet", "-b", "main")

    def git(self, *args, data=None, check=True):
        return subprocess.run([GIT, "-c", "commit.gpgsign=false", "-c", "user.name=Fixture",
            "-c", "user.email=fixture@example.invalid", *args], cwd=self.repo, env=self.env,
            input=data, capture_output=True, check=check, timeout=30)

    @staticmethod
    def credential():
        return ("gh" + "p_" + "A" * 36).encode()

    def pointer(self, data, name="asset.bin", *, digest=None, size=None, payload=True):
        oid = digest or hashlib.sha256(data).hexdigest()
        raw = ("version https://git-lfs.github.com/spec/v1\noid sha256:" + oid + "\nsize " + str(len(data) if size is None else size) + "\n").encode()
        (self.repo / name).write_bytes(raw)
        store = self.repo / ".git/lfs/objects" / oid[:2] / oid[2:4] / oid
        if payload:
            store.parent.mkdir(parents=True, exist_ok=True)
            store.write_bytes(data)
        self.git("add", "--", name)
        return oid, store

    def commit(self):
        self.git("commit", "--quiet", "-m", "fixture")
        return self.git("rev-parse", "HEAD").stdout.strip().decode()

    def gate(self, code, *, records=None, extra=()):
        oid = self.git("rev-parse", "HEAD").stdout.strip().decode()
        records = records if records is not None else f"refs/heads/main {oid} refs/heads/main {'0'*40}\n".encode()
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(self.entry), "gate", "pre-push", "--repo", str(self.repo),
            "--remote", "fixture", "--url", "https://example.invalid/repository", "--json", *extra],
            cwd=self.repo, env=self.env, input=records, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertNotIn(b"Traceback", result.stderr)
        self.assertEqual(list((self.base / "tmp").iterdir()), [])
        return json.loads(result.stdout)

    def test_child_data_directory_is_disposable(self):
        child = subprocess.run(
            [sys.executable, "-I", "-S", "-c",
             "import os; print(os.environ['LOCALAPPDATA'])"],
            env=self.env, capture_output=True, text=True, check=True, timeout=5,
        )
        self.assertEqual(Path(child.stdout.strip()).resolve(), (self.base / "data").resolve())

    def test_clean_local_payload_is_fully_inspected_without_mutation(self):
        data = b"safe payload\n" * 17
        oid, store = self.pointer(data)
        self.commit()
        before = store.read_bytes()
        value = self.gate(0)
        self.assertTrue(value["coverage_complete"])
        self.assertEqual(value["counts"]["lfs_objects"], 1)
        self.assertEqual(value["counts"]["lfs_payload_bytes"], len(data))
        self.assertEqual(store.read_bytes(), before)

    def test_payload_secret_is_detected_and_never_printed(self):
        data = b"binary\0" + self.credential() + b"\n"
        self.pointer(data)
        self.commit()
        value = self.gate(1)
        self.assertEqual(value["security_outcome"], "findings")
        self.assertGreater(value["counts"]["processed_findings"], 0)
        self.assertNotIn(self.credential().decode(), json.dumps(value))

    def test_unavailable_and_mismatched_payloads_are_incomplete(self):
        oid, store = self.pointer(b"safe payload")
        self.commit()
        for content in (None, b"wrong size", b"X" * len(b"safe payload")):
            with self.subTest(content=content):
                if content is None:
                    store.unlink()
                else:
                    store.write_bytes(content)
                value = self.gate(2)
                self.assertFalse(value["coverage_complete"])
                self.assertIn(value["reason"], {"lfs_payload_unavailable", "lfs_payload_invalid"})

    def test_declared_digest_and_size_must_match_local_payload(self):
        for digest, size in (("f" * 64, None), (None, 1)):
            with self.subTest(digest=digest, size=size):
                self.pointer(b"safe payload", digest=digest, size=size)
                self.commit()
                self.assertEqual(self.gate(2)["reason"], "lfs_payload_invalid")

    def test_shared_payload_preserves_logical_occurrences(self):
        data = b"shared payload\n" * 100
        self.pointer(data, "first.bin")
        self.pointer(data, "second.bin")
        oid = self.commit()
        raw = f"refs/heads/a {oid} refs/heads/a {'0'*40}\nrefs/heads/b {oid} refs/heads/b {'0'*40}\n".encode()
        value = self.gate(0, records=raw)
        self.assertEqual(value["counts"]["lfs_objects"], 1)
        self.assertEqual(value["counts"]["lfs_payload_bytes"], len(data))
        self.assertEqual(value["counts"]["lfs_occurrences"], 2)
        self.assertEqual(value["counts"]["lfs_logical_bytes"], len(data) * 2)

    def test_late_payload_failure_retains_prior_findings(self):
        self.pointer(self.credential(), "a.bin")
        self.pointer(b"missing payload", "z.bin", payload=False)
        self.commit()
        value = self.gate(2)
        self.assertEqual(value["security_outcome"], "findings")
        self.assertGreater(value["counts"]["processed_findings"], 0)
        self.assertEqual(value["counts"]["lfs_objects"], 1)

    def test_noncanonical_pointer_and_symlink_store_are_incomplete(self):
        oid, store = self.pointer(b"safe payload")
        raw = (self.repo / "asset.bin").read_bytes()
        (self.repo / "asset.bin").write_bytes(raw.replace(b"size 12", b"size 012"))
        self.git("add", ".")
        self.commit()
        self.assertEqual(self.gate(2)["reason"], "lfs_pointer_invalid")
        (self.repo / "asset.bin").write_bytes(raw)
        self.git("add", ".")
        self.commit()
        target = self.base / "outside-payload"
        store.rename(target)
        store.symlink_to(target)
        self.assertEqual(self.gate(2)["reason"], "lfs_payload_unavailable")

    def binding(self, endpoint, *, steps=None):
        import importlib.util
        spec = importlib.util.spec_from_file_location("lfs_fixture_cli", self.entry.parent.parent / "hooks/runtime/scan_cli.py")
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        digest = hashlib.sha256()
        for name, raw in (("scan-secrets.py", self.entry.read_bytes()), ("scan_cli.py", (self.entry.parent.parent / "hooks/runtime/scan_cli.py").read_bytes()),
                          ("scan_status.py", (self.entry.parent.parent / "hooks/runtime/scan_status.py").read_bytes()),
                          *((name + ".py", (self.entry.parent.parent / "hooks/runtime" / (name + ".py")).read_bytes()) for name in cli.MODULES)):
            digest.update(name.encode() + b"\0" + raw)
        selected_steps = steps if steps is not None else [{"kind": "lfs"}]
        binary = None
        tool = None
        if any(step["kind"] == "lfs" for step in selected_steps):
            binary = Path(os.environ.get("TEST_GIT_LFS") or shutil.which("git-lfs") or "/tmp/design-b-lfs-3.8.0/git-lfs-3.8.0/git-lfs").resolve()
            version = subprocess.run([str(binary), "version"], check=True, capture_output=True, timeout=5)
            self.assertTrue(version.stdout.startswith(b"git-lfs/3.8.0 "))
            tool = {"path": str(binary), "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "version": "3.8.0"}
        identity = hashlib.sha256(b"\0".join(str(path).encode() for path in (self.repo, self.repo / ".git", self.repo / ".git"))).hexdigest()
        value = dict(schema_version=1, build=digest.hexdigest(), repository_identity=identity, remote="fixture", url=str(self.base / "remote.git"),
            budget_file=None, interpreter=str(Path(sys.executable).resolve()), data_directory=str(self.base / "data/scan-secrets"), downstream_seconds=20, endpoint=endpoint.url,
            lfs=tool, steps=selected_steps)
        if not any(step["kind"] == "lfs" for step in value["steps"]):
            value.update(lfs=None, endpoint=None)
        path = self.base / "binding.json"
        path.write_text(json.dumps(value))
        path.chmod(0o600)
        return path

    def install_dispatch(self, endpoint, *, steps=None):
        import shlex
        binding = self.binding(endpoint, steps=steps)
        hook = self.repo / ".git/hooks/pre-push"
        command = ([str(self.launcher)] if getattr(self, "launcher", None) else [sys.executable, "-I", "-S", "-B", str(self.entry)])
        hook.write_text("#!/bin/sh\nexec " + shlex.join([*command, "dispatch", "pre-push", "--json", "--repo", str(self.repo), "--binding", str(binding), "--"]) + ' "$@"\n')
        hook.chmod(0o755)
        remote = self.base / "remote.git"
        if not remote.exists():
            self.git("init", "--quiet", "--bare", str(remote))
            self.git("remote", "add", "fixture", str(remote))
        return remote

    def test_actual_push_uploads_exact_verified_payload(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        data = b"verified LFS transfer\n" * 101
        oid, store = self.pointer(data)
        head = self.commit()
        remote = self.install_dispatch(endpoint)
        result = self.git("push", "fixture", "main", check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(endpoint.payloads, {oid: data})
        self.assertEqual(endpoint.received_bytes, len(data))
        self.assertEqual(sum(len(batch["objects"]) for batch in endpoint.batches), 1)
        self.assertEqual(self.git("--git-dir=" + str(remote), "rev-parse", "refs/heads/main").stdout.strip().decode(), head)
        self.assertEqual(store.read_bytes(), data)
        self.assertEqual(list((self.base / "tmp").iterdir()), [])

    def hook(self, name, body):
        path = self.base / name
        path.write_text("#!" + sys.executable + "\n" + body)
        path.chmod(0o700)
        return {"kind": "hook", "path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

    def assert_zero_transfer(self, endpoint):
        self.assertEqual(endpoint.batches, [])
        self.assertEqual(endpoint.payloads, {})
        self.assertEqual(endpoint.received_bytes, 0)

    def test_rejection_before_upload_has_zero_batches_objects_and_bytes(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.pointer(self.credential())
        self.commit()
        marker = self.base / "downstream-ran"
        step = self.hook("downstream", "from pathlib import Path\nPath(" + repr(str(marker)) + ").touch()\n")
        self.install_dispatch(endpoint, steps=[step, {"kind": "lfs"}])
        result = self.git("push", "fixture", "main", check=False)
        self.assertNotEqual(result.returncode, 0)
        value = json.loads(result.stdout)
        self.assertEqual(value["outcome"], "complete_findings")
        self.assertEqual(value["exit_code"], 1)
        self.assertEqual(value["phase"], "complete")
        self.assertEqual(value["reason"], "findings")
        self.assertIsNone(value["diagnostic"])
        self.assertGreater(value["counts"]["processed_findings"], 0)
        self.assertIn("recovery", value)
        self.assertFalse(marker.exists())
        self.assert_zero_transfer(endpoint)
        self.assertEqual(list((self.base / "tmp").iterdir()), [])

    def test_ordered_hooks_replay_original_stdin_and_source_mutation_uses_private_bytes(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        data = b"original verified payload\n" * 131
        oid, store = self.pointer(data)
        self.commit()
        order = self.base / "order"
        inputs = [self.base / "stdin-first", self.base / "stdin-last"]
        args = [self.base / "args-first", self.base / "args-last"]
        bodies = []
        for index in (0, 1):
            body = "from pathlib import Path\nimport sys,json\nPath(" + repr(str(inputs[index])) + ").write_bytes(sys.stdin.buffer.read())\n"
            body += "Path(" + repr(str(args[index])) + ").write_text(json.dumps(sys.argv[1:]))\n"
            body += "with open(" + repr(str(order)) + ",'a') as f: f.write(" + repr(str(index) + "\n") + ")\n"
            if index == 0:
                body += "Path(" + repr(str(store)) + ").write_bytes(b'changed original store')\n"
            bodies.append(self.hook("preserved-" + str(index), body))
        self.install_dispatch(endpoint, steps=[bodies[0], {"kind": "lfs"}, bodies[1]])
        result = self.git("push", "fixture", "main", check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(endpoint.payloads, {oid: data})
        self.assertEqual(store.read_bytes(), b"changed original store")
        self.assertEqual(order.read_text(), "0\n1\n")
        self.assertEqual(inputs[0].read_bytes(), inputs[1].read_bytes())
        self.assertTrue(inputs[0].read_bytes().endswith(b"\n"))
        self.assertEqual(json.loads(args[0].read_bytes()), ["fixture", str(self.base / "remote.git")])
        self.assertEqual(args[0].read_bytes(), args[1].read_bytes())
        self.assertEqual(sum(len(batch["objects"]) for batch in endpoint.batches), 1)

    def test_downstream_failure_preserves_exit_and_prevents_later_upload(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.pointer(b"clean payload")
        self.commit()
        first = self.hook("failure", "import sys\nsys.stdin.buffer.read()\nsys.exit(47)\n")
        self.install_dispatch(endpoint, steps=[first, {"kind": "lfs"}])
        result = self.git("push", "fixture", "main", check=False)
        self.assertNotEqual(result.returncode, 0)
        value = json.loads(result.stdout)
        self.assertEqual(value["exit_code"], 47)
        self.assertEqual(value["reason"], "downstream_failed")
        self.assert_zero_transfer(endpoint)
        self.assertEqual(list((self.base / "tmp").iterdir()), [])

    def test_missing_and_corrupt_current_handoff_block_before_transfer(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        data = b"clean payload"
        oid, _ = self.pointer(data)
        self.commit()
        body = "from pathlib import Path\nimport os\nroot=next(Path(os.environ['TMPDIR']).glob('scan-dispatch-*'))\n(root/'handoff.json').unlink()\n"
        step = self.hook("alter-current-handoff", body)
        self.install_dispatch(endpoint, steps=[step, {"kind": "lfs"}])
        result = self.git("push", "fixture", "main", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assert_zero_transfer(endpoint)
        body = "from pathlib import Path\nimport os\nroot=next(Path(os.environ['TMPDIR']).glob('scan-dispatch-*'))\np=root/'payloads'/" + repr(oid) + "\np.chmod(0o600)\np.write_bytes(b'X'*" + str(len(data)) + ")\n"
        step = self.hook("corrupt-current-payload", body)
        self.binding(endpoint, steps=[step, {"kind": "lfs"}])
        result = self.git("push", "fixture", "main", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assert_zero_transfer(endpoint)
        self.assertEqual(list((self.base / "tmp").iterdir()), [])

    def test_empty_transaction_does_not_run_any_downstream_step(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        marker = self.base / "ran"
        step = self.hook("must-not-run", "from pathlib import Path\nPath(" + repr(str(marker)) + ").touch()\n")
        self.pointer(b"safe")
        self.commit()
        binding = self.binding(endpoint, steps=[step, {"kind": "lfs"}])
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(self.entry), "dispatch", "pre-push", "--json", "--repo", str(self.repo),
            "--binding", str(binding), "--", "fixture", str(self.base / "remote.git")], cwd=self.repo, env=self.env,
            input=b"", capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(marker.exists())
        self.assert_zero_transfer(endpoint)

    def dispatch_process(self, binding, *, raw=None):
        if raw is None:
            oid = self.git("rev-parse", "HEAD").stdout.strip().decode()
            raw = f"refs/heads/main {oid} refs/heads/main {'0'*len(oid)}\n".encode()
        process = subprocess.Popen([sys.executable, "-I", "-S", "-B", str(self.entry), "dispatch", "pre-push", "--json", "--repo", str(self.repo),
            "--binding", str(binding), "--", "fixture", str(self.base / "remote.git")], cwd=self.repo, env=self.env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        process.stdin.write(raw)
        process.stdin.close()
        process.stdin = None
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        return process

    def test_actual_multiref_push_deduplicates_payload_transfer(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        data = b"shared clean payload\n" * 37
        oid, _ = self.pointer(data, "a.bin")
        self.pointer(data, "b.bin")
        self.commit()
        self.git("branch", "second")
        self.install_dispatch(endpoint)
        result = self.git("push", "fixture", "main", "second", check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        value = json.loads(result.stdout)
        self.assertEqual(value["inspection_counts"]["lfs_objects"], 1)
        self.assertEqual(value["inspection_counts"]["lfs_occurrences"], 2)
        self.assertEqual(value["inspection_counts"]["lfs_logical_bytes"], 2 * len(data))
        self.assertEqual(endpoint.payloads, {oid: data})
        self.assertEqual(endpoint.received_bytes, len(data))
        self.assertEqual(sum(len(batch["objects"]) for batch in endpoint.batches), 1)

    def test_missing_and_corrupt_source_have_zero_transfer(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        data = b"source payload"
        oid, store = self.pointer(data)
        self.commit()
        self.install_dispatch(endpoint)
        for content in (None, b"X" * len(data), b"wrong length"):
            with self.subTest(content=content):
                if content is None:
                    store.unlink()
                else:
                    store.write_bytes(content)
                result = self.git("push", "fixture", "main", check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assert_zero_transfer(endpoint)
                self.assertEqual(list((self.base / "tmp").iterdir()), [])

    def test_required_audit_failure_is_zero_transfer(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.pointer(b"safe payload")
        self.commit()
        self.install_dispatch(endpoint)
        unsafe = self.base / "data"
        unsafe.write_bytes(b"ordinary file")
        result = self.git("push", "fixture", "main", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assert_zero_transfer(endpoint)
        self.assertEqual(unsafe.read_bytes(), b"ordinary file")

    def test_cancel_before_upload_cleans_private_files_and_child(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.pointer(b"clean payload")
        self.commit()
        marker = self.base / "hook-pid"
        body = "from pathlib import Path\nimport os,time\nPath(" + repr(str(marker)) + ").write_text(str(os.getpid()))\ntime.sleep(30)\n"
        step = self.hook("pause", body)
        binding = self.binding(endpoint, steps=[step, {"kind": "lfs"}])
        process = self.dispatch_process(binding)
        deadline = time.monotonic() + 10
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(.01)
        self.assertTrue(marker.exists())
        child = int(marker.read_text())
        process.send_signal(signal.SIGINT)
        stdout, stderr = process.communicate(timeout=8)
        self.assertEqual(process.returncode, 130, stdout + stderr)
        self.assertEqual(json.loads(stdout)["reason"], "cancelled")
        with self.assertRaises(ProcessLookupError):
            os.kill(child, 0)
        self.assert_zero_transfer(endpoint)
        self.assertEqual(list((self.base / "tmp").iterdir()), [])

    def test_cancel_during_active_transfer_stops_uploader_and_cleans_files(self):
        endpoint = RecordingEndpoint()
        endpoint.stall = True
        self.addCleanup(endpoint.close)
        self.pointer(b"safe payload\n" * (2 * 1024 * 1024))
        self.commit()
        binding = self.binding(endpoint)
        process = self.dispatch_process(binding)
        self.assertTrue(endpoint.active.wait(15), "real uploader did not start transfer")
        self.assertGreater(endpoint.received_bytes, 0)
        # Native PID/PPID inventory is used only for process-lifetime evidence.
        rows = subprocess.run(["ps", "-axo", "pid=,ppid="], check=True, capture_output=True, text=True).stdout.splitlines()
        parents = {int(row.split()[0]): int(row.split()[1]) for row in rows}
        descendants = {process.pid}
        while True:
            expanded = descendants | {pid for pid, parent in parents.items() if parent in descendants}
            if expanded == descendants:
                break
            descendants = expanded
        self.assertGreater(len(descendants), 1)
        process.send_signal(signal.SIGINT)
        stdout, stderr = process.communicate(timeout=8)
        self.assertEqual(process.returncode, 130, stdout + stderr)
        self.assertEqual(json.loads(stdout)["reason"], "cancelled")
        for pid in descendants - {process.pid}:
            with self.assertRaises(ProcessLookupError, msg=str(pid)):
                os.kill(pid, 0)
        self.assertEqual(list((self.base / "tmp").iterdir()), [])
        # Already transmitted bytes are not recalled. The server releases only
        # after cancellation/cleanup assertions, so it cannot make them pass.
        endpoint.release.set()

    def test_custom_transfer_or_storage_is_explicitly_unsupported(self):
        self.pointer(b"safe payload")
        self.commit()
        self.git("config", "lfs.standalonetransferagent", "custom-agent")
        self.assertEqual(self.gate(2)["reason"], "lfs_unsupported")

    def test_help_status_and_gate_do_not_upload(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.pointer(b"safe payload")
        self.commit()
        self.binding(endpoint)
        for arguments in (("dispatch", "--help"), ("help", "dispatch"), ("--version",), ("status", "--repo", str(self.repo), "--json")):
            result = subprocess.run([sys.executable, "-I", "-S", "-B", str(self.entry), *arguments], env=self.env, cwd=self.repo,
                input=b"ignored", capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.gate(0)
        self.assert_zero_transfer(endpoint)

    def test_hundreds_of_tiny_distinct_payloads_have_no_hidden_metadata_cap(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        expected = {}
        for index in range(900):
            data = ("small payload %04d\n" % index).encode()
            oid, _ = self.pointer(data, "asset-%04d.bin" % index)
            expected[oid] = data
        self.commit()
        # The700-payload exploratory run was below128KiB. This900-payload
        # paired control actually activates the restored hidden cap.
        for capped in (True, False):
            with self.subTest(restored_hidden_cap=capped):
                self.entry = self.fixture_runtime("metadata-cap") if capped else CLI
                if capped:
                    runtime = self.entry.parent.parent / "hooks/runtime/scan_dispatch.py"
                    text = runtime.read_text()
                    needle = 'maximum=4096 + result["counts"]["lfs_objects"] * 256'
                    self.assertIn(needle, text)
                    runtime.write_text(text.replace(needle, 'maximum=131072'))
                self.install_dispatch(endpoint)
                result = self.git("push", "fixture", "main", check=False)
                if capped:
                    self.assertNotEqual(result.returncode, 0)
                    self.assert_zero_transfer(endpoint)
                else:
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(endpoint.payloads, expected)
                    self.assertEqual(endpoint.received_bytes, sum(map(len, expected.values())))
                    value = json.loads(result.stdout)
                    self.assertEqual(value["inspection_counts"]["lfs_objects"], 900)
        self.entry = CLI

    def test_non_lfs_dispatch_needs_no_lfs_tool_or_endpoint(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        (self.repo / "safe.txt").write_text("safe content\n")
        self.git("add", ".")
        self.commit()
        binding = self.binding(endpoint, steps=[])
        value = json.loads(binding.read_bytes())
        self.assertIsNone(value["lfs"])
        self.assertIsNone(value["endpoint"])
        process = self.dispatch_process(binding)
        stdout, stderr = process.communicate(timeout=10)
        self.assertEqual(process.returncode, 0, stdout + stderr)
        self.assert_zero_transfer(endpoint)

    def fixture_runtime(self, label):
        source = self.base / label
        (source / "scripts").mkdir(parents=True)
        shutil.copytree(ROOT / "hooks/runtime", source / "hooks/runtime")
        shutil.copyfile(CLI, source / "scripts/scan-secrets.py")
        return source / "scripts/scan-secrets.py"

    def test_payload_ancestor_swap_cannot_write_foreign_inventory(self):
        # Honest counterfactual control: the held-directory repair preceded this
        # regression. A disposable variant restores the unsafe pathname create.
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        data = b"safe payload\n"
        oid, _ = self.pointer(data)
        self.commit()
        for unsafe in (False, True):
            with self.subTest(unsafe=unsafe):
                entry = self.fixture_runtime("ancestor-" + str(unsafe))
                runtime = entry.parent.parent / "hooks/runtime"
                marker = self.base / ("pinned-" + str(unsafe))
                release = self.base / ("release-" + str(unsafe))
                dispatch = runtime / "scan_dispatch.py"
                text = dispatch.read_text()
                needle = '    payloads = directory.child("payloads")\n    return directory, payloads, request'
                injected = ('    payloads = directory.child("payloads")\n'
                    '    import time\n    Path(' + repr(str(marker)) + ').write_text(str(directory.path))\n'
                    '    until=time.monotonic()+10\n    while not Path(' + repr(str(release)) + ').exists():\n'
                    '        if time.monotonic()>until: raise ValueError()\n        time.sleep(.005)\n'
                    '    return directory, payloads, request')
                self.assertIn(needle, text)
                dispatch.write_text(text.replace(needle, injected))
                if unsafe:
                    lfs = runtime / "scan_lfs.py"
                    original = 'target = self.resources.enter_context(self.directory.create(oid))'
                    restored = 'target = self.resources.enter_context(os.fdopen(os.open(self.directory.path / oid, os.O_CREAT | os.O_EXCL | os.O_RDWR | os.O_NOFOLLOW, 0o600), "w+b"))'
                    self.assertIn(original, lfs.read_text())
                    lfs.write_text(lfs.read_text().replace(original, restored))
                self.entry = entry
                binding = self.binding(endpoint)
                process = self.dispatch_process(binding)
                deadline = time.monotonic() + 10
                while not marker.exists() and time.monotonic() < deadline:
                    time.sleep(.005)
                self.assertTrue(marker.exists())
                invocation = Path(marker.read_text())
                foreign = self.base / ("foreign-" + str(unsafe))
                foreign.mkdir()
                sentinel = foreign / "sentinel"
                sentinel.write_bytes(b"foreign bytes unchanged")
                (invocation / "payloads").rename(invocation / "pinned-original")
                (invocation / "payloads").symlink_to(foreign, target_is_directory=True)
                release.touch()
                stdout, stderr = process.communicate(timeout=12)
                self.assertEqual(process.returncode, 2, stdout + stderr)
                self.assertEqual(sentinel.read_bytes(), b"foreign bytes unchanged")
                self.assertEqual((foreign / oid).exists(), unsafe)
                if unsafe:
                    self.assertEqual((foreign / oid).read_bytes(), data)
                self.assert_zero_transfer(endpoint)
                self.assertEqual(list((self.base / "tmp").iterdir()), [])
        self.entry = CLI

    def test_temporary_budget_failure_does_not_leak_open_file_descriptor(self):
        # This source-fixture intervention invokes a real over-budget write
        # through production dispatch and records live descriptor inventory.
        # The unsafe control restores charge-after-open solely in its copy.
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        (self.repo / "safe").write_text("safe\n")
        self.git("add", ".")
        self.commit()
        for unsafe in (False, True):
            with self.subTest(unsafe=unsafe):
                entry = self.fixture_runtime("budget-" + str(unsafe))
                runtime = entry.parent.parent / "hooks/runtime"
                inventory = self.base / ("descriptor-inventory-" + str(unsafe))
                dispatch = runtime / "scan_dispatch.py"
                needle = '            context.deadline = context.started + limits["max_seconds"]'
                injected = (needle + '\n            before=set(os.listdir("/dev/fd"))\n'
                    '            try: directory.write("over-budget", b"x" * (context.limits.max_temp_bytes+1))\n'
                    '            finally: Path(' + repr(str(inventory)) + ').write_text(str(len(set(os.listdir("/dev/fd"))-before)))')
                self.assertIn(needle, dispatch.read_text())
                dispatch.write_text(dispatch.read_text().replace(needle, injected))
                if unsafe:
                    private = runtime / "scan_private.py"
                    needle = '        self.context.charge_temp(len(raw))\n        descriptor = os.open(name, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, mode, dir_fd=self.descriptor)'
                    replacement = '        descriptor = os.open(name, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, mode, dir_fd=self.descriptor)\n        self.context.charge_temp(len(raw))'
                    self.assertIn(needle, private.read_text())
                    private.write_text(private.read_text().replace(needle, replacement))
                self.entry = entry
                binding = self.binding(endpoint, steps=[])
                # Use the approved minimum profile; the injected write exceeds
                # that actual limit rather than mocking accounting or storage.
                value = json.loads(binding.read_bytes())
                from_defaults = {"checkpoint": {"max_objects":4096,"max_candidate_bytes":67108864,"max_seconds":30,"max_capture_bytes":134217728,"max_temp_bytes":268435456},
                    "publication": {"max_objects":20000,"max_candidate_bytes":268435456,"max_seconds":120,"max_capture_bytes":536870912,"max_temp_bytes":1048576}, "schema_version":1}
                budget_path = self.base / ("capacity-budget-" + str(unsafe) + ".json")
                budget_path.write_text(json.dumps(from_defaults))
                value["budget_file"] = str(budget_path)
                binding.write_text(json.dumps(value))
                process = self.dispatch_process(binding)
                stdout, stderr = process.communicate(timeout=10)
                self.assertEqual(process.returncode, 2, stdout + stderr)
                self.assertEqual(int(inventory.read_text()), 1 if unsafe else 0)
                self.assert_zero_transfer(endpoint)
                self.assertEqual(list((self.base / "tmp").iterdir()), [])
        self.entry = CLI

    def test_verified_macos_system_temp_aliases_preserve_dispatch(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.pointer(b"safe alias payload")
        self.commit()
        binding = self.binding(endpoint)
        for alias in (Path("/tmp"), Path("/var")):
            with self.subTest(alias=str(alias)):
                self.assertTrue(alias.is_symlink())
                self.assertEqual(alias.lstat().st_uid, 0)
                parent = alias.resolve(strict=True) / "tmp" if alias.name == "var" else alias.resolve(strict=True)
                with tempfile.TemporaryDirectory(prefix="t6-alias-", dir=parent) as temporary:
                    actual = Path(temporary).resolve()
                    lexical = alias / actual.relative_to(alias.resolve())
                    self.env["TMPDIR"] = str(lexical)
                    process = self.dispatch_process(binding)
                    stdout, stderr = process.communicate(timeout=15)
                    self.assertEqual(process.returncode, 0, stdout + stderr)
                    self.assertEqual(list(actual.iterdir()), [])

    def test_preserved_hook_keeps_original_path_and_sibling_semantics(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.pointer(b"safe payload")
        self.commit()
        sibling = self.base / "sibling-data"
        sibling.write_text("read through original path\n")
        output = self.base / "sibling-result"
        hook = self.base / "sibling-hook"
        hook.write_text('#!/bin/sh\ncat "$(dirname "$0")/sibling-data" > ' + repr(str(output)) + '\ncat >/dev/null\n')
        hook.chmod(0o700)
        step = {"kind": "hook", "path": str(hook), "sha256": hashlib.sha256(hook.read_bytes()).hexdigest()}
        self.install_dispatch(endpoint, steps=[step, {"kind": "lfs"}])
        result = self.git("push", "fixture", "main", check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(output.read_text(), sibling.read_text())

    def test_lfs_endpoint_preserves_semicolon_path_exactly(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        endpoint.url += "/tenant;retained"
        self.pointer(b"safe payload")
        self.commit()
        self.install_dispatch(endpoint)
        result = self.git("push", "fixture", "main", check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(endpoint.request_paths, ["/tenant;retained/objects/batch"])

    def test_budget_file_edits_are_captured_exactly_and_invalid_configuration_exits_three(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.pointer(b"safe budget payload\n")
        self.commit()
        observed = self.base / "observed-budget-digest"
        step = self.hook("budget-observer", "from pathlib import Path\nimport os,json\nr=next(Path(os.environ['TMPDIR']).glob('scan-dispatch-*'))\nPath(" + repr(str(observed)) + ").write_text(json.loads((r/'request.json').read_bytes())['budget_identity'])\n")
        binding = self.binding(endpoint, steps=[step, {"kind": "lfs"}])
        budget = self.base / "owner-selected-budget.json"
        defaults = {"schema_version":1,
            "checkpoint":{"max_objects":4096,"max_candidate_bytes":67108864,"max_seconds":30,"max_capture_bytes":134217728,"max_temp_bytes":268435456},
            "publication":{"max_objects":20000,"max_candidate_bytes":268435456,"max_seconds":120,"max_capture_bytes":536870912,"max_temp_bytes":805306368}}
        budget.write_text(json.dumps(defaults, indent=3) + "\n")
        value = json.loads(binding.read_bytes())
        value["budget_file"] = str(budget)
        binding.write_text(json.dumps(value))
        for content, expected in ((budget.read_bytes(), 0), (b'{"schema_version":1}\n', 3),
                                  ((json.dumps(defaults, indent=1) + "\n").encode(), 0)):
            budget.write_bytes(content)
            process = self.dispatch_process(binding)
            stdout, stderr = process.communicate(timeout=15)
            self.assertEqual(process.returncode, expected, stdout + stderr)
            if expected == 0:
                self.assertEqual(observed.read_text(), hashlib.sha256(content).hexdigest())
            else:
                result = json.loads(stdout)
                self.assertEqual(result["reason"], "budget_invalid")
                self.assertEqual(result["phase"], "configuration")
                self.assertIn("recovery", result)
        self.assertEqual(list((self.base / "tmp").iterdir()), [])

    def test_whole_invocation_root_replacement_preserves_foreign_files(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.pointer(b"safe payload")
        self.commit()
        marker = self.base / "replaced-root-path"
        body = ("from pathlib import Path\nimport os\nroot=next(Path(os.environ['TMPDIR']).glob('scan-dispatch-*'))\n"
            "moved=root.with_name(root.name+'-owned-moved')\nroot.rename(moved)\nroot.mkdir(mode=0o700)\n"
            "(root/'foreign-sentinel').write_bytes(b'foreign root bytes')\nPath(" + repr(str(marker)) + ").write_text(str(root))\n")
        step = self.hook("replace-whole-root", body)
        binding = self.binding(endpoint, steps=[step, {"kind": "lfs"}])
        process = self.dispatch_process(binding)
        stdout, stderr = process.communicate(timeout=15)
        self.assertEqual(process.returncode, 2, stdout + stderr)
        root = Path(marker.read_text())
        self.assertTrue((root / "foreign-sentinel").exists(), "cleanup deleted a replacement root")
        self.assertEqual((root / "foreign-sentinel").read_bytes(), b"foreign root bytes")
        self.assertFalse(root.with_name(root.name + "-owned-moved").exists())
        self.assert_zero_transfer(endpoint)

    def test_nonzero_hook_must_leave_safe_capture_before_result_is_consumed(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.pointer(b"safe payload")
        self.commit()
        step = self.hook("unsafe-output-capture", "import os,sys\nos.fchmod(sys.stdout.fileno(),0o644)\nsys.exit(47)\n")
        binding = self.binding(endpoint, steps=[step, {"kind": "lfs"}])
        process = self.dispatch_process(binding)
        stdout, stderr = process.communicate(timeout=15)
        self.assertEqual(process.returncode, 2, stdout + stderr)
        self.assertNotEqual(json.loads(stdout)["reason"], "downstream_failed")
        self.assert_zero_transfer(endpoint)
        self.assertEqual(list((self.base / "tmp").iterdir()), [])

    def test_configured_audit_directory_ignores_ambient_redirect(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.pointer(b"safe payload")
        self.commit()
        binding = self.binding(endpoint)
        decoy = self.base / "ambient-data"
        decoy.write_bytes(b"foreign audit location")
        self.env["XDG_DATA_HOME"] = str(decoy)
        process = self.dispatch_process(binding)
        stdout, stderr = process.communicate(timeout=15)
        self.assertEqual(process.returncode, 0, stdout + stderr)
        self.assertTrue((self.base / "data/scan-secrets").is_dir())
        self.assertEqual(decoy.read_bytes(), b"foreign audit location")

    def test_non_lfs_sha256_git_dispatch_preserves_existing_support(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.repo = self.base / "sha256-repo"
        self.repo.mkdir()
        self.git("init", "--quiet", "--object-format=sha256", "-b", "main")
        (self.repo / "safe.txt").write_text("safe SHA256 content\n")
        self.git("add", ".")
        self.commit()
        binding = self.binding(endpoint, steps=[])
        process = self.dispatch_process(binding)
        stdout, stderr = process.communicate(timeout=15)
        self.assertEqual(process.returncode, 0, stdout + stderr)
        self.assert_zero_transfer(endpoint)

    def test_after_upload_downstream_failure_reports_transmitted_objects(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        data = b"safe payload already sent"
        oid, _ = self.pointer(data)
        self.commit()
        step = self.hook("failure-after-upload", "import sys\nsys.stdin.buffer.read()\nsys.exit(47)\n")
        binding = self.binding(endpoint, steps=[{"kind":"lfs"}, step])
        process = self.dispatch_process(binding)
        stdout, stderr = process.communicate(timeout=15)
        self.assertEqual(process.returncode, 47, stdout + stderr)
        self.assertEqual(json.loads(stdout)["uploaded_objects"], 1)
        self.assertEqual(endpoint.payloads, {oid:data})
        self.assertEqual(endpoint.received_bytes, len(data))
        self.assertEqual(list((self.base / "tmp").iterdir()), [])

    def test_even_whitespace_alteration_of_admitted_handoff_is_rejected(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.pointer(b"safe payload")
        self.commit()
        body = "from pathlib import Path\nimport os\nr=next(Path(os.environ['TMPDIR']).glob('scan-dispatch-*'))\nwith (r/'handoff.json').open('ab') as f: f.write(b' ')\n"
        step = self.hook("alter-handoff-bytes", body)
        binding = self.binding(endpoint, steps=[step, {"kind":"lfs"}])
        process = self.dispatch_process(binding)
        stdout, stderr = process.communicate(timeout=15)
        self.assertEqual(process.returncode, 2, stdout + stderr)
        self.assert_zero_transfer(endpoint)

    def test_cleanup_faults_after_success_or_downstream_failure_are_coherent(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        data = b"safe payload before cleanup failure"
        self.pointer(data)
        self.commit()
        for kind, expected, downstream_error in (("scan",2,False),("generic",2,False),("cancel",130,False),("scan",2,True)):
            with self.subTest(kind=kind, downstream_error=downstream_error):
                entry = self.fixture_runtime("terminal-" + kind + str(downstream_error))
                private = entry.parent.parent / "hooks/runtime/scan_private.py"
                needle = '                        os.rmdir(entry.name, dir_fd=self.parent_descriptor)\n                        return'
                injected = {"scan": 'raise ScanSecurityError("cleanup_failed", "repository", capture_step="cleanup")',
                    "generic": 'raise ValueError("fixture cleanup failure")', "cancel": 'raise KeyboardInterrupt'}[kind]
                self.assertIn(needle, private.read_text())
                private.write_text(private.read_text().replace(needle, '                        os.rmdir(entry.name, dir_fd=self.parent_descriptor)\n                        ' + injected))
                self.entry = entry
                steps = [{"kind":"lfs"}]
                if downstream_error:
                    steps.append(self.hook("terminal-downstream-failure", "import sys\nsys.exit(47)\n"))
                binding = self.binding(endpoint, steps=steps)
                process = self.dispatch_process(binding)
                stdout, stderr = process.communicate(timeout=15)
                self.assertEqual(process.returncode, expected, stdout + stderr)
                value = json.loads(stdout)
                self.assertEqual(value["exit_code"], expected)
                self.assertEqual(value["outcome"], "incomplete")
                self.assertNotEqual(value["phase"], "complete")
                self.assertNotEqual(value["recovery"], "No action required.")
                self.assertEqual(value["uploaded_objects"], 1)
                self.assertNotIn(b"Traceback", stderr)
                self.assertEqual(list((self.base / "tmp").iterdir()), [])
        self.entry = CLI

    def test_source_free_real_installed_launcher_delivers_verified_payload(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        data = b"installed verified payload\n" * 123
        oid, _ = self.pointer(data)
        head = self.commit()
        source_entry = self.fixture_runtime("source-to-remove")
        shutil.copy2(ROOT / "scripts/scan_install_windows.py", source_entry.parent / "scan_install_windows.py")
        destination = self.base / "installed runtime"
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(ROOT / "scripts/install-scan-secrets.py"), "install", "--json",
            "--source-dir", str(source_entry.parent.parent), "--destination", str(destination)], cwd=self.repo, env=self.env,
            capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        shutil.rmtree(source_entry.parent.parent)
        self.entry = destination / "scripts/scan-secrets.py"
        self.launcher = destination / "scan-secrets"
        remote = self.install_dispatch(endpoint)
        result = self.git("push", "fixture", "main", check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(endpoint.payloads, {oid:data})
        self.assertEqual(endpoint.received_bytes, len(data))
        self.assertEqual(self.git("--git-dir=" + str(remote), "rev-parse", "refs/heads/main").stdout.strip().decode(), head)
        manifest = json.loads((destination / "installation.json").read_bytes())
        self.assertEqual(len(manifest["files"]), 23)
        self.assertEqual(list((self.base / "tmp").iterdir()), [])

    def test_persistent_payload_storage_stays_charged_until_handoff(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.pointer(b"safe payload\n" * 100)
        self.commit()
        self.entry = self.fixture_runtime("persistent-residency")
        module = self.entry.parent.parent / "hooks/runtime/scan_dispatch.py"
        marker = self.base / "residency-control-created"
        needle = 'def write_handoff(directory, request, records):\n'
        injected = (needle + '    try:\n        directory.write("residency-control", b"x" * (directory.context.limits.max_temp_bytes-sum(r["size"] for r in records)+1))\n'
            '    finally:\n        Path(' + repr(str(marker)) + ').write_text(str((directory.path/"residency-control").exists()))\n')
        self.assertIn(needle, module.read_text())
        module.write_text(module.read_text().replace(needle, injected))
        binding = self.binding(endpoint)
        defaults = {"schema_version":1,
            "checkpoint":{"max_objects":4096,"max_candidate_bytes":67108864,"max_seconds":30,"max_capture_bytes":134217728,"max_temp_bytes":268435456},
            "publication":{"max_objects":20000,"max_candidate_bytes":268435456,"max_seconds":120,"max_capture_bytes":536870912,"max_temp_bytes":1048576}}
        budget = self.base / "resident-budget.json"
        budget.write_text(json.dumps(defaults))
        value = json.loads(binding.read_bytes())
        value["budget_file"] = str(budget)
        binding.write_text(json.dumps(value))
        process = self.dispatch_process(binding)
        stdout, stderr = process.communicate(timeout=15)
        self.assertEqual(process.returncode, 2, stdout + stderr)
        self.assertEqual(marker.read_text(), "False", "resident payload bytes were released before the handoff write")
        status = subprocess.run([sys.executable, "-I", "-S", "-B", str(self.entry), "status", "--repo", str(self.repo), "--json"],
            cwd=self.repo, env=self.env, capture_output=True, timeout=5)
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        last = json.loads(status.stdout)["last_scan"]
        self.assertEqual(last["outcome"], "incomplete")
        self.assertEqual(last["reason"], "temporary_bytes_limit")
        self.assert_zero_transfer(endpoint)
        self.assertEqual(list((self.base / "tmp").iterdir()), [])

    def test_historical_git_only_publication_counts_remain_readable(self):
        self.pointer(b"safe payload")
        self.commit()
        self.gate(0)
        reports = list((self.base / "data/scan-secrets/status").glob("*.json"))
        self.assertEqual(len(reports), 1)
        report = json.loads(reports[0].read_bytes())
        report["build"] = "09c5d1e64561b2c42789f95eaee3fa031fa743b84ef40f085e01f0bfddff9fab"
        for key in ("lfs_objects", "lfs_payload_bytes", "lfs_occurrences", "lfs_logical_bytes"):
            del report["counts"][key]
        reports[0].write_text(json.dumps(report))
        result = subprocess.run([sys.executable, "-I", "-S", "-B", str(self.entry), "status", "--repo", str(self.repo), "--json"],
            cwd=self.repo, env=self.env, capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        value = json.loads(result.stdout)
        self.assertTrue(value["historical"])
        self.assertFalse(value["authorizes_publication"])
        self.assertIsNotNone(value["last_scan"])

    @staticmethod
    def owner_budget():
        return {"schema_version":1,
            "checkpoint":{"max_objects":4096,"max_candidate_bytes":67108864,"max_seconds":30,"max_capture_bytes":134217728,"max_temp_bytes":268435456},
            "publication":{"max_objects":20000,"max_candidate_bytes":268435456,"max_seconds":120,"max_capture_bytes":536870912,"max_temp_bytes":805306368}}

    def test_private_budget_staging_failure_is_infrastructure_not_invalid_configuration(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        (self.repo / "safe").write_text("safe\n")
        self.git("add", ".")
        self.commit()
        self.entry = self.fixture_runtime("budget-staging-failure")
        private = self.entry.parent.parent / "hooks/runtime/scan_private.py"
        needle = '    def write(self, name, raw, mode=0o600):\n'
        self.assertIn(needle, private.read_text())
        private.write_text(private.read_text().replace(needle, needle + '        if name == "budget.json": raise OSError(28, "fixture full private storage")\n'))
        binding = self.binding(endpoint, steps=[])
        process = self.dispatch_process(binding)
        stdout, stderr = process.communicate(timeout=10)
        self.assertEqual(process.returncode, 2, stdout + stderr)
        value = json.loads(stdout)
        self.assertNotEqual(value["reason"], "budget_invalid")
        self.assertEqual(value["outcome"], "incomplete")
        self.assertNotIn(b"fixture full", stdout + stderr)
        self.assert_zero_transfer(endpoint)
        self.assertEqual(list((self.base / "tmp").iterdir()), [])

    def test_current_owner_budget_rejects_writable_or_hardlinked_replacements(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.pointer(b"safe local payload")
        self.commit()
        binding = self.binding(endpoint)
        budget = self.base / "trusted-owner-budget.json"
        budget.write_text(json.dumps(self.owner_budget()))
        value = json.loads(binding.read_bytes())
        value["budget_file"] = str(budget)
        binding.write_text(json.dumps(value))
        for kind in ("owner0644", "world_writable", "hard_link", "owner0600"):
            with self.subTest(kind=kind):
                alias = self.base / "budget-hardlink"
                if kind == "owner0644":
                    budget.chmod(0o644)
                elif kind == "world_writable":
                    budget.chmod(0o666)
                elif kind == "hard_link":
                    budget.chmod(0o644)
                    os.link(budget, alias)
                else:
                    alias.unlink()
                    budget.chmod(0o600)
                endpoint.batches.clear()
                endpoint.payloads.clear()
                endpoint.received_bytes = 0
                process = self.dispatch_process(binding)
                stdout, stderr = process.communicate(timeout=15)
                if kind in {"world_writable", "hard_link"}:
                    self.assertEqual(process.returncode, 3, stdout + stderr)
                    self.assertEqual(json.loads(stdout)["reason"], "budget_untrusted")
                    self.assert_zero_transfer(endpoint)
                else:
                    self.assertEqual(process.returncode, 0, stdout + stderr)
                self.assertEqual(list((self.base / "tmp").iterdir()), [])

    def test_invalid_dispatch_arguments_are_bounded_in_human_and_json_modes(self):
        for json_mode in (False, True):
            with self.subTest(json_mode=json_mode):
                result = subprocess.run([sys.executable, "-I", "-S", "-B", str(self.entry), "dispatch", "pre-push", *(["--json"] if json_mode else [])],
                    cwd=self.repo, env=self.env, input=b"unused", capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                self.assertNotIn(b"Traceback", result.stdout + result.stderr)
                self.assertLess(len(result.stdout + result.stderr), 2048)
                if json_mode:
                    value = json.loads(result.stdout)
                    self.assertEqual(value["schema"], "scan_secrets_dispatch_v1")
                    self.assertEqual(value["exit_code"], 3)
                else:
                    self.assertEqual(result.stdout, b"")
                    self.assertIn(b"invalid_arguments", result.stderr)

    def test_root_replacement_before_handoff_cannot_write_foreign_inventory(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.pointer(b"safe payload")
        self.commit()
        self.entry = self.fixture_runtime("root-before-handoff")
        module = self.entry.parent.parent / "hooks/runtime/scan_dispatch.py"
        marker = self.base / "root-pinned-before-handoff"
        release = self.base / "root-replacement-done"
        needle = '    payloads = directory.child("payloads")\n    return directory, payloads, request'
        injected = ('    payloads = directory.child("payloads")\n'
            '    import time\n    Path(' + repr(str(marker)) + ').write_text(str(directory.path))\n'
            '    until=time.monotonic()+10\n    while not Path(' + repr(str(release)) + ').exists():\n'
            '        if time.monotonic()>until: raise ValueError()\n        time.sleep(.005)\n'
            '    return directory, payloads, request')
        self.assertIn(needle, module.read_text())
        module.write_text(module.read_text().replace(needle, injected))
        binding = self.binding(endpoint)
        process = self.dispatch_process(binding)
        deadline = time.monotonic() + 10
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(.005)
        self.assertTrue(marker.exists())
        root = Path(marker.read_text())
        moved = root.with_name(root.name + "-owned-original")
        root.rename(moved)
        root.mkdir(mode=0o700)
        sentinel = root / "foreign-sentinel"
        sentinel.write_bytes(b"foreign original inventory")
        release.touch()
        stdout, stderr = process.communicate(timeout=15)
        self.assertEqual(process.returncode, 2, stdout + stderr)
        self.assertEqual(sorted(path.name for path in root.iterdir()), ["foreign-sentinel"])
        self.assertEqual(sentinel.read_bytes(), b"foreign original inventory")
        self.assertFalse(moved.exists())
        self.assert_zero_transfer(endpoint)

    def test_cancel_during_scanner_acquisition_cleans_scanner_and_dispatch_files(self):
        endpoint = RecordingEndpoint()
        self.addCleanup(endpoint.close)
        self.pointer(b"safe payload")
        self.commit()
        self.entry = self.fixture_runtime("cancel-acquisition")
        module = self.entry.parent.parent / "hooks/runtime/scan_publication.py"
        marker = self.base / "scanner-acquisition-pid"
        needle = 'def scan(repository, transaction, build, *, payload_directory=None, retained=None):\n'
        injected = needle + '    Path(' + repr(str(marker)) + ').write_text(str(os.getpid()))\n    time.sleep(30)\n'
        self.assertIn(needle, module.read_text())
        module.write_text(module.read_text().replace(needle, injected))
        binding = self.binding(endpoint)
        process = self.dispatch_process(binding)
        deadline = time.monotonic() + 10
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(.005)
        self.assertTrue(marker.exists())
        child = int(marker.read_text())
        process.send_signal(signal.SIGINT)
        stdout, stderr = process.communicate(timeout=8)
        self.assertEqual(process.returncode, 130, stdout + stderr)
        with self.assertRaises(ProcessLookupError):
            os.kill(child, 0)
        self.assert_zero_transfer(endpoint)
        self.assertEqual(list((self.base / "tmp").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
