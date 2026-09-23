#!/usr/bin/env python3
"""Public-envelope tests for repository-state guard hooks."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = {
    "copilot": ROOT / ".copilot/hooks/scripts/repository-state.py",
    "gemini": ROOT / ".gemini/hooks/scripts/repository-state.py",
    "codex": ROOT / ".codex/hooks/repository-state.py",
}


class RepositoryStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / "tracked.txt").write_text("first\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "tracked.txt"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "initial"], check=True)
        (self.repo / "tracked.txt").write_text("changed\n")
        (self.repo / "staged.txt").write_text("staged\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "staged.txt"], check=True)
        (self.repo / "untracked.txt").write_text("untracked\n")

    def invoke(self, provider, tool, tool_input, *, cwd=None, raw=None):
        if provider == "copilot":
            payload = {"toolName": tool, "toolArgs": tool_input, "cwd": str(cwd or self.repo)}
        else:
            payload = {"hook_event_name": "BeforeTool" if provider == "gemini" else "PreToolUse",
                       "tool_name": tool, "tool_input": tool_input, "cwd": str(cwd or self.repo)}
        completed = subprocess.run([sys.executable, "-I", "-S", "-B", str(SCRIPTS[provider])],
                                   input=raw if raw is not None else json.dumps(payload), text=True,
                                   capture_output=True, timeout=5, env=os.environ.copy())
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def denied(self, provider, output):
        if provider == "copilot":
            self.assertEqual(output["permissionDecision"], "deny")
            return output["permissionDecisionReason"]
        if provider == "gemini":
            self.assertEqual(output["decision"], "deny")
            return output["reason"]
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")
        return output["hookSpecificOutput"]["permissionDecisionReason"]

    def test_provider_registration_and_isolated_codex_merge(self):
        copilot = json.loads((ROOT / ".copilot/hooks/hooks.json").read_text())
        for event in ("preToolUse",):
            commands = [hook.get("bash", "") for hook in copilot["hooks"][event]]
            self.assertEqual(sum("repository-state.py" in command for command in commands), 1)
            guard = next(hook for hook in copilot["hooks"][event] if "repository-state.py" in hook.get("bash", ""))
            self.assertIn("repository-state.py", guard["powershell"])
        gemini = json.loads((ROOT / ".gemini/global-settings.json").read_text())
        hooks = [hook for group in gemini["hooks"]["BeforeTool"] for hook in group["hooks"]]
        self.assertEqual(sum(hook.get("name") == "repository-state" for hook in hooks), 1)
        codex = json.loads((ROOT / ".codex/global-hooks.json").read_text())
        handlers = [hook for group in codex["hooks"]["PreToolUse"] for hook in group["hooks"]]
        guard = [hook for hook in handlers if hook.get("command") == "python3 ~/.codex/hooks/repository-state.py"]
        self.assertEqual(len(guard), 1)
        self.assertIn("repository-state.py", guard[0]["commandWindows"])
        destination = Path(self.temp.name) / "hooks.json"
        destination.write_text(json.dumps({"hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": "echo private"}]}]}}))
        completed = subprocess.run([sys.executable, str(ROOT / "scripts/install-codex-hooks.py"),
                                    "--template", str(ROOT / ".codex/global-hooks.json"),
                                    "--destination", str(destination)], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        installed = json.loads(destination.read_text())
        commands = [hook.get("command") for group in installed["hooks"]["PreToolUse"] for hook in group["hooks"]]
        self.assertIn("echo private", commands)
        self.assertEqual(commands.count("python3 ~/.codex/hooks/repository-state.py"), 1)

    def test_direct_metadata_writes_and_read_only_calls(self):
        tools = {"copilot": ("edit", "bash"), "gemini": ("write_file", "run_shell_command"), "codex": ("Edit", "Bash")}
        for provider, (editor, shell) in tools.items():
            with self.subTest(provider=provider):
                reason = self.denied(provider, self.invoke(provider, editor, {"file_path": str(self.repo / ".git/config"), "content": "bad"}))
                self.assertIn("Git metadata", reason)
                self.denied(provider, self.invoke(provider, shell, {"command": "echo bad > .git/config"}))
                self.denied(provider, self.invoke(provider, shell, {"command": "Set-Content .GIT\\config bad"}))
                self.assertEqual(self.invoke(provider, shell, {"command": "git status --short"}), {})
                self.assertEqual(self.invoke(provider, shell, {"command": "git diff --cached -- tracked.txt"}), {})
                self.assertEqual(self.invoke(provider, shell, {"command": "cat .git/config"}), {})
                self.assertEqual(self.invoke(provider, editor, {"file_path": "notes.md", "content": "fine"}), {})

    def test_discarding_git_commands_always_require_user_run(self):
        variants = ("git checkout -- tracked.txt", "git restore tracked.txt", "git reset --hard HEAD",
                    "git clean -fd", "git switch -f main", "git checkout main", "git stash clear",
                    "git -C . restore --staged staged.txt", "git checkout-index -f tracked.txt",
                    "git read-tree --reset HEAD", "git worktree remove --force other")
        for provider, shell in (("copilot", "bash"), ("gemini", "run_shell_command"), ("codex", "Bash")):
            for command in variants:
                with self.subTest(provider=provider, command=command):
                    reason = self.denied(provider, self.invoke(provider, shell, {"command": command}))
                    self.assertIn("git status", reason)
                    self.assertIn("git diff --cached", reason)
                    self.assertIn("user", reason.lower())
            self.assertEqual(self.invoke(provider, shell, {"command": "git clean -nd"}), {})

    def test_malformed_payload_and_linked_worktree_paths_fail_closed(self):
        gitdir = Path(self.temp.name) / "external-git"
        gitdir.mkdir()
        common = Path(self.temp.name) / "common-git"
        common.mkdir()
        (gitdir / "commondir").write_text("../common-git\n")
        pointer_repo = Path(self.temp.name) / "worktree"
        pointer_repo.mkdir()
        (pointer_repo / ".git").write_text(f"gitdir: {gitdir}\n")
        for provider, editor in (("copilot", "write"), ("gemini", "write_file"), ("codex", "Write")):
            with self.subTest(provider=provider):
                self.denied(provider, self.invoke(provider, editor, {"file_path": str(gitdir / "index"), "content": "bad"}, cwd=pointer_repo))
                self.denied(provider, self.invoke(provider, editor, {"file_path": str(common / "config"), "content": "bad"}, cwd=pointer_repo))
                self.denied(provider, self.invoke(provider, editor, {"file_path": str(pointer_repo / ".git"), "content": "bad"}, cwd=pointer_repo))
                shell = {"copilot": "bash", "gemini": "run_shell_command", "codex": "Bash"}[provider]
                self.denied(provider, self.invoke(provider, shell, {"command": f"echo bad > {common / 'config'}"}, cwd=pointer_repo))
                self.denied(provider, self.invoke(provider, editor, {"file_path": ".git/config", "content": "bad"}, raw="not json"))

    def test_missing_workspace_path_fails_closed(self):
        for provider, shell in (("copilot", "bash"), ("gemini", "run_shell_command"), ("codex", "Bash")):
            if provider == "copilot":
                payload = {"toolName": shell, "toolArgs": {"command": "git status"}}
            else:
                payload = {"tool_name": shell, "tool_input": {"command": "git status"}}
            self.denied(provider, self.invoke(provider, shell, {}, raw=json.dumps(payload)))

    def test_vscode_payload_and_script_authoring(self):
        payload = {"hook_event_name": "PreToolUse", "tool_name": "Edit",
                   "tool_input": {"file_path": "sample.py", "content": "Path(\".git/config\").write_text(\"bad\")"},
                   "cwd": str(self.repo)}
        output = self.invoke("copilot", "unused", {}, raw=json.dumps(payload))
        self.assertIn("Git metadata write", self.denied("copilot", output))
        for provider, editor in (("copilot", "edit"), ("gemini", "write_file"), ("codex", "Edit")):
            output = self.invoke(provider, editor, {"file_path": "sample.ps1", "content": "Set-Content .git/config bad"})
            self.denied(provider, output)

    def test_shell_quoted_prose_does_not_trigger_git_guard(self):
        for provider, shell in (("copilot", "bash"), ("gemini", "run_shell_command"), ("codex", "Bash")):
            for command in ("echo 'git checkout branch'", "echo 'note; git restore file'", "echo git checkout branch", "echo '.git/config > file'", "echo 'sed -i s/a/b/ .git/config'", "cat .git/config > copy.txt"):
                with self.subTest(provider=provider, command=command):
                    self.assertEqual(self.invoke(provider, shell, {"command": command}), {})
            self.denied(provider, self.invoke(provider, shell, {"command": "git checkout branch"}))
            self.denied(provider, self.invoke(provider, shell, {"command": "git checkout 'unfinished"}))
            self.denied(provider, self.invoke(provider, shell, {"command": "echo bad > .git/config"}))
            self.denied(provider, self.invoke(provider, shell, {"command": "bash -c 'git checkout branch'"}))
            self.denied(provider, self.invoke(provider, shell, {"command": "pwsh -Command 'git restore tracked.txt'"}))
            self.denied(provider, self.invoke(provider, shell, {"command": "python -c \"open('.git/config','w')\""}))

    def test_in_place_editor_cannot_mutate_git_metadata(self):
        command = " ".join(("sed", "-i", "-e", "s/a/b/", ".git/config"))
        for provider, shell in (("copilot", "bash"), ("gemini", "run_shell_command"), ("codex", "Bash")):
            with self.subTest(provider=provider):
                reason = self.denied(provider, self.invoke(provider, shell, {"command": command}))
                self.assertIn("Git metadata write", reason)

    def test_other_literal_metadata_mutators_are_denied(self):
        mutations = (
            " ".join(("sed", "--in-place", "-e", "s/a/b/", ".git/config")),
            " ".join(("sed", "-Ei", "-e", "s/a/b/", ".git/config")),
            " ".join(("perl", "-pi", "-e", "s/a/b/", ".git/config")),
            " ".join(("truncate", "-s", "0", ".git/config")),
            " ".join(("install", "source.txt", ".git/config")),
        )
        reads = (
            " ".join(("sed", "-n", "-e", "p", ".git/config")),
            " ".join(("perl", "-ne", "print", ".git/config")),
        )
        for provider, shell in (("copilot", "bash"), ("gemini", "run_shell_command"), ("codex", "Bash")):
            for command in mutations:
                with self.subTest(provider=provider, command=command):
                    self.denied(provider, self.invoke(provider, shell, {"command": command}))
            for command in reads:
                with self.subTest(provider=provider, command=command):
                    self.assertEqual(self.invoke(provider, shell, {"command": command}), {})

    def test_windows_executable_names_are_guarded(self):
        commands = (
            " ".join(("sed.exe", "-i", "-e", "s/a/b/", ".GIT\\config")),
            " ".join(("perl.exe", "-pi", "-e", "s/a/b/", ".GIT\\config")),
            " ".join(("truncate.exe", "-s", "0", ".GIT\\config")),
            " ".join(("install.exe", "source.txt", ".GIT\\config")),
        )
        for provider, shell in (("copilot", "powershell"), ("gemini", "run_shell_command"), ("codex", "Bash")):
            for command in commands:
                with self.subTest(provider=provider, command=command):
                    self.denied(provider, self.invoke(provider, shell, {"command": command}))

    def test_documentation_can_quote_a_blocked_command(self):
        for provider, editor in (("copilot", "edit"), ("gemini", "write_file"), ("codex", "Edit")):
            self.assertEqual(self.invoke(provider, editor, {"file_path": "guide.md", "content": "Example: echo x > .git/config"}), {})

    def test_unreadable_layout_preserves_safe_git_inspection(self):
        broken = Path(self.temp.name) / "broken"
        broken.mkdir()
        (broken / ".git").write_text("wrong pointer\n")
        for provider, shell in (("copilot", "bash"), ("gemini", "run_shell_command"), ("codex", "Bash")):
            self.assertEqual(self.invoke(provider, shell, {"command": "git status"}, cwd=broken), {})
            reason = self.denied(provider, self.invoke(provider, shell, {"command": "echo x > .git/config"}, cwd=broken))
            self.assertIn("layout", reason)

    def test_codex_apply_patch_uses_command_field(self):
        safe_patch = "*** Begin Patch\n*** Add File: notes.md\n+safe\n*** End Patch"
        blocked_patch = "*** Begin Patch\n*** Update File: .git/config\n+bad\n*** End Patch"
        self.assertEqual(self.invoke("codex", "apply_patch", {"command": safe_patch}), {})
        self.denied("codex", self.invoke("codex", "apply_patch", {"command": blocked_patch}))

    def test_patch_metadata_path_and_symlink_alias(self):
        alias = self.repo / "alias"
        alias.symlink_to(self.repo / ".git", target_is_directory=True)
        for provider, editor in (("copilot", "edit"), ("gemini", "write_file"), ("codex", "apply_patch")):
            self.denied(provider, self.invoke(provider, editor, {"file_path": "alias/config", "content": "bad"}))
            self.denied(provider, self.invoke(provider, "apply_patch", "*** Begin Patch\n*** Update File: .git/config\n*** End Patch"))

    def test_indirect_script_is_documented_limit(self):
        for provider, shell in (("copilot", "bash"), ("gemini", "run_shell_command"), ("codex", "Bash")):
            self.assertEqual(self.invoke(provider, shell, {"command": "python3 unknown.py"}), {})


if __name__ == "__main__":
    unittest.main()
