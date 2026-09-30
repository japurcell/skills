#!/usr/bin/env python3
"""Public subprocess acceptance for selected agent-asset installations."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("agent-assets.py")
SKILL = b"---\nname: caveman\ndescription: Speak briefly\n---\nFixture skill.\n"


class TeamInstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="agent assets ")
        self.root = Path(self.temporary.name)
        self.source = self.root / "source repo"
        self.target = self.root / "target repo"
        for repo in (self.source, self.target):
            repo.mkdir()
            self.git(repo, "init", "-b", "main")
        skill = self.source / "skills/caveman/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_bytes(SKILL)
        catalog = {
            "schema_version": 1,
            "assets": {"skill:caveman": {
                "source_paths": [{"path": "skills/caveman/SKILL.md", "content": "text", "line_endings": "lf"}],
                "requires": [], "clients": ["codex"], "rendering": "skill",
                "os": [], "runtime": [],
            }},
            "bundles": {},
        }
        (self.source / "distribution").mkdir()
        (self.source / "distribution/catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
        self.git(self.source, "add", ".")
        self.commit = self.git(self.source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                               "-c", "commit.gpgsign=false", "commit", "-m", "fixture")
        self.commit = self.git(self.source, "rev-parse", "HEAD").strip()

    def tearDown(self):
        self.temporary.cleanup()

    def git(self, repo, *args):
        result = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], text=True, capture_output=True,
                              cwd=self.target)

    def install(self, *args):
        return self.cli("install", "--repo", str(self.target), "--source", str(self.source),
                        "--client", "codex", "--asset", "skill:caveman", "--format", "json", *args)

    def files(self):
        return {p.relative_to(self.target).as_posix(): p.read_bytes()
                for p in self.target.rglob("*") if p.is_file() and ".git" not in p.relative_to(self.target).parts}

    def test_installs_one_committed_skill_with_provenance_and_untouched_index(self):
        index = self.git(self.target, "ls-files", "--stage")
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["command"], "install")
        self.assertEqual(report["source"]["commit"], self.commit)
        self.assertRegex(report["source"]["digest"], r"^[0-9a-f]{64}$")
        self.assertEqual(self.target.joinpath(".agents/skills/caveman/SKILL.md").read_bytes(), SKILL)
        selection = json.loads(self.target.joinpath(".agent-assets/selection.json").read_bytes())
        lock = json.loads(self.target.joinpath(".agent-assets/lock.json").read_bytes())
        self.assertEqual(selection["assets"], ["skill:caveman"])
        self.assertEqual(selection["clients"], ["codex"])
        self.assertEqual(selection["installation_id"], lock["installation_id"])
        self.assertEqual(lock["source"]["commit"], self.commit)
        self.assertEqual(lock["items"][0]["baseline_digest"], hashlib.sha256(SKILL).hexdigest())
        self.assertEqual(self.git(self.target, "ls-files", "--stage"), index)
        self.assertEqual(set(self.files()), {".agents/skills/caveman/SKILL.md", ".agent-assets/selection.json",
                                            ".agent-assets/lock.json", ".gitattributes"})
        self.assertEqual(self.git(self.target, "check-attr", "eol", "--", ".agents/skills/caveman/SKILL.md").strip(),
                         ".agents/skills/caveman/SKILL.md: eol: lf")

    def test_repeated_install_makes_no_writes(self):
        self.assertEqual(self.install().returncode, 0)
        before = self.files()
        stats = {p.relative_to(self.target).as_posix(): (p.stat().st_mtime_ns, p.stat().st_ino)
                 for p in self.target.rglob("*") if p.is_file() and ".git" not in p.relative_to(self.target).parts}
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["changes"], {"added": 0, "updated": 0, "retained": 1, "removed": 0})
        self.assertEqual(self.files(), before)
        self.assertEqual({p.relative_to(self.target).as_posix(): (p.stat().st_mtime_ns, p.stat().st_ino)
                          for p in self.target.rglob("*") if p.is_file() and ".git" not in p.relative_to(self.target).parts}, stats)

    def test_dirty_selected_source_refuses_but_unrelated_docs_do_not(self):
        path = self.source / "skills/caveman/SKILL.md"
        path.write_bytes(b"dirty\n")
        before = self.files()
        result = self.install()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_SOURCE_DIRTY", result.stderr)
        self.assertEqual(self.files(), before)
        path.write_bytes(SKILL)
        self.source.joinpath("notes.md").write_text("uncommitted note\n", encoding="utf-8")
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.target.joinpath(".agents/skills/caveman/SKILL.md").read_bytes(), SKILL)

    def test_occupied_destination_stops_whole_install(self):
        destination = self.target / ".agents/skills/caveman/SKILL.md"
        destination.parent.mkdir(parents=True)
        destination.write_bytes(SKILL)
        before = self.files()
        result = self.install()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_CONFLICT", result.stderr)
        self.assertEqual(self.files(), before)

    def test_preserves_unrelated_attributes_and_compatible_policy_without_ownership(self):
        attributes = b"*.png -text\n.agents/skills/caveman/SKILL.md text eol=lf\n"
        self.target.joinpath(".gitattributes").write_bytes(attributes)
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.target.joinpath(".gitattributes").read_bytes(), attributes)
        lock = json.loads(self.target.joinpath(".agent-assets/lock.json").read_bytes())
        self.assertEqual(lock["attributes"], [])
        self.assertEqual(self.install().returncode, 0)

    def test_incompatible_attributes_refuse_without_writes(self):
        self.target.joinpath(".gitattributes").write_bytes(b"*.md text eol=crlf\n")
        before = self.files()
        result = self.install()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_CONFLICT", result.stderr)
        self.assertEqual(self.files(), before)

    def test_linked_parent_refuses_without_touching_external_files(self):
        external = self.root / "external"
        external.mkdir()
        self.target.joinpath(".agents").symlink_to(external, target_is_directory=True)
        result = self.install()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_CONFLICT", result.stderr)
        self.assertEqual(list(external.iterdir()), [])
        self.assertEqual(self.files(), {})

    def test_rejects_credential_url_before_acquisition_without_echoing_secret(self):
        result = self.install("--source", "https://fixture:private-value@example.invalid/repo.git")
        self.assertEqual(result.returncode, 2)
        self.assertIn("ASSET_SOURCE_INVALID", result.stderr)
        self.assertNotIn("private-value", result.stderr + result.stdout)
        self.assertEqual(self.files(), {})

    def test_revision_pin_uses_recorded_committed_bytes_after_branch_advances(self):
        self.source.joinpath("skills/caveman/SKILL.md").write_bytes(b"new revision\n")
        self.git(self.source, "add", ".")
        self.git(self.source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "advance")
        result = self.install("--revision", self.commit)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["source"]["commit"], self.commit)
        self.assertEqual(json.loads(result.stdout)["source"]["policy"], {"kind": "revision", "value": self.commit})
        self.assertEqual(self.target.joinpath(".agents/skills/caveman/SKILL.md").read_bytes(), SKILL)

    def test_materializes_independent_supporting_files_with_declared_bytes_and_modes(self):
        values = {"notice.txt": (b"notice\r\n", "text", "lf", False),
                  "launch.cmd": (b"@echo off\n", "text", "crlf", False),
                  "image.bin": (b"\x00\xff\r\n", "binary", "none", False),
                  "run.sh": (b"#!/bin/sh\necho fixture\n", "text", "lf", True)}
        catalog_path = self.source / "distribution/catalog.json"
        catalog = json.loads(catalog_path.read_bytes())
        for name, (data, content, endings, executable) in values.items():
            path = self.source / "skills/caveman" / name
            path.write_bytes(data)
            if executable:
                path.chmod(0o755)
            catalog["assets"]["skill:caveman"]["source_paths"].append(
                {"path": f"skills/caveman/{name}", "content": content, "line_endings": endings})
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        self.git(self.source, "add", ".")
        self.git(self.source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "supporting files")
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = {"notice.txt": b"notice\n", "launch.cmd": b"@echo off\r\n", "image.bin": b"\x00\xff\r\n",
                    "run.sh": b"#!/bin/sh\necho fixture\n"}
        for name, data in expected.items():
            destination = self.target / ".agents/skills/caveman" / name
            self.assertEqual(destination.read_bytes(), data)
            self.assertNotEqual(destination.stat().st_ino, self.source.joinpath("skills/caveman", name).stat().st_ino)
        if os.name != "nt":
            self.assertEqual(self.target.joinpath(".agents/skills/caveman/run.sh").stat().st_mode & 0o777, 0o755)
        attrs = self.git(self.target, "check-attr", "text", "eol", "--", ".agents/skills/caveman/image.bin", ".agents/skills/caveman/launch.cmd")
        self.assertIn("image.bin: text: unset", attrs)
        self.assertIn("launch.cmd: eol: crlf", attrs)

    def test_rejects_nonportable_catalog_paths_before_destination_writes(self):
        catalog_path = self.source / "distribution/catalog.json"
        original = catalog_path.read_bytes()
        for invalid in ("skills/caveman/../escape", "skills/caveman/CON.txt", "skills/caveman/x:stream", "skills/caveman/end."):
            with self.subTest(path=invalid):
                catalog = json.loads(original)
                catalog["assets"]["skill:caveman"]["source_paths"].append(
                    {"path": invalid, "content": "text", "line_endings": "lf"})
                catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
                self.git(self.source, "add", ".")
                self.git(self.source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                         "-c", "commit.gpgsign=false", "commit", "-m", "invalid path")
                result = self.install()
                self.assertEqual(result.returncode, 2)
                self.assertIn("ASSET_CATALOG_INVALID", result.stderr)
                self.assertEqual(self.files(), {})

    def test_casefolded_output_collision_refuses_before_copies(self):
        catalog_path = self.source / "distribution/catalog.json"
        catalog = json.loads(catalog_path.read_bytes())
        catalog["assets"]["skill:caveman"]["source_paths"].append(
            {"path": "skills/caveman/skill.md", "content": "text", "line_endings": "lf"})
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        self.git(self.source, "add", ".")
        self.git(self.source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "colliding catalog")
        result = self.install()
        self.assertEqual(result.returncode, 2)
        self.assertIn("ASSET_CATALOG_INVALID", result.stderr)
        self.assertEqual(self.files(), {})

    def test_higher_precedence_unspecified_rule_refuses_before_writes(self):
        directory = self.target / ".agents/skills/caveman"
        directory.mkdir(parents=True)
        directory.joinpath(".gitattributes").write_bytes(b"SKILL.md !text !eol\n")
        before = self.files()
        result = self.install()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_CONFLICT", result.stderr)
        self.assertEqual(self.files(), before)

    def test_duplicate_catalog_keys_fail_before_writes(self):
        path = self.source / "distribution/catalog.json"
        path.write_bytes(path.read_bytes().replace(b'"schema_version": 1', b'"schema_version": 9, "schema_version": 1'))
        self.git(self.source, "add", ".")
        self.git(self.source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "ambiguous catalog")
        result = self.install()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_CATALOG_INVALID", result.stderr)
        self.assertEqual(self.files(), {})

    def test_unsupported_record_version_stops_repetition_without_writes(self):
        self.assertEqual(self.install().returncode, 0)
        path = self.target / ".agent-assets/lock.json"
        lock = json.loads(path.read_bytes())
        lock["renderer_version"] = 900
        path.write_text(json.dumps(lock), encoding="utf-8")
        before = self.files()
        result = self.install()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_RECORD_INVALID", result.stderr)
        self.assertEqual(self.files(), before)

    def test_owned_attribute_marker_edit_refuses_repetition_without_writes(self):
        self.assertEqual(self.install().returncode, 0)
        path = self.target / ".gitattributes"
        path.write_bytes(path.read_bytes().replace(b"# agent-assets begin\n", b""))
        before = self.files()
        result = self.install()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_CONFLICT", result.stderr)
        self.assertEqual(self.files(), before)

    def test_selected_source_link_is_not_followed(self):
        path = self.source / "skills/caveman/SKILL.md"
        path.unlink()
        outside = self.root / "private.md"
        outside.write_bytes(b"outside-private\n")
        path.symlink_to(outside)
        self.git(self.source, "add", ".")
        self.git(self.source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "linked source")
        result = self.install()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_SOURCE_INVALID", result.stderr)
        self.assertNotIn("outside-private", result.stdout + result.stderr)
        self.assertEqual(self.files(), {})

    def test_acquires_remote_default_branch_in_disposable_git_clone(self):
        before = self.git(self.source, "status", "--porcelain=v1")
        result = self.install("--source", self.source.as_uri())
        self.assertEqual(result.returncode, 0, result.stderr)
        source = json.loads(result.stdout)["source"]
        self.assertEqual(source["kind"], "git")
        self.assertEqual(source["policy"], {"kind": "branch", "value": "main"})
        self.assertEqual(source["commit"], self.commit)
        self.assertEqual(self.target.joinpath(".agents/skills/caveman/SKILL.md").read_bytes(), SKILL)
        self.assertEqual(self.git(self.source, "status", "--porcelain=v1"), before)

    def test_refuses_option_like_revision_and_preserves_target(self):
        result = self.install("--revision=--help")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_SOURCE_INVALID", result.stderr)
        self.assertEqual(self.files(), {})

    def test_target_staged_index_and_source_index_are_untouched(self):
        self.target.joinpath("teammate.txt").write_bytes(b"staged content\n")
        self.git(self.target, "add", "teammate.txt")
        before = {repo: ((repo / ".git/index").read_bytes(), (repo / ".git/index").stat().st_mtime_ns,
                         (repo / ".git/index").stat().st_ino) for repo in (self.source, self.target)}
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        after = {repo: ((repo / ".git/index").read_bytes(), (repo / ".git/index").stat().st_mtime_ns,
                        (repo / ".git/index").stat().st_ino) for repo in (self.source, self.target)}
        self.assertEqual(after, before)

    def test_conflict_json_has_stable_report_envelope(self):
        destination = self.target / ".agents/skills/caveman/SKILL.md"
        destination.parent.mkdir(parents=True)
        destination.write_bytes(b"personal\n")
        result = self.install()
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["command"], "install")
        self.assertEqual(report["conflicts"][0]["code"], "ASSET_CONFLICT")
        self.assertEqual(set(report), {"schema_version", "command", "source", "selection", "changes", "conflicts", "warnings"})

    def test_selected_clean_filter_is_not_executed(self):
        marker = self.root / "filter-ran"
        self.source.joinpath(".gitattributes").write_text("skills/caveman/SKILL.md filter=unsafe\n", encoding="utf-8")
        self.git(self.source, "add", ".gitattributes")
        self.git(self.source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "filter policy")
        self.git(self.source, "config", "filter.unsafe.clean", f"touch '{marker}'; cat")
        result = self.install()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_SOURCE_INVALID", result.stderr)
        self.assertFalse(marker.exists())
        self.assertEqual(self.files(), {})

    def test_unlisted_same_length_dirty_file_never_executes_clean_filter(self):
        marker = self.root / "unlisted-filter-ran"
        path = self.source / "skills/caveman/unlisted.txt"
        path.write_bytes(b"baseline\n")
        self.source.joinpath(".gitattributes").write_text("skills/caveman/unlisted.txt filter=unsafe\n", encoding="utf-8")
        self.git(self.source, "add", ".")
        self.git(self.source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "unlisted filter")
        self.git(self.source, "config", "filter.unsafe.clean", f"touch '{marker}'; cat")
        path.write_bytes(b"baseLINE\n")
        result = self.install()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse(marker.exists(), "Git clean filter executed while inspecting selected source dirtiness")
        self.assertIn("ASSET_SOURCE_INVALID", result.stderr)
        self.assertEqual(self.files(), {})

    def test_source_digest_covers_catalog_executable_intent(self):
        first = self.install()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.git(self.source, "update-index", "--chmod=+x", "distribution/catalog.json")
        self.git(self.source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "catalog mode")
        self.source.joinpath("distribution/catalog.json").chmod(0o755)
        second_target = self.root / "second target"
        second_target.mkdir()
        self.git(second_target, "init", "-b", "main")
        second = self.install("--repo", str(second_target))
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertNotEqual(json.loads(first.stdout)["source"]["digest"], json.loads(second.stdout)["source"]["digest"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=("team-install", "selection", "lifecycle", "providers", "scopes"))
    args, remaining = parser.parse_known_args()
    if args.group not in (None, "team-install"):
        parser.error(f"group {args.group} has no implemented cases yet")
    unittest.main(argv=[sys.argv[0], *remaining])


if __name__ == "__main__":
    main()
