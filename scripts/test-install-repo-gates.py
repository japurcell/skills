#!/usr/bin/env python3
"""Repository gate preview, activation, composition and recovery through public CLIs."""
import hashlib
import errno
import json
import os
from pathlib import Path
import shutil
import signal
import time
import stat
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parent.parent
PYTHON = str(Path(sys.executable).resolve())
GIT = "/Library/Developer/CommandLineTools/usr/bin/git" if sys.platform == "darwin" else shutil.which("git")


class RepositoryPreviewTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="repository preview ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.home = self.root / "home"
        self.home.mkdir()
        self.captures = self.root / "temporary captures"
        self.captures.mkdir()
        self.repo = self.root / "repository with spaces"
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.env.update(HOME=str(self.home), USERPROFILE=str(self.home),
            XDG_CONFIG_HOME=str(self.home / "config"), XDG_DATA_HOME=str(self.home / "data"),
            LOCALAPPDATA=str(self.home / "local"), TMPDIR=str(self.captures), TEMP=str(self.captures), TMP=str(self.captures), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_SYSTEM=os.devnull)
        self.git("init", "-q", str(self.repo), cwd=self.root)

    def git(self, *args, cwd=None):
        result = subprocess.run([GIT, *args], cwd=cwd or self.repo, env=self.env,
            capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        return result.stdout

    def command(self, *args, entry=None, env=None, git=GIT):
        arguments = list(args)
        if git is not None and "--dry-run" in arguments:
            arguments.extend(["--git", git])
        return subprocess.run([PYTHON, "-I", "-S", "-B", str(entry or SOURCE / "scripts/scan-secrets.py"),
            *arguments], env=env or self.env, cwd=self.root, capture_output=True, text=True, timeout=15)

    def preview(self, *args, action="install", entry=None, env=None):
        result = self.command("hooks", action, "--repo", str(self.repo), "--dry-run", "--json", *args,
            entry=entry, env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        value = json.loads(result.stdout)
        self.assertEqual(value["schema"], "scan_secrets_repo_install_v1")
        self.assertFalse(value["activated"])
        self.assertFalse(value["changes_applied"])
        self.assertFalse(value["authorizes_publication"])
        return value

    def fingerprint(self):
        return [(str(path.relative_to(self.root)), path.lstat().st_mode,
            os.readlink(path) if path.is_symlink() else hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None)
            for path in sorted(self.root.rglob("*"))]

    def activate(self, *options, action="install"):
        result = self.command("hooks", action, "--repo", str(self.repo), "--git", GIT, "--json", *options)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_install_reinstall_commit_gate_and_uninstall_public_workflow(self):
        original = (self.repo / ".git/config").read_bytes()
        installed = self.activate()
        self.assertTrue(installed["activated"])
        before = self.fingerprint()
        repeated = self.activate()
        self.assertFalse(repeated["changes_applied"])
        self.assertEqual(before, self.fingerprint())
        path = self.repo / "content.txt"
        path.write_text("safe content\n")
        self.git("add", "content.txt")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
                 "commit", "-q", "-m", "clean")
        path.write_text("token=" + "ghp_" + "A" * 36 + "\n")
        self.git("add", "content.txt")
        rejected = subprocess.run([GIT, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-q", "-m", "blocked"], cwd=self.repo, env=self.env,
            capture_output=True, text=True, timeout=15)
        self.assertNotEqual(rejected.returncode, 0, rejected.stdout + rejected.stderr)
        self.assertIn("content.txt", rejected.stderr)
        self.assertNotIn("ghp_" + "A" * 36, rejected.stderr)
        self.activate(action="uninstall")
        self.assertEqual((self.repo / ".git/config").read_bytes(), original)

    def hook(self, name, body):
        path = self.repo / ".git/hooks" / name
        path.write_text("#!/bin/sh\n" + body)
        path.chmod(0o755)
        return path

    def test_absent_original_hook_directories_preserve_real_git_operations(self):
        for custom in (False, True):
            with self.subTest(custom_hooks_path=custom):
                self.repo = self.root / ("custom hooks repository" if custom else "empty template repository")
                self.git("init", "-q", "--template=", "-b", "main", str(self.repo), cwd=self.root)
                original_hooks = self.root / "missing hooks" / "nested" if custom else self.repo / ".git/hooks"
                if custom:
                    self.git("config", "core.hooksPath", str(original_hooks))
                self.assertFalse(original_hooks.exists())
                original_config = (self.repo / ".git/config").read_bytes()
                self.activate()
                (self.repo / "content.txt").write_text("safe content\n")
                self.git("add", "content.txt")
                self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                         "-c", "commit.gpgsign=false", "commit", "-qm", "clean")
                committed = self.git("rev-parse", "HEAD")
                self.git("update-ref", "refs/heads/repair", committed.decode().strip())
                self.git("checkout", "-q", "repair")
                self.assertEqual(self.git("rev-parse", "HEAD"), committed)
                self.assertEqual(self.git("show", "HEAD:content.txt"), b"safe content\n")
                self.assertFalse(original_hooks.exists())
                self.activate(action="uninstall")
                self.assertEqual((self.repo / ".git/config").read_bytes(), original_config)
                self.assertFalse(original_hooks.exists())

    def test_original_hook_ancestor_drift_still_blocks_passthrough(self):
        for replacement in ("missing", "symlink", "file"):
            with self.subTest(replacement=replacement):
                self.repo = self.root / (replacement + " hooks repository")
                self.git("init", "-q", str(self.repo), cwd=self.root)
                original_hooks = self.repo / ".git/hooks"
                if replacement == "missing":
                    self.hook("prepare-commit-msg", "exit 0\n")
                self.activate()
                directory = Path(self.owner_manifest()["installed_value"])
                shutil.rmtree(original_hooks)
                if replacement == "symlink":
                    target = self.root / "foreign hooks"
                    target.mkdir()
                    original_hooks.symlink_to(target, target_is_directory=True)
                elif replacement == "file":
                    original_hooks.write_text("not a hook directory\n")
                result = subprocess.run([str(directory / "prepare-commit-msg")], cwd=self.repo,
                    env=self.env, input=b"", capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn(b"original_hook_drift", result.stderr)

    def test_actual_push_rejects_intermediate_history_before_original_hook(self):
        remote = self.root / "remote.git"
        self.git("init", "--bare", "-q", str(remote), cwd=self.root)
        self.git("remote", "add", "origin", str(remote))
        marker = self.root / "push-hook-ran"
        self.hook("pre-push", "printf '%s\\n' \"$0\" > '" + str(marker) + "'\ncat >> '" + str(marker) + "'\n")
        self.activate()
        path = self.repo / "content.txt"
        for message, text in (("first", "safe\n"),):
            path.write_text(text)
            self.git("add", "content.txt")
            self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", message)
        self.git("push", "-q", "origin", "HEAD:refs/heads/main")
        self.assertIn(str(self.repo / ".git/hooks/pre-push"), marker.read_text())
        self.assertIn("refs/heads/main", marker.read_text())
        marker.unlink()
        # Use the explicit Git bypass only to construct outgoing bad history.
        for message, text in (("bad", "token=" + "ghp_" + "B" * 36 + "\n"), ("repaired tip", "safe again\n")):
            path.write_text(text)
            self.git("add", "content.txt")
            self.git("-c", "core.hooksPath=" + os.devnull, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", message)
        before = self.git("rev-parse", "refs/heads/main", cwd=remote)
        rejected = subprocess.run([GIT, "push", "origin", "HEAD:refs/heads/main"], cwd=self.repo,
            env=self.env, capture_output=True, text=True, timeout=20)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("content.txt", rejected.stderr)
        self.assertNotIn("ghp_" + "B" * 36, rejected.stderr)
        self.assertFalse(marker.exists())
        self.assertEqual(self.git("rev-parse", "refs/heads/main", cwd=remote), before)

    def test_original_paths_args_protocol_and_unrelated_config_survive(self):
        marker = self.root / "hook-observations"
        resource = self.repo / ".git/hooks/resource"
        resource.write_text("sibling content\n")
        self.hook("commit-msg", 'printf "%s\\n" "$0" "$1" >> "' + str(marker) + '"\ncat "$(dirname "$0")/resource" >> "' + str(marker) + '"\n')
        self.hook("post-commit", 'printf "post\\n" >> "' + str(marker) + '"\n')
        self.activate()
        self.git("config", "fixture.unrelated", "keep-current")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "fixture")
        content = marker.read_text()
        self.assertIn(str(self.repo / ".git/hooks/commit-msg"), content)
        self.assertIn("sibling content", content)
        self.assertTrue(content.endswith("post\n"))
        self.activate(action="uninstall")
        self.assertEqual(self.git("config", "fixture.unrelated").strip(), b"keep-current")
        self.assertEqual(self.preview(action="uninstall")["snapshot"]["ownership"]["state"], "retired")

    def test_git_pin_ignores_repository_path_shim_and_preserves_hook_path(self):
        binary = self.repo / "bin"
        binary.mkdir()
        marker = self.root / "shim-ran"
        shim = binary / "git"
        shim.write_text("#!/bin/sh\ntouch '" + str(marker) + "'\nexit 99\n")
        shim.chmod(0o755)
        seen = self.root / "original-path"
        self.hook("pre-commit", 'printf "%s" "$PATH" > "' + str(seen) + '"\n')
        env = dict(self.env, PATH=str(binary) + os.pathsep + self.env.get("PATH", os.defpath))
        result = subprocess.run([GIT, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "fixture"],
            cwd=self.repo, env=env, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists())
        baseline = seen.read_text()
        self.activate()
        result = subprocess.run([GIT, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "installed fixture"],
            cwd=self.repo, env=env, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists())
        self.assertEqual(seen.read_text(), baseline)

    def test_uninstall_from_healthy_source_preserves_changed_original_and_missing_helper(self):
        hook = self.hook("pre-commit", "exit 0\n")
        self.activate()
        hook.write_text("#!/bin/sh\nexit 17\n")
        manifest = json.loads((self.repo / ".git/scan-secrets/repository-installation.json").read_text())
        helper = Path(manifest["installed_value"]).parent / "bundle/hooks/runtime/scan_dispatch.py"
        helper.unlink()
        result = self.activate(action="uninstall")
        self.assertFalse(result["activated"])
        self.assertIn("exit 17", hook.read_text())
        self.assertEqual(self.preview()["snapshot"]["hooks_path"]["source"], "default")

    def test_missing_scanner_does_not_block_original_checkout_protocol(self):
        marker = self.root / "checkout-ran"
        self.hook("post-checkout", 'printf "%s\\n" "$0" "$@" > "' + str(marker) + '"\n')
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "initial")
        self.activate()
        manifest = json.loads((self.repo / ".git/scan-secrets/repository-installation.json").read_text())
        (Path(manifest["installed_value"]).parent / "bundle/hooks/runtime/scan_dispatch.py").unlink()
        self.git("checkout", "-qb", "repair")
        self.assertIn(str(self.repo / ".git/hooks/post-checkout"), marker.read_text())
        denied = subprocess.run([GIT, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "blocked"],
            cwd=self.repo, env=self.env, capture_output=True, text=True, timeout=15)
        self.assertNotEqual(denied.returncode, 0)

    def owner_manifest(self):
        return json.loads((self.repo / ".git/scan-secrets/repository-installation.json").read_text())

    def test_explicit_binding_update_and_reinstall_after_uninstall_keep_backups(self):
        self.activate("--remote", "first", "--url", str(self.root / "first.git"))
        first = self.owner_manifest()
        old_generation = Path(first["installed_value"]).parent
        self.activate("--remote", "second", "--url", str(self.root / "second.git"))
        second = self.owner_manifest()
        self.assertNotEqual(first["installed_value"], second["installed_value"])
        self.assertTrue((old_generation / "backups/config.before").is_file())
        chosen = json.loads((Path(second["installed_value"]).parent / second["bindings"][0]).read_text())
        self.assertEqual(chosen["remote"], "second")
        self.activate(action="uninstall")
        self.activate()
        self.assertTrue(self.owner_manifest()["phase"] == "active")
        self.assertTrue((old_generation / "backups/config.before").is_file())

    def test_rewrite_destinations_are_refused_before_mutation(self):
        self.git("config", "remote.origin.url", "shortcut:repo")
        self.git("config", "url." + str(self.root / "actual") + ".insteadOf", "shortcut:")
        before = self.fingerprint()
        result = self.command("hooks", "install", "--repo", str(self.repo), "--git", GIT, "--json")
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "installation_url_rewrite_unsupported")
        self.assertEqual(before, self.fingerprint())

    def test_relevant_global_hook_configuration_drift_blocks_actual_push(self):
        first = self.home / "original hooks"
        second = self.home / "changed hooks"
        first.mkdir()
        second.mkdir()
        self.git("config", "--global", "core.hooksPath", str(first))
        remote = self.root / "remote.git"
        self.git("init", "--bare", "-q", str(remote), cwd=self.root)
        self.git("remote", "add", "origin", str(remote))
        self.activate()
        self.git("config", "--global", "user.name", "unrelated setting")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "initial")
        self.git("push", "-q", "origin", "HEAD:refs/heads/main")
        self.git("config", "--global", "core.hooksPath", str(second))
        rejected = subprocess.run([GIT, "push", "origin", "HEAD:refs/heads/other"], cwd=self.repo,
            env=self.env, capture_output=True, text=True, timeout=20)
        self.assertNotEqual(rejected.returncode, 0, rejected.stdout + rejected.stderr)
        self.assertIn("hook_configuration_drift", rejected.stderr)

    def test_branch_dependent_hooks_are_refused_before_activation(self):
        conditional = self.home / "branch-config"
        conditional.write_text('[core]\n hooksPath = branch-hooks\n')
        self.git("config", "includeIf.onbranch:other.path", str(conditional))
        before = self.fingerprint()
        result = self.command("hooks", "install", "--repo", str(self.repo), "--git", GIT, "--json")
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "installation_branch_include_unsupported")
        self.assertEqual(before, self.fingerprint())

    def test_real_standard_lfs_install_blocks_transfer_then_delivers_checked_bytes(self):
        import importlib.util
        specification = importlib.util.spec_from_file_location("lfs_fixture", SOURCE / "scripts/test-scan-secrets-lfs.py")
        support = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(support)
        endpoint = support.RecordingEndpoint()
        self.addCleanup(endpoint.close)
        lfs = Path(os.environ.get("TEST_GIT_LFS", "/tmp/design-b-lfs-3.8.0/git-lfs-3.8.0/git-lfs"))
        self.assertTrue(lfs.is_file(), "TEST_GIT_LFS must select the real Git LFS 3.8.0 fixture tool")
        remote = self.root / "remote.git"
        self.git("init", "--bare", "-q", str(remote), cwd=self.root)
        self.git("remote", "add", "origin", str(remote))
        installed = subprocess.run([str(lfs), "install", "--local"], cwd=self.repo, env=self.env,
            capture_output=True, text=True, timeout=10)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.activate("--lfs", str(lfs), "--lfs-endpoint", endpoint.url)
        def pointer(raw):
            oid = hashlib.sha256(raw).hexdigest()
            payload = self.repo / ".git/lfs/objects" / oid[:2] / oid[2:4] / oid
            payload.parent.mkdir(parents=True, exist_ok=True)
            payload.write_bytes(raw)
            (self.repo / "payload.bin").write_text("version https://git-lfs.github.com/spec/v1\noid sha256:" + oid + "\nsize " + str(len(raw)) + "\n")
            self.git("add", "payload.bin")
            return oid
        pointer(b"token=" + b"ghp_" + b"C" * 36 + b"\n")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "pointer")
        denied = subprocess.run([GIT, "push", "origin", "HEAD:refs/heads/main"], cwd=self.repo,
            env=self.env, capture_output=True, text=True, timeout=20)
        self.assertNotEqual(denied.returncode, 0)
        self.assertIn("payload.bin", denied.stderr)
        self.assertEqual(endpoint.received_bytes, 0)
        self.assertEqual(endpoint.batches, [])
        clean = b"verified clean payload\n"
        oid = pointer(clean)
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--amend", "-qm", "clean pointer")
        self.git("push", "-q", "origin", "HEAD:refs/heads/main")
        self.assertEqual(endpoint.payloads, {oid: clean})
        self.assertEqual(endpoint.received_bytes, len(clean))

    def test_installed_commit_rechecks_budget_trust_and_uses_edited_content(self):
        budget = self.home / "budget.json"
        document = {"schema_version": 1,
            "checkpoint": {"max_objects": 4096, "max_candidate_bytes": 67108864, "max_seconds": 30,
                "max_capture_bytes": 134217728, "max_temp_bytes": 268435456},
            "publication": {"max_objects": 20000, "max_candidate_bytes": 268435456, "max_seconds": 120,
                "max_capture_bytes": 536870912, "max_temp_bytes": 805306368}}
        budget.write_text(json.dumps(document))
        budget.chmod(0o600)
        self.activate("--budget-file", str(budget))
        budget.chmod(0o666)
        result = subprocess.run([GIT, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "untrusted"],
            cwd=self.repo, env=self.env, capture_output=True, text=True, timeout=15)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        budget.chmod(0o600)
        document["checkpoint"]["max_objects"] = 1
        budget.write_text(json.dumps(document))
        for name in ("one.txt", "two.txt"):
            (self.repo / name).write_text("safe\n")
        self.git("add", "one.txt", "two.txt")
        result = subprocess.run([GIT, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "over edited limit"],
            cwd=self.repo, env=self.env, capture_output=True, text=True, timeout=15)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("snapshot_count_limit", result.stderr)

    def fault_process(self, mode, phase="prepared", action="install", scope=None):
        marker = self.root / (mode + "-" + phase + "-reached")
        wrapper = self.root / "os-fault-boundary.py"
        wrapper.write_text("""import hashlib, json, os, runpy, signal, sys, time
from pathlib import Path
entry, repository, git, marker, mode, phase, action, scope = sys.argv[1:]
sys.argv = [entry, 'hooks', action, '--repo', repository, '--git', git, '--json']
if scope != 'none':
    sys.argv += ['--scope', scope]
owner = Path(repository) / '.git/scan-secrets/repository-installation.json'
config = Path(repository) / '.git/config'
inside = False
activated = False
def fault(event, arguments):
    global inside, activated
    if inside or activated or event not in {'os.scandir', 'open'}:
        return
    inside = True
    try:
        if not owner.is_file():
            return
        value = json.loads(owner.read_text())
        ready = phase == 'prepared' and value['phase'] == 'prepared' and event == 'os.scandir'
        ready = ready or (phase == 'promoted' and value['phase'] == 'prepared' and event == 'open'
            and str(arguments[0]).endswith('.repository-installation.json.new')
            and hashlib.sha256(config.read_bytes()).hexdigest() == value['after'])
        ready = ready or (phase == 'retiring' and value['phase'] == 'retiring' and event == 'open' and arguments[0] == 'config')
        if not ready:
            return
        activated = True
        Path(marker).write_text('OS boundary reached')
        if mode == 'interrupt':
            os.kill(os.getpid(), signal.SIGINT)
        if mode == 'failure':
            raise OSError('PRIVATE-CREDENTIAL')
        while True:
            time.sleep(0.01)
    finally:
        inside = False
sys.addaudithook(fault)
runpy.run_path(entry, run_name='__main__')
""")
        process = subprocess.Popen([PYTHON, "-I", "-S", "-B", str(wrapper), str(SOURCE / "scripts/scan-secrets.py"),
            str(self.repo), GIT, str(marker), mode, phase, action, scope or "none"], env=self.env, cwd=self.root,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        deadline = time.monotonic() + 8
        while not marker.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.005)
        self.assertTrue(marker.exists(), process.communicate(timeout=5) if process.poll() is not None else "fault boundary was not reached")
        self.addCleanup(lambda: process.poll() is None and process.kill())
        return process

    def test_prepared_cancellation_recovers_through_public_cli(self):
        original = (self.repo / ".git/config").read_bytes()
        process = self.fault_process("interrupt")
        stdout, stderr = process.communicate(timeout=5)
        self.assertEqual(process.returncode, 130, stdout + stderr)
        self.assertNotIn("PRIVATE-CREDENTIAL", stdout + stderr)
        self.assertEqual((self.repo / ".git/config").read_bytes(), original)
        self.assertEqual(self.owner_manifest()["phase"], "prepared")
        self.assertEqual(self.activate()["outcome"], "recovered")
        self.assertEqual(self.owner_manifest()["phase"], "active")

    def test_journaled_hard_kill_and_cooperating_writers_recover(self):
        original = (self.repo / ".git/config").read_bytes()
        process = self.fault_process("kill")
        concurrent = self.command("hooks", "install", "--repo", str(self.repo), "--git", GIT, "--json")
        self.assertEqual(json.loads(concurrent.stdout)["reason"], "installation_busy")
        writer = subprocess.run([GIT, "config", "fixture.concurrent", "must-not-overwrite"], cwd=self.repo,
            env=self.env, capture_output=True, text=True, timeout=5)
        self.assertNotEqual(writer.returncode, 0)
        self.assertEqual((self.repo / ".git/config").read_bytes(), original)
        process.kill()
        process.communicate(timeout=5)
        self.assertEqual(process.returncode, -signal.SIGKILL)
        self.assertTrue((self.repo / ".git/config.lock").exists())
        self.assertEqual(self.activate()["outcome"], "recovered")
        self.assertFalse((self.repo / ".git/config.lock").exists())

    def test_foreign_replacement_config_lock_is_never_recovered(self):
        process = self.fault_process("kill")
        process.kill()
        process.communicate(timeout=5)
        lock = self.repo / ".git/config.lock"
        lock.rename(self.repo / ".git/retained-owned-lock")
        lock.write_bytes(b"foreign writer content\n")
        lock.chmod(0o600)
        before = self.fingerprint()
        result = self.command("hooks", "install", "--repo", str(self.repo), "--git", GIT, "--json")
        self.assertEqual(json.loads(result.stdout)["reason"], "installation_config_busy")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(before, self.fingerprint())

    def test_post_promotion_and_retiring_hard_kills_recover(self):
        process = self.fault_process("kill", "promoted")
        process.kill()
        process.communicate(timeout=5)
        self.assertEqual(self.owner_manifest()["phase"], "prepared")
        self.assertEqual(self.activate()["outcome"], "recovered")
        process = self.fault_process("kill", "retiring", action="uninstall")
        process.kill()
        process.communicate(timeout=5)
        self.assertEqual(self.owner_manifest()["phase"], "retiring")
        self.activate(action="uninstall")
        self.assertEqual(self.owner_manifest()["phase"], "retired")

    def test_enabled_worktree_scope_does_not_change_siblings_or_extensions(self):
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "initial")
        linked = self.root / "linked repository"
        self.git("worktree", "add", "-qb", "linked", str(linked))
        original = self.repo
        self.repo = linked
        before = self.fingerprint()
        refused = self.command("hooks", "install", "--repo", str(linked), "--git", GIT, "--json")
        self.assertEqual(json.loads(refused.stdout)["reason"], "installation_shared_worktree_scope_unsupported")
        self.assertEqual(before, self.fingerprint())
        self.git("config", "extensions.worktreeConfig", "true")
        shared = (original / ".git/config").read_bytes()
        self.activate("--scope", "worktree")
        self.assertEqual((original / ".git/config").read_bytes(), shared)
        sibling = subprocess.run([GIT, "config", "--get", "core.hooksPath"], cwd=original, env=self.env, capture_output=True, timeout=5)
        self.assertEqual(sibling.returncode, 1)
        self.assertEqual(sibling.stdout, b"")
        self.activate("--scope", "worktree", action="uninstall")
        self.assertEqual((original / ".git/config").read_bytes(), shared)
        gitdir = Path(self.git("rev-parse", "--absolute-git-dir").decode().strip())
        self.assertFalse((gitdir / "config.worktree").exists())

    def test_all_unrelated_hook_protocols_keep_original_path_streams_and_status(self):
        names = ("applypatch-msg", "pre-applypatch", "post-applypatch", "pre-merge-commit", "prepare-commit-msg", "commit-msg", "post-commit", "pre-rebase", "post-checkout", "post-merge", "pre-receive", "update", "proc-receive", "post-receive", "post-update", "reference-transaction", "push-to-checkout", "pre-auto-gc", "post-rewrite", "sendemail-validate", "fsmonitor-watchman", "p4-changelist", "p4-prepare-changelist", "p4-post-changelist", "p4-pre-submit", "post-index-change")
        for name in names:
            self.hook(name, 'printf "%s\\n" "$0" "$@"\ncat\nexit 7\n')
        self.activate()
        directory = Path(self.owner_manifest()["installed_value"])
        payload = b"protocol\x00bytes\xff\n"
        for name in names:
            with self.subTest(hook=name):
                result = subprocess.run([str(directory / name), "argument with spaces", "second"],
                    cwd=self.repo, env=self.env, input=payload, capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 7, result.stderr)
                expected = str(self.repo / ".git/hooks" / name).encode() + b"\nargument with spaces\nsecond\n" + payload
                self.assertEqual(result.stdout, expected)
                self.assertEqual(result.stderr, b"")

    def test_installed_partial_and_alternate_index_commits_use_selected_content(self):
        for name in ("chosen.txt", "other.txt"):
            (self.repo / name).write_text("safe\n")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "initial")
        self.activate()
        (self.repo / "other.txt").write_text("token=" + "ghp_" + "D" * 36 + "\n")
        self.git("add", "other.txt")
        (self.repo / "chosen.txt").write_text("safe chosen edit\n")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--only", "chosen.txt", "-qm", "partial clean")
        index = self.root / "alternate-index"
        environment = dict(self.env, GIT_INDEX_FILE=str(index))
        for arguments in (("read-tree", "HEAD"), ("add", "chosen.txt")):
            result = subprocess.run([GIT, *arguments], cwd=self.repo, env=environment, capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([GIT, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "alternate clean"],
            cwd=self.repo, env=environment, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        denied = subprocess.run([GIT, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "real index blocked"],
            cwd=self.repo, env=self.env, capture_output=True, text=True, timeout=15)
        self.assertNotEqual(denied.returncode, 0)
        self.assertIn("other.txt", denied.stderr)

    def test_installed_commit_accounts_for_parent_and_child_capture_bytes(self):
        empty = subprocess.run([GIT, "hash-object", "-w", "--stdin"], input=b"", cwd=self.repo, env=self.env, capture_output=True, timeout=5)
        self.assertEqual(empty.returncode, 0)
        oid = empty.stdout.strip()
        rows = b"".join(b"100644 " + oid + b"\tentry-" + str(index).encode().zfill(6) + b".txt\n" for index in range(8000))
        indexed = subprocess.run([GIT, "update-index", "--index-info"], input=rows, cwd=self.repo, env=self.env, capture_output=True, timeout=5)
        self.assertEqual(indexed.returncode, 0, indexed.stderr)
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "large unchanged index")
        (self.repo / "entry-000000.txt").write_text("safe changed content\n")
        self.git("add", "entry-000000.txt")
        budget = self.home / "small-budget.json"
        budget.write_text(json.dumps({"schema_version": 1,
            "checkpoint": {"max_objects": 4096, "max_candidate_bytes": 1048576, "max_seconds": 30,
                "max_capture_bytes": 1048576, "max_temp_bytes": 4194304},
            "publication": {"max_objects": 20000, "max_candidate_bytes": 268435456, "max_seconds": 120,
                "max_capture_bytes": 536870912, "max_temp_bytes": 805306368}}))
        budget.chmod(0o600)
        direct = self.command("gate", "pre-commit", "--repo", str(self.repo), "--budget-file", str(budget), "--json", "--git", GIT)
        self.assertEqual(direct.returncode, 0, direct.stdout + direct.stderr)
        self.activate("--budget-file", str(budget))
        denied = subprocess.run([GIT, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "composed over budget"],
            cwd=self.repo, env=self.env, capture_output=True, text=True, timeout=15)
        self.assertNotEqual(denied.returncode, 0, denied.stdout + denied.stderr)
        self.assertIn("capture_bytes_limit", denied.stderr)

    def test_staging_uses_held_git_ancestry_without_foreign_writes(self):
        foreign = self.root / "foreign metadata"
        foreign.mkdir()
        retained = self.root / "retained metadata"
        marker = self.root / "ancestry boundary reached"
        wrapper = self.root / "ancestry-boundary.py"
        wrapper.write_text("""import os, runpy, sys
from pathlib import Path
entry, repository, git, foreign, retained, marker = sys.argv[1:]
sys.argv = [entry, 'hooks', 'install', '--repo', repository, '--git', git, '--json']
gitdir = Path(repository) / '.git'
activated = False
def fault(event, arguments):
    global activated
    if activated:
        return
    selected = Path(str(arguments[0])) if arguments and event in {'tempfile.mkdtemp', 'os.mkdir'} else None
    if selected is None or not selected.name.startswith('.scan-secrets-prepare-'):
        return
    activated = True
    gitdir.rename(retained)
    gitdir.symlink_to(foreign, target_is_directory=True)
    Path(marker).write_text('held-parent substitution reached')
sys.addaudithook(fault)
runpy.run_path(entry, run_name='__main__')
""")
        original_config = (self.repo / ".git/config").read_bytes()
        before = list(foreign.iterdir())
        result = subprocess.run([PYTHON, "-I", "-S", "-B", str(wrapper), str(SOURCE / "scripts/scan-secrets.py"),
            str(self.repo), GIT, str(foreign), str(retained), str(marker)], env=self.env,
            capture_output=True, text=True, timeout=10)
        self.assertTrue(marker.exists(), result.stdout + result.stderr)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(foreign.iterdir()), before)
        self.assertEqual((retained / "config").read_bytes(), original_config)

    def test_config_edit_keeps_held_directory_under_late_ancestor_substitution(self):
        foreign = self.root / "foreign metadata"
        foreign.mkdir()
        retained = self.root / "retained metadata"
        marker = self.root / "config-edit substitution reached"
        wrapper = self.root / "config-edit-boundary.py"
        wrapper.write_text("""import os, runpy, sys
from pathlib import Path
entry, repository, git, foreign, retained, marker = sys.argv[1:]
sys.argv = [entry, 'hooks', 'install', '--repo', repository, '--git', git, '--json']
gitdir = Path(repository) / '.git'
activated = False
def fault(event, arguments):
    global activated
    if activated or event != 'open' or arguments[0] != 'config-edit':
        return
    activated = True
    stage = next(path for path in gitdir.iterdir() if path.name.startswith('.scan-secrets-prepare-'))
    generation = next((stage / 'installations').iterdir())
    gitdir.rename(retained)
    gitdir.symlink_to(foreign, target_is_directory=True)
    redirected = Path(foreign) / stage.name / 'installations' / generation.name
    redirected.mkdir(parents=True)
    (redirected / 'config-edit').write_text('[core]\\n hooksPath = foreign\\n[fixture]\\n keep = foreign\\n')
    Path(marker).write_text(str(redirected))
sys.addaudithook(fault)
runpy.run_path(entry, run_name='__main__')
""")
        result = subprocess.run([PYTHON, "-I", "-S", "-B", str(wrapper), str(SOURCE / "scripts/scan-secrets.py"),
            str(self.repo), GIT, str(foreign), str(retained), str(marker)], env=self.env, capture_output=True, text=True, timeout=10)
        self.assertTrue(marker.exists(), result.stdout + result.stderr)
        self.assertNotEqual(result.returncode, 0)
        redirected = Path(marker.read_text())
        self.assertEqual([path.name for path in redirected.iterdir()], ["config-edit"])
        self.assertEqual((redirected / "config-edit").read_text(), "[core]\n hooksPath = foreign\n[fixture]\n keep = foreign\n")

    def test_source_free_neutral_install_activates_self_contained_real_git_gates(self):
        source = self.root / "disposable source"
        shutil.copytree(SOURCE / "hooks", source / "hooks", ignore=shutil.ignore_patterns("__pycache__"))
        (source / "scripts").mkdir()
        for name in ("scan-secrets.py", "scan_install_windows.py"):
            shutil.copy2(SOURCE / "scripts" / name, source / "scripts" / name)
        destination = self.home / "private neutral runtime"
        installed = subprocess.run([PYTHON, "-I", "-S", "-B", str(SOURCE / "scripts/install-scan-secrets.py"),
            "install", "--source-dir", str(source), "--destination", str(destination), "--json"],
            env=self.env, capture_output=True, text=True, timeout=15)
        self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
        shutil.rmtree(source)
        remote = self.root / "remote.git"
        self.git("init", "--bare", "-q", str(remote), cwd=self.root)
        self.git("remote", "add", "origin", str(remote))
        activated = subprocess.run([str(destination / "scan-secrets"), "hooks", "install", "--repo", str(self.repo), "--git", GIT, "--json"],
            env=self.env, capture_output=True, text=True, timeout=15)
        self.assertEqual(activated.returncode, 0, activated.stdout + activated.stderr)
        shutil.rmtree(destination)
        (self.repo / "safe.txt").write_text("safe content\n")
        self.git("add", "safe.txt")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "self contained")
        self.git("push", "-q", "origin", "HEAD:refs/heads/main")
        self.activate(action="uninstall")

    def test_global_include_and_relative_original_hooks_are_preserved(self):
        original = (self.repo / ".git/config").read_bytes()
        include = self.home / "global included settings"
        include.write_text('[core]\n hooksPath = relative-hooks\n')
        self.git("config", "--global", "include.path", str(include))
        directory = self.repo / "relative-hooks"
        directory.mkdir()
        marker = self.root / "relative-original-ran"
        hook = directory / "pre-commit"
        hook.write_text('#!/bin/sh\nprintf "%s" "$0" > "' + str(marker) + '"\n')
        hook.chmod(0o755)
        global_before = (self.home / ".gitconfig").read_bytes()
        included_before = include.read_bytes()
        self.activate()
        self.assertEqual((self.home / ".gitconfig").read_bytes(), global_before)
        self.assertEqual(include.read_bytes(), included_before)
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "relative hook")
        self.assertEqual(marker.read_text(), str(hook))
        self.activate(action="uninstall")
        self.assertEqual((self.repo / ".git/config").read_bytes(), original)
        self.assertEqual(include.read_bytes(), included_before)

    def test_unknown_owned_inventory_is_preserved_and_diagnosed(self):
        self.activate()
        directory = Path(self.owner_manifest()["installed_value"]).parent
        unknown = directory / "unknown-user-file"
        unknown.write_text("preserve me\n")
        before = self.fingerprint()
        result = self.command("hooks", "uninstall", "--repo", str(self.repo), "--git", GIT, "--json")
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "installation_owned_inventory_drift")
        self.assertEqual(before, self.fingerprint())

    def test_changed_owned_bytes_and_hardlinks_are_never_overwritten(self):
        self.activate()
        directory = Path(self.owner_manifest()["installed_value"]).parent
        owned = directory / "bundle/hooks/runtime/scan_dispatch.py"
        owned.write_bytes(owned.read_bytes() + b"\n# user edit\n")
        external = self.home / "external hard link"
        os.link(owned, external)
        before = self.fingerprint()
        result = self.command("hooks", "uninstall", "--repo", str(self.repo), "--git", GIT, "--json")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(before, self.fingerprint())
        self.assertEqual(owned.read_bytes(), external.read_bytes())

    def test_reinstall_captures_safe_original_hook_additions(self):
        self.activate()
        hook = self.hook("pre-commit", "exit 7\n")
        denied = subprocess.run([GIT, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "drift refused"],
            cwd=self.repo, env=self.env, capture_output=True, text=True, timeout=15)
        self.assertNotEqual(denied.returncode, 0)
        self.activate()
        directory = Path(self.owner_manifest()["installed_value"])
        result = subprocess.run([str(directory / "pre-commit")], cwd=self.repo, env=self.env, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(hook.read_text(), "#!/bin/sh\nexit 7\n")

    def test_long_paths_and_all_present_hooks_never_activate_unreadable_ownership(self):
        parent = self.root
        for index in range(9):
            parent = parent / (str(index) + "p" * 59)
            parent.mkdir()
        selected = parent / "repository"
        self.repo.rename(selected)
        self.repo = selected
        names = ("applypatch-msg", "pre-applypatch", "post-applypatch", "pre-commit", "pre-merge-commit", "prepare-commit-msg", "commit-msg", "post-commit", "pre-rebase", "post-checkout", "post-merge", "pre-push", "pre-receive", "update", "proc-receive", "post-receive", "post-update", "reference-transaction", "push-to-checkout", "pre-auto-gc", "post-rewrite", "sendemail-validate", "fsmonitor-watchman", "p4-changelist", "p4-prepare-changelist", "p4-post-changelist", "p4-pre-submit", "post-index-change")
        for name in names:
            self.hook(name, "exit 0\n")
        original = (self.repo / ".git/config").read_bytes()
        result = self.command("hooks", "install", "--repo", str(self.repo), "--git", GIT, "--json")
        value = json.loads(result.stdout)
        if result.returncode == 0:
            self.assertTrue(value["activated"])
            self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "long-path proof")
            self.activate(action="uninstall")
        else:
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertEqual(value["reason"], "installation_ownership_limit")
            self.assertEqual(value["limit"], 65536)
            self.assertGreater(value["measured"], value["limit"])
            self.assertFalse((self.repo / ".git/scan-secrets").exists())
        self.assertEqual((self.repo / ".git/config").read_bytes(), original)

    def test_prepared_worktree_install_uninstalls_back_to_absent_configuration(self):
        self.git("config", "extensions.worktreeConfig", "true")
        original = (self.repo / ".git/config").read_bytes()
        process = self.fault_process("interrupt", scope="worktree")
        stdout, stderr = process.communicate(timeout=5)
        self.assertEqual(process.returncode, 130, stdout + stderr)
        self.assertFalse((self.repo / ".git/config.worktree").exists())
        self.activate("--scope", "worktree", action="uninstall")
        self.assertFalse((self.repo / ".git/config.worktree").exists())
        self.assertEqual((self.repo / ".git/config").read_bytes(), original)

    def test_unrelated_proc_receive_keeps_duplex_stream_timing(self):
        import select
        self.hook("proc-receive", 'printf "READY\\n"\nIFS= read -r line\nprintf "RECEIVED:%s\\n" "$line"\nexit 7\n')
        self.activate()
        path = Path(self.owner_manifest()["installed_value"]) / "proc-receive"
        process = subprocess.Popen([str(path)], cwd=self.repo, env=self.env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            self.assertTrue(select.select([process.stdout], [], [], 3)[0], "original hook must send before input EOF")
            self.assertEqual(process.stdout.readline(), b"READY\n")
            process.stdin.write(b"client message\n")
            process.stdin.flush()
            self.assertTrue(select.select([process.stdout], [], [], 3)[0])
            self.assertEqual(process.stdout.readline(), b"RECEIVED:client message\n")
            process.stdin.close()
            process.stdin = None
            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual((process.returncode, stdout, stderr), (7, b"", b""))
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)

    def test_two_install_uninstall_cycles_preserve_exact_original_local_config(self):
        config = self.repo / ".git/config"
        original = config.read_bytes() + b'\n# preserve this location and formatting\n[core]\n    hooksPath = "relative hooks" # original comment\n[fixture]\n  untouched = exact-bytes\n'
        config.write_bytes(original)
        for cycle in range(2):
            with self.subTest(cycle=cycle):
                self.activate()
                self.activate(action="uninstall")
                self.assertEqual(config.read_bytes(), original)

    def test_malformed_owned_dispatcher_types_are_invalid_configuration_without_writes(self):
        path = self.repo / ".git/scan-secrets/repository-installation.json"
        path.parent.mkdir(mode=0o700)
        for installed_value in (None, [], 7):
            with self.subTest(installed_value=installed_value):
                path.write_text(json.dumps({"schema": "scan_secrets_repository_owner_v1", "installed_value": installed_value}))
                path.chmod(0o600)
                before = self.fingerprint()
                for options in (("--dry-run",), ()):
                    result = self.command("hooks", "uninstall", "--repo", str(self.repo), "--git", GIT, "--json", *options)
                    self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                    value = json.loads(result.stdout)
                    self.assertEqual(value["reason"], "installation_ownership_invalid")
                    self.assertEqual(value["phase"], "ownership")
                    self.assertIn("Preserve", value["recovery"])
                    self.assertEqual(before, self.fingerprint())

    def test_explicit_reinstall_refreshes_same_path_trusted_git_identity(self):
        selected = self.root / "trusted direct Git"
        shutil.copyfile(GIT, selected)
        selected.chmod(0o755)
        arguments = ("hooks", "install", "--repo", str(self.repo), "--git", str(selected), "--json")
        installed = self.command(*arguments)
        self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
        before = selected.stat()
        os.utime(selected, ns=(before.st_atime_ns, before.st_mtime_ns + 1000000))
        refreshed = self.command(*arguments)
        self.assertEqual(refreshed.returncode, 0, refreshed.stdout + refreshed.stderr)
        self.assertTrue(json.loads(refreshed.stdout)["changes_applied"], "an explicit reinstall must refresh the current admitted Git identity")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "refreshed direct Git")

    def test_prepared_recovery_refuses_conflicting_explicit_selection(self):
        process = self.fault_process("interrupt")
        process.communicate(timeout=10)
        self.assertEqual(process.returncode, 130)
        self.assertEqual(self.owner_manifest()["phase"], "prepared")
        before = self.fingerprint()
        result = self.command("hooks", "install", "--repo", str(self.repo), "--git", GIT,
            "--remote", "selected", "--url", str(self.root / "selected.git"), "--json")
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "installation_recovery_selection_changed")
        self.assertEqual(before, self.fingerprint())
        self.activate(action="uninstall")
        self.activate("--remote", "selected", "--url", str(self.root / "selected.git"))

    def test_install_requires_finishing_retiring_recovery(self):
        self.activate()
        process = self.fault_process("kill", "retiring", action="uninstall")
        process.kill()
        process.communicate(timeout=10)
        self.assertEqual(self.owner_manifest()["phase"], "retiring")
        before = self.fingerprint()
        result = self.command("hooks", "install", "--repo", str(self.repo), "--git", GIT, "--json")
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "installation_retirement_recovery_required")
        self.assertEqual(before, self.fingerprint())
        self.activate(action="uninstall")
        self.activate()

    def test_control_character_repository_path_is_never_displayed(self):
        selected = self.repo.with_name("repository \x1b[31mPRIVATE-CREDENTIAL")
        self.repo.rename(selected)
        self.repo = selected
        before = self.fingerprint()
        for options in (("--no-color",), ("--no-color", "--json")):
            result = self.command("hooks", "install", "--repo", str(selected), "--dry-run", *options)
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertNotIn("\x1b", result.stdout + result.stderr)
            self.assertNotIn("PRIVATE-CREDENTIAL", result.stdout + result.stderr)
            if "--json" in options:
                self.assertEqual(json.loads(result.stdout)["reason"], "installation_path_invalid")
            else:
                self.assertEqual(result.stdout, "")
                self.assertIn("installation_path_invalid", result.stderr)
        self.assertEqual(before, self.fingerprint())

    def test_private_budget_through_verified_system_temp_alias(self):
        directory = tempfile.TemporaryDirectory(prefix="preview budget ", dir="/private/tmp" if sys.platform == "darwin" else None)
        self.addCleanup(directory.cleanup)
        physical = Path(directory.name).resolve() / "budget.json"
        physical.write_text(json.dumps({"schema_version": 1,
            "checkpoint": {"max_objects": 4096, "max_candidate_bytes": 67108864, "max_seconds": 30,
                "max_capture_bytes": 134217728, "max_temp_bytes": 268435456},
            "publication": {"max_objects": 20000, "max_candidate_bytes": 268435456, "max_seconds": 120,
                "max_capture_bytes": 536870912, "max_temp_bytes": 805306368}}))
        physical.chmod(0o600)
        alias = Path("/tmp") / physical.relative_to("/private/tmp") if sys.platform == "darwin" else physical
        before = self.fingerprint()
        physical_identity = (physical.stat().st_mode, physical.stat().st_ino, physical.read_bytes())
        direct = self.preview("--budget-file", str(physical))["snapshot"]
        alternate = self.preview("--budget-file", str(alias))["snapshot"]
        self.assertEqual(direct["locations"]["budget_file"], alternate["locations"]["budget_file"])
        self.assertEqual(direct["budget"], alternate["budget"])
        self.assertEqual((physical.stat().st_mode, physical.stat().st_ino, physical.read_bytes()), physical_identity)
        self.assertEqual(before, self.fingerprint())

    def test_malformed_repository_metadata_has_actionable_safe_error(self):
        head = self.repo / ".git/HEAD"
        original_head = head.read_bytes()
        cases = ((head, b""), (head, b"PRIVATE-CREDENTIAL\0"))
        for path, raw in cases:
            path.write_bytes(raw)
            before = self.fingerprint()
            result = self.command("hooks", "install", "--repo", str(self.repo), "--dry-run", "--json")
            self.assertEqual(result.returncode, 2, result.stdout)
            value = json.loads(result.stdout)
            self.assertEqual(value["reason"], "installation_metadata_unsafe")
            self.assertEqual(value["phase"], "discovery")
            self.assertIn("metadata", value["recovery"])
            self.assertNotIn("PRIVATE-CREDENTIAL", result.stdout + result.stderr)
            self.assertEqual(before, self.fingerprint())
        head.write_bytes(original_head)
        metadata = self.root / "metadata"
        (self.repo / ".git").rename(metadata)
        (self.repo / ".git").write_bytes(b"PRIVATE-CREDENTIAL\n")
        before = self.fingerprint()
        result = self.command("hooks", "install", "--repo", str(self.repo), "--dry-run", "--json")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertEqual(json.loads(result.stdout)["reason"], "installation_metadata_unsafe")
        self.assertNotIn("PRIVATE-CREDENTIAL", result.stdout + result.stderr)
        self.assertEqual(before, self.fingerprint())

    def test_ambient_git_is_pinned_or_refused_without_side_effects(self):
        before = self.fingerprint()
        env = dict(self.env, PATH="/usr/bin:/bin")
        result = self.command("hooks", "install", "--repo", str(self.repo), "--dry-run", "--json", env=env, git=None)
        if sys.platform == "darwin":
            self.assertEqual(result.returncode, 3, result.stdout[:200])
            self.assertEqual(json.loads(result.stdout)["reason"], "installation_git_selection_required")
            self.assertIn("--git", json.loads(result.stdout)["recovery"])
        else:
            self.assertEqual(result.returncode, 0, result.stdout[:200])
            self.assertEqual(json.loads(result.stdout)["snapshot"]["git_selection"], "trusted_path")
        self.assertEqual(before, self.fingerprint())

    def test_alias_to_launcher_is_refused_after_resolution(self):
        alias = self.home / "git alias"
        target = Path("/usr/bin/git") if sys.platform == "darwin" else Path(GIT)
        alias.symlink_to(target)
        before = self.fingerprint()
        result = self.command("hooks", "install", "--repo", str(self.repo), "--dry-run", "--json", git=str(alias))
        if sys.platform == "darwin":
            self.assertEqual(result.returncode, 3, result.stdout[:200])
            self.assertEqual(json.loads(result.stdout)["reason"], "installation_git_selection_required")
        else:
            self.assertEqual(result.returncode, 0, result.stdout[:200])
            self.assertEqual(json.loads(result.stdout)["snapshot"]["git"], str(target.resolve()))
        self.assertEqual(before, self.fingerprint())

    def test_source_free_real_installed_preview_keeps_repository_and_home_unchanged(self):
        source = self.root / "disposable source"
        shutil.copytree(SOURCE / "hooks", source / "hooks", ignore=shutil.ignore_patterns("__pycache__"))
        (source / "scripts").mkdir()
        for name in ("scan-secrets.py", "scan_install_windows.py"):
            shutil.copy2(SOURCE / "scripts" / name, source / "scripts" / name)
        destination = self.home / "private runtime"
        installed = subprocess.run([PYTHON, "-I", "-S", "-B", str(SOURCE / "scripts/install-scan-secrets.py"),
            "install", "--source-dir", str(source), "--destination", str(destination), "--json"],
            env=self.env, capture_output=True, text=True, timeout=15)
        self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
        self.assertEqual(len(json.loads((destination / "installation.json").read_text())["files"]), 23)
        shutil.rmtree(source)
        before = self.fingerprint()
        for action in ("install", "uninstall"):
            result = subprocess.run([str(destination / "scan-secrets"), "hooks", action, "--repo", str(self.repo),
                "--dry-run", "--no-input", "--git", GIT, "--json"], env=self.env, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            value = json.loads(result.stdout)
            self.assertEqual(value["snapshot"]["locations"]["entrypoint"], str(destination / "scripts/scan-secrets.py"))
            self.assertFalse(value["changes_applied"])
            self.assertEqual(result.stderr, "")
        self.assertEqual(before, self.fingerprint())

    def test_file_limit_names_measurement_without_disclosing_bytes(self):
        hook = self.repo / ".git/hooks/post-merge"
        hook.write_bytes(b"PRIVATE-CREDENTIAL" + b"x" * 65536)
        before = self.fingerprint()
        result = self.command("hooks", "install", "--repo", str(self.repo), "--dry-run", "--json")
        self.assertEqual(result.returncode, 2, result.stdout[:200])
        value = json.loads(result.stdout)
        self.assertEqual(value["reason"], "installation_git_output_limit")
        self.assertEqual(value["measured"], hook.stat().st_size)
        self.assertEqual(value["limit"], 65536)
        self.assertEqual(value["unit"], "bytes")
        self.assertNotIn("PRIVATE-CREDENTIAL", result.stdout + result.stderr)
        self.assertEqual(before, self.fingerprint())

    def test_stalled_metadata_is_bounded_and_cleans_private_capture(self):
        pipe = self.home / "stalled config"
        os.mkfifo(pipe)
        self.git("config", "include.path", str(pipe))
        before = self.fingerprint()
        started = time.monotonic()
        result = self.command("hooks", "install", "--repo", str(self.repo), "--dry-run", "--json")
        self.assertLess(time.monotonic() - started, 5)
        self.assertEqual(result.returncode, 2, result.stdout[:200])
        self.assertIn(json.loads(result.stdout)["reason"], {"installation_git_timeout", "installation_scan_timeout"})
        self.assertEqual(list(self.captures.iterdir()), [])
        self.assertEqual(before, self.fingerprint())

    def test_cancellation_cleans_capture_and_remains_read_only(self):
        pipe = self.home / "stalled config"
        os.mkfifo(pipe)
        self.git("config", "include.path", str(pipe))
        before = self.fingerprint()
        process = subprocess.Popen([PYTHON, "-I", "-S", "-B", str(SOURCE / "scripts/scan-secrets.py"),
            "hooks", "install", "--repo", str(self.repo), "--dry-run", "--git", GIT, "--json"], cwd=self.root, env=self.env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        writer = None
        try:
            deadline = time.monotonic() + 3
            while writer is None and process.poll() is None and time.monotonic() < deadline:
                try:
                    writer = os.open(pipe, os.O_WRONLY | os.O_NONBLOCK)
                except OSError as error:
                    if error.errno != errno.ENXIO:
                        raise
                    time.sleep(0.005)
            self.assertIsNotNone(writer, "Git must be reading fixture configuration before cancellation")
            process.send_signal(signal.SIGINT)
            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 130, stdout + stderr)
            self.assertEqual(json.loads(stdout)["reason"], "cancelled")
            self.assertEqual(stderr, b"")
            self.assertEqual(list(self.captures.iterdir()), [])
            self.assertEqual(before, self.fingerprint())
        finally:
            if writer is not None:
                os.close(writer)
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)

    def test_ordinary_and_enabled_linked_worktrees_report_scope_honestly(self):
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
            "commit", "--allow-empty", "-q", "-m", "initial")
        linked = self.root / "linked worktree"
        self.git("worktree", "add", "-q", "-b", "linked", str(linked))
        original = self.repo
        self.repo = linked
        before = self.fingerprint()
        ordinary = self.preview()["snapshot"]
        self.assertTrue(ordinary["repository"]["linked"])
        self.assertFalse(ordinary["repository"]["worktree_config_enabled"])
        self.assertEqual(ordinary["repository"]["proposed_scope"], "shared_config_requires_scope_decision")
        self.assertEqual(set(ordinary["repository"]["worktrees"]), {str(original), str(linked)})
        self.assertEqual(ordinary["hooks_path"]["effective"], str(original / ".git/hooks"))
        self.assertEqual(before, self.fingerprint())
        self.git("config", "extensions.worktreeConfig", "true")
        self.git("config", "--worktree", "core.hooksPath", "per-worktree hooks")
        before = self.fingerprint()
        enabled = self.preview()["snapshot"]
        self.assertTrue(enabled["repository"]["worktree_config_enabled"])
        self.assertEqual(enabled["repository"]["proposed_scope"], "selected_worktree")
        self.assertEqual(enabled["hooks_path"]["entries"][-1]["scope"], "worktree")
        self.assertEqual(before, self.fingerprint())

    def test_unknown_arguments_never_mutate(self):
        before = self.fingerprint()
        for action in ("install", "uninstall"):
            for options, reason in ((["--dry-run", "--unknown=PRIVATE-CREDENTIAL"], "invalid_arguments"),
                    (["--dry-r"], "invalid_arguments")):
                result = self.command("hooks", action, "--repo", str(self.repo), "--json", *options)
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                value = json.loads(result.stdout)
                self.assertEqual(value["schema"], "scan_secrets_repo_install_v1")
                self.assertEqual(value["reason"], reason)
                self.assertFalse(value["activated"])
                self.assertFalse(value["changes_applied"])
                self.assertNotIn("PRIVATE-CREDENTIAL", result.stdout + result.stderr)
                self.assertEqual(result.stderr, "")
        self.assertEqual(before, self.fingerprint())

    def test_help_version_noargs_common_options_and_thin_helper(self):
        before = self.fingerprint()
        for arguments in ((), ("--help",), ("--version",), ("help", "hooks"), ("hooks",),
                ("hooks", "install", "--help"), ("hooks", "uninstall", "--help")):
            result = self.command(*arguments, env=dict(self.env, PATH=""))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "")
        for action in ("install", "uninstall"):
            result = self.command("hooks", action, "--repo", str(self.repo), "--dry-run", "--quiet", "--no-input", "--no-color")
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))
            self.preview("--quiet", "--no-color", "--no-input", action=action)
            helper = self.command(action, "--repo", str(self.repo), "--dry-run", "--json", entry=SOURCE / "scripts/install-repo-gates.py")
            self.assertEqual(helper.returncode, 0, helper.stderr)
            self.assertEqual(json.loads(helper.stdout)["action"], action)
        self.assertEqual(before, self.fingerprint())

    def test_open_stdin_is_never_read(self):
        process = subprocess.Popen([PYTHON, "-I", "-S", "-B", str(SOURCE / "scripts/scan-secrets.py"),
            "hooks", "install", "--repo", str(self.repo), "--dry-run", "--no-input", "--git", GIT, "--json"],
            cwd=self.root, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            self.assertEqual(process.wait(timeout=5), 0)
            self.assertEqual(json.loads(process.stdout.read())["outcome"], "preview")
            self.assertEqual(process.stderr.read(), b"")
        finally:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)

    def test_missing_repository_is_invalid_and_safe(self):
        result = self.command("hooks", "install", "--repo", str(self.root / "PRIVATE-CREDENTIAL"), "--dry-run", "--json")
        self.assertEqual(result.returncode, 3, result.stdout)
        self.assertEqual(json.loads(result.stdout)["reason"], "not_repository")
        self.assertNotIn("PRIVATE-CREDENTIAL", result.stdout + result.stderr)

    def test_duplicate_empty_and_url_hook_settings_are_refused(self):
        config = self.repo / ".git/config"
        base = config.read_text()
        for settings, reason in ((" hooksPath = first\n hooksPath = second\n", "installation_hooks_path_ambiguous"),
                (" hooksPath =\n", "installation_path_invalid"),
                (" hooksPath = https://PRIVATE-CREDENTIAL@example.invalid/hooks\n", "installation_path_unsupported")):
            config.write_text(base + "\n[core]\n" + settings)
            before = self.fingerprint()
            result = self.command("hooks", "install", "--repo", str(self.repo), "--dry-run", "--json")
            self.assertEqual(result.returncode, 3, result.stdout)
            self.assertEqual(json.loads(result.stdout)["reason"], reason)
            self.assertNotIn("PRIVATE-CREDENTIAL", result.stdout + result.stderr)
            self.assertEqual(before, self.fingerprint())

    def test_redirects_and_execution_settings_never_run_helpers(self):
        marker = self.root / "HELPER-RAN"
        helper = self.repo / "helper"
        helper.write_text("#!/bin/sh\ntouch '" + str(marker) + "'\n")
        helper.chmod(0o755)
        self.git("config", "core.fsmonitor", str(helper))
        self.git("config", "credential.helper", "!" + str(helper))
        self.git("config", "core.sshCommand", str(helper))
        self.git("config", "remote.origin.url", "https://PRIVATE-CREDENTIAL@example.invalid/repo")
        env = dict(self.env, GIT_DIR=str(self.root / "nonexistent"), GIT_WORK_TREE=str(self.home),
            GIT_INDEX_FILE=str(self.root / "nonexistent-index"), GIT_CONFIG_COUNT="1",
            GIT_CONFIG_KEY_0="core.hooksPath", GIT_CONFIG_VALUE_0="PRIVATE-CREDENTIAL", GIT_CONFIG_PARAMETERS="'core.hooksPath'='PRIVATE-CREDENTIAL'")
        before = self.fingerprint()
        value = self.preview(env=env)
        self.assertEqual(value["snapshot"]["hooks_path"]["source"], "default")
        self.assertNotIn("PRIVATE-CREDENTIAL", json.dumps(value))
        self.assertFalse(marker.exists())
        self.assertEqual(before, self.fingerprint())

    def test_linked_hooks_and_config_sources_are_refused_without_touching_targets(self):
        external = self.home / "external"
        external.write_text("PRIVATE-CREDENTIAL")
        for path in (self.repo / ".git/hooks/pre-commit", self.home / ".gitconfig"):
            path.symlink_to(external)
            before = self.fingerprint()
            result = self.command("hooks", "install", "--repo", str(self.repo), "--dry-run", "--json")
            self.assertEqual(result.returncode, 2, result.stdout[:200])
            self.assertNotIn("PRIVATE-CREDENTIAL", result.stdout + result.stderr)
            self.assertEqual(before, self.fingerprint())
            path.unlink()

    def test_unsupported_real_interpreter_is_rejected_before_discovery(self):
        selected = os.environ.get("TEST_UNSUPPORTED_PYTHON")
        if selected is None:
            selected = ("/Library/Developer/CommandLineTools/usr/bin/python3" if sys.platform == "darwin"
                        else shutil.which("python3.11") or shutil.which("python3.10"))
        self.assertIsNotNone(selected, "Set TEST_UNSUPPORTED_PYTHON to a real Python before 3.12; this negative fixture is required")
        old = Path(selected)
        self.assertTrue(old.is_file(), "TEST_UNSUPPORTED_PYTHON must select an existing unsupported interpreter")
        version = subprocess.run([str(old), "-I", "-S", "-B", "-c", "import sys; print(sys.version_info < (3, 12))"], capture_output=True, text=True, timeout=5)
        self.assertEqual(version.stdout.strip(), "True", "Fixture requires a real unsupported Python before 3.12")
        before = self.fingerprint()
        result = subprocess.run([str(old), "-I", "-S", "-B", str(SOURCE / "scripts/scan-secrets.py"),
            "hooks", "install", "--repo", str(self.repo), "--dry-run", "--json"], env=self.env,
            capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "installation_interpreter_unsupported")
        self.assertEqual(before, self.fingerprint())

    def test_repository_git_path_shim_is_refused_without_execution(self):
        binary = self.repo / "bin"
        binary.mkdir()
        marker = self.root / "GIT-SHIM-RAN"
        shim = binary / "git"
        shim.write_text("#!/bin/sh\ntouch '" + str(marker) + "'\nexit 0\n")
        shim.chmod(0o755)
        env = dict(self.env, PATH=str(binary) + os.pathsep + self.env.get("PATH", os.defpath))
        before = self.fingerprint()
        result = self.command("hooks", "install", "--repo", str(self.repo), "--dry-run", "--json", env=env, git=None)
        self.assertEqual(result.returncode, 3, result.stdout[:200])
        self.assertEqual(json.loads(result.stdout)["reason"], "installation_git_location_unsafe")
        self.assertFalse(marker.exists())
        self.assertEqual(before, self.fingerprint())

    def test_redirected_git_metadata_parent_is_refused(self):
        metadata = self.root / "metadata"
        (self.repo / ".git").rename(metadata)
        alias = self.root / "linked metadata"
        alias.symlink_to(metadata, target_is_directory=True)
        (self.repo / ".git").write_text("gitdir: " + str(alias) + "\n")
        before = self.fingerprint()
        result = self.command("hooks", "install", "--repo", str(self.repo), "--dry-run", "--json")
        self.assertEqual(result.returncode, 2, result.stdout[:200])
        self.assertEqual(json.loads(result.stdout)["reason"], "installation_metadata_unsafe")
        self.assertEqual(before, self.fingerprint())

    def test_configuration_precedence_includes_and_relative_hook_cwd(self):
        global_hooks = self.home / "shared hooks"
        global_hooks.mkdir()
        (self.home / ".gitconfig").write_text('[core]\n hooksPath = "' + str(global_hooks) + '"\n')
        included = self.home / "conditional include"
        included.write_text('[core]\n hooksPath = "relative hooks"\n')
        self.git("config", "--local", "includeIf.gitdir:" + str(self.repo / ".git") + ".path", str(included))
        for directory, name, mode in ((self.repo / "relative hooks", "post-checkout", 0o755),
                (self.repo / ".git/relative hooks", "pre-receive", 0o644)):
            directory.mkdir()
            (directory / name).write_text("#!/bin/sh\nexit 99\n")
            (directory / name).chmod(mode)
        before = self.fingerprint()
        snapshot = self.preview()["snapshot"]
        entries = snapshot["hooks_path"]["entries"]
        self.assertEqual([item["scope"] for item in entries], ["global", "local"])
        self.assertEqual([item["origin"] for item in entries], [str(self.home / ".gitconfig"), str(included)])
        self.assertEqual(snapshot["hooks_path"]["effective"], "relative hooks")
        originals = {item["name"]: item for item in snapshot["hooks"]}
        self.assertEqual(originals["post-checkout"]["path"], str(self.repo / "relative hooks/post-checkout"))
        self.assertTrue(originals["post-checkout"]["executable"])
        self.assertEqual(originals["pre-receive"]["path"], str(self.repo / ".git/relative hooks/pre-receive"))
        self.assertFalse(originals["pre-receive"]["executable"])
        self.assertEqual(before, self.fingerprint())

    def test_owner_selected_global_config_matches_real_git_origins(self):
        selected = self.home / "selected global config"
        hooks = self.home / "selected hooks"
        hooks.mkdir()
        selected.write_text('[core]\n hooksPath = "' + str(hooks) + '"\n')
        self.env["GIT_CONFIG_GLOBAL"] = str(selected)
        expected = self.git("config", "--includes", "--null", "--show-origin", "--show-scope", "--get-all", "core.hooksPath").split(b"\0")
        before = self.fingerprint()
        entry = self.preview()["snapshot"]["hooks_path"]["entries"][-1]
        self.assertEqual([entry["scope"].encode(), ("file:" + entry["origin"]).encode(), entry["value"].encode()], expected[:-1])
        self.assertEqual(before, self.fingerprint())

    def test_malformed_and_unknown_ownership_have_safe_exact_state(self):
        owner = self.repo / ".git/scan-secrets/repository-installation.json"
        owner.parent.mkdir()
        for raw, reason in ((b'{"secret":"PRIVATE-CREDENTIAL",', "installation_ownership_invalid"),
                (b'{"schema":"unknown","secret":"PRIVATE-CREDENTIAL"}', "installation_ownership_unsupported")):
            owner.write_bytes(raw)
            owner.chmod(0o600)
            before = self.fingerprint()
            result = self.command("hooks", "uninstall", "--repo", str(self.repo), "--dry-run", "--json")
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            value = json.loads(result.stdout)
            self.assertEqual(value["reason"], reason)
            self.assertEqual(value["ownership"]["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertNotIn("PRIVATE-CREDENTIAL", result.stdout + result.stderr)
            self.assertEqual(before, self.fingerprint())

    def test_budget_requires_private_file_and_trusted_ancestry(self):
        budget = self.home / "budget.json"
        budget.write_text(json.dumps({"schema_version": 1,
            "checkpoint": {"max_objects": 4096, "max_candidate_bytes": 67108864, "max_seconds": 30,
                "max_capture_bytes": 134217728, "max_temp_bytes": 268435456},
            "publication": {"max_objects": 20000, "max_candidate_bytes": 268435456, "max_seconds": 120,
                "max_capture_bytes": 536870912, "max_temp_bytes": 805306368}}))
        budget.chmod(0o644)
        before = self.fingerprint()
        result = self.command("hooks", "install", "--repo", str(self.repo), "--budget-file", str(budget), "--dry-run", "--json")
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "installation_budget_untrusted")
        self.assertEqual(before, self.fingerprint())
        budget.chmod(0o600)
        value = self.preview("--budget-file", str(budget))
        self.assertEqual(value["snapshot"]["locations"]["budget_file"], str(budget))
        self.assertEqual(value["snapshot"]["budget"]["identity"], hashlib.sha256(budget.read_bytes()).hexdigest())
        self.home.chmod(0o777)
        before = self.fingerprint()
        result = self.command("hooks", "install", "--repo", str(self.repo), "--budget-file", str(budget), "--dry-run", "--json")
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "installation_location_untrusted")
        self.assertEqual(before, self.fingerprint())

    def test_default_preview_is_useful_and_preserves_every_byte_and_mode(self):
        marker = self.root / "HOOK-RAN"
        hook = self.repo / ".git/hooks/post-checkout"
        hook.write_text("#!/bin/sh\ntouch '" + str(marker) + "'\n")
        hook.chmod(0o755)
        before = self.fingerprint()
        value = self.preview()
        snapshot = value["snapshot"]
        self.assertEqual(snapshot["repository"]["root"], str(self.repo))
        self.assertEqual(snapshot["hooks_path"]["source"], "default")
        original = next(item for item in snapshot["hooks"] if item["name"] == "post-checkout")
        self.assertTrue(original["executable"])
        self.assertEqual(original["sha256"], hashlib.sha256(hook.read_bytes()).hexdigest())
        self.assertTrue(snapshot["interpreter"]["sqlite_setconfig"])
        self.assertEqual(snapshot["ownership"]["state"], "absent")
        self.assertIn("pre-receive", [item["name"] for item in snapshot["hooks"]])
        self.assertTrue(value["proposed_operations"])
        self.assertEqual(before, self.fingerprint())
        self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
