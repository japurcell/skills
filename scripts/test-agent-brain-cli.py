#!/usr/bin/env python3
"""Public subprocess tests for the agent-brain CLI's first milestone."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CLI = Path(__file__).parents[1] / "skills" / "agent-brain" / "scripts" / "agent-brain.py"


class AgentBrainCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_cli(
        self,
        *arguments: str,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        variables = os.environ.copy()
        if environment:
            variables.update(environment)
        return subprocess.run(
            [sys.executable, str(CLI), *arguments],
            cwd=self.repository,
            text=True,
            capture_output=True,
            check=False,
            env=variables,
            stdin=subprocess.DEVNULL,
            timeout=5,
        )

    def run_cli_bytes(
        self,
        *arguments: str,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        variables = os.environ.copy()
        if environment:
            variables.update(environment)
        return subprocess.run(
            [sys.executable, str(CLI), *arguments],
            cwd=self.repository,
            capture_output=True,
            check=False,
            env=variables,
            stdin=subprocess.DEVNULL,
            timeout=5,
        )

    def tree_snapshot(self) -> dict[str, tuple[str, bytes | str | None]]:
        snapshot: dict[str, tuple[str, bytes | str | None]] = {}
        for path in sorted(self.repository.rglob("*")):
            relative = path.relative_to(self.repository).as_posix()
            if path.is_symlink():
                snapshot[relative] = ("symlink", os.readlink(path))
            elif path.is_dir():
                snapshot[relative] = ("directory", None)
            elif path.is_file():
                snapshot[relative] = ("file", path.read_bytes())
        return snapshot

    def write_recall_fixture(self) -> tuple[str, str]:
        guidance = self.repository / "guidance"
        guidance.mkdir()
        first_content = "# First artifact\n\nKeep the policy intact.\n"
        second_content = "# Second artifact\n\nScope-specific exception.\n"
        (guidance / "a.md").write_text(first_content, encoding="utf-8")
        (guidance / "b.md").write_text(second_content, encoding="utf-8")
        config_directory = self.repository / ".agents" / "context"
        config_directory.mkdir(parents=True)
        (config_directory / "config.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "repository_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                    "knowledge_roots": [{"path": "guidance", "ownership": "read_only"}],
                    "mapped_units": [
                        {
                            "id": "22222222-2222-4222-8222-222222222222",
                            "path": "guidance/b.md",
                            "unit": "whole",
                        },
                        {
                            "id": "11111111-1111-4111-8111-111111111111",
                            "path": "guidance/a.md",
                            "unit": "whole",
                        },
                    ],
                    "startup": [
                        {"id": "22222222-2222-4222-8222-222222222222", "loading_mode": "whole"},
                        {"id": "11111111-1111-4111-8111-111111111111", "loading_mode": "whole"},
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return first_content, second_content

    def test_bare_invocation_lists_commands_without_mutating_repository(self) -> None:
        before = self.tree_snapshot()
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Commands:", result.stdout)
        for command in ("recall", "learn", "dream", "setup", "doctor", "status"):
            self.assertIn(command, result.stdout)
        self.assertEqual(result.stderr, "")
        self.assertEqual(self.tree_snapshot(), before)

    def test_help_aliases_and_version_are_read_only(self) -> None:
        before = self.tree_snapshot()
        for arguments in (
            ("-h",),
            ("--help",),
            ("help",),
            ("help", "status"),
            ("status", "-h"),
            ("status", "--help"),
            ("doctor", "-h"),
            ("doctor", "--help"),
            ("recall", "-h"),
            ("recall", "--help"),
            ("learn", "-h"),
            ("learn", "--help"),
            ("dream", "-h"),
            ("dream", "--help"),
            ("setup", "-h"),
            ("setup", "--help"),
        ):
            with self.subTest(arguments=arguments):
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(result.stdout.strip())
                self.assertEqual(result.stderr, "")
                self.assertEqual(self.tree_snapshot(), before)

    def test_status_and_doctor_report_missing_state_without_creating_it(self) -> None:
        before = self.tree_snapshot()
        for command in ("status", "doctor"):
            with self.subTest(command=command):
                result = self.run_cli(command)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("uninitialized", result.stdout)
                self.assertIn(".agents/context/config.json", result.stdout)
                self.assertIn(".agents/context/state", result.stdout)
                self.assertEqual(result.stderr, "")
                self.assertEqual(self.tree_snapshot(), before)
                self.assertIn("Active integration context: unavailable", result.stdout)
                self.assertIn("CLI never launches a model", result.stdout)

    def test_doctor_marks_malformed_present_configuration_invalid(self) -> None:
        self.write_recall_fixture()
        config_path = self.repository / ".agents" / "context" / "config.json"
        config_path.write_text("{\n", encoding="utf-8")
        before = self.tree_snapshot()
        result = self.run_cli("doctor", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        self.assertEqual(record["setup_status"], "invalid")
        self.assertEqual(record["operation_status"], "ok")
        self.assertEqual(record["checks"][0]["status"], "invalid")
        self.assertIn("invalid JSON", record["checks"][0]["detail"])
        self.assertEqual(result.stderr, "")
        self.assertEqual(self.tree_snapshot(), before)

    def test_presentation_flags_work_before_and_after_read_only_commands(self) -> None:
        before = self.tree_snapshot()
        for arguments, command in (
            (("--json", "status"), "status"),
            (("status", "--json"), "status"),
            (("--json", "doctor"), "doctor"),
            (("doctor", "--json"), "doctor"),
        ):
            with self.subTest(arguments=arguments):
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 0, result.stderr)
                record = json.loads(result.stdout)
                self.assertEqual(record["operation_status"], "ok")
                self.assertEqual(record["command"], command)
                self.assertEqual(record["setup_status"], "uninitialized")
                self.assertEqual(result.stderr, "")
                if command == "status":
                    example_path = CLI.parents[1] / "examples" / "inspection-uninitialized-v1.json"
                    self.assertEqual(record, json.loads(example_path.read_text(encoding="utf-8")))
                self.assertEqual(self.tree_snapshot(), before)

    def test_json_usage_errors_write_one_result_to_stdout_and_action_to_stderr(self) -> None:
        before = self.tree_snapshot()
        for arguments in (
            ("--json", "status", "--unknown"),
            ("status", "--json", "--unknown"),
            ("recall", "--json", "--config"),
        ):
            with self.subTest(arguments=arguments):
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 2)
                record = json.loads(result.stdout)
                self.assertEqual(record["operation_status"], "error")
                self.assertEqual(record["error"]["code"], "USAGE_INVALID")
                self.assertEqual(result.stdout.count("\"operation_status\""), 1)
                self.assertIn("USAGE_INVALID", result.stderr)
                self.assertIn("Next action:", result.stderr)
                self.assertEqual(self.tree_snapshot(), before)

    def test_long_options_do_not_accept_abbreviations(self) -> None:
        before = self.tree_snapshot()
        for arguments in (("--ver",), ("status", "--j"), ("--co", "unused.json", "status")):
            with self.subTest(arguments=arguments):
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("error:", result.stderr)
                self.assertEqual(self.tree_snapshot(), before)

    def test_each_command_help_explains_inputs_effects_and_example(self) -> None:
        for command in ("recall", "learn", "dream", "setup", "doctor", "status", "help"):
            with self.subTest(command=command):
                arguments = (command, "recall", "--help") if command == "help" else (command, "--help")
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Inputs:", result.stdout)
                self.assertIn("Effects:", result.stdout)
                self.assertIn("Example:", result.stdout)
                self.assertIn("agent:", result.stdout)
                if command in ("learn", "dream"):
                    self.assertIn("registered integration is required", result.stdout)
                    self.assertIn("UTF-8 JSON", result.stdout)
                if command == "setup":
                    self.assertIn("not available from this CLI", result.stdout)
                self.assertEqual(result.stderr, "")
                self.assertEqual(self.tree_snapshot(), {})

    def test_recall_prints_complete_artifacts_once_in_configured_order(self) -> None:
        first_content, second_content = self.write_recall_fixture()
        before = self.tree_snapshot()
        result = self.run_cli("recall")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLess(result.stdout.index(second_content), result.stdout.index(first_content))
        self.assertEqual(result.stdout.count(first_content), 1)
        self.assertEqual(result.stdout.count(second_content), 1)
        self.assertIn("Informational output only", result.stdout)
        self.assertNotIn("delivery receipt", result.stdout.lower())
        self.assertEqual(result.stderr, "")
        self.assertEqual(self.tree_snapshot(), before)

    def test_bundled_configuration_example_is_accepted_and_reads_whole_artifact(self) -> None:
        example_path = CLI.parents[1] / "examples" / "config-v1.json"
        config_path = self.repository / ".agents" / "context" / "config.json"
        config_path.parent.mkdir(parents=True)
        config_path.write_bytes(example_path.read_bytes())
        artifact = self.repository / ".agents" / "instructions" / "repo.md"
        artifact.parent.mkdir(parents=True)
        content = "# Repository instruction\n\nRead this complete artifact.\n"
        artifact.write_text(content, encoding="utf-8")
        before = self.tree_snapshot()
        result = self.run_cli("--json", "recall")
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        self.assertEqual(record["artifacts"][0]["content"], content)
        self.assertTrue(record["informational_only"])
        self.assertEqual(result.stderr, "")
        self.assertEqual(self.tree_snapshot(), before)

    def test_json_recall_returns_complete_informational_artifacts(self) -> None:
        first_content, second_content = self.write_recall_fixture()
        before = self.tree_snapshot()
        for arguments in (("--json", "recall"), ("recall", "--json")):
            with self.subTest(arguments=arguments):
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 0, result.stderr)
                record = json.loads(result.stdout)
                self.assertEqual(record["operation_status"], "ok")
                self.assertEqual(record["command"], "recall")
                self.assertTrue(record["informational_only"])
                self.assertEqual(
                    [artifact["content"] for artifact in record["artifacts"]],
                    [second_content, first_content],
                )
                self.assertEqual(result.stderr, "")
                self.assertEqual(self.tree_snapshot(), before)

    def test_recall_and_json_are_utf8_under_non_utf8_process_locale(self) -> None:
        _, second_content = self.write_recall_fixture()
        unicode_content = "# Unicode guidance\n\nCafé, snowman ☃, and brain 🧠.\n"
        (self.repository / "guidance" / "a.md").write_text(unicode_content, encoding="utf-8")
        before = self.tree_snapshot()
        for arguments in (("recall",), ("--json", "recall")):
            with self.subTest(arguments=arguments):
                result = self.run_cli_bytes(*arguments, environment={"PYTHONIOENCODING": "cp1252"})
                stdout = result.stdout.decode("utf-8")
                stderr = result.stderr.decode("utf-8")
                self.assertEqual(result.returncode, 0, stderr)
                self.assertEqual(stderr, "")
                if "--json" in arguments:
                    record = json.loads(stdout)
                    self.assertEqual(
                        [artifact["content"] for artifact in record["artifacts"]],
                        [second_content, unicode_content],
                    )
                else:
                    self.assertEqual(stdout.count(unicode_content), 1)
                    self.assertEqual(stdout.count(second_content), 1)
                self.assertEqual(self.tree_snapshot(), before)

    def test_malformed_configuration_is_reported_on_stderr_without_mutation(self) -> None:
        self.write_recall_fixture()
        config_path = self.repository / ".agents" / "context" / "config.json"
        config_path.write_text("{\n", encoding="utf-8")
        before = self.tree_snapshot()
        result = self.run_cli("recall")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("CONFIGURATION_INVALID", result.stderr)
        self.assertIn("invalid JSON", result.stderr)
        self.assertEqual(self.tree_snapshot(), before)

    def test_duplicate_json_keys_are_rejected_before_recall(self) -> None:
        self.write_recall_fixture()
        config_path = self.repository / ".agents" / "context" / "config.json"
        config_text = config_path.read_text(encoding="utf-8")
        duplicate_key_config = config_text.replace(
            '"schema_version": 1,',
            '"schema_version": 1,\n  "schema_version": 1,',
            1,
        )
        config_path.write_text(duplicate_key_config, encoding="utf-8")
        before = self.tree_snapshot()
        result = self.run_cli("--json", "recall")
        self.assertEqual(result.returncode, 2)
        error_record = json.loads(result.stdout)
        self.assertEqual(error_record["error"]["code"], "CONFIGURATION_INVALID")
        self.assertIn("duplicate JSON key", error_record["error"]["cause"])
        self.assertIn("CONFIGURATION_INVALID", result.stderr)
        self.assertIn("Next action:", result.stderr)
        self.assertEqual(self.tree_snapshot(), before)

    def test_duplicate_mapped_unit_ids_are_rejected(self) -> None:
        self.write_recall_fixture()
        config_path = self.repository / ".agents" / "context" / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["mapped_units"][1]["id"] = config["mapped_units"][0]["id"]
        config_path.write_text(json.dumps(config), encoding="utf-8")
        before = self.tree_snapshot()
        result = self.run_cli("recall")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("duplicate mapped unit id", result.stderr)
        self.assertEqual(self.tree_snapshot(), before)

    def test_repository_identity_must_be_a_canonical_uuid(self) -> None:
        self.write_recall_fixture()
        config_path = self.repository / ".agents" / "context" / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["repository_id"] = "pilot-repository"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        before = self.tree_snapshot()
        result = self.run_cli("recall")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("repository_id must be a UUID", result.stderr)
        self.assertEqual(self.tree_snapshot(), before)

    def test_unsupported_config_version_is_rejected_without_mutation(self) -> None:
        self.write_recall_fixture()
        config_path = self.repository / ".agents" / "context" / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["schema_version"] = 2
        config_path.write_text(json.dumps(config), encoding="utf-8")
        before = self.tree_snapshot()
        result = self.run_cli("recall")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("schema_version must be 1", result.stderr)
        self.assertEqual(self.tree_snapshot(), before)

    def test_mapped_path_cannot_escape_repository_or_its_knowledge_roots(self) -> None:
        self.write_recall_fixture()
        config_path = self.repository / ".agents" / "context" / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["mapped_units"][0]["path"] = "../../outside.md"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        before = self.tree_snapshot()
        result = self.run_cli("recall")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("dot segments", result.stderr)
        self.assertEqual(self.tree_snapshot(), before)

    def test_windows_drive_path_is_rejected_even_with_repository_root_mapping(self) -> None:
        self.write_recall_fixture()
        config_path = self.repository / ".agents" / "context" / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["knowledge_roots"] = [{"path": ".", "ownership": "read_only"}]
        config["mapped_units"][0]["path"] = "C:/outside.md"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        before = self.tree_snapshot()
        result = self.run_cli("recall")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("must stay within the repository", result.stderr)
        self.assertEqual(self.tree_snapshot(), before)

    def test_configuration_rejects_noncanonical_dot_segments(self) -> None:
        self.write_recall_fixture()
        config_path = self.repository / ".agents" / "context" / "config.json"
        original = json.loads(config_path.read_text(encoding="utf-8"))
        for path in ("guidance/./a.md", "guidance/a/../b.md"):
            with self.subTest(path=path):
                config = json.loads(json.dumps(original))
                config["mapped_units"][0]["path"] = path
                config_path.write_text(json.dumps(config), encoding="utf-8")
                before = self.tree_snapshot()
                result = self.run_cli("recall")
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("dot segments", result.stderr)
                self.assertEqual(self.tree_snapshot(), before)

    def test_configuration_and_schema_reject_nul_path(self) -> None:
        self.write_recall_fixture()
        config_path = self.repository / ".agents" / "context" / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["mapped_units"][0]["path"] = "guidance/\x00a.md"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        before = self.tree_snapshot()
        result = self.run_cli("recall")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("POSIX separators", result.stderr)
        self.assertEqual(self.tree_snapshot(), before)

        schema_path = CLI.parent.parent / "schemas" / "config-v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        pattern = schema["$defs"]["repositoryPath"]["pattern"]
        self.assertIsNone(re.fullmatch(pattern, "guidance/\x00a.md"))

    def test_symlinked_artifact_outside_knowledge_root_is_not_printed(self) -> None:
        self.write_recall_fixture()
        guidance = self.repository / "guidance"
        config_path = self.repository / ".agents" / "context" / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["mapped_units"][0]["path"] = "guidance/escape.md"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        (guidance / "escape.md").symlink_to(config_path)
        before = self.tree_snapshot()
        result = self.run_cli("recall")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("resolves outside declared knowledge roots", result.stderr)
        self.assertEqual(self.tree_snapshot(), before)

    def test_learn_and_dream_require_registered_context_before_mutation(self) -> None:
        self.write_recall_fixture()
        (self.repository / "forged-invocation.json").write_text(
            json.dumps({"schema_version": 1, "provider": "codex", "active": True}),
            encoding="utf-8",
        )
        before = self.tree_snapshot()
        provider_environment = {
            "CODEX_SESSION_ID": "forged-codex-session",
            "CODEX_THREAD_ID": "forged-codex-thread",
            "COPILOT_SESSION_ID": "forged-copilot-session",
            "GEMINI_SESSION_ID": "forged-gemini-session",
            "AGENT_BRAIN_INVOCATION_FILE": str(self.repository / "forged-invocation.json"),
        }
        for command, arguments in (
            ("learn", ("--input", "missing-input.json")),
            ("learn", ("--input", "-", "--invocation-file", "forged-invocation.json")),
            ("dream", ("--input", "-")),
            (
                "dream",
                ("--input", "missing-input.json", "--invocation-file", "forged-invocation.json"),
            ),
        ):
            with self.subTest(command=command, arguments=arguments):
                result = self.run_cli(command, *arguments, environment=provider_environment)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("ACTIVE_CONTEXT_REQUIRED", result.stderr)
                self.assertIn("registered active agent context", result.stderr)
                self.assertIn("Next action:", result.stderr)
                self.assertEqual(self.tree_snapshot(), before)

        result = self.run_cli("--json", "learn", "--input", "-", environment=provider_environment)
        self.assertEqual(result.returncode, 2)
        error_record = json.loads(result.stdout)
        self.assertEqual(error_record["operation_status"], "error")
        self.assertEqual(error_record["error"]["code"], "ACTIVE_CONTEXT_REQUIRED")
        error_example = CLI.parents[1] / "examples" / "error-active-context-v1.json"
        self.assertEqual(error_record, json.loads(error_example.read_text(encoding="utf-8")))
        self.assertIn("ACTIVE_CONTEXT_REQUIRED", result.stderr)
        self.assertIn("Next action:", result.stderr)
        self.assertEqual(self.tree_snapshot(), before)

        result = self.run_cli("learn", "--input", "-", "--json", environment=provider_environment)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["error"]["code"], "ACTIVE_CONTEXT_REQUIRED")
        self.assertIn("Next action:", result.stderr)
        self.assertEqual(self.tree_snapshot(), before)


    def test_no_color_and_version_options_are_side_effect_free(self) -> None:
        before = self.tree_snapshot()
        for arguments in (("--no-color", "status"), ("status", "--no-color")):
            with self.subTest(arguments=arguments):
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("\x1b[", result.stdout)
                self.assertEqual(result.stderr, "")
                self.assertEqual(self.tree_snapshot(), before)

        metadata_path = CLI.parents[1] / "schemas" / "version.json"
        bundle_version = json.loads(metadata_path.read_text(encoding="utf-8"))["bundle_version"]
        for arguments in (("--version",), ("-V",)):
            with self.subTest(arguments=arguments):
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, f"agent-brain {bundle_version}\n")
                self.assertEqual(result.stderr, "")
                self.assertEqual(self.tree_snapshot(), before)

    def test_version_only_invocation_does_not_write_bytecode_into_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as bundle_directory:
            bundle = Path(bundle_directory) / "agent-brain"
            shutil.copytree(
                CLI.parents[1],
                bundle,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            entrypoint = bundle / "scripts" / "agent-brain.py"
            bundle_version = json.loads((bundle / "schemas" / "version.json").read_text(encoding="utf-8"))[
                "bundle_version"
            ]
            for arguments in (("--version",), ("--help",)):
                with self.subTest(arguments=arguments):
                    result = subprocess.run(
                        [sys.executable, str(entrypoint), *arguments],
                        cwd=self.repository,
                        text=True,
                        capture_output=True,
                        check=False,
                        stdin=subprocess.DEVNULL,
                        timeout=5,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    if arguments == ("--version",):
                        self.assertEqual(result.stdout, f"agent-brain {bundle_version}\n")
                    else:
                        self.assertIn("Commands:", result.stdout)
                    self.assertEqual(result.stderr, "")
                    self.assertFalse(any(bundle.rglob("__pycache__")))

    def test_setup_is_explicitly_unavailable_without_mutation(self) -> None:
        before = self.tree_snapshot()
        for arguments in (("setup",), ("--json", "setup"), ("setup", "--json")):
            with self.subTest(arguments=arguments):
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 2)
                if "--json" in arguments:
                    record = json.loads(result.stdout)
                    self.assertEqual(record["error"]["code"], "COMMAND_NOT_AVAILABLE")
                    self.assertIn("COMMAND_NOT_AVAILABLE", result.stderr)
                else:
                    self.assertEqual(result.stdout, "")
                    self.assertIn("COMMAND_NOT_AVAILABLE", result.stderr)
                self.assertEqual(self.tree_snapshot(), before)


if __name__ == "__main__":
    unittest.main()
