#!/usr/bin/env python3
"""Public disposable software and repository setup processes; no native certification."""
from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import shutil
import signal
import shlex
import subprocess
import sys
import tempfile
import time
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts/install-agent-brain.py"


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agent-brain-setup-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.home = self.base / "home café's space"
        self.repo = self.base / "repo café's space"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.env = dict(os.environ, HOME=str(self.home), PYTHONDONTWRITEBYTECODE="1")

    def run_json(self, argv, expected=0):
        result = subprocess.run([str(value) for value in argv], cwd=self.repo, env=self.env,
            text=True, input="", capture_output=True, timeout=10)
        self.assertEqual(result.returncode, expected, (result.stdout, result.stderr))
        return json.loads(result.stdout)

    def install(self, *extra, expected=0):
        return self.run_json([sys.executable, INSTALL, "--source", ROOT / "skills/agent-brain",
            "--software-dir", self.home / ".local/share/agent-brain", "--bin-dir", self.home / ".local/bin",
            "--python", sys.executable, "--json", *extra], expected)

    def cli(self, *args, expected=0):
        return self.run_json([self.launcher, *args, "--json"], expected)

    def stage_input(self, operation, ready, value, expected=0):
        path = self.base / "foreground-proposal.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return self.cli("learn", operation, "--invocation-file", ready["invocation_file"], "--input", path, expected=expected)

    def save_plan(self, plan):
        path = self.base / "reviewed-plan.json"
        path.write_text(json.dumps(plan), encoding="utf-8")
        return path

    def native_fixture(self, provider="codex", mode="cli", integration=None):
        installed = self.install()
        self.launcher = Path(installed["launcher"])
        self.bundle = Path(installed["bundle_path"])
        config_path = self.repo / ".agents/context/config.json"
        if not config_path.exists():
            first = self.cli("setup")
            self.cli("setup", "--apply", "--plan", self.save_plan(first))
        config = json.loads(config_path.read_text())
        name = integration or provider + "-" + mode
        cert = str(uuid.uuid4())
        events = ["startup", "task", "scope", "checkpoint", "resume", "context_lost", "recover", "pause", "cancel", "child_start", "child_stop"]
        config["providers"][name] = {"enabled": True, "kind": "native", "core_version": "0.1.0", "adapter_version": "native-1",
            "schema_version": 1, "certification_id": cert, "support_record": ".agents/context/" + name + "-support.json",
            "events": events, "max_attempts": 3}
        config_path.write_text(json.dumps(config))
        permissions = self.repo / (name + "-permissions.json")
        permissions.write_text('{"mode":"offline"}')
        lifecycle = self.repo / (name + "-lifecycle.json")
        lifecycle.write_text('{"hooks":"offline fixture observed configuration"}')
        sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        files = [(p.relative_to(self.bundle).as_posix(), sha(p)) for p in sorted((self.bundle / "scripts").rglob("*.py"))]
        native_events = {"codex": ["SessionStart", "UserPromptSubmit", "PreToolUse", "Stop"],
            "copilot": ["sessionStart", "userPromptTransformed", "preToolUse", "agentStop"],
            "gemini": ["SessionStart", "BeforeAgent", "BeforeTool", "AfterAgent"]}[provider]
        support = {"schema_version": 1, "kind": "native", "status": "offline_fixture", "repository_id": config["repository_id"],
            "repository_root": str(self.repo), "worktree_root": str(self.repo), "platform": sys.platform,
            "filesystem_id": str(self.repo.stat().st_dev), "events": events, "core_version": "0.1.0", "adapter_version": "native-1",
            "certification_id": cert, "provider": provider, "provider_version": "offline-build-1", "entry_mode": mode,
            "native_events": native_events, "adapter_path": str(self.bundle / "assets/adapters" / (provider + ".py")),
            "adapter_revision": sha(self.bundle / "assets/adapters" / (provider + ".py")), "bundle_path": str(self.bundle),
            "bundle_revision": hashlib.sha256(json.dumps(files, separators=(",", ":")).encode()).hexdigest(),
            "permissions": {"path": permissions.name, "revision": sha(permissions)},
            "lifecycle_config": {"path": lifecycle.name, "revision": sha(lifecycle)}, "native_deadline_seconds": 5,
            "immediate_model_boundary": True, "child_delivery": False, "evidence": "offline_translation_only", "scope": {}}
        (self.repo / config["providers"][name]["support_record"]).write_text(json.dumps(support))
        return name

    def native_hook(self, provider, event, **extra):
        path = self.repo / {"codex": ".codex/hooks.json", "copilot": ".github/hooks/agent-brain.json", "gemini": ".gemini/settings.json"}[provider]
        item = json.loads(path.read_text())["hooks"][event][-1]
        command = item["bash"] if provider == "copilot" else item["hooks"][0]["command"]
        payload = {"cwd": str(self.repo), "sessionId" if provider == "copilot" else "session_id": "offline-conversation"}
        payload.update(extra)
        argv = ["pwsh", "-NoProfile", "-Command", command] if command.startswith("& ") else command
        result = subprocess.run(argv, shell=isinstance(argv, str), cwd=self.repo, env=self.env,
            input=json.dumps(payload), text=True, capture_output=True, timeout=8)
        self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))
        return json.loads(result.stdout)

    def test_matching_native_apply_unrelated_hooks_and_deleted_entire_runtime(self):
        self.native_fixture()
        hooks = self.repo / ".codex/hooks.json"
        hooks.parent.mkdir(exist_ok=True)
        unrelated = {"hooks": [{"type": "command", "command": "echo unrelated"}]}
        hooks.write_text(json.dumps({"trust": "user-controlled", "hooks": {"Stop": [unrelated]}}))
        plan = self.cli("setup")
        self.assertEqual(plan["activation"], "active")
        applied = self.cli("setup", "--apply", "--plan", self.save_plan(plan))
        actual = json.loads(hooks.read_text())
        self.assertEqual(actual["trust"], "user-controlled")
        self.assertEqual(actual["hooks"]["Stop"][0], unrelated)
        started = self.native_hook("codex", "SessionStart", source="startup")
        self.assertIn("No learned knowledge has been recorded.", json.dumps(started))
        status = self.cli("status")
        self.assertEqual(status["activation_status"], "active")
        self.assertEqual(status["state_status"], "available")
        identity = (self.repo / ".agents/context/expected-runtime.json").read_bytes()
        shutil.rmtree(self.repo / ".agents/context/state")
        missing = self.cli("status")
        self.assertEqual(missing["activation_status"], "incomplete")
        self.assertEqual(missing["state_status"], "unavailable")
        denied = self.native_hook("codex", "SessionStart", source="startup")
        self.assertIn("STATE_UNAVAILABLE", json.dumps(denied))
        self.assertFalse((self.repo / ".agents/context/state").exists())
        self.assertEqual((self.repo / ".agents/context/expected-runtime.json").read_bytes(), identity)
        repeated = self.cli("setup", "--apply", "--plan", self.save_plan(plan), expected=1)
        self.assertEqual(repeated["error"]["code"], "STATE_UNAVAILABLE")
        self.assertFalse((self.repo / ".agents/context/state").exists())
        disabled = self.cli("setup", "--deactivate")
        self.cli("setup", "--apply", "--plan", self.save_plan(disabled))
        self.assertFalse((self.repo / ".agents/context/state").exists())
        self.assertEqual((self.repo / ".agents/context/expected-runtime.json").read_bytes(), identity)

    def test_incomplete_and_incompatible_shipping_sources_fail_before_effects(self):
        source = self.base / "shipping-source"
        source.mkdir()
        for kind in ("empty", "partial", "core", "adapter", "schema"):
            if kind != "empty":
                shutil.rmtree(source)
                shutil.copytree(ROOT / "skills/agent-brain", source, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            if kind == "partial":
                (source / "scripts/agent-brain.py").unlink()
            elif kind in ("core", "schema"):
                path = source / "schemas/version.json"
                value = json.loads(path.read_text())
                value["bundle_version" if kind == "core" else "schema_version"] = "999.0.0" if kind == "core" else 999
                path.write_text(json.dumps(value))
            elif kind == "adapter":
                path = source / "scripts/agent_brain/software.py"
                path.write_text(path.read_text().replace('ADAPTER_VERSION = "native-1"', 'ADAPTER_VERSION = "native-999"'))
            result = self.install("--source", source, expected=2)
            self.assertEqual(result["error"]["code"], "SOFTWARE_UNAVAILABLE", kind)
            self.assertFalse((self.home / ".local/share/agent-brain").exists(), kind)
            self.assertFalse((self.home / ".local/bin").exists(), kind)

    def test_packaged_shipping_source_installs_without_authoring_evals(self):
        source = self.base / "packaged-shipping-source"
        shutil.copytree(ROOT / "skills/agent-brain", source, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "evals"))
        installed = self.install("--source", source)
        self.assertTrue((Path(installed["bundle_path"]) / "scripts/agent-brain.py").is_file())
        self.assertFalse((Path(installed["bundle_path"]) / "evals").exists())
        result = subprocess.run([installed["launcher"], "--help"], cwd=self.repo, env=self.env,
            text=True, capture_output=True, timeout=3)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_equals_config_selects_its_exact_pin_before_importing_another_bundle(self):
        installed = self.install()
        self.launcher = Path(installed["launcher"])
        first = self.cli("setup")
        self.cli("setup", "--apply", "--plan", self.save_plan(first))
        source = self.base / "new-shipping-source"
        shutil.copytree(ROOT / "skills/agent-brain", source, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        with (source / "SKILL.md").open("a", encoding="utf-8") as stream:
            stream.write("\n<!-- Exact custom configuration pin fixture. -->\n")
        updated = self.install("--source", source)
        custom = json.loads((self.repo / ".agents/context/config.json").read_text())
        manifest_path = Path(updated["bundle_path"]) / "software.json"
        manifest = json.loads(manifest_path.read_text())
        custom["software"] = {key: manifest[key] for key in ("bundle_path", "core_version", "adapter_version", "schema_version")}
        custom["software"]["manifest_revision"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        (self.repo / "custom-config.json").write_text(json.dumps(custom))
        old = Path(installed["bundle_path"]) / "scripts/agent_brain/cli.py"
        old.chmod(0o600)
        with old.open("a", encoding="utf-8") as stream:
            stream.write("\nfrom pathlib import Path\nPath('unpinned-code-ran').write_text('invalid')\n")
        status = self.cli("status", "--config=custom-config.json")
        self.assertEqual(status["software_status"], "available")
        self.assertFalse((self.repo / "unpinned-code-ran").exists())

    def test_malformed_config_and_unavailable_state_destination_have_no_effects(self):
        self.native_fixture()
        path = self.repo / ".agents/context/config.json"
        original = path.read_bytes()
        path.write_text('{"schema_version":1,"schema_version":1}')
        self.cli("setup", expected=2)
        self.assertEqual(path.read_text(), '{"schema_version":1,"schema_version":1}')
        path.write_bytes(original)
        state = self.repo / ".agents/context/state"
        state.write_text("Existing unrelated ordinary file.\n")
        plan = self.cli("setup")
        self.assertIn({"name": "state destination", "status": "unsupported"}, plan["prerequisites"])
        failure = self.cli("setup", "--apply", "--plan", self.save_plan(plan), expected=2)
        self.assertEqual(failure["error"]["code"], "SETUP_UNSUPPORTED")
        self.assertEqual(state.read_text(), "Existing unrelated ordinary file.\n")
        self.assertEqual(path.read_bytes(), original)
        self.assertFalse((self.repo / ".codex/hooks.json").exists())

    def activate(self):
        plan = self.cli("setup")
        return self.cli("setup", "--apply", "--plan", self.save_plan(plan))

    def test_installed_launcher_foreground_is_admitted_and_preserves_pending_work(self):
        self.native_fixture()
        self.activate()
        self.native_hook("codex", "SessionStart", source="startup")
        stopped = self.native_hook("codex", "Stop")
        line = next(line for line in stopped["reason"].splitlines() if "--native-foreground" in line)
        admitted = self.native_hook("codex", "PreToolUse", tool_input={"command": line})
        self.assertNotIn("deny", json.dumps(admitted))
        result = subprocess.run(line + " --classification ready_to_complete", shell=True, cwd=self.repo,
            env=self.env, capture_output=True, text=True, timeout=8)
        self.assertEqual(result.returncode, 0, result.stderr)
        ready = json.loads(result.stdout)
        self.assertEqual(ready["next_action"]["kind"], "learn")
        command = shlex.join([str(self.launcher), "learn", "start", "--invocation-file", ready["invocation_file"],
            "--config", str(self.repo / ".agents/context/config.json"), "--json"])
        self.assertIn(command, ready["next_action"]["procedure"].splitlines())
        self.assertNotIn("deny", json.dumps(self.native_hook("codex", "PreToolUse", tool_input={"command": command})))
        stage = subprocess.run([str(self.launcher), "learn", "start", "--invocation-file", ready["invocation_file"], "--json"],
            cwd=self.repo, env=self.env, capture_output=True, text=True, timeout=5)
        self.assertEqual(stage.returncode, 0, stage.stderr)
        self.assertEqual(json.loads(stage.stdout)["stage_outcome"], "incomplete")

    def custom_config_commands(self, shell):
        self.native_fixture()
        (self.repo / "src").mkdir()
        (self.repo / "src/app.py").write_text("print('offline fixture')\n")
        support_path = self.repo / ".agents/context/codex-cli-support.json"
        support = json.loads(support_path.read_text())
        support["scope"] = {"paths": ["src/app.py"]}
        support_path.write_text(json.dumps(support))
        default = self.repo / ".agents/context/config.json"
        custom = default.with_name("custom café's config.json")
        default.rename(custom)
        plan = self.cli("setup", "--config", custom, "--shell", shell)
        self.cli("setup", "--apply", "--plan", self.save_plan(plan))
        self.native_hook("codex", "SessionStart", source="startup")
        stopped = self.native_hook("codex", "Stop")
        continuation = next(line for line in stopped["reason"].splitlines() if "--native-foreground" in line)
        source = self.base / "new unactivated software"
        shutil.copytree(ROOT / "skills/agent-brain", source, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        with (source / "scripts/agent_brain/cli.py").open("a", encoding="utf-8") as stream:
            stream.write("\nfrom pathlib import Path\nPath('unpinned-code-ran').write_text('wrong bundle imported')\n")
        newer = self.install("--source", source)
        self.assertNotEqual(newer["bundle_path"], str(self.bundle))

        def execute(command):
            argv = ["pwsh", "-NoProfile", "-Command", command] if shell == "powershell" else command
            result = subprocess.run(argv, shell=isinstance(argv, str), cwd=self.repo, env=self.env,
                capture_output=True, text=True, timeout=8)
            self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))
            self.assertFalse((self.repo / "unpinned-code-ran").exists())
            return json.loads(result.stdout)

        ready = execute(continuation + " --classification ready_to_complete")
        self.assertIn("--config", continuation)
        self.assertNotIn("deny", json.dumps(self.native_hook("codex", "PreToolUse", tool_input={"command": continuation})))
        commands = [line for line in ready["next_action"]["procedure"].splitlines()
            if line.startswith("& '") or line.startswith(shlex.quote(str(self.launcher)) + " ")]
        self.assertEqual(len(commands), 4)
        review = self.repo / "REVIEW.json"
        review.write_text(json.dumps(self.tip_input(ready, ".agents/memory/custom-tip.md")), encoding="utf-8")
        for command in commands:
            self.assertIn("--config", command)
            self.assertNotIn("deny", json.dumps(self.native_hook("codex", "PreToolUse", tool_input={"command": command})))
            outcome = execute(command)
        self.assertEqual(outcome["stage_outcome"], "changed")
        self.assertTrue((self.repo / ".agents/memory/custom-tip.md").is_file())
        self.assertEqual(self.cli("status", "--config", custom)["software_status"], "available")
        self.assertFalse(default.exists())

    def test_custom_config_commands_keep_pinned_bundle_before_import(self):
        self.custom_config_commands("posix")

    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell executable is required for this shell process case")
    def test_custom_config_powershell_commands_keep_pinned_bundle_before_import(self):
        self.custom_config_commands("powershell")

    def ready_native(self):
        self.native_hook("codex", "SessionStart", source="startup")
        stopped = self.native_hook("codex", "Stop")
        line = next(line for line in stopped["reason"].splitlines() if "--native-foreground" in line)
        result = subprocess.run(line + " --classification ready_to_complete", shell=True, cwd=self.repo,
            env=self.env, capture_output=True, text=True, timeout=8)
        self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))
        return json.loads(result.stdout)

    def tip_input(self, ready, target):
        identity = str(uuid.uuid4())
        annotation = {"schema_version": 1, "id": identity, "kind": "fact", "status": "established", "applies": {"paths": ["src/app.py"]},
            "evidence": {"sources": [{"source": "foreground task observation"}], "verified_at": "2026-10-06",
                "verification_note": "A small focused change succeeded after the oversized patch was rejected."}}
        content = '# Small patch tip\n<!-- agent-brain ' + json.dumps(annotation) + ' -->\nUse smaller focused patches after an oversized patch is rejected.\n'
        paths = {unit["path"] for unit in ready["delivery"]["units"]}
        if (self.repo / "src/app.py").is_file():
            paths.add("src/app.py")
        review = {"scope": ready["obligations"][0]["scope"],
            "guidance": [{name: unit[name] for name in ("id", "content_revision", "input_revision")} for unit in ready["delivery"]["units"]],
            "sources": [{"path": name, "revision": hashlib.sha256((self.repo / name).read_bytes()).hexdigest(),
                "note": "Read the current controlling guidance."} for name in sorted(paths)], "note": "Retain the observed scoped workaround."}
        prior = (self.repo / target).read_bytes() if (self.repo / target).exists() else None
        return {"schema_version": 1, "outcome": "changed", "review": review,
            "proposal": {"base_input_revision": ready["input_revision"], "rationale": "Retain a scoped observed workaround.",
                "changes": [{"path": target, "base_revision": hashlib.sha256(prior).hexdigest() if prior is not None else None, "content": content}],
                "claims": [{"id": identity, "type": "tip", "action": "add", "scope": ready["obligations"][0]["scope"],
                    "evidence": {"failure": "An oversized patch was rejected.", "workaround": "A small focused patch succeeded.",
                        "verified_at": "2026-10-06", "result": "observed"}}]}}

    def test_protected_file_root_and_writable_knowledge_publish_without_ambiguous_ownership(self):
        (self.repo / "AGENTS.md").write_text("# Policy\nRead this controlling protected document first.\n")
        (self.repo / ".agents/memory").mkdir(parents=True)
        (self.repo / ".agents/memory/INDEX.md").write_text("# Index\nRead this map after AGENTS.md.\n")
        (self.repo / ".agents/instructions").mkdir()
        self.native_fixture()
        (self.repo / "src").mkdir()
        (self.repo / "src/app.py").write_text("print('offline fixture')\n")
        support_path = self.repo / ".agents/context/codex-cli-support.json"
        support = json.loads(support_path.read_text())
        support["scope"] = {"paths": ["src/app.py"]}
        support_path.write_text(json.dumps(support))
        config_path = self.repo / ".agents/context/config.json"
        config = json.loads(config_path.read_text())
        config["maintenance"] = {"enabled": False}
        unit = config["mapped_units"][0]
        unit.pop("unit", None)
        unit.update(selector={"type": "document"}, kind="policy", status="established", applies={"paths": ["src/**"]})
        config_path.write_text(json.dumps(config))
        self.activate()
        ready = self.ready_native()
        self.assertEqual([item["path"] for item in ready["delivery"]["artifacts"]][:2], ["AGENTS.md", ".agents/memory/INDEX.md"])
        original = (self.repo / "AGENTS.md").read_bytes()
        invalid = self.stage_input("prepare", ready, self.tip_input(ready, "AGENTS.md"), expected=2)
        self.assertEqual(invalid["error"]["code"], "WRITABLE_SCOPE_INVALID")
        payload = self.tip_input(ready, ".agents/memory/patch-tip.md")
        self.stage_input("prepare", ready, payload)
        published = self.cli("learn", "publish", "--invocation-file", ready["invocation_file"])
        self.assertIn("publication", published)
        self.assertEqual((self.repo / ".agents/memory/patch-tip.md").read_text(), payload["proposal"]["changes"][0]["content"])
        self.assertEqual((self.repo / "AGENTS.md").read_bytes(), original)
        completed = self.cli("learn", "complete", "--invocation-file", ready["invocation_file"])
        self.assertEqual(completed["stage_outcome"], "changed")
        self.assertIn("Use smaller focused patches", json.dumps(self.cli("recall", "--all-guidance")))

    def test_deactivation_preserves_hooks_added_after_activation_and_pending_history(self):
        self.native_fixture()
        self.activate()
        self.native_hook("codex", "SessionStart", source="startup")
        hooks = self.repo / ".codex/hooks.json"
        document = json.loads(hooks.read_text())
        unrelated = {"hooks": [{"type": "command", "command": "echo later unrelated"}]}
        document["hooks"]["Stop"].append(unrelated)
        hooks.write_text(json.dumps(document))
        before = self.cli("status")
        history = self.repo / ".agents/context/history/portable-note.md"
        history.parent.mkdir(parents=True, exist_ok=True)
        history.write_text("Preserve portable history.\n")
        plan = self.cli("setup", "--deactivate")
        self.assertEqual(plan["activation"], "disabled")
        self.cli("setup", "--apply", "--plan", self.save_plan(plan))
        actual = json.loads(hooks.read_text())
        self.assertEqual(actual["hooks"], {"Stop": [unrelated]})
        self.assertEqual(history.read_text(), "Preserve portable history.\n")
        after = self.cli("status")
        self.assertEqual(after["activation_status"], "disabled")
        self.assertEqual(after["work_sessions"][0]["work_session_id"], before["work_sessions"][0]["work_session_id"])
        self.assertFalse(json.loads((self.repo / ".agents/context/config.json").read_text())["providers"]["codex-cli"]["enabled"])

    def test_stale_plan_and_unknown_pin_fail_before_effects(self):
        self.launcher = Path(self.install()["launcher"])
        plan = self.cli("setup")
        (self.repo / ".gitignore").write_text("unrelated\n")
        error = self.cli("setup", "--apply", "--plan", self.save_plan(plan), expected=2)
        self.assertEqual(error["error"]["code"], "SETUP_STALE")
        self.assertFalse((self.repo / ".agents/context/config.json").exists())
        self.install("--core-version", "9.9.9", expected=2)
        self.install("--adapter-version", "unknown", expected=2)
        self.install("--schema-version", "2", expected=2)

    def private_paths_are_ignored(self, *names):
        checked = subprocess.run(["git", "check-ignore", "-z", "--stdin"], cwd=self.repo,
            input="\0".join(names) + "\0", capture_output=True, text=True, timeout=3)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(set(checked.stdout.rstrip("\0").split("\0")), set(names))
        status = subprocess.check_output(["git", "-c", "core.quotepath=false", "status", "--porcelain", "--untracked-files=all"],
            cwd=self.repo, text=True)
        for name in names:
            self.assertNotIn(name, status)

    def test_private_operational_journals_backups_and_runtime_remain_ignored_after_inverse(self):
        self.native_fixture("gemini")
        settings = self.repo / ".gemini/settings.json"
        settings.parent.mkdir(exist_ok=True)
        canary = "synthetic-private-settings-canary"
        settings.write_text(json.dumps({"GEMINI_API_KEY": canary}))
        root_ignore = "unrelated.log\n!.agents/context/setup-history/**\n"
        (self.repo / ".gitignore").write_text(root_ignore)
        marker = self.repo / ".agents/context/.gitignore"
        unrelated = "unrelated.tmp\n!public.tmp\n"
        marker.write_text(unrelated)
        config_path = self.repo / ".agents/context/config.json"
        config = json.loads(config_path.read_text())
        config["state_dir"] = ".agents/context/runtime [one] café's space"
        config_path.write_text(json.dumps(config))
        first = self.activate()
        journal = self.repo / first["journal_path"]
        self.assertIn(canary, journal.read_text())
        self.assertTrue(marker.read_text().startswith(unrelated))
        second = self.activate()
        backup = json.loads((self.repo / second["journal_path"]).read_text())["backup_path"]
        self.assertTrue((self.repo / backup).is_file())
        private = (first["journal_path"], second["journal_path"], backup,
            config["state_dir"] + "/brain.sqlite3", ".agents/context/activation-local.json",
            ".agents/context/expected-runtime.json", ".agents/context/publication.lock",
            ".agents/context/.agent-brain-private-canary")
        (self.repo / private[-1]).write_text(canary)
        self.private_paths_are_ignored(*private)
        self.cli("setup", "--rollback", self.repo / second["journal_path"])
        self.cli("setup", "--rollback", journal)
        self.assertEqual((self.repo / ".gitignore").read_text(), root_ignore)
        self.assertEqual(json.loads(settings.read_text()), {"GEMINI_API_KEY": canary})
        self.private_paths_are_ignored(*private)
        for name in (".agents/context/config.json", ".agents/context/map.md",
                ".agents/context/history/portable.md", ".agents/context/candidates/portable.md", ".agents/context/public.tmp"):
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text("Portable public artifact.\n")
            checked = subprocess.run(["git", "check-ignore", name], cwd=self.repo, capture_output=True)
            self.assertEqual(checked.returncode, 1, name)

    def test_interrupted_private_intent_is_ignored_before_root_ignore_and_after_rollback(self):
        self.native_fixture("gemini")
        settings = self.repo / ".gemini/settings.json"
        settings.parent.mkdir(exist_ok=True)
        canary = "synthetic-interrupted-private-canary"
        settings.write_text(json.dumps({"GEMINI_API_KEY": canary}))
        (self.repo / ".gitignore").unlink()
        plan = self.cli("setup")
        reviewed = self.save_plan(plan)
        barrier = self.repo / ".agents/context/setup-fixture-barrier.json"
        barrier.write_text(json.dumps({"after": ".agents/context/config.json"}))
        with subprocess.Popen([str(self.launcher), "setup", "--apply", "--plan", str(reviewed), "--json"],
                cwd=self.repo, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            reached = self.repo / ".agents/context/setup-fixture-reached"
            until = time.monotonic() + 5
            while not reached.exists() and time.monotonic() < until:
                time.sleep(0.02)
            self.assertTrue(reached.exists())
            process.send_signal(signal.SIGINT)
            stdout, stderr = process.communicate(timeout=4)
        self.assertEqual(process.returncode, 130, stderr)
        self.assertEqual(json.loads(stdout)["error"]["code"], "SETUP_INTERRUPTED")
        self.assertFalse((self.repo / ".gitignore").exists())
        journal = self.repo / (".agents/context/setup-history/" + plan["id"] + ".json")
        self.assertIn(canary, journal.read_text())
        self.private_paths_are_ignored(journal.relative_to(self.repo).as_posix(),
            ".agents/context/setup-fixture-barrier.json", ".agents/context/setup-fixture-reached")
        self.cli("setup", "--rollback", journal)
        self.assertFalse((self.repo / ".gitignore").exists())
        self.private_paths_are_ignored(journal.relative_to(self.repo).as_posix())

    def test_private_operational_tracking_or_knowledge_overlap_fails_before_effects(self):
        self.native_fixture()
        journal = next((self.repo / ".agents/context/setup-history").glob("*.json"))
        subprocess.run(["git", "add", "-f", str(journal)], cwd=self.repo, check=True)
        failure = self.cli("setup", expected=2)
        self.assertEqual(failure["error"]["code"], "SETUP_CONFLICT")
        subprocess.run(["git", "rm", "--cached", "-q", str(journal)], cwd=self.repo, check=True)
        path = self.repo / ".agents/context/config.json"
        config = json.loads(path.read_text())
        before = (self.repo / ".agents/context/.gitignore").read_bytes()
        for scenario in (dict(config, state_dir=".agents/context/private\n/history"),
                dict(config, knowledge_roots=[*config["knowledge_roots"], {"path": ".agents/context/state", "ownership": "agent_brain"}])):
            path.write_text(json.dumps(scenario))
            failure = self.cli("setup", expected=2)
            self.assertEqual(failure["error"]["code"], "SETUP_CONFLICT")
            self.assertEqual((self.repo / ".agents/context/.gitignore").read_bytes(), before)
        self.assertFalse((self.repo / ".agents/context/state").exists())
        self.assertFalse((self.repo / ".codex/hooks.json").exists())

    def test_unsupported_certification_never_activates_from_a_flag(self):
        self.native_fixture()
        path = self.repo / ".agents/context/codex-cli-support.json"
        record = json.loads(path.read_text())
        record["status"] = "unproven"
        path.write_text(json.dumps(record))
        before = (self.repo / ".agents/context/config.json").read_bytes()
        plan = self.cli("setup")
        self.assertEqual(plan["activation"], "disabled")
        self.assertEqual(plan["prerequisites"][-1]["status"], "unsupported")
        error = self.cli("setup", "--apply", "--plan", self.save_plan(plan), expected=2)
        self.assertEqual(error["error"]["code"], "SETUP_UNSUPPORTED")
        self.assertEqual((self.repo / ".agents/context/config.json").read_bytes(), before)
        self.assertFalse((self.repo / ".codex/hooks.json").exists())

    def test_interrupted_apply_denies_authority_and_rolls_back_exact_effects(self):
        self.native_fixture()
        plan = self.cli("setup")
        reviewed = self.save_plan(plan)
        barrier = self.repo / ".agents/context/setup-fixture-barrier.json"
        barrier.write_text(json.dumps({"after": ".codex/hooks.json"}))
        with subprocess.Popen([str(self.launcher), "setup", "--apply", "--plan", str(reviewed), "--json"],
                cwd=self.repo, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            reached = self.repo / ".agents/context/setup-fixture-reached"
            until = time.monotonic() + 5
            while not reached.exists() and time.monotonic() < until:
                time.sleep(0.02)
            self.assertTrue(reached.exists())
            process.send_signal(signal.SIGINT)
            stdout, stderr = process.communicate(timeout=4)
        self.assertEqual(process.returncode, 130, stderr)
        self.assertEqual(json.loads(stdout)["error"]["code"], "SETUP_INTERRUPTED")
        status = self.cli("status")
        self.assertEqual(status["activation_status"], "incomplete")
        self.assertFalse(any((self.repo / name).exists() for name in plan["selectors"]))
        journals = list((self.repo / ".agents/context/setup-history").glob("*.json"))
        journal = next(path for path in journals if json.loads(path.read_text())["status"] == "applying")
        self.cli("setup", "--rollback", journal)
        self.assertFalse((self.repo / ".codex/hooks.json").exists())
        self.assertTrue((self.repo / ".agents/context/expected-runtime.json").exists())

    def test_malformed_linked_and_unexpected_owned_hook_edits_are_preserved(self):
        self.native_fixture()
        self.activate()
        hooks = self.repo / ".codex/hooks.json"
        current = json.loads(hooks.read_text())
        current["hooks"]["Stop"][0]["hooks"][0]["command"] = "echo unexpected owned edit"
        hooks.write_text(json.dumps(current))
        error = self.cli("setup", "--deactivate", expected=2)
        self.assertEqual(error["error"]["code"], "SETUP_CONFLICT")
        self.assertIn("unexpected owned edit", hooks.read_text())
        hooks.write_text("{malformed")
        self.cli("setup", expected=2)
        hooks.unlink()
        hooks.symlink_to(self.base / "outside-hooks.json")
        self.cli("setup", expected=2)
        self.assertTrue(hooks.is_symlink())

    def test_simultaneous_providers_and_modes_keep_distinct_selectors_and_sessions(self):
        self.native_fixture("codex", "cli")
        self.activate()
        self.native_hook("codex", "SessionStart", source="startup")
        original = self.cli("status")["work_sessions"][0]["work_session_id"]
        self.native_fixture("copilot", "cli")
        self.native_fixture("gemini", "cli")
        self.native_fixture("codex", "desktop")
        self.activate()
        index = json.loads((self.repo / ".agents/context/native-registrations.json").read_text())
        self.assertEqual({item["integration_id"] for item in index["integrations"]}, {"codex-cli", "codex-desktop", "copilot-cli", "gemini-cli"})
        self.assertEqual(len(list((self.repo / ".agents/context/registrations").glob("*.json"))), 4)
        for provider, event in (("copilot", "sessionStart"), ("gemini", "SessionStart"), ("codex", "SessionStart")):
            self.assertIn("No learned knowledge", json.dumps(self.native_hook(provider, event, source="startup")))
        status = self.cli("status")
        self.assertIn(original, [item["work_session_id"] for item in status["work_sessions"]])
        self.assertEqual(len(status["work_sessions"]), 4)

    @unittest.skipUnless(os.name == "posix", "POSIX lock fixture; native Windows has separate certification")
    def test_apply_and_rollback_share_the_selected_publication_lock(self):
        import fcntl
        self.native_fixture()
        config_path = self.repo / ".agents/context/config.json"
        selected = json.loads(config_path.read_text())
        selected["state_dir"] = ".agents/context/custom café's runtime"
        config_path.write_text(json.dumps(selected))
        applied = self.activate()
        self.native_hook("codex", "SessionStart", source="startup")
        plan = self.cli("setup", "--deactivate")
        reviewed = self.save_plan(plan)
        hooks = (self.repo / ".codex/hooks.json").read_bytes()
        config = (self.repo / ".agents/context/config.json").read_bytes()
        with open(self.repo / selected["state_dir"] / "publication.lock", "a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            before = time.monotonic()
            failure = self.cli("setup", "--apply", "--plan", reviewed, expected=1)
            self.assertLess(time.monotonic() - before, 2.5)
            self.assertEqual(failure["error"]["code"], "PUBLICATION_CONTENDED")
            inverse = self.cli("setup", "--rollback", applied["journal_path"], expected=1)
            self.assertEqual(inverse["error"]["code"], "PUBLICATION_CONTENDED")
            self.assertEqual((self.repo / ".codex/hooks.json").read_bytes(), hooks)
            self.assertEqual((self.repo / ".agents/context/config.json").read_bytes(), config)
        self.cli("setup", "--apply", "--plan", reviewed)

    def test_supported_inventory_upgrade_preserves_a_live_prepared_handle_and_history(self):
        (self.repo / ".agents/memory").mkdir(parents=True)
        self.native_fixture()
        (self.repo / "src").mkdir()
        (self.repo / "src/app.py").write_text("print('offline fixture')\n")
        support_path = self.repo / ".agents/context/codex-cli-support.json"
        support = json.loads(support_path.read_text())
        support["scope"] = {"paths": ["src/app.py"]}
        support_path.write_text(json.dumps(support))
        config_path = self.repo / ".agents/context/config.json"
        config = json.loads(config_path.read_text())
        config["maintenance"] = {"enabled": False}
        unit = config["mapped_units"][0]
        unit.pop("unit", None)
        unit.update(selector={"type": "document"}, kind="policy", status="established", applies={"paths": ["src/**"]})
        config_path.write_text(json.dumps(config))
        self.activate()
        ready = self.ready_native()
        payload = self.tip_input(ready, ".agents/memory/patch-tip.md")
        prepared = self.stage_input("prepare", ready, payload)
        before = self.cli("status")
        stopped = self.native_hook("codex", "Stop")
        continuation = next(line for line in stopped["reason"].splitlines() if "--native-foreground" in line)
        source = self.base / "updated-shipping-source"
        shutil.copytree(ROOT / "skills/agent-brain", source, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        with (source / "SKILL.md").open("a", encoding="utf-8") as stream:
            stream.write("\n<!-- Offline inventory migration fixture. -->\n")
        updated = self.install("--source", source)
        new_bundle = Path(updated["bundle_path"])
        support_path = self.repo / ".agents/context/codex-cli-support.json"
        support = json.loads(support_path.read_text())
        support["bundle_path"] = str(new_bundle)
        support["adapter_path"] = str(new_bundle / "assets/adapters/codex.py")
        support_path.write_text(json.dumps(support))
        argv = [sys.executable, new_bundle / "scripts/agent-brain.py"]
        plan = self.run_json([*argv, "setup", "--json"])
        applied = self.run_json([*argv, "setup", "--apply", "--plan", self.save_plan(plan), "--json"])
        self.assertTrue((self.repo / ".agents/context/setup-backups" / (plan["id"] + ".sqlite3")).is_file())
        after = self.cli("status")
        self.assertEqual(after["work_sessions"], before["work_sessions"])
        self.assertNotIn("deny", json.dumps(self.native_hook("codex", "PreToolUse", tool_input={"command": continuation})))
        continued = subprocess.run(continuation + " --classification ready_to_complete", shell=True, cwd=self.repo,
            env=self.env, text=True, capture_output=True, timeout=6)
        self.assertEqual(continued.returncode, 0, (continued.stdout, continued.stderr))
        published = self.cli("learn", "publish", "--invocation-file", ready["invocation_file"])
        self.assertEqual(published["publication"]["id"], prepared["publication"]["id"])
        self.assertEqual((self.repo / ".agents/memory/patch-tip.md").read_text(), payload["proposal"]["changes"][0]["content"])
        completed = self.cli("learn", "complete", "--invocation-file", ready["invocation_file"])
        self.assertEqual(completed["stage_outcome"], "changed")

    def test_forged_inverse_journal_cannot_replace_protected_policy(self):
        (self.repo / "AGENTS.md").write_text("Protected original policy.\n")
        self.native_fixture()
        applied = self.activate()
        path = self.repo / applied["journal_path"]
        journal = json.loads(path.read_text())
        journal["changes"].insert(0, {"path": "AGENTS.md", "before": "forged policy\n", "after": "Protected original policy.\n",
            "before_revision": hashlib.sha256(b"forged policy\n").hexdigest(), "after_revision": hashlib.sha256(b"Protected original policy.\n").hexdigest()})
        journal["integrity"] = hashlib.sha256(json.dumps({key: value for key, value in journal.items() if key != "integrity"}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        path.write_text(json.dumps(journal))
        error = self.cli("setup", "--rollback", path, expected=2)
        self.assertEqual(error["error"]["code"], "SETUP_HISTORY_UNAVAILABLE")
        self.assertEqual((self.repo / "AGENTS.md").read_text(), "Protected original policy.\n")

    def test_fresh_first_task_publishes_focused_knowledge_without_existing_kb(self):
        self.native_fixture()
        self.assertFalse((self.repo / ".agents/memory").exists())
        self.assertFalse((self.repo / ".agents/instructions").exists())
        (self.repo / "src").mkdir()
        (self.repo / "src/app.py").write_text("print('offline fixture')\n")
        path = self.repo / ".agents/context/codex-cli-support.json"
        support = json.loads(path.read_text())
        support["scope"] = {"paths": ["src/app.py"]}
        path.write_text(json.dumps(support))
        self.activate()
        ready = self.ready_native()
        self.assertTrue(ready["delivery"]["complete"])
        payload = self.tip_input(ready, ".agents/memory/first-task-tip.md")
        self.stage_input("prepare", ready, payload)
        self.cli("learn", "publish", "--invocation-file", ready["invocation_file"])
        self.cli("learn", "complete", "--invocation-file", ready["invocation_file"])
        self.assertEqual((self.repo / ".agents/memory/first-task-tip.md").read_text(), payload["proposal"]["changes"][0]["content"])
        self.assertIn("Use smaller focused patches", json.dumps(self.cli("recall", "--path", "src/app.py")))

    def test_competing_publication_blocks_setup_effects_until_the_checked_set_finishes(self):
        (self.repo / ".agents/memory").mkdir(parents=True)
        self.native_fixture()
        (self.repo / "src").mkdir()
        (self.repo / "src/app.py").write_text("print('offline fixture')\n")
        support_path = self.repo / ".agents/context/codex-cli-support.json"
        support = json.loads(support_path.read_text())
        support["scope"] = {"paths": ["src/app.py"]}
        support_path.write_text(json.dumps(support))
        config_path = self.repo / ".agents/context/config.json"
        config = json.loads(config_path.read_text())
        config["state_dir"] = ".agents/context/competing café's runtime"
        config["maintenance"] = {"enabled": False}
        unit = config["mapped_units"][0]
        unit.pop("unit", None)
        unit.update(selector={"type": "document"}, kind="policy", status="established", applies={"paths": ["src/**"]})
        config_path.write_text(json.dumps(config))
        self.activate()

        ready = self.ready_native()
        payload = self.tip_input(ready, ".agents/memory/patch-tip.md")
        prepared = self.stage_input("prepare", ready, payload)
        plan = self.cli("setup", "--deactivate")
        reviewed = self.save_plan(plan)
        original_config = config_path.read_bytes()
        original_hooks = (self.repo / ".codex/hooks.json").read_bytes()
        env = self.env | {"AGENT_BRAIN_FIXTURE_BARRIER": "before_intent"}
        with subprocess.Popen([str(self.launcher), "learn", "publish", "--invocation-file", ready["invocation_file"], "--json"],
                cwd=self.repo, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            barrier = self.repo / config["state_dir"] / "barrier.json"
            until = time.monotonic() + 5
            while not barrier.exists() and process.poll() is None and time.monotonic() < until:
                time.sleep(0.02)
            if not barrier.exists():
                stdout, stderr = process.communicate(timeout=2)
                self.fail((stdout, stderr))
            failure = self.cli("setup", "--apply", "--plan", reviewed, expected=1)
            self.assertEqual(failure["error"]["code"], "PUBLICATION_CONTENDED")
            self.assertEqual(config_path.read_bytes(), original_config)
            self.assertEqual((self.repo / ".codex/hooks.json").read_bytes(), original_hooks)
            self.assertFalse((self.repo / ".agents/memory/patch-tip.md").exists())
            barrier.with_suffix(".release").write_text("release\n")
            stdout, stderr = process.communicate(timeout=4)
        self.assertEqual(process.returncode, 0, (stdout, stderr))
        self.assertEqual(json.loads(stdout)["publication"]["id"], prepared["publication"]["id"])
        self.cli("learn", "complete", "--invocation-file", ready["invocation_file"])
        self.assertEqual((self.repo / ".agents/memory/patch-tip.md").read_text(), payload["proposal"]["changes"][0]["content"])
        stale = self.cli("setup", "--apply", "--plan", reviewed, expected=2)
        self.assertEqual(stale["error"]["code"], "SETUP_STALE")
        self.activate()

    def test_installed_source_gates_select_their_known_provider_from_ordinary_payloads(self):
        self.native_fixture("copilot")
        self.native_fixture("gemini")
        for tree in (".github/hooks/scripts", ".gemini/hooks/scripts"):
            shutil.copytree(ROOT / tree, self.repo / tree)
        (self.repo / ".agents/sources").mkdir(parents=True)
        summaries = self.repo / ".agents/memory/sources"
        summaries.mkdir(parents=True)
        (summaries / "source-ingest-manifest.json").write_text('{"version":1,"entries":[]}')
        skill = self.repo / ".agents/skills/ingest-source/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("# Focused ingestion\nProcess all blocking sources in one run.\n")
        engine = self.repo / ".github/hooks/scripts/helpers/auto_ingest.py"
        bridge = self.bundle / "scripts/integration-bridge.py"
        config_path = self.repo / ".agents/context/config.json"
        config = json.loads(config_path.read_text())
        config["source_ingestion"] = {"enabled": True, "engine_path": engine.relative_to(self.repo).as_posix(),
            "engine_revision": hashlib.sha256(engine.read_bytes()).hexdigest(), "bridge_path": str(bridge),
            "bridge_revision": hashlib.sha256(bridge.read_bytes()).hexdigest()}
        config_path.write_text(json.dumps(config))
        self.activate()
        for provider, script in (("copilot", ".github/hooks/scripts/auto-ingest-source.py"), ("gemini", ".gemini/hooks/scripts/auto-ingest.py")):
            payload = {"cwd": str(self.repo), "source": "startup",
                "sessionId" if provider == "copilot" else "session_id": "ordinary-" + provider,
                "provider": "forged-other-provider", "integration_id": "forged-other-integration"}
            if provider == "gemini":
                payload["hook_event_name"] = "SessionStart"
            result = subprocess.run([sys.executable, str(self.repo / script)], cwd=self.repo, env=self.env,
                input=json.dumps(payload), text=True, capture_output=True, timeout=6)
            self.assertEqual(result.returncode, 0, result.stderr)
            outputs = [json.loads(line) for line in result.stdout.splitlines()]
            context = outputs[-1].get("additionalContext") or outputs[-1]["hookSpecificOutput"]["additionalContext"]
            self.assertIn("--native-foreground", context)
            self.assertNotIn("restore the configured agent-brain bridge", context)
            command = next(line for line in context.splitlines() if "--native-foreground" in line)
            completed = subprocess.run(command, shell=True, cwd=self.repo, env=self.env,
                text=True, capture_output=True, timeout=7)
            self.assertEqual(completed.returncode, 0, (completed.stdout, completed.stderr))
        self.assertEqual(len(self.cli("status")["work_sessions"]), 2)

    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell executable is required for this shell process case")
    def test_powershell_commands_with_spaces_nonascii_and_apostrophes_are_admitted(self):
        self.native_fixture()
        plan = self.cli("setup", "--shell", "powershell")
        self.cli("setup", "--apply", "--plan", self.save_plan(plan))
        self.assertIn("No learned knowledge", json.dumps(self.native_hook("codex", "SessionStart", source="startup")))
        stopped = self.native_hook("codex", "Stop")
        line = next(line for line in stopped["reason"].splitlines() if "--native-foreground" in line)
        self.assertTrue(line.startswith("& '"))
        self.assertIn("café''s space", line)
        self.assertNotIn("deny", json.dumps(self.native_hook("codex", "PreToolUse", tool_input={"command": line})))
        result = subprocess.run(["pwsh", "-NoProfile", "-Command", line + " --classification ready_to_complete"],
            cwd=self.repo, env=self.env, capture_output=True, text=True, timeout=8)
        self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))
        self.assertIn("invocation_file", json.loads(result.stdout))
        denied = self.native_hook("codex", "PreToolUse", tool_input={"command": line + "; Write-Output forged"})
        self.assertIn("deny", json.dumps(denied))

    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell executable is required for this launcher simulation")
    def test_windows_launcher_files_and_powershell_help_are_disposable_simulations(self):
        installed = self.install("--platform", "windows")
        cmd = Path(installed["launcher"])
        self.assertEqual(cmd.suffix, ".cmd")
        self.assertIn(b"\r\n", cmd.read_bytes())
        result = subprocess.run(["pwsh", "-NoProfile", "-File", str(cmd.with_suffix(".ps1")), "setup", "--help"],
            cwd=self.repo, env=self.env, capture_output=True, text=True, timeout=8)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--apply", result.stdout)
        self.assertEqual(list(self.repo.iterdir()), [self.repo / ".git"])

    def test_fresh_minimal_plan_is_read_only_and_apply_is_reversible(self):
        self.launcher = Path(self.install()["launcher"])
        (self.repo / "AGENTS.md").write_text("# Instructions\nRead this protected policy first.\n")
        before = sorted(path.relative_to(self.repo).as_posix() for path in self.repo.rglob("*"))
        plan = self.cli("setup")
        self.assertEqual(plan["operation_status"], "ok")
        self.assertEqual(plan["activation"], "disabled")
        self.assertEqual(sorted(path.relative_to(self.repo).as_posix() for path in self.repo.rglob("*")), before)
        self.assertIn("AGENTS.md", [unit["path"] for unit in plan["configuration"]["mapped_units"]])
        path = self.save_plan(plan)
        applied = self.cli("setup", "--apply", "--plan", path)
        self.assertEqual(applied["activation"], "disabled")
        self.assertEqual((self.repo / "AGENTS.md").read_text(), "# Instructions\nRead this protected policy first.\n")
        config = json.loads((self.repo / ".agents/context/config.json").read_text())
        self.assertEqual(config["knowledge_roots"][0], {"path": "AGENTS.md", "ownership": "read_only", "type": "file"})
        self.assertFalse((self.repo / ".agents/context/state").exists())
        recalled = self.cli("recall")
        self.assertIn("Read this protected policy first.", json.dumps(recalled))
        self.assertEqual(self.cli("setup", "--apply", "--plan", path)["journal_path"], applied["journal_path"])
        self.cli("setup", "--rollback", applied["journal_path"])
        self.assertFalse((self.repo / ".agents/context/config.json").exists())
        self.assertEqual((self.repo / "AGENTS.md").read_text(), "# Instructions\nRead this protected policy first.\n")

    def test_copied_immutable_bundle_and_launcher_are_separate_from_activation(self):
        installed = self.install()
        self.assertEqual(installed["core_version"], "0.1.0")
        self.assertTrue(Path(installed["bundle_path"]).is_dir())
        self.assertEqual(list(self.repo.iterdir()), [self.repo / ".git"])
        self.launcher = Path(installed["launcher"])
        help_result = subprocess.run([str(self.launcher), "setup", "--help"], cwd=self.repo,
            env=self.env, capture_output=True, text=True, timeout=5)
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("--apply", help_result.stdout)
        again = self.install()
        self.assertEqual(again["bundle_path"], installed["bundle_path"])


if __name__ == "__main__":
    unittest.main()
