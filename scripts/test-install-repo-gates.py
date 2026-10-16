#!/usr/bin/env python3
"""Read-only repository gate preview through the public CLI."""
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
        self.assertEqual(len(json.loads((destination / "installation.json").read_text())["files"]), 20)
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

    def test_unknown_arguments_and_non_dry_run_never_mutate(self):
        before = self.fingerprint()
        for action in ("install", "uninstall"):
            for options, reason in (([], "installation_activation_unavailable"),
                    (["--dry-run", "--unknown=PRIVATE-CREDENTIAL"], "invalid_arguments"),
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
