#!/usr/bin/env python3
"""Staged gate proof through isolated CLI processes and real Git commits."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts/scan-secrets.py"
GIT = shutil.which("git")


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="git-gate-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SCAN_", "PYTHON"))}
        self.env.update(HOME=str(self.base / "home"), USERPROFILE=str(self.base / "home"),
                        XDG_DATA_HOME=str(self.base / "data"), XDG_CONFIG_HOME=str(self.base / "config"),
                        GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        self.git("init", "--quiet")

    def git(self, *args, data=None, env=None, check=True):
        return subprocess.run([GIT, "-c", "commit.gpgsign=false", "-c", "user.name=Fixture",
            "-c", "user.email=fixture@example.invalid", *args], cwd=self.repo, env=env or self.env,
            input=data, capture_output=True, check=check, timeout=15)

    def cli(self, *args, env=None, entry=CLI):
        return subprocess.run([sys.executable, "-I", "-S", "-B", str(entry), *args], cwd=self.repo,
            env=env or self.env, input=b"unused stdin", capture_output=True, timeout=45)

    def gate(self, code, *args, env=None):
        process = self.cli("gate", "pre-commit", "--repo", str(self.repo), "--json", *args, env=env)
        self.assertEqual(process.returncode, code, process.stdout + process.stderr)
        self.assertNotIn(b"Traceback", process.stderr)
        return json.loads(process.stdout)

    @staticmethod
    def credential():
        return ("gh" + "p_" + "A" * 36).encode()

    def push_gate(self, code, data, *args, env=None):
        process = subprocess.run([sys.executable, "-I", "-S", "-B", str(CLI), "gate", "pre-push",
            "--repo", str(self.repo), "--remote", "fixture", "--url", "https://user:private@example.invalid/repo",
            "--json", *args], cwd=self.repo, env=env or self.env, input=data, capture_output=True, timeout=20)
        self.assertEqual(process.returncode, code, process.stdout + process.stderr)
        self.assertNotIn(b"private@example", process.stdout + process.stderr)
        self.assertNotIn(b"Traceback", process.stderr)
        return json.loads(process.stdout)

    def transaction(self, oid=None, old=None, ref="refs/heads/published"):
        oid = oid or self.head().strip().decode()
        return f"refs/heads/nonhead {oid} {ref} {old or '0' * len(oid)}\n".encode()

    def install_push_dispatcher(self, mutation=None, *, budget_file=None):
        import hashlib
        sys.path.insert(0, str(ROOT))
        from hooks.runtime import scan_cli, scan_budget
        digest = hashlib.sha256()
        for name, raw in (("scan-secrets.py", CLI.read_bytes()), ("scan_cli.py", (ROOT / "hooks/runtime/scan_cli.py").read_bytes()),
                          ("scan_status.py", (ROOT / "hooks/runtime/scan_status.py").read_bytes()),
                          *((name + ".py", (ROOT / "hooks/runtime" / (name + ".py")).read_bytes()) for name in scan_cli.MODULES)):
            digest.update(name.encode() + b"\0" + raw)
        identity = hashlib.sha256(b"\0".join(str(path).encode() for path in (self.repo, self.repo / ".git", self.repo / ".git"))).hexdigest()
        hook = self.repo / ".git/hooks/pre-push"
        hook.write_text("#!" + sys.executable + " -I\n" +
            "import hashlib,json,subprocess,sys\n" +
            "sys.path.insert(0," + repr(str(ROOT)) + ")\nfrom hooks.runtime.scan_gate import validate_result\n" +
            "raw=sys.stdin.buffer.read(1048577)\n" +
            "destination=hashlib.sha256(b'publication-destination-v1\\0'+sys.argv[1].encode()+b'\\0'+sys.argv[2].encode()).hexdigest()\n" +
            "transaction=hashlib.sha256(b'publication-transaction-v1\\0'+bytes.fromhex(destination)+b'\\0'+raw).hexdigest()\n" +
            "p=subprocess.run(" + repr([sys.executable,"-I","-S","-B",str(CLI),"gate","pre-push","--json","--repo",str(self.repo), *(["--budget-file", budget_file] if budget_file else [])]) +
            "+['--remote',sys.argv[1],'--url',sys.argv[2]],input=raw,capture_output=True)\n" +
            "response=p.stdout\nmutation=" + repr(mutation) + "\n" +
            "if mutation=='missing': response=b''\nelif mutation=='malformed': response=b'{}'\nelif mutation:\n v=json.loads(response)\n v[mutation]='0'*64 if mutation.endswith('identity') or mutation=='build' else 'mismatched'\n response=json.dumps(v).encode()\n" +
            "try:\n validate_result(response,p.returncode,action='pre-push',build=" + repr(digest.hexdigest()) +
            ",repository_identity=" + repr(identity) + ",index_identity=None,budget_identity=" + repr(scan_budget.load_budget(budget_file)[1]) +
            ",transaction_identity=transaction,destination_identity=destination)\nexcept Exception: sys.exit(2)\nsys.exit(p.returncode)\n")
        hook.chmod(0o755)

    def remote(self):
        remote = self.base / "remote.git"
        self.git("init", "--bare", "--quiet", str(remote))
        self.git("remote", "add", "fixture", str(remote))
        return remote

    def test_actual_push_transfers_checked_oid_and_blocks_history(self):
        self.seed()
        remote = self.remote()
        self.install_push_dispatcher()
        self.git("push", "fixture", "HEAD:refs/heads/clean")
        self.assertEqual(self.git("--git-dir=" + str(remote), "rev-parse", "refs/heads/clean").stdout, self.head())
        (self.repo / "selected.txt").write_bytes(self.credential())
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "unsafe")
        blocked = self.head().strip()
        self.assertNotEqual(self.git("push", "fixture", "HEAD:refs/heads/blocked", check=False).returncode, 0)
        self.assertNotEqual(self.git("--git-dir=" + str(remote), "cat-file", "-e", blocked.decode(), check=False).returncode, 0)
        self.assertNotEqual(self.git("--git-dir=" + str(remote), "rev-parse", "--verify", "refs/heads/blocked", check=False).returncode, 0)

    def test_publication_nonhead_explicit_multiref_tags_force_and_delete(self):
        self.seed()
        remote = self.remote()
        original = self.head().strip().decode()
        self.git("branch", "other")
        (self.repo / "selected.txt").write_text("latest safe\n")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "latest")
        self.git("tag", "-a", "safe-tag", "-m", "safe annotated message")
        self.install_push_dispatcher()
        self.git("push", "fixture", "other:refs/heads/nonhead", original + ":refs/heads/explicit", "refs/tags/safe-tag")
        self.assertEqual(self.git("--git-dir=" + str(remote), "rev-parse", "refs/heads/nonhead").stdout.strip().decode(), original)
        self.git("push", "fixture", "HEAD:refs/heads/explicit")
        self.git("push", "--force", "fixture", original + ":refs/heads/explicit")
        self.assertEqual(self.git("--git-dir=" + str(remote), "rev-parse", "refs/heads/explicit").stdout.strip().decode(), original)
        self.git("push", "fixture", ":refs/heads/nonhead")
        self.assertNotEqual(self.git("--git-dir=" + str(remote), "rev-parse", "--verify", "refs/heads/nonhead", check=False).returncode, 0)
        self.git("tag", "-a", "unsafe-tag", "-m", self.credential().decode())
        tag = self.git("rev-parse", "unsafe-tag").stdout.strip().decode()
        value = self.push_gate(1, self.transaction(tag, ref="refs/tags/unsafe-tag"))
        self.assertTrue(any(f["path"].startswith("tag:") for f in value["findings"]))
        self.assertNotEqual(self.git("push", "fixture", "unsafe-tag", check=False).returncode, 0)
        self.assertNotEqual(self.git("--git-dir=" + str(remote), "cat-file", "-e", tag, check=False).returncode, 0)

    def test_publication_commit_messages_are_policy_content(self):
        self.seed()
        self.git("commit", "--allow-empty", "--quiet", "-m", self.credential().decode())
        value = self.push_gate(1, self.transaction())
        self.assertTrue(any(f["path"].startswith("commit:") for f in value["findings"]))

    def test_publication_remote_old_is_only_verified_transaction_baseline(self):
        self.seed(self.credential())
        old = self.head().strip().decode()
        self.git("branch", "already-local")
        (self.repo / "selected.txt").write_text("safe now\n")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "safe latest")
        # An unrelated local branch or remote-tracking ref is not a baseline.
        self.git("update-ref", "refs/remotes/fixture/cached", old)
        self.push_gate(1, self.transaction())
        value = self.push_gate(0, self.transaction(old=old))
        self.assertTrue(value["coverage_complete"])
        # A missing remote old tip must fall back to full local history.
        self.push_gate(1, self.transaction(old="e" * 40))

    def test_publication_reused_remote_blob_still_checks_every_new_path(self):
        self.seed(b"innocent bytes\n")
        old = self.head().strip().decode()
        (self.repo / "credentials").write_bytes(b"innocent bytes\n")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "reuse bytes")
        value = self.push_gate(1, self.transaction(old=old))
        self.assertTrue(any(f["pattern"] == "credential_path" and f["path"] == "credentials" for f in value["findings"]))
        self.assertGreaterEqual(value["counts"]["path_occurrences"], 2)
        self.assertGreaterEqual(value["counts"]["candidate_bytes"], 30)
        remote = self.remote()
        self.install_push_dispatcher()
        self.git("push", "fixture", old + ":refs/heads/path")
        self.assertNotEqual(self.git("push", "fixture", "HEAD:refs/heads/path", check=False).returncode, 0)
        self.assertEqual(self.git("--git-dir=" + str(remote), "rev-parse", "refs/heads/path").stdout.strip().decode(), old)

    def test_publication_missing_required_objects_never_fetches_or_guesses(self):
        self.seed()
        old = self.head().strip().decode()
        (self.repo / "selected.txt").write_text("new safe\n")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "new")
        transaction = self.transaction()
        # Promisor config cannot run a remote helper to repair missing ancestry.
        marker = self.base / "fetch-ran"
        self.git("config", "extensions.partialClone", "fixture")
        self.git("config", "remote.fixture.promisor", "true")
        self.git("config", "remote.fixture.url", "ext::touch " + str(marker))
        missing = self.repo / ".git/objects" / old[:2] / old[2:]
        missing.unlink()
        value = self.push_gate(2, transaction)
        self.assertEqual(value["reason"], "object_missing")
        self.assertFalse(marker.exists())
        self.assertFalse(value["coverage_complete"])

    def test_publication_missing_blob_and_shallow_graft_alternate_redirects_block(self):
        self.seed()
        transaction = self.transaction()
        for relative, raw in (("shallow", self.head()), ("info/grafts", self.head()),
                              ("objects/info/alternates", str(self.base).encode() + b"\n"),
                              ("objects/info/http-alternates", b"https://example.invalid/objects\n")):
            path = self.repo / ".git" / relative
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(raw)
            value = self.push_gate(2, transaction)
            self.assertEqual(value["reason"], "history_unsupported")
            path.unlink()
        if os.name != "nt":
            objects = self.repo / ".git/objects"
            moved = self.repo / ".git/moved-objects"
            objects.rename(moved)
            objects.symlink_to(moved, target_is_directory=True)
            self.assertEqual(self.push_gate(2, transaction)["reason"], "history_unsupported")
            objects.unlink()
            moved.rename(objects)
        oid = self.git("rev-parse", "HEAD:selected.txt").stdout.decode().strip()
        (self.repo / ".git/objects" / oid[:2] / oid[2:]).unlink()
        self.assertEqual(self.push_gate(2, transaction)["reason"], "object_missing")

    def test_publication_replacement_and_hostile_environment_cannot_hide_secret(self):
        self.seed(self.credential())
        oid = self.git("rev-parse", "HEAD:selected.txt").stdout.decode().strip()
        other = self.git("hash-object", "-w", "--stdin", data=b"safe replacement\n").stdout.decode().strip()
        self.git("replace", oid, other)
        env = {**self.env, "SCAN_MODE":"warn", "GUARD_MODE":"warn", "SCAN_SECRETS_SKIP":"1", "SECRETS_ALLOWLIST":".*",
               "GIT_DIR":str(self.base / "missing"), "GIT_OBJECT_DIRECTORY":str(self.base / "missing"),
               "GIT_ALTERNATE_OBJECT_DIRECTORIES":str(self.base), "GIT_CONFIG_COUNT":"1",
               "GIT_CONFIG_KEY_0":"core.fsmonitor", "GIT_CONFIG_VALUE_0":"evil"}
        self.assertGreater(self.push_gate(1, self.transaction(), env=env)["counts"]["processed_findings"], 0)

    def test_publication_corrupt_commit_tree_blob_and_tag_are_not_proof(self):
        import zlib
        self.seed()
        self.git("tag", "-a", "tag", "-m", "tag message")
        for spec, kind in (("HEAD", "commit"), ("HEAD^{tree}", "tree"), ("HEAD:selected.txt", "blob"), ("tag", "tag")):
            oid = self.git("rev-parse", spec).stdout.decode().strip()
            raw = self.git("cat-file", kind, oid).stdout
            object_file = self.repo / ".git/objects" / oid[:2] / oid[2:]
            original = object_file.read_bytes()
            substituted = raw[:-1] + bytes([raw[-1] ^ 1])
            object_file.chmod(0o600)
            object_file.write_bytes(zlib.compress(kind.encode() + b" " + str(len(raw)).encode() + b"\0" + substituted))
            value = self.push_gate(2, self.transaction(oid if kind == "tag" else None))
            self.assertEqual(value["reason"], "git_output_invalid")
            # A corrupt remote-old graph must never permit an exclusion either.
            self.assertEqual(self.push_gate(2, self.transaction(old=oid))["reason"], "git_output_invalid")
            object_file.write_bytes(original)

    def test_publication_late_corruption_preserves_findings(self):
        import zlib
        self.seed()
        (self.repo / "a.txt").write_bytes(self.credential())
        (self.repo / "z.txt").write_bytes(b"original\n")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "two paths")
        oid = self.git("rev-parse", "HEAD:z.txt").stdout.decode().strip()
        path = self.repo / ".git/objects" / oid[:2] / oid[2:]
        path.chmod(0o600)
        path.write_bytes(zlib.compress(b"blob 9\0impostor\n"))
        value = self.push_gate(2, self.transaction())
        self.assertEqual(value["security_outcome"], "findings")
        self.assertGreater(value["counts"]["processed_findings"], 0)

    def test_publication_missing_lfs_payload_is_explicitly_incomplete(self):
        self.seed(b"version https://git-lfs.github.com/spec/v1\noid sha256:" + b"a" * 64 + b"\nsize 42\n")
        value = self.push_gate(2, self.transaction())
        self.assertEqual(value["reason"], "lfs_payload_unavailable")
        self.assertFalse(value["coverage_complete"])

    def test_publication_empty_and_deletion_only_are_clean_transactions(self):
        empty = self.push_gate(0, b"")
        self.assertEqual(empty["counts"]["git_objects"], 0)
        self.assertEqual(empty["counts"]["transaction_bytes"], 0)
        self.seed(self.credential())
        value = self.push_gate(0, f"(delete) {'0'*40} refs/heads/gone {'e'*40}\n".encode())
        self.assertEqual(value["counts"]["selected_objects"], 0)
        self.assertEqual(value["counts"]["candidate_bytes"], 0)

    def test_publication_input_is_complete_bounded_and_never_echoed(self):
        self.seed()
        valid = self.transaction()
        for raw in (b"\n", valid[:-1], valid + b"trailing", valid.replace(b" ", b"\t", 1),
                    valid.replace(b"refs/heads/published", b"refs/heads/../bad"),
                    valid.replace(self.head().strip(), b"a"*64, 1)):
            value = self.push_gate(2, raw)
            self.assertEqual(value["reason"], "transaction_invalid")
        self.assertEqual(self.push_gate(2, b"".join(valid.replace(b"refs/heads/published", f"refs/heads/ref-{number}".encode()) for number in range(4097)))["reason"], "transaction_records_limit")
        self.assertEqual(self.push_gate(2, b"x" * 1048577)["reason"], "transaction_bytes_limit")
        for raw in (b"", valid, valid[:10]):
            with subprocess.Popen([sys.executable,"-I","-S","-B",str(CLI),"gate","pre-push","--remote","fixture","--url","fixture","--json"],
                    cwd=self.repo, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
                if raw:
                    p.stdin.write(raw)
                    p.stdin.flush()
                p.wait(timeout=4)
                stdout, stderr = p.communicate()
                self.assertEqual(p.returncode, 2, stdout + stderr)
                self.assertEqual(json.loads(stdout)["reason"], "transaction_timeout")
        if os.name != "nt":
            import pty
            master, slave = pty.openpty()
            try:
                p = subprocess.run([sys.executable,"-I","-S","-B",str(CLI),"gate","pre-push","--remote","fixture","--url","fixture","--json"],
                    cwd=self.repo, env=self.env, stdin=slave, capture_output=True, timeout=3)
                self.assertEqual(p.returncode, 2)
                self.assertEqual(json.loads(p.stdout)["reason"], "transaction_interactive")
            finally:
                os.close(master)
                os.close(slave)

    def test_publication_invalid_results_block_actual_transfer(self):
        self.seed()
        remote = self.remote()
        for mutation in ("missing", "malformed", "transaction_identity", "destination_identity", "build", "policy_version", "scope", "budget_profile"):
            self.install_push_dispatcher(mutation)
            self.assertNotEqual(self.git("push", "fixture", "HEAD:refs/heads/invalid", check=False).returncode, 0)
            self.assertNotEqual(self.git("--git-dir=" + str(remote), "rev-parse", "--verify", "refs/heads/invalid", check=False).returncode, 0)
            self.assertNotEqual(self.git("--git-dir=" + str(remote), "cat-file", "-e", self.head().strip().decode(), check=False).returncode, 0)

    def test_publication_audit_status_and_failure_are_independent(self):
        self.seed(self.credential())
        value = self.push_gate(1, self.transaction())
        records = [json.loads(row) for row in (self.base / "data/scan-secrets/audit.jsonl").read_text().splitlines()]
        self.assertEqual((records[-1]["action"],records[-1]["profile"],records[-1]["route"],records[-1]["scope"]),
                         ("pre-push","publication_v1","git_gate","outgoing"))
        status = json.loads(self.cli("status", "--json").stdout)
        self.assertEqual(status["last_scan"]["policy_version"], "publication_v1")
        self.assertFalse(status["authorizes_publication"])
        self.assertEqual(status["last_scan"]["transaction_identity"], value["transaction_identity"])
        self.assertEqual(status["last_scan"]["budget_profile"], "publication")
        self.assertEqual(records[-1]["scanResult"]["transaction_identity"], value["transaction_identity"])
        self.assertEqual(records[-1]["scanResult"]["accounting_units"]["max_objects"], "objects")
        directory = self.base / "data/scan-secrets/status"
        shutil.rmtree(directory)
        directory.write_text("blocked status")
        self.assertEqual(self.push_gate(1, self.transaction())["status_outcome"], "failed")
        audit = directory.parent / "audit.jsonl"
        audit.unlink()
        audit.mkdir()
        value = self.push_gate(2, self.transaction())
        self.assertEqual(value["audit_outcome"], "failed")
        self.assertEqual(value["security_outcome"], "findings")

    def publication_budget(self, **overrides):
        path = Path(self.budget())
        value = json.loads(path.read_text())
        value["publication"].update(overrides)
        path.write_text(json.dumps(value))
        return str(path)

    def test_publication_capacity_and_repeated_occurrence_units(self):
        body = b"\0" * 600000
        self.seed(body)
        (self.repo / "again.bin").write_bytes(body)
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "repeat")
        transaction = self.transaction()
        value = self.push_gate(0, transaction)
        self.assertGreaterEqual(value["counts"]["candidate_bytes"], 1800000)
        self.assertLess(value["counts"]["object_body_bytes"], 601000)
        self.assertGreaterEqual(value["counts"]["path_occurrences"], 3)
        self.assertEqual(value["accounting_units"]["max_objects"], "objects")
        self.assertEqual(value["limits"]["max_objects"], 20000)
        value = self.push_gate(2, transaction, "--budget-file", self.publication_budget(max_candidate_bytes=1048576))
        self.assertEqual(value["reason"], "total_bytes_limit")
        self.assertEqual(value["diagnostic"]["unit"], "bytes")
        value = self.push_gate(2, transaction, "--budget-file", self.publication_budget(max_objects=1))
        self.assertEqual(value["reason"], "object_count_limit")
        self.assertEqual(value["diagnostic"]["unit"], "objects")
        (self.repo / "large.bin").write_bytes(b"\0" * 1100000)
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "large")
        for key, reason in (("max_capture_bytes","capture_bytes_limit"),("max_temp_bytes","temporary_bytes_limit")):
            value = self.push_gate(2, self.transaction(), "--budget-file", self.publication_budget(**{key:1048576}))
            self.assertEqual(value["reason"], reason)
            self.assertEqual(value["limits"][key], 1048576)

    def test_publication_large_binary_full_stream_and_large_tree(self):
        self.seed(b"\0" * 9000000 + self.credential())
        # A tree beyond a single 64 KiB chunk exercises nested spool cursors.
        for number in range(1800):
            (self.repo / f"path-{number:05}.txt").write_text("same safe bytes\n")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "large tree")
        value = self.push_gate(1, self.transaction())
        self.assertTrue(value["coverage_complete"])
        self.assertGreater(value["counts"]["candidate_bytes"], 18000000)
        self.assertGreater(value["counts"]["path_occurrences"], 1800)
        self.assertGreater(value["counts"]["processed_findings"], 0)

    def test_publication_missing_remote_subgraph_falls_back_without_partial_exclusion(self):
        self.seed(self.credential())
        old = self.head().strip().decode()
        (self.repo / "selected.txt").write_text("clean outgoing root\n")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "clean")
        current = self.head().strip().decode()
        # A locally available old commit points to one missing object. Its
        # other verified nodes cannot become a partial subtraction baseline.
        tree = self.git("rev-parse", old + "^{tree}").stdout.strip().decode()
        raw = self.git("cat-file", "commit", old).stdout.replace(b"tree " + tree.encode(), b"tree " + b"f"*40)
        incomplete_old = self.git("hash-object", "-t", "commit", "-w", "--stdin", data=raw).stdout.strip().decode()
        value = self.push_gate(1, self.transaction(current, incomplete_old))
        self.assertGreater(value["counts"]["processed_findings"], 0)

    def test_publication_structurally_invalid_typed_edges_are_incomplete(self):
        self.seed()
        blob = self.git("rev-parse", "HEAD:selected.txt").stdout.strip()
        tree = self.git("rev-parse", "HEAD^{tree}").stdout.strip()
        raw = b"tree " + tree + b"\nparent " + blob + b"\nauthor Fixture <fixture@example.invalid> 0 +0000\ncommitter Fixture <fixture@example.invalid> 0 +0000\n\nsafe\n"
        oid = self.git("hash-object", "-t", "commit", "-w", "--stdin", data=raw).stdout.decode().strip()
        value = self.push_gate(2, self.transaction(oid))
        self.assertEqual(value["reason"], "git_output_invalid")

    def test_publication_direct_tree_and_blob_tips_are_covered(self):
        self.seed(self.credential())
        for spec in ("HEAD^{tree}", "HEAD:selected.txt"):
            oid = self.git("rev-parse", spec).stdout.decode().strip()
            self.assertGreater(self.push_gate(1, self.transaction(oid))["counts"]["processed_findings"], 0)

    def test_publication_sha256_repository_uses_format_specific_oids(self):
        other = self.base / "sha256"
        process = self.git("init", "--quiet", "--object-format=sha256", str(other), check=False)
        self.assertEqual(process.returncode, 0, "installed Git must support required SHA-256 fixture: " + process.stderr.decode())
        self.repo = other
        self.seed()
        value = self.push_gate(0, self.transaction())
        self.assertTrue(value["coverage_complete"])
        self.assertEqual(len(self.head().strip()), 64)
        remote = self.base / "sha256-remote.git"
        self.git("init", "--quiet", "--bare", "--object-format=sha256", str(remote))
        self.git("remote", "add", "fixture", str(remote))
        self.install_push_dispatcher()
        self.git("push", "fixture", "HEAD:refs/heads/sha256")
        self.assertEqual(self.git("--git-dir=" + str(remote), "rev-parse", "refs/heads/sha256").stdout, self.head())
        (self.repo / "selected.txt").write_bytes(self.credential())
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "unsafe")
        self.assertNotEqual(self.git("push", "fixture", "HEAD:refs/heads/blocked", check=False).returncode, 0)
        self.assertNotEqual(self.git("--git-dir=" + str(remote), "cat-file", "-e", self.head().decode().strip(), check=False).returncode, 0)

    def test_publication_help_version_and_noargs_never_wait_for_stdin(self):
        for args in ((), ("--version",), ("--help",), ("gate",), ("gate","--help"), ("gate","pre-push","--help")):
            with subprocess.Popen([sys.executable,"-I","-S","-B",str(CLI),*args], cwd=self.base, env=self.env,
                    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE) as p:
                p.wait(timeout=3)
                stdout, stderr = p.communicate()
                self.assertEqual(p.returncode, 0, stdout + stderr)
        self.seed()
        for args in (("--rep","."),("--force",),("--scope","outgoing")):
            process = self.cli("gate","pre-push","--remote","fixture","--url","fixture","--json",*args)
            self.assertEqual(process.returncode,3)
        p = subprocess.run([sys.executable,"-I","-S","-B",str(CLI),"--json","--no-input","--quiet","--no-color",
            "gate","pre-push","--remote","fixture","--url","fixture"], cwd=self.repo,env=self.env,input=self.transaction(),capture_output=True,timeout=10)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        self.assertEqual(json.loads(p.stdout)["scope"],"outgoing")
        with subprocess.Popen([sys.executable,"-I","-S","-B",str(CLI),"gate","pre-push","--remote","fixture","--url","fixture","--json"],
                cwd=self.repo,env=self.env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE) as p:
            p.stdout.close()
            p.communicate(self.transaction(), timeout=10)
            self.assertNotEqual(p.returncode,0)
            self.assertNotIn(b"Traceback",p.stderr.read() if not p.stderr.closed else b"")

    def test_publication_neutral_installed_bundle_uses_exact_closure(self):
        destination = self.base / "installed-publication"
        process = subprocess.run([sys.executable,"-I","-S","-B",str(ROOT / "scripts/install-scan-secrets.py"),"install",
            "--source-dir",str(ROOT),"--destination",str(destination),"--json"],cwd=self.base,env=self.env,capture_output=True,timeout=30)
        self.assertEqual(process.returncode,0,process.stdout+process.stderr)
        manifest = json.loads((destination / "installation.json").read_text())
        self.assertEqual(len(manifest["files"]),22)
        self.seed(self.credential())
        process = subprocess.run([sys.executable,"-I","-S","-B",str(destination / "scripts/scan-secrets.py"),"gate","pre-push",
            "--remote","fixture","--url","fixture","--json"],cwd=self.repo,env=self.env,input=self.transaction(),capture_output=True,timeout=20)
        self.assertEqual(process.returncode,1,process.stdout+process.stderr)
        self.assertEqual(json.loads(process.stdout)["policy_version"],"publication_v1")

    def publication_capture_wrapper(self, target, mode):
        directory = self.base / "capture-bin"
        directory.mkdir(exist_ok=True)
        marker = self.base / "capture-started"
        wrapper = directory / "git"
        wrapper.write_text("#!" + sys.executable + "\n" +
            "import os,subprocess,sys,time\nfrom pathlib import Path\n" +
            "data=sys.stdin.buffer.read() if sys.argv[1:2]==['cat-file'] else None\n" +
            "if data==" + repr(target.encode() + b"\n") + ":\n" +
            " mode=" + repr(mode) + "\n" +
            " if mode=='fail':\n  sys.stderr.buffer.write(" + repr(self.credential()) + ")\n  sys.exit(128)\n" +
            " child=os.fork()\n if child==0:\n  time.sleep(60)\n  os._exit(0)\n" +
            " Path(" + repr(str(marker)) + ").write_text(str(os.getpid())+' '+str(child))\n" +
            " if mode=='stall': time.sleep(60)\n" +
            "p=subprocess.run([" + repr(GIT) + ",*sys.argv[1:]],input=data)\nsys.exit(p.returncode)\n")
        wrapper.chmod(0o755)
        return {**self.env,"PATH":str(directory)+os.pathsep+self.env["PATH"]}, marker

    def assert_process_gone(self, pid):
        observed = subprocess.run(["ps","-o","stat=","-p",str(pid)],capture_output=True,timeout=2)
        self.assertEqual(observed.stderr,b"")
        self.assertTrue(not observed.stdout.strip() or observed.stdout.lstrip().startswith(b"Z"),observed.stdout)

    def test_publication_late_git_failure_and_descendant_preserve_findings(self):
        if os.name != "posix":
            self.skipTest("native Windows cleanup is a separate proof")
        self.seed()
        (self.repo / "a.txt").write_bytes(self.credential())
        (self.repo / "z.txt").write_text("late safe object\n")
        self.git("add", ".")
        self.git("commit","--quiet","-m","late failure")
        target = self.git("rev-parse","HEAD:z.txt").stdout.decode().strip()
        for mode, reason in (("fail","git_failed"),("held","git_descendant_running")):
            env, marker = self.publication_capture_wrapper(target, mode)
            value = self.push_gate(2,self.transaction(),env=env)
            self.assertEqual(value["reason"],reason)
            self.assertEqual(value["security_outcome"],"findings")
            self.assertNotIn(self.credential(),json.dumps(value).encode())
            if marker.exists():
                for pid in marker.read_text().split():
                    self.assert_process_gone(int(pid))
                marker.unlink()

    def test_publication_absolute_scan_deadline_and_cancellation_cleanup(self):
        if os.name != "posix":
            self.skipTest("native Windows cleanup is a separate proof")
        import signal
        import time
        self.seed()
        (self.repo / "a.txt").write_bytes(self.credential())
        (self.repo / "z.txt").write_text("late safe object\n")
        self.git("add", ".")
        self.git("commit","--quiet","-m","cancel")
        target = self.git("rev-parse","HEAD:z.txt").stdout.decode().strip()
        env, marker = self.publication_capture_wrapper(target,"stall")
        private_temp = self.base / "publication-temp"
        private_temp.mkdir(mode=0o700)
        env["TMPDIR"] = str(private_temp)
        value = self.push_gate(2,self.transaction(),"--budget-file",self.publication_budget(max_seconds=1),env=env)
        self.assertEqual(value["reason"],"scan_timeout")
        self.assertEqual(value["security_outcome"],"findings")
        for pid in marker.read_text().split():
            self.assert_process_gone(int(pid))
        marker.unlink()
        self.assertEqual(list(private_temp.iterdir()),[])
        p = subprocess.Popen([sys.executable,"-I","-S","-B",str(CLI),"gate","pre-push","--remote","fixture","--url","fixture","--json"],
            cwd=self.repo,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            p.stdin.write(self.transaction())
            p.stdin.close()
            p.stdin = None
            deadline = time.monotonic()+5
            while not marker.exists() and time.monotonic()<deadline:
                time.sleep(.01)
            self.assertTrue(marker.exists())
            databases = list(private_temp.rglob("*.sqlite3"))
            self.assertEqual(len(databases),1)
            self.assertEqual(databases[0].stat().st_mode & 0o777,0o600)
            self.assertEqual(databases[0].stat().st_uid,os.getuid())
            self.assertFalse(any(path.name.endswith(("-journal","-wal","-shm")) for path in private_temp.rglob("*")))
            visible_bytes = sum(path.stat().st_size for path in private_temp.rglob("*") if path.is_file())
            p.send_signal(signal.SIGINT)
            stdout, stderr = p.communicate(timeout=4)
            self.assertEqual(p.returncode,130,stdout+stderr)
            value = json.loads(stdout)
            self.assertEqual(value["reason"],"cancelled")
            self.assertEqual(value["security_outcome"],"findings")
            self.assertGreater(value["counts"]["processed_findings"],0)
            self.assertGreaterEqual(value["counts"]["temp_peak_bytes"],visible_bytes)
            self.assertEqual(list(private_temp.iterdir()),[])
            for pid in marker.read_text().split():
                self.assert_process_gone(int(pid))
        finally:
            if p.poll() is None:
                p.kill()
                p.communicate()

    def test_publication_optional_helpers_and_repository_state_stay_untouched(self):
        import hashlib
        self.seed()
        marker = self.base / "helper-ran"
        helper = self.base / "optional-helper"
        helper.write_text("#!/bin/sh\nprintf unsafe > '" + str(marker) + "'\ncat\n")
        helper.chmod(0o755)
        (self.repo / ".gitattributes").write_text("*.txt filter=fixture diff=fixture\n")
        self.git("add",".gitattributes")
        self.git("commit","--quiet","-m","attributes")
        for key in ("filter.fixture.clean","diff.fixture.textconv","core.fsmonitor","core.alternateRefsCommand"):
            self.git("config",key,str(helper))
        before = {str(p.relative_to(self.repo)):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.repo.rglob("*") if p.is_file()}
        self.push_gate(0,self.transaction())
        self.assertFalse(marker.exists())
        after = {str(p.relative_to(self.repo)):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.repo.rglob("*") if p.is_file()}
        self.assertEqual(before,after)

    def test_publication_malformed_structures_and_unsafe_tree_paths_are_incomplete(self):
        self.seed()
        blob = self.git("rev-parse","HEAD:selected.txt").stdout.decode().strip()
        for body, reason in ((b"100644 ../bad\0" + bytes.fromhex(blob), "publication_path_unsupported"),
                     (b"100644 z.txt\0" + bytes.fromhex(blob) + b"100644 a.txt\0" + bytes.fromhex(blob), "git_output_invalid")):
            oid = self.git("hash-object","--literally","-t","tree","-w","--stdin",data=body).stdout.decode().strip()
            value = self.push_gate(2,self.transaction(oid))
            self.assertEqual(value["reason"],reason)
        tree = self.git("rev-parse","HEAD^{tree}").stdout.strip()
        malformed = b"tree " + tree + b"\n\nmissing required identities\n"
        oid = self.git("hash-object","--literally","-t","commit","-w","--stdin",data=malformed).stdout.decode().strip()
        self.assertEqual(self.push_gate(2,self.transaction(oid))["reason"],"git_output_invalid")
        raw = self.git("cat-file","commit","HEAD").stdout
        oversized_tree_line = raw.replace(b"tree "+tree,b"tree "+tree+b" "*300,1)
        bad_commit = self.git("hash-object","--literally","-t","commit","-w","--stdin",data=oversized_tree_line).stdout.decode().strip()
        self.assertEqual(self.push_gate(2,self.transaction(bad_commit))["reason"],"git_output_invalid")
        tip = self.head().strip()
        tag = b"object "+tip+b"\ntype commit\ntag malformed\n\nsafe\n"
        for field in (b"object "+tip,b"type commit"):
            bad = self.git("hash-object","--literally","-t","tag","-w","--stdin",data=tag.replace(field,field+b" "*300,1)).stdout.decode().strip()
            self.assertEqual(self.push_gate(2,self.transaction(bad))["reason"],"git_output_invalid")

    def test_publication_required_audit_failure_blocks_clean_actual_push(self):
        self.seed()
        remote = self.remote()
        audit = self.base / "data/scan-secrets/audit.jsonl"
        audit.mkdir(parents=True)
        self.install_push_dispatcher()
        self.assertNotEqual(self.git("push","fixture","HEAD:refs/heads/audit-blocked",check=False).returncode,0)
        self.assertNotEqual(self.git("--git-dir="+str(remote),"cat-file","-e",self.head().decode().strip(),check=False).returncode,0)
        self.assertNotEqual(self.git("--git-dir="+str(remote),"rev-parse","--verify","refs/heads/audit-blocked",check=False).returncode,0)

    def test_publication_display_cap_does_not_claim_inspection_completeness(self):
        self.seed((self.credential() + b"\n") * 150)
        value = self.push_gate(1,self.transaction())
        self.assertEqual(value["counts"]["retained_findings"],100)
        self.assertGreater(value["counts"]["omitted_findings"],0)
        self.assertTrue(value["coverage_complete"])
        (self.repo / "selected.txt").write_bytes((self.credential() + b"\n") * 1001)
        self.git("add",".")
        self.git("commit","--quiet","-m","inspection cap")
        value = self.push_gate(2,self.transaction())
        self.assertEqual(value["reason"],"findings_limit")
        self.assertEqual(value["security_outcome"],"findings")
        self.assertFalse(value["coverage_complete"])
        self.assertEqual(len(value["findings"]),100)

    def test_publication_absent_optional_info_directories_allow_clean_actual_push(self):
        self.seed()
        remote = self.remote()
        for number, relative in enumerate(("objects/info","info","config")):
            path = self.repo / ".git" / relative
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
            self.assertEqual(self.git("fsck","--strict").returncode,0)
            self.assertTrue(self.push_gate(0,self.transaction())["coverage_complete"])
            self.install_push_dispatcher()
            ref = f"refs/heads/absent-info-{number}"
            self.git("push",str(remote),"HEAD:"+ref)
            self.assertEqual(self.git("--git-dir="+str(remote),"rev-parse",ref).stdout,self.head())

    def test_publication_object_budget_counts_distinct_objects_not_repeated_paths(self):
        body = b"safe repeated bytes\n"
        blob = self.git("hash-object","-w","--stdin",data=body).stdout.strip()
        tree = self.git("mktree",data=b"".join(b"100644 blob "+blob+b"\t"+name+b"\n" for name in (b"a.txt",b"b.txt",b"c.txt"))).stdout.strip().decode()
        self.git("update-ref","refs/tags/reused-tree",tree)
        self.assertEqual(self.git("fsck","--strict").returncode,0)
        self.assertEqual(len(self.git("cat-file","--batch-all-objects","--batch-check=%(objectname)").stdout.splitlines()),2)
        budget = self.publication_budget(max_objects=2)
        value = self.push_gate(0,self.transaction(tree,ref="refs/tags/reused-tree"),"--budget-file",budget)
        self.assertEqual(value["counts"]["git_objects"],2)
        self.assertEqual(value["counts"]["path_occurrences"],3)
        self.assertEqual(value["counts"]["candidate_bytes"],3*len(body))
        remote = self.remote()
        self.install_push_dispatcher(budget_file=budget)
        self.git("push","fixture","refs/tags/reused-tree")
        self.assertEqual(self.git("--git-dir="+str(remote),"rev-parse","refs/tags/reused-tree").stdout.strip().decode(),tree)
        self.git("repack","-ad")
        packed = self.push_gate(0,self.transaction(tree,old="e"*40,ref="refs/tags/reused-tree"),"--budget-file",budget)
        self.assertEqual(packed["counts"]["git_objects"],2)
        self.assertEqual(packed["counts"]["candidate_bytes"],3*len(body))
        # Duplicate names with different modes can be separated in Git's tree
        # sort order. They still must be rejected by streamed name uniqueness.
        empty = self.git("mktree",data=b"").stdout.strip()
        malformed = b"100644 same\0"+bytes.fromhex(blob.decode())+b"100644 same.mid\0"+bytes.fromhex(blob.decode())+b"40000 same\0"+bytes.fromhex(empty.decode())
        bad = self.git("hash-object","--literally","-t","tree","-w","--stdin",data=malformed).stdout.decode().strip()
        self.assertEqual(self.push_gate(2,self.transaction(bad))["reason"],"git_output_invalid")

    def test_publication_deletion_only_needs_no_local_history_coverage(self):
        self.seed()
        remote = self.remote()
        self.git("push","fixture","HEAD:refs/heads/delete-me")
        old = self.head().decode().strip()
        (self.repo / ".git/shallow").write_bytes(self.head())
        self.install_push_dispatcher()
        # This actual deletion sends no local tip and no content. A shallow
        # source still has enough context to delete the remote ref safely.
        self.git("push","fixture",":refs/heads/delete-me")
        self.assertNotEqual(self.git("--git-dir="+str(remote),"rev-parse","--verify","refs/heads/delete-me",check=False).returncode,0)
        value = self.push_gate(0,f"(delete) {'0'*40} refs/heads/delete-me {old}\n".encode())
        self.assertEqual(value["counts"]["git_objects"],0)
        self.assertEqual(value["counts"]["candidate_bytes"],0)
        # The same source arrangement must still reject any nonzero local tip.
        self.assertEqual(self.push_gate(2,self.transaction())["reason"],"history_unsupported")

    def test_publication_unused_large_config_is_not_candidate_content(self):
        self.seed()
        remote = self.remote()
        config = self.repo / ".git/config"
        with config.open("ab") as handle:
            handle.write(b"# harmless optional comment\n"*4000)
        self.assertGreater(config.stat().st_size,65536)
        self.assertEqual(self.git("fsck","--strict").returncode,0)
        self.assertTrue(self.push_gate(0,self.transaction())["coverage_complete"])
        self.install_push_dispatcher()
        self.git("push","fixture","HEAD:refs/heads/large-config")
        self.assertEqual(self.git("--git-dir="+str(remote),"rev-parse","refs/heads/large-config").stdout,self.head())

    def test_publication_long_signed_headers_and_identities_stream_before_message(self):
        self.seed()
        raw = self.git("cat-file","commit","HEAD").stdout
        header, _, message = raw.partition(b"\n\n")
        author_start = header.index(b"author Fixture ")
        author_name_bytes = 65536-author_start-len(b"author ")-1
        header = header.replace(b"author Fixture ",b"author "+b"N"*author_name_bytes+b" ")
        header = header.replace(b"committer Fixture ",b"committer "+b"N"*70000+b" ")
        self.assertEqual(header[65535:65537],b" <")
        header = header.replace(b"<fixture@example.invalid>",b"<fixture@"+b"d"*70000+b".invalid>")
        header += b"\ngpgsig -----BEGIN PGP SIGNATURE-----\n "+b"A"*70000+b"\n -----END PGP SIGNATURE-----"
        signed = header+b"\n\n"+message
        oid = self.git("hash-object","-t","commit","-w","--stdin",data=signed).stdout.decode().strip()
        self.git("update-ref","refs/heads/signed",oid)
        self.assertEqual(self.git("fsck","--strict").returncode,0)
        remote = self.remote()
        self.install_push_dispatcher()
        self.git("push","fixture","refs/heads/signed")
        self.assertEqual(self.git("--git-dir="+str(remote),"rev-parse","refs/heads/signed").stdout.strip().decode(),oid)
        unsafe = self.git("hash-object","-t","commit","-w","--stdin",data=header+b"\n\n"+self.credential()+b"\n").stdout.decode().strip()
        value = self.push_gate(1,self.transaction(unsafe))
        self.assertTrue(any(f["path"].startswith("commit:") for f in value["findings"]))
        self.assertNotEqual(self.git("push","fixture",unsafe+":refs/heads/unsafe-signed",check=False).returncode,0)
        self.assertNotEqual(self.git("--git-dir="+str(remote),"cat-file","-e",unsafe,check=False).returncode,0)

    def test_publication_unsupported_path_boundary_is_explicit_and_blocks_transfer(self):
        body = b"safe bytes\n"
        blob = self.git("hash-object","-w","--stdin",data=body).stdout.strip()
        name = b"z"*220
        subtree = self.git("mktree",data=b"100644 blob "+blob+b"\tleaf.txt\n").stdout.strip()
        for _ in range(19):
            subtree = self.git("mktree",data=b"040000 tree "+subtree+b"\t"+name+b"\n").stdout.strip()
        tree = self.git("mktree",data=b"040000 tree "+subtree+b"\t"+name+b"\n").stdout.decode().strip()
        self.git("update-ref","refs/tags/unsupported-path",tree)
        self.assertEqual(self.git("fsck","--strict").returncode,0)
        value = self.push_gate(2,self.transaction(tree,ref="refs/tags/unsupported-path"))
        self.assertEqual(value["reason"],"publication_path_unsupported")
        self.assertEqual(value["diagnostic"]["unit"],"bytes")
        self.assertEqual(value["diagnostic"]["limit"],4096)
        self.assertGreater(value["diagnostic"]["measured"],4096)
        self.assertNotIn(name,json.dumps(value).encode())
        remote = self.remote()
        self.install_push_dispatcher()
        self.assertNotEqual(self.git("push","fixture","refs/tags/unsupported-path",check=False).returncode,0)
        self.assertNotEqual(self.git("--git-dir="+str(remote),"cat-file","-e",tree,check=False).returncode,0)
        secret = self.git("hash-object","-w","--stdin",data=self.credential()).stdout.strip()
        late = self.git("mktree",data=b"100644 blob "+secret+b"\ta.txt\n040000 tree "+subtree+b"\t"+name+b"\n").stdout.decode().strip()
        value = self.push_gate(2,self.transaction(late))
        self.assertEqual(value["reason"],"publication_path_unsupported")
        self.assertEqual(value["security_outcome"],"findings")
        self.assertGreater(value["counts"]["processed_findings"],0)
        self.assertFalse(value["coverage_complete"])
        status = json.loads(self.cli("status","--json").stdout)
        self.assertEqual(status["last_scan"]["reason"],"publication_path_unsupported")
        self.assertFalse(status["authorizes_publication"])
        help_result = self.cli("gate","pre-push","--help")
        self.assertEqual(help_result.returncode,0)
        self.assertIn(b"4096",help_result.stdout)

    def test_publication_scans_removed_intermediate_secret(self):
        self.seed()
        (self.repo / "selected.txt").write_bytes(self.credential())
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "intermediate")
        (self.repo / "selected.txt").write_text("safe latest\n")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "removed")
        value = self.push_gate(1, self.transaction())
        self.assertEqual(value["scope"], "outgoing")
        self.assertEqual(value["policy_version"], "publication_v1")
        self.assertEqual(value["budget_profile"], "publication")
        self.assertTrue(value["coverage_complete"])
        self.assertGreater(value["counts"]["processed_findings"], 0)

    def test_changed_staged_files_are_full_versions_independent_of_worktree_bytes(self):
        path = self.repo / "selected.txt"
        path.write_bytes(self.credential())
        self.git("add", ".")
        path.write_text("clean worktree\n")
        value = self.gate(1)
        self.assertEqual(value["schema"], "scan_secrets_gate_v1")
        self.assertEqual(value["action"], "pre-commit")
        self.assertEqual(value["scope"], "index")
        self.assertEqual(value["policy_version"], "selected_staged_v1")
        self.assertEqual(value["budget_profile"], "checkpoint")
        self.assertEqual(value["audit_outcome"], "written")
        path.write_text("clean staged\n")
        self.git("add", ".")
        path.write_bytes(self.credential())
        self.assertTrue(self.gate(0)["coverage_complete"])

    def install_dispatcher(self, *, mutation=None, extra_args=()):
        # Temporary test composition only. T7 owns production hook installation.
        import hashlib
        sys.path.insert(0, str(ROOT))
        from hooks.runtime import scan_cli, scan_budget
        build = hashlib.sha256()
        for name, raw in (("scan-secrets.py", CLI.read_bytes()), ("scan_cli.py", (ROOT / "hooks/runtime/scan_cli.py").read_bytes()),
                          ("scan_status.py", (ROOT / "hooks/runtime/scan_status.py").read_bytes()),
                          *((name + ".py", (ROOT / "hooks/runtime" / (name + ".py")).read_bytes()) for name in scan_cli.MODULES)):
            build.update(name.encode() + b"\0" + raw)
        identity = hashlib.sha256(b"\0".join(str(path).encode() for path in
            (self.repo, self.repo / ".git", self.repo / ".git"))).hexdigest()
        budget_identity = scan_budget.load_budget(None)[1]
        hook = self.repo / ".git/hooks/pre-commit"
        hook.write_text("#!" + sys.executable + " -I\n" +
            "import hashlib,json,os,subprocess,sys\nfrom pathlib import Path\n" +
            "sys.path.insert(0," + repr(str(ROOT)) + ")\nfrom hooks.runtime.scan_gate import validate_result\n" +
            "index=Path(os.environ.get('GIT_INDEX_FILE', '.git/index'))\n" +
            "index_identity=hashlib.sha256(b'selected-index-v1\\0'+(index.read_bytes() if index.exists() else b'absent')).hexdigest()\n" +
            "p=subprocess.run(" + repr([sys.executable, "-I", "-S", "-B", str(CLI), "gate", "pre-commit", "--json", "--repo", str(self.repo), *extra_args]) + ",capture_output=True)\n" +
            "raw=p.stdout\nmutation=" + repr(mutation) + "\n" +
            "if mutation=='missing': raw=b''\nelif mutation=='malformed': raw=b'{}'\n" +
            "elif mutation:\n v=json.loads(raw)\n v[mutation]=('selected_index_v1' if mutation=='policy_version' else '0'*64 if mutation in {'build','repository_identity','index_identity','budget_identity'} else 'mismatched')\n raw=json.dumps(v).encode()\n" +
            "try:\n validate_result(raw,p.returncode,action='pre-commit',build=" + repr(build.hexdigest()) +
            ",repository_identity=" + repr(identity) + ",index_identity=index_identity,budget_identity=" + repr(budget_identity) + ")\n" +
            "except Exception: sys.exit(2)\nsys.exit(p.returncode)\n")
        hook.chmod(0o755)

    def seed(self, raw=b"base\n"):
        (self.repo / "selected.txt").write_bytes(raw)
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "base")

    def head(self):
        return self.git("rev-parse", "--verify", "HEAD").stdout

    def test_actual_commit_blocks_staged_secret_and_allows_clean_index(self):
        self.seed()
        self.install_dispatcher()
        before = self.head()
        path = self.repo / "selected.txt"
        path.write_bytes(self.credential())
        self.git("add", ".")
        path.write_text("clean worktree\n")
        self.assertNotEqual(self.git("commit", "--quiet", "-m", "blocked", check=False).returncode, 0)
        self.assertEqual(self.head(), before)
        path.write_text("safe staged\n")
        self.git("add", ".")
        path.write_bytes(self.credential())
        self.git("commit", "--quiet", "-m", "clean")
        self.assertNotEqual(self.head(), before)
        self.assertEqual(self.git("show", "HEAD:selected.txt").stdout, b"safe staged\n")

    def test_unchanged_fixture_allows_unrelated_commit_but_full_changed_file_blocks(self):
        self.seed(self.credential() + b"\n")
        self.install_dispatcher()
        before = self.head()
        (self.repo / "unrelated.txt").write_text("safe unrelated change\n")
        self.git("add", "unrelated.txt")
        # An existing fixture in another unchanged file is outside this commit.
        process = self.git("commit", "--quiet", "-m", "safe unrelated change", check=False)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertNotEqual(self.head(), before)
        self.assertEqual(self.git("show", "HEAD:unrelated.txt").stdout, b"safe unrelated change\n")
        # The old secret's line did not change, but the selected file did.
        before = self.head()
        (self.repo / "selected.txt").write_bytes(self.credential() + b"\nnew safe line\n")
        self.git("add", "selected.txt")
        value = self.gate(1)
        self.assertEqual(value["scope_description"], "changed_staged_files")
        self.assertEqual(value["counts"]["candidates"], 1)
        self.assertGreater(value["counts"]["processed_findings"], 0)
        process = self.git("commit", "--quiet", "-m", "old secret on unchanged line", check=False)
        self.assertNotEqual(process.returncode, 0)
        self.assertEqual(self.head(), before)
        # Deleting that old fixture contributes no absent content to inspect.
        self.git("rm", "--force", "--", "selected.txt")
        (self.repo / "unrelated.txt").write_text("another safe change\n")
        self.git("add", "unrelated.txt")
        self.assertEqual(self.gate(0)["counts"]["candidates"], 1)
        self.git("commit", "--quiet", "-m", "remove old fixture and change safe file")
        self.assertNotEqual(self.head(), before)

    def test_alternate_index_and_real_partial_commit_select_the_actual_tree(self):
        self.seed()
        alternate = self.base / "alternate-index"
        env = {**self.env, "GIT_INDEX_FILE": str(alternate)}
        self.git("read-tree", "HEAD", env=env)
        path = self.repo / "selected.txt"
        path.write_bytes(self.credential())
        self.git("add", ".", env=env)
        path.write_text("safe working copy\n")
        self.assertGreater(self.gate(1, env=env)["counts"]["processed_findings"], 0)
        self.assertEqual(self.cli("check", "--scope", "index", "--json", env=env).returncode, 0)
        self.install_dispatcher()
        before = self.head()
        self.assertNotEqual(self.git("commit", "--quiet", "-m", "alternate", env=env, check=False).returncode, 0)
        self.assertEqual(self.head(), before)
        # --only supplies a temporary next-index, not the ordinary index.
        path.write_bytes(self.credential())
        self.assertNotEqual(self.git("commit", "--only", "selected.txt", "-m", "partial blocked", check=False).returncode, 0)
        self.assertEqual(self.head(), before)
        path.write_text("safe partial\n")
        self.git("commit", "--only", "selected.txt", "-m", "partial allowed")
        self.assertEqual(self.git("show", "HEAD:selected.txt").stdout, b"safe partial\n")
        # The normal index may contain an unsafe unrelated staged path.
        (self.repo / "other.txt").write_bytes(self.credential())
        self.git("add", "other.txt")
        path.write_text("safe next partial\n")
        self.git("commit", "--only", "selected.txt", "-m", "partial ignores unrelated staged")
        self.assertEqual(self.git("ls-tree", "--name-only", "HEAD").stdout, b"selected.txt\n")

    def test_empty_unborn_and_split_index_are_honest(self):
        empty = self.gate(0)
        self.assertEqual(empty["counts"]["candidates"], 0)
        self.seed()
        self.git("update-index", "--split-index")
        (self.repo / "selected.txt").write_bytes(self.credential())
        self.git("add", ".")
        self.assertGreater(self.gate(1)["counts"]["processed_findings"], 0)

    def test_unresolved_index_never_reports_clean(self):
        self.seed()
        oid = self.git("hash-object", "-w", "--stdin", data=b"safe\n").stdout.strip()
        self.git("update-index", "--index-info", data=b"0 " + b"0" * 40 + b"\tselected.txt\n" +
                 b"100644 " + oid + b" 1\tselected.txt\n100644 " + oid + b" 2\tselected.txt\n")
        (self.repo / "unrelated.txt").write_text("safe staged file\n")
        self.git("add", "unrelated.txt")
        self.assertEqual(self.gate(2)["reason"], "index_unresolved")

    def test_skip_warn_environment_and_unrelated_git_redirects_do_not_authorize(self):
        (self.repo / "selected.txt").write_bytes(self.credential())
        self.git("add", ".")
        env = {**self.env, "SCAN_MODE": "warn", "GUARD_MODE": "warn", "SKIP_SECRETS_SCAN": "1",
               "SCAN_SECRETS_SKIP": "1", "SECRETS_ALLOWLIST": ".*", "GIT_DIR": str(self.base / "absent"),
               "GIT_OBJECT_DIRECTORY": str(self.base / "absent"), "GIT_CONFIG_COUNT": "1",
               "GIT_CONFIG_KEY_0": "core.fsmonitor", "GIT_CONFIG_VALUE_0": "evil"}
        self.assertGreater(self.gate(1, env=env)["counts"]["processed_findings"], 0)

    def test_selected_index_rejects_missing_linked_or_special_inputs(self):
        for selected in (str(self.base / "absent"), ""):
            self.gate(2, env={**self.env, "GIT_INDEX_FILE": selected})
        if os.name != "nt":
            link = self.base / "linked"
            link.symlink_to(self.repo / ".git")
            self.gate(2, env={**self.env, "GIT_INDEX_FILE": str(link / "index")})
            fifo = self.base / "fifo"
            os.mkfifo(fifo)
            self.gate(2, env={**self.env, "GIT_INDEX_FILE": str(fifo)})

    def test_substituted_loose_blob_bytes_are_not_coverage_evidence(self):
        import zlib
        raw = b"clean original\n"
        path = self.repo / "selected.txt"
        path.write_bytes(raw)
        self.git("add", ".")
        oid = self.git("rev-parse", ":selected.txt").stdout.decode().strip()
        substituted = b"clean impostor\n"
        object_file = self.repo / ".git/objects" / oid[:2] / oid[2:]
        object_file.chmod(0o600)
        object_file.write_bytes(zlib.compress(b"blob " + str(len(substituted)).encode() + b"\0" + substituted))
        value = self.gate(2)
        self.assertEqual(value["reason"], "git_output_invalid")
        self.assertFalse(value["coverage_complete"])

    def test_missing_empty_malformed_or_mismatched_results_block_actual_commit(self):
        self.seed()
        for mutation in ("missing", "malformed", "action", "schema", "build", "policy_version", "scope",
                         "repository_identity", "index_identity", "budget_identity", "exit_code",
                         "coverage_complete", "audit_outcome", "outcome", "counts", "security_outcome",
                         "scope_identity", "accounting_units", "budget_profile"):
            with self.subTest(mutation=mutation):
                self.install_dispatcher(mutation=mutation)
                before = self.head()
                (self.repo / "selected.txt").write_text("safe changed " + str(mutation))
                self.git("add", ".")
                self.assertNotEqual(self.git("commit", "--quiet", "-m", "invalid result", check=False).returncode, 0)
                self.assertEqual(self.head(), before)

    def test_audit_and_display_outcomes_are_independent(self):
        self.seed()
        path = self.repo / "selected.txt"
        path.write_bytes(self.credential())
        self.git("add", ".")
        # A failed informational display must retain the findings exit.
        status = self.base / "data/scan-secrets/status"
        status.parent.mkdir(parents=True, mode=0o700)
        status.write_text("blocked display directory")
        value = self.gate(1)
        self.assertEqual(value["status_outcome"], "failed")
        self.assertEqual(value["audit_outcome"], "written")
        records = [json.loads(row) for row in (status.parent / "audit.jsonl").read_text().splitlines()]
        self.assertEqual(records[-1]["action"], "pre-commit")
        self.assertEqual(records[-1]["profile"], "selected_staged_v1")
        self.assertEqual(records[-1]["route"], "git_gate")
        self.assertEqual(records[-1]["scope"], "index")
        # Required audit failure stays incomplete, retaining known findings.
        audit = status.parent / "audit.jsonl"
        audit.unlink()
        audit.mkdir()
        value = self.gate(2)
        self.assertEqual(value["audit_outcome"], "failed")
        self.assertEqual(value["security_outcome"], "findings")
        self.assertGreater(value["counts"]["processed_findings"], 0)
        path.write_text("safe\n")
        self.git("add", ".")
        self.assertEqual(self.gate(2)["reason"], "audit_unavailable")
        self.install_dispatcher()
        before = self.head()
        self.assertNotEqual(self.git("commit", "--quiet", "-m", "audit unavailable", check=False).returncode, 0)
        self.assertEqual(self.head(), before)

    def test_late_corrupt_object_preserves_known_findings(self):
        import zlib
        (self.repo / "a.txt").write_bytes(self.credential())
        (self.repo / "z.txt").write_bytes(b"original\n")
        self.git("add", ".")
        oid = self.git("rev-parse", ":z.txt").stdout.decode().strip()
        object_file = self.repo / ".git/objects" / oid[:2] / oid[2:]
        object_file.chmod(0o600)
        object_file.write_bytes(zlib.compress(b"blob 9\0impostor\n"))
        value = self.gate(2)
        self.assertEqual(value["reason"], "git_output_invalid")
        self.assertEqual(value["security_outcome"], "findings")
        self.assertGreater(value["counts"]["processed_findings"], 0)
        self.assertTrue(value["findings"])

    def budget(self, **overrides):
        path = self.base / "budget.json"
        path.write_text(json.dumps(dict(schema_version=1,
            checkpoint=dict(max_objects=4096, max_candidate_bytes=67108864, max_seconds=30,
                            max_capture_bytes=134217728, max_temp_bytes=268435456),
            publication=dict(max_objects=20000, max_candidate_bytes=268435456, max_seconds=120,
                             max_capture_bytes=536870912, max_temp_bytes=805306368))))
        value = json.loads(path.read_text())
        value["checkpoint"].update(overrides)
        path.write_text(json.dumps(value))
        return str(path)

    def test_checkpoint_capacity_is_finite_and_reports_actual_units(self):
        for name in ("a.txt", "b.txt"):
            (self.repo / name).write_text("safe\n")
        self.git("add", ".")
        value = self.gate(2, "--budget-file", self.budget(max_objects=1))
        self.assertEqual(value["reason"], "snapshot_count_limit")
        self.assertEqual(value["diagnostic"]["unit"], "snapshots")
        self.assertEqual(value["limits"]["max_objects"], 1)
        self.assertEqual(value["accounting_units"]["max_seconds"], "seconds")
        (self.repo / "a.txt").write_bytes(b"\0" * 1048577)
        self.git("add", ".")
        self.assertEqual(self.gate(2, "--budget-file", self.budget(max_candidate_bytes=1048576))["reason"], "total_bytes_limit")
        for key, reason in (("max_capture_bytes", "capture_bytes_limit"), ("max_temp_bytes", "temporary_bytes_limit")):
            self.assertEqual(self.gate(2, "--budget-file", self.budget(**{key:1048576}))["reason"], reason)

    def test_gate_arguments_help_open_stdin_and_closed_output_are_bounded(self):
        for args in (("gate",), ("gate", "--help"), ("help", "gate"), ("gate", "pre-commit", "--help")):
            with subprocess.Popen([sys.executable, "-I", "-S", "-B", str(CLI), *args], cwd=self.base,
                    env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                process.wait(timeout=3)
                stdout, stderr = process.communicate()
                self.assertEqual(process.returncode, 0, stderr)
                self.assertTrue(stdout)
        for args in (("gate", "pre-commit", "--force"), ("gate", "pre-commit", "--rep", "."),
                     ("gate", "pre-push"), ("gate", "pre-commit", "--scope", "worktree")):
            self.assertEqual(self.cli(*args, "--json").returncode, 3)
        with subprocess.Popen([sys.executable, "-I", "-S", "-B", str(CLI), "gate", "pre-commit", "--json"],
                cwd=self.repo, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            process.wait(timeout=3)
            stdout, stderr = process.communicate()
            self.assertEqual(process.returncode, 0, stdout + stderr)
        with subprocess.Popen([sys.executable, "-I", "-S", "-B", str(CLI), "gate", "pre-commit", "--json"],
                cwd=self.repo, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            process.stdout.close()
            process.wait(timeout=3)
            stderr = process.stderr.read()
            self.assertNotEqual(process.returncode, 0)
            self.assertNotIn(b"Traceback", stderr)

    def test_cancellation_terminates_gate_git_capture(self):
        if os.name == "nt":
            self.skipTest("POSIX signal fixture; native Windows proof remains separate")
        import signal
        import time
        binary = self.base / "bin"
        binary.mkdir()
        marker = self.base / "started"
        wrapper = binary / "git"
        wrapper.write_text("#!" + sys.executable + "\nimport os,time\nfrom pathlib import Path\nPath(" + repr(str(marker)) + ").write_text(str(os.getpid()))\ntime.sleep(60)\n")
        wrapper.chmod(0o755)
        with subprocess.Popen([sys.executable, "-I", "-S", "-B", str(CLI), "gate", "pre-commit", "--json"],
                cwd=self.repo, env={**self.env, "PATH": str(binary) + os.pathsep + self.env["PATH"]},
                stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            deadline = time.monotonic() + 3
            while not marker.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(marker.exists())
            child = int(marker.read_text())
            try:
                process.send_signal(signal.SIGINT)
                stdout, stderr = process.communicate(timeout=3)
                self.assertEqual(process.returncode, 130, stdout + stderr)
                self.assertEqual(json.loads(stdout)["reason"], "cancelled")
                observed = subprocess.run(["ps", "-o", "stat=", "-p", str(child)], capture_output=True, timeout=2)
                self.assertEqual(observed.stderr, b"")
                self.assertTrue(not observed.stdout.strip() or observed.stdout.lstrip().startswith(b"Z"), observed.stdout)
            finally:
                try:
                    os.kill(child, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_missing_gate_dependency_fails_closed(self):
        sys.path.insert(0, str(ROOT))
        from hooks.runtime.scan_cli import MODULES
        source = self.base / "source"
        (source / "scripts").mkdir(parents=True)
        (source / "hooks/runtime").mkdir(parents=True)
        shutil.copy2(CLI, source / "scripts/scan-secrets.py")
        for name in (*MODULES, "scan_cli", "scan_status"):
            if name != "scan_gate":
                shutil.copy2(ROOT / "hooks/runtime" / (name + ".py"), source / "hooks/runtime" / (name + ".py"))
        process = self.cli("gate", "pre-commit", "--json", entry=source / "scripts/scan-secrets.py")
        self.assertEqual(process.returncode, 2)
        self.assertEqual(json.loads(process.stdout)["reason"], "runtime_unavailable")

    def test_gate_failure_schema_survives_multiple_common_prefix_flags(self):
        process = self.cli("--json", "--no-input", "--quiet", "gate", "pre-commit", "--repo", str(self.base))
        self.assertEqual(process.returncode, 3)
        value = json.loads(process.stdout)
        self.assertEqual(value["schema"], "scan_secrets_gate_v1")
        self.assertEqual(value["exit_code"], 3)
        self.assertEqual(value["reason"], "not_repository")

    def test_neutral_installed_bundle_selects_changed_files_without_source_checkout(self):
        sys.path.insert(0, str(ROOT))
        from hooks.runtime.scan_cli import MODULES
        source = self.base / "copied-source"
        (source / "scripts").mkdir(parents=True)
        (source / "hooks/runtime").mkdir(parents=True)
        shutil.copy2(CLI, source / "scripts/scan-secrets.py")
        shutil.copy2(ROOT / "scripts/scan_install_windows.py", source / "scripts/scan_install_windows.py")
        for name in (*MODULES, "scan_cli", "scan_status"):
            shutil.copy2(ROOT / "hooks/runtime" / (name + ".py"), source / "hooks/runtime" / (name + ".py"))
        destination = self.base / "installed"
        process = subprocess.run([sys.executable, "-I", "-S", "-B", str(ROOT / "scripts/install-scan-secrets.py"),
            "install", "--source-dir", str(source), "--destination", str(destination), "--json"],
            cwd=self.base, env=self.env, capture_output=True, timeout=30)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        manifest = json.loads((destination / "installation.json").read_text())
        self.assertEqual(len(manifest["files"]), 22)
        shutil.rmtree(source)
        self.seed(self.credential() + b"\n")
        (self.repo / "unrelated.txt").write_text("safe unrelated staged change\n")
        self.git("add", "unrelated.txt")
        entry = destination / "scripts/scan-secrets.py"
        process = self.cli("gate", "pre-commit", "--json", entry=entry)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        value = json.loads(process.stdout)
        self.assertEqual(value["scope_description"], "changed_staged_files")
        self.assertEqual(value["counts"]["candidates"], 1)
        (self.repo / "selected.txt").write_bytes(self.credential() + b"\nnew safe line\n")
        self.git("add", "selected.txt")
        process = self.cli("gate", "pre-commit", "--json", entry=entry)
        self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
        value = json.loads(process.stdout)
        self.assertEqual(value["schema"], "scan_secrets_gate_v1")
        self.assertEqual(value["audit_outcome"], "written")
        self.assertEqual(value["policy_version"], "selected_staged_v1")

    @unittest.skipUnless(sys.platform == "darwin", "macOS fixed system aliases")
    def test_selected_index_accepts_verified_macos_system_alias(self):
        alias = Path("/tmp")
        self.assertTrue(alias.is_symlink())
        target = alias.resolve(strict=True)
        self.assertEqual(target, Path("/private/tmp"))
        temporary = tempfile.TemporaryDirectory(prefix="git-gate-alias-", dir=target)
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name).resolve() / "repo"
        self.repo.mkdir()
        self.git("init", "--quiet")
        self.seed()
        (self.repo / "selected.txt").write_text("safe changed staged version\n")
        self.git("add", "selected.txt")
        physical = self.repo / ".git/index"
        selected = alias / physical.relative_to(target)
        self.assertEqual(selected.resolve(strict=True), physical)
        self.assertEqual(self.gate(0, env={**self.env, "GIT_INDEX_FILE": str(selected)})["counts"]["candidates"], 1)

    def test_gate_never_runs_optional_helpers_or_mutates_repository(self):
        import hashlib
        self.seed()
        marker = self.base / "helper-ran"
        helper = self.base / "optional-helper"
        helper.write_text("#!/bin/sh\nprintf unsafe > '" + str(marker) + "'\ncat\n")
        helper.chmod(0o755)
        (self.repo / ".gitattributes").write_text("*.txt filter=fixture diff=fixture\n")
        self.git("add", ".gitattributes")
        self.git("config", "filter.fixture.clean", str(helper))
        self.git("config", "filter.fixture.required", "true")
        self.git("config", "diff.fixture.textconv", str(helper))
        self.git("config", "core.fsmonitor", str(helper))
        def fingerprint():
            return {str(p.relative_to(self.repo)): (p.stat().st_mode, hashlib.sha256(p.read_bytes()).hexdigest())
                    for p in self.repo.rglob("*") if p.is_file()}
        before = fingerprint()
        self.gate(0)
        self.assertFalse(marker.exists())
        self.assertEqual(fingerprint(), before)

    def test_gate_repository_named_status_keeps_gate_error_schema(self):
        (self.base / "status").mkdir()
        process = subprocess.run([sys.executable, "-I", "-S", "-B", str(CLI), "gate", "pre-commit", "--repo", "status", "--json"],
            cwd=self.base, env=self.env, input=b"unused stdin", capture_output=True, timeout=5)
        self.assertEqual(process.returncode, 3)
        value = json.loads(process.stdout)
        self.assertEqual(value["schema"], "scan_secrets_gate_v1")
        self.assertEqual(value["reason"], "not_repository")

    def test_gate_default_capacity_reaches_late_staged_secret_beyond_legacy_limits(self):
        for number in range(300):
            (self.repo / f"candidate-{number:04}.bin").write_bytes(b"\0" * 32768)
        (self.repo / "candidate-0299.bin").write_bytes(b"\0" * 32768 + self.credential())
        self.git("add", ".")
        value = self.gate(1)
        self.assertEqual(value["counts"]["inspected_snapshots"], 300)
        self.assertGreater(value["counts"]["candidate_bytes"], 8388608)
        self.assertTrue(value["coverage_complete"])
        self.assertEqual(value["limits"]["max_objects"], 4096)

    def test_help_or_invalid_gate_invocation_cannot_authorize_commit(self):
        self.seed()
        for extra in (("--help",), ("--force",)):
            self.install_dispatcher(extra_args=extra)
            (self.repo / "selected.txt").write_text("safe changed " + extra[0])
            self.git("add", ".")
            before = self.head()
            self.assertNotEqual(self.git("commit", "--quiet", "-m", "no gate result", check=False).returncode, 0)
            self.assertEqual(self.head(), before)

    def test_renamed_and_new_credential_paths_reusing_old_blob_stay_selected(self):
        self.seed()
        self.install_dispatcher()
        oid = self.git("rev-parse", "HEAD:selected.txt").stdout
        before = self.head()
        self.git("mv", "selected.txt", "credentials.cfg")
        self.assertEqual(self.git("rev-parse", ":credentials.cfg").stdout, oid)
        value = self.gate(1)
        self.assertIn("credential_path", {finding["pattern"] for finding in value["findings"]})
        self.assertNotEqual(self.git("commit", "--quiet", "-m", "credential path rename", check=False).returncode, 0)
        self.assertEqual(self.head(), before)
        self.git("reset", "--hard", "HEAD")
        (self.repo / "credentials.cfg").write_bytes(b"base\n")
        self.git("add", "credentials.cfg")
        self.assertEqual(self.git("rev-parse", ":credentials.cfg").stdout, oid)
        self.assertEqual(self.gate(1)["counts"]["candidates"], 1)
        self.assertNotEqual(self.git("commit", "--quiet", "-m", "new credential path", check=False).returncode, 0)
        self.assertEqual(self.head(), before)

    def test_status_displays_old_policy_and_admits_new_policy_only_for_index(self):
        self.seed()
        (self.repo / "selected.txt").write_text("safe changed content\n")
        self.git("add", "selected.txt")
        self.gate(0)
        process = self.cli("status", "--json")
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(json.loads(process.stdout)["last_scan"]["policy_version"], "selected_staged_v1")
        records = list((self.base / "data/scan-secrets/status").glob("*.json"))
        self.assertEqual(len(records), 1)
        record = json.loads(records[0].read_text())
        record["policy_version"] = "selected_index_v1"
        records[0].write_text(json.dumps(record))
        process = self.cli("status", "--json")
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        value = json.loads(process.stdout)
        self.assertTrue(value["historical"])
        self.assertFalse(value["authorizes_publication"])
        self.assertEqual(value["last_scan"]["policy_version"], "selected_index_v1")
        record.update(policy_version="selected_staged_v1", scope="worktree")
        records[0].write_text(json.dumps(record))
        self.assertEqual(self.cli("status", "--json").returncode, 2)

    def test_sha256_selection_keeps_full_changed_bytes_and_blob_hash_verification(self):
        import zlib
        self.repo = self.base / "sha256-repo"
        self.repo.mkdir()
        self.git("init", "--quiet", "--object-format=sha256")
        self.seed(self.credential() + b"\n")
        self.install_dispatcher()
        (self.repo / "unrelated.txt").write_text("safe unrelated change\n")
        self.git("add", "unrelated.txt")
        self.git("commit", "--quiet", "-m", "safe unrelated SHA256 commit")
        before = self.head()
        (self.repo / "selected.txt").write_bytes(self.credential() + b"\nnew safe line\n")
        self.git("add", "selected.txt")
        self.assertEqual(self.gate(1)["counts"]["candidates"], 1)
        self.assertNotEqual(self.git("commit", "--quiet", "-m", "unchanged secret line SHA256", check=False).returncode, 0)
        self.assertEqual(self.head(), before)
        oid = self.git("rev-parse", ":selected.txt").stdout.decode().strip()
        self.assertEqual(len(oid), 64)
        object_file = self.repo / ".git/objects" / oid[:2] / oid[2:]
        object_file.chmod(0o600)
        substituted = b"clean substituted bytes\n"
        object_file.write_bytes(zlib.compress(b"blob " + str(len(substituted)).encode() + b"\0" + substituted))
        self.assertEqual(self.gate(2)["reason"], "git_output_invalid")


if __name__ == "__main__":
    unittest.main()
