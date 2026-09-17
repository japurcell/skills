#!/usr/bin/env python3

"""Public CLI tests for the managed Codex-agent converter."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("install-codex-agents.py")
MANIFEST = ".skills-repo-agents.json"
LOCK = ".skills-repo-agents.lock"


class CodexAgentConverterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.sources = self.root / "agents"
        self.destination = self.root / "codex-agents"
        self.sources.mkdir()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_agent(
        self,
        filename: str,
        *,
        name: str = "helper",
        description: str = "Helpful agent",
        body: str = "\nInstructions.\n",
        metadata: str = "",
    ) -> Path:
        source = self.sources / filename
        source.write_text(
            f"---\nname: {name}\ndescription: {description}\n{metadata}---\n{body}",
            encoding="utf-8",
            newline="",
        )
        return source

    def run_converter(self, *, environment: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        variables = os.environ.copy()
        if environment:
            variables.update(environment)
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--source-dir", str(self.sources), "--destination-dir", str(self.destination)],
            text=True,
            capture_output=True,
            check=False,
            env=variables,
        )

    def assert_failure_without_mutation(self, before: dict[str, bytes]) -> None:
        result = self.run_converter()
        self.assertNotEqual(result.returncode, 0, result)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr)
        after = {
            path.relative_to(self.destination).as_posix(): path.read_bytes()
            for path in self.destination.rglob("*")
            if path.is_file()
        } if self.destination.exists() else {}
        self.assertEqual(after, before)

    def destination_bytes(self) -> dict[str, bytes]:
        if not self.destination.exists():
            return {}
        return {
            path.relative_to(self.destination).as_posix(): path.read_bytes()
            for path in self.destination.rglob("*")
            if path.is_file()
        }

    def test_converts_exact_bodies_and_stable_toml(self) -> None:
        bodies = {
            "plain.md": "\nLeading blank line. unicode: café. $HOME \\\\ \"quote\" '''.\n",
            "double.md": "first\r\nsecond\r\n",
            "single.md": "no final newline",
        }
        self.write_agent("plain.md", name="plain", body=bodies["plain.md"])
        self.write_agent("literal.md", name="literal", description="Plain # and colon: text", body="literal\n")
        self.sources.joinpath("double.md").write_bytes(
            b'---\r\nname: "double agent"\r\ndescription: "Quoted description"\r\n---\r\nfirst\r\nsecond\r\n'
        )
        self.sources.joinpath("single.md").write_bytes(
            b"---\nname: 'single-agent'\ndescription: 'Single quoted: it''s # literal'\n---\nno final newline"
        )

        result = self.run_converter()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r"^Codex agents: 4 installed, 0 updated, 0 unchanged, 0 removed\.\n$")
        self.assertEqual(result.stderr, "")
        first_install = self.destination_bytes()
        for output, body in (("plain.toml", bodies["plain.md"]), ("double.toml", bodies["double.md"]), ("single.toml", bodies["single.md"])):
            parsed = tomllib.loads((self.destination / output).read_text(encoding="utf-8"))
            self.assertEqual(parsed["developer_instructions"], body)
            self.assertIn("# Generated from agents/", (self.destination / output).read_text(encoding="utf-8"))
        self.assertEqual(tomllib.loads((self.destination / "literal.toml").read_text(encoding="utf-8"))["description"], "Plain # and colon: text")
        self.assertEqual(tomllib.loads((self.destination / "single.toml").read_text(encoding="utf-8"))["description"], "Single quoted: it's # literal")
        if os.name != "nt":
            self.assertEqual(stat.S_IMODE((self.destination / "plain.toml").stat().st_mode), 0o600)

        second = self.run_converter()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("0 installed, 0 updated, 4 unchanged, 0 removed", second.stdout)
        self.assertEqual(first_install, self.destination_bytes())

    def test_rejects_strict_frontmatter_before_creating_destination(self) -> None:
        invalid_sources = {
            "missing.md": b"---\nname: helper\n---\nbody\n",
            "duplicate.md": b"---\nname: helper\nname: again\ndescription: desc\n---\nbody\n",
            "unknown.md": b"---\nname: helper\ndescription: desc\ntools: read\n---\nbody\n",
            "yaml.md": b"---\nname: [helper]\ndescription: desc\n---\nbody\n",
            "delimiter.md": b" ---\nname: helper\ndescription: desc\n---\nbody\n",
            "bom.md": b"\xef\xbb\xbf---\nname: helper\ndescription: desc\n---\nbody\n",
            "utf8.md": b"---\nname: helper\ndescription: desc\n---\n\xff",
            "empty.md": b"---\nname: helper\ndescription: desc\n---\n \t\n",
            "reserved.md": b"---\nname: worker\ndescription: desc\n---\nbody\n",
        }
        for filename, content in invalid_sources.items():
            with self.subTest(filename=filename):
                for path in self.sources.iterdir():
                    path.unlink()
                self.sources.joinpath(filename).write_bytes(content)
                result = self.run_converter()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn(filename, result.stderr)
                self.assertFalse(self.destination.exists())

    def test_rejects_source_and_identity_collisions_without_mutation(self) -> None:
        self.write_agent("one.md", name="one")
        self.write_agent("two.md", name="ONE")
        self.assert_failure_without_mutation({})
        self.sources.joinpath("two.md").unlink()
        self.write_agent("ONE.md", name="two")
        self.assert_failure_without_mutation({})
        self.sources.joinpath("ONE.md").unlink()
        if hasattr(os, "symlink"):
            target = self.write_agent("target.md", name="target")
            self.sources.joinpath("linked.md").symlink_to(target)
            result = self.run_converter()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("linked.md", result.stderr)
            self.assertFalse(self.destination.exists())

    def test_updates_removes_and_preserves_unmanaged_files(self) -> None:
        self.write_agent("one.md", name="one", body="one\n")
        self.write_agent("two.md", name="two", body="two\n")
        self.assertEqual(self.run_converter().returncode, 0)
        unmanaged = self.destination / "personal.toml"
        unmanaged.write_text('name = "personal"\ndescription = "Mine"\ndeveloper_instructions = "Keep"\n', encoding="utf-8")
        self.write_agent("one.md", name="one", body="updated\n")
        self.sources.joinpath("two.md").unlink()
        result = self.run_converter()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("0 installed, 1 updated, 0 unchanged, 1 removed", result.stdout)
        self.assertEqual(tomllib.loads((self.destination / "one.toml").read_text(encoding="utf-8"))["developer_instructions"], "updated\n")
        self.assertFalse((self.destination / "two.toml").exists())
        self.assertTrue(unmanaged.exists())
        manifest = json.loads((self.destination / MANIFEST).read_text(encoding="utf-8"))
        self.assertEqual(manifest, {"version": 1, "agents": [{"source": "one.md", "output": "one.toml", "name": "one"}]})

    def test_rejects_unsafe_destination_state_without_mutation(self) -> None:
        self.write_agent("helper.md")
        self.destination.mkdir()
        collision = self.destination / "helper.toml"
        collision.write_text("personal", encoding="utf-8")
        before = self.destination_bytes()
        self.assert_failure_without_mutation(before)
        collision.unlink()
        self.destination.joinpath(LOCK).write_text("active", encoding="utf-8")
        self.assert_failure_without_mutation({LOCK: b"active"})
        self.destination.joinpath(LOCK).unlink()
        self.destination.joinpath(MANIFEST).write_text('{"version": 2, "agents": []}', encoding="utf-8")
        self.assert_failure_without_mutation({MANIFEST: b'{"version": 2, "agents": []}'})

    def test_recreates_missing_managed_output_and_cleans_only_owned_stale_files(self) -> None:
        self.write_agent("one.md", name="one", body="one\n")
        self.write_agent("two.md", name="two", body="two\n")
        self.assertEqual(self.run_converter().returncode, 0)
        self.destination.joinpath("one.toml").unlink()
        self.sources.joinpath("two.md").unlink()
        self.destination.joinpath("unrelated.txt").write_text("keep", encoding="utf-8")
        result = self.run_converter()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 installed, 0 updated, 0 unchanged, 1 removed", result.stdout)
        self.assertTrue(self.destination.joinpath("one.toml").exists())
        self.assertFalse(self.destination.joinpath("two.toml").exists())
        self.assertEqual(self.destination.joinpath("unrelated.txt").read_text(encoding="utf-8"), "keep")

    def test_empty_source_removes_all_owned_outputs_deterministically(self) -> None:
        self.write_agent("one.md", name="one")
        self.assertEqual(self.run_converter().returncode, 0)
        self.sources.joinpath("one.md").unlink()
        first = self.run_converter()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("0 installed, 0 updated, 0 unchanged, 1 removed", first.stdout)
        manifest = self.destination.joinpath(MANIFEST).read_bytes()
        self.assertEqual(json.loads(manifest), {"version": 1, "agents": []})
        second = self.run_converter()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("0 installed, 0 updated, 0 unchanged, 0 removed", second.stdout)
        self.assertEqual(manifest, self.destination.joinpath(MANIFEST).read_bytes())

    def test_rejects_links_and_casefolded_legacy_outputs_before_mutation(self) -> None:
        self.write_agent("helper.md", name="helper")
        self.destination.mkdir()
        if not hasattr(os, "symlink"):
            self.skipTest("Symbolic links are not available on this platform")
        outside = self.root / "outside"
        outside.write_text("outside", encoding="utf-8")
        self.destination.joinpath(MANIFEST).symlink_to(outside)
        self.assert_failure_without_mutation({MANIFEST: b"outside"})
        self.destination.joinpath(MANIFEST).unlink()
        self.destination.joinpath("helper.toml").symlink_to(outside)
        self.assert_failure_without_mutation({"helper.toml": b"outside"})
        self.destination.joinpath("helper.toml").unlink()
        self.destination.joinpath(MANIFEST).write_text(
            '{"version": 1, "agents": [{"source": "helper.md", "output": "Helper.toml", "name": "helper"}]}',
            encoding="utf-8",
        )
        self.destination.joinpath("Helper.toml").write_text("old", encoding="utf-8")
        self.assert_failure_without_mutation(self.destination_bytes())

    def test_rejects_root_lock_and_managed_output_links_without_mutation(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("Symbolic links are not available on this platform")
        self.write_agent("helper.md")
        redirect = self.root / "redirect"
        redirect.mkdir()
        self.destination.symlink_to(redirect, target_is_directory=True)
        result = self.run_converter()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(self.destination), result.stderr)
        self.destination.unlink()

        self.assertEqual(self.run_converter().returncode, 0)
        outside = self.root / "outside"
        outside.write_text("outside", encoding="utf-8")
        self.destination.joinpath("helper.toml").unlink()
        self.destination.joinpath("helper.toml").symlink_to(outside)
        self.assert_failure_without_mutation(self.destination_bytes())
        self.destination.joinpath("helper.toml").unlink()
        self.destination.joinpath(LOCK).symlink_to(outside)
        self.assert_failure_without_mutation(self.destination_bytes())

    def test_rejects_malformed_manifest_before_changing_existing_agents(self) -> None:
        self.write_agent("helper.md")
        self.destination.mkdir()
        self.destination.joinpath(MANIFEST).write_text("not json", encoding="utf-8")
        self.destination.joinpath("keep.txt").write_text("keep", encoding="utf-8")
        self.assert_failure_without_mutation(self.destination_bytes())

    def test_inspects_nested_unmanaged_toml_and_rejects_bad_toml(self) -> None:
        self.write_agent("helper.md", name="helper")
        nested = self.destination / "nested"
        nested.mkdir(parents=True)
        nested.joinpath("same.toml").write_text(
            'name = "HELPER"\ndescription = "Personal"\ndeveloper_instructions = "Personal"\n', encoding="utf-8"
        )
        self.assert_failure_without_mutation(self.destination_bytes())
        nested.joinpath("same.toml").write_text("not valid = [", encoding="utf-8")
        self.assert_failure_without_mutation(self.destination_bytes())

    def test_rolls_back_caught_apply_failures(self) -> None:
        self.write_agent("one.md", name="one", body="old one\n")
        self.write_agent("two.md", name="two", body="old two\n")
        self.assertEqual(self.run_converter().returncode, 0)
        before = self.destination_bytes()
        self.write_agent("one.md", name="one", body="new one\n")
        self.write_agent("two.md", name="two", body="new two\n")
        result = self.run_converter(environment={"CODEX_AGENT_TEST_FAIL_AFTER_REPLACEMENTS": "1"})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(before, self.destination_bytes())
        self.assertFalse((self.destination / LOCK).exists())

    def test_rejects_non_directories_and_cli_usage(self) -> None:
        self.write_agent("helper.md")
        source_file = self.sources / "helper.md"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--source-dir", str(source_file), "--destination-dir", str(self.destination)],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn(str(source_file), result.stderr)
        usage = subprocess.run([sys.executable, str(SCRIPT)], text=True, capture_output=True, check=False)
        self.assertEqual(usage.returncode, 2)
        self.assertIn("usage:", usage.stderr)


if __name__ == "__main__":
    unittest.main()
