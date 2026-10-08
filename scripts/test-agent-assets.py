#!/usr/bin/env python3
"""Public subprocess acceptance for selected agent-asset installations."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import shutil
import tomllib
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


SCRIPT = Path(__file__).with_name("agent-assets.py")
SKILL = b"---\nname: caveman\ndescription: Speak briefly\n---\nFixture skill.\n"


class Fixture(unittest.TestCase):
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

class TeamInstallTests(Fixture):
    def test_modern_metadata_requirement_cannot_be_omitted_or_mistyped(self):
        self.target.joinpath(".gitattributes").write_bytes(b'.gitattributes text eol=lf\n')
        self.assertEqual(self.install().returncode, 0)
        lock_path = self.target / ".agent-assets/lock.json"
        original = json.loads(lock_path.read_bytes())
        source_index = self.source.joinpath(".git/index").read_bytes()
        for corruption in ("missing", "type", "version"):
            with self.subTest(corruption=corruption):
                lock = json.loads(json.dumps(original))
                if corruption == "missing":
                    lock.pop("attribute_file_policy")
                elif corruption == "type":
                    lock["attribute_file_policy"] = "text eol=lf"
                else:
                    lock["schema_version"] = 1
                lock_path.write_text(json.dumps(lock), encoding="utf-8")
                before = SelectionTests.fingerprint(self)
                for command in (("status", "--check"), ("restore",)):
                    result = self.cli(*command, "--repo", str(self.target))
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertIn("ASSET_RECORD_INVALID", result.stderr)
                    self.assertEqual(SelectionTests.fingerprint(self), before)
                    self.assertEqual(self.source.joinpath(".git/index").read_bytes(), source_index)

    def test_borrowed_metadata_policy_drift_is_read_only_failure(self):
        attributes = self.target / ".gitattributes"
        attributes.write_bytes(b'.gitattributes text eol=lf\n*.png -text\n')
        self.assertEqual(self.install().returncode, 0)
        lock = json.loads(self.target.joinpath(".agent-assets/lock.json").read_bytes())
        self.assertNotIn(".gitattributes", [entry["destination"] for entry in lock["attributes"]])
        attributes.write_bytes(attributes.read_bytes() + b'.gitattributes text eol=crlf\n')
        before = SelectionTests.fingerprint(self)
        result = self.cli("status", "--repo", str(self.target), "--check", "--format", "json")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(".gitattributes", [entry["destination"] for entry in json.loads(result.stdout)["verification"]["drift"]])
        self.assertEqual(SelectionTests.fingerprint(self), before)

    def test_older_authentic_records_update_to_metadata_checkout_policy(self):
        self.assertEqual(self.install().returncode, 0)
        lock_path = self.target / ".agent-assets/lock.json"
        lock = json.loads(lock_path.read_bytes())
        lock["attributes"] = [entry for entry in lock["attributes"] if entry["destination"] != ".gitattributes"]
        lock.pop("attribute_file_policy", None)
        lock["schema_version"] = 1
        selection_path = self.target / ".agent-assets/selection.json"
        selection = json.loads(selection_path.read_bytes())
        selection["schema_version"] = 1
        selection_bytes = json.dumps(selection, sort_keys=True, separators=(",", ":")).encode()
        selection_path.write_bytes(selection_bytes)
        lock["selection_digest"] = hashlib.sha256(selection_bytes).hexdigest()
        lock_path.write_text(json.dumps(lock), encoding="utf-8")
        attributes = self.target / ".gitattributes"
        attributes.write_bytes(attributes.read_bytes().replace(b'".gitattributes" text eol=lf\n', b""))
        self.assertEqual(self.cli("status", "--repo", str(self.target), "--check").returncode, 0)
        result = self.cli("restore", "--repo", str(self.target))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b'".gitattributes" text eol=lf\n', attributes.read_bytes())
        self.assertEqual(self.cli("status", "--repo", str(self.target), "--check").returncode, 0)

    def test_metadata_checkout_conflicts_preserve_the_complete_target(self):
        for policy in (b'.gitattributes text eol=crlf\n', b'.gitattributes filter=foreign\n'):
            self.target.joinpath(".gitattributes").write_bytes(policy)
            before = SelectionTests.fingerprint(self)
            result = self.install()
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("ASSET_CONFLICT", result.stderr)
            self.assertEqual(SelectionTests.fingerprint(self), before)

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


class SelectionTests(Fixture):
    def fingerprint(self):
        return {p.relative_to(self.target).as_posix(): (p.lstat().st_mode, p.lstat().st_mtime_ns,
                                                      p.read_bytes() if p.is_file() else None)
                for p in self.target.rglob("*")}

    def save_catalog(self, catalog):
        self.source.joinpath("distribution/catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
        self.git(self.source, "add", ".")
        self.git(self.source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "selection fixture")

    def catalog(self):
        return json.loads(self.source.joinpath("distribution/catalog.json").read_text())

    def add_skill(self, catalog, name, requires=()):
        path = f"skills/{name}/SKILL.md"
        target = self.source / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"Skill {name}.\n", encoding="utf-8")
        catalog["assets"][f"skill:{name}"] = {
            "source_paths": [{"path": path, "content": "text", "line_endings": "lf"}],
            "requires": list(requires), "clients": ["codex"], "rendering": "skill", "os": [], "runtime": [],
        }

    def test_bundle_installs_literal_transitive_shared_closure(self):
        catalog = self.catalog()
        self.add_skill(catalog, "left", ["skill:caveman"])
        self.add_skill(catalog, "right", ["skill:caveman"])
        self.add_skill(catalog, "review", ["skill:left", "skill:right"])
        catalog["bundles"]["review"] = ["skill:review"]
        self.save_catalog(catalog)
        result = self.cli("install", "--repo", str(self.target), "--source", str(self.source),
                          "--client", "codex", "--bundle", "review", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        lock = json.loads(self.target.joinpath(".agent-assets/lock.json").read_bytes())
        self.assertEqual(lock["assets"], ["skill:caveman", "skill:left", "skill:review", "skill:right"])
        selection = json.loads(self.target.joinpath(".agent-assets/selection.json").read_bytes())
        self.assertEqual(selection["assets"], [])
        self.assertEqual(selection["bundles"], ["review"])
        self.assertEqual(self.target.joinpath(".agents/skills/left/SKILL.md").read_bytes(), b"Skill left.\n")
        self.assertEqual(self.target.joinpath(".agents/skills/right/SKILL.md").read_bytes(), b"Skill right.\n")
        self.assertEqual(self.target.joinpath(".agents/skills/review/SKILL.md").read_bytes(), b"Skill review.\n")
        self.assertEqual(self.target.joinpath(".agents/skills/caveman/SKILL.md").read_bytes(), SKILL)

    def test_list_and_install_report_every_missing_dependency_chain_without_writes(self):
        catalog = self.catalog()
        self.add_skill(catalog, "left", ["skill:domain-modeling"])
        self.add_skill(catalog, "right", ["skill:domain-modeling"])
        self.add_skill(catalog, "workflow", ["skill:left", "skill:right"])
        catalog["assets"]["skill:domain-modeling"] = {
            "source_paths": [], "requires": [], "clients": ["codex"], "rendering": "skill",
            "os": [], "runtime": [], "unavailable_reason": "Required skill has no maintained source.",
        }
        self.save_catalog(catalog)
        before = self.fingerprint()
        result = self.cli("list", "--source", str(self.source), "--client", "codex", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        asset = json.loads(result.stdout)["assets"]["skill:workflow"]
        self.assertFalse(asset["available"])
        self.assertEqual([entry["chain"] for entry in asset["missing"]], [
            ["skill:workflow", "skill:left", "skill:domain-modeling"],
            ["skill:workflow", "skill:right", "skill:domain-modeling"],
        ])
        result = self.install("--asset", "skill:workflow")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_DEPENDENCY_MISSING", result.stderr)
        self.assertIn("skill:workflow -> skill:left -> skill:domain-modeling", result.stderr)
        self.assertIn("skill:workflow -> skill:right -> skill:domain-modeling", result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_all_six_clients_install_at_documented_skill_paths(self):
        catalog = self.catalog()
        catalog["assets"]["skill:caveman"]["clients"] = ["codex", "copilot", "gemini", "claude", "cursor", "opencode"]
        self.save_catalog(catalog)
        for client, prefix in [("codex", ".agents"), ("copilot", ".agents"), ("gemini", ".agents"),
                               ("claude", ".claude"), ("cursor", ".agents"), ("opencode", ".agents")]:
            with self.subTest(client=client):
                target = self.root / client
                target.mkdir()
                self.git(target, "init", "-b", "main")
                result = self.cli("install", "--repo", str(target), "--source", str(self.source),
                                  "--client", client, "--asset", "skill:caveman", "--format", "json")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(target.joinpath(f"{prefix}/skills/caveman/SKILL.md").read_bytes(), SKILL)
                lock = json.loads(target.joinpath(".agent-assets/lock.json").read_bytes())
                self.assertEqual([item["destination"] for item in lock["items"]], [f"{prefix}/skills/caveman/SKILL.md"])

    def test_hooks_and_agents_refuse_skills_only_clients_and_pending_renderers(self):
        catalog = self.catalog()
        for asset_id, rendering in [("hook:tool-guard", "hook"), ("agent:reviewer", "agent")]:
            catalog["assets"][asset_id] = {"source_paths": [], "requires": [], "clients": ["codex", "copilot", "gemini"],
                                         "rendering": rendering, "os": [], "runtime": []}
        self.save_catalog(catalog)
        before = self.fingerprint()
        for asset_id in ["hook:tool-guard", "agent:reviewer"]:
            for client in ["claude", "cursor", "opencode", "codex", "copilot", "gemini"]:
                with self.subTest(asset=asset_id, client=client):
                    result = self.cli("install", "--repo", str(self.target), "--source", str(self.source),
                                      "--client", client, "--asset", asset_id, "--format", "json")
                    self.assertEqual(result.returncode, 1, result.stderr)
                    expected = "ASSET_CLIENT_UNSUPPORTED" if client in ["claude", "cursor", "opencode"] else "ASSET_RENDERER_UNAVAILABLE"
                    self.assertIn(expected, result.stderr)
                    self.assertEqual(self.fingerprint(), before)
        result = self.cli("list", "--source", str(self.source), "--client", "codex", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)["assets"]["hook:tool-guard"]["installable"])

    def test_malformed_catalog_is_rejected_by_list_before_writes(self):
        cases = [
            ("bundles", [], "bundles"),
            ("schema_version", True, "schema"),
            ("asset-field", ("requires", "skill:absent"), "requires"),
            ("asset-field", ("clients", ["unknown-client"]), "clients"),
            ("asset-field", ("runtime", "python"), "runtime"),
            ("asset-field", ("os", ["unknown-os"]), "os"),
            ("asset-field", ("rendering", "import-python"), "rendering"),
            ("asset-field", ("source_root", "outside/caveman"), "source_root"),
            ("asset-field", ("source_root", ".agents/skills/other"), "source_root"),
            ("asset-field", ("source_root", "../skills/caveman"), "source_root"),
            ("asset-field", ("source_paths", [{"path": "../escape", "content": "text", "line_endings": "lf"}]), "path"),
            ("asset-field", ("source_paths", [{"path": "skills/caveman/evals/output.md", "content": "text", "line_endings": "lf"}]), "eval output"),
            ("asset-field", ("source_paths", []), "missing skill entry point"),
        ]
        for field, value, hint in cases:
            with self.subTest(field=field, hint=hint):
                catalog = self.catalog()
                if field == "asset-field":
                    key, data = value
                    catalog["assets"]["skill:caveman"][key] = data
                else:
                    catalog[field] = value
                self.save_catalog(catalog)
                before = self.fingerprint()
                result = self.cli("list", "--source", str(self.source), "--format", "json")
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("ASSET_CATALOG_INVALID", result.stderr)
                self.assertEqual(self.fingerprint(), before)
                # Start the next public case from the original committed fixture.
                self.git(self.source, "reset", "--hard", self.commit)

    def test_preserves_shared_reference_and_license_for_requested_skills(self):
        catalog = self.catalog()
        self.add_skill(catalog, "secure", ["reference:security-checklist", "notice:repository-license"])
        catalog["assets"]["skill:caveman"]["requires"] = ["notice:repository-license"]
        for asset_id, path, data, rendering in [
            ("reference:security-checklist", "references/security-checklist.md", b"Security checklist.\n", "reference"),
            ("notice:repository-license", "LICENSE", b"Fixture license notice.\n", "notice"),
        ]:
            self.source.joinpath(path).parent.mkdir(parents=True, exist_ok=True)
            self.source.joinpath(path).write_bytes(data)
            catalog["assets"][asset_id] = {
                "source_paths": [{"path": path, "content": "text", "line_endings": "lf"}],
                "requires": [], "clients": ["codex"], "os": [], "runtime": [], "rendering": rendering,
            }
        self.save_catalog(catalog)
        result = self.install("--asset", "skill:secure")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.target.joinpath(".agents/references/security-checklist.md").read_bytes(), b"Security checklist.\n")
        self.assertEqual(self.target.joinpath(".agent-assets/notices/LICENSE").read_bytes(), b"Fixture license notice.\n")
        lock = json.loads(self.target.joinpath(".agent-assets/lock.json").read_bytes())
        self.assertEqual(lock["assets"], ["notice:repository-license", "reference:security-checklist", "skill:caveman", "skill:secure"])

    def test_undeclared_runtime_file_refuses_the_entire_selection(self):
        runtime = self.source / "skills/caveman/scripts/needed.py"
        runtime.parent.mkdir()
        runtime.write_text("print('required runtime')\n", encoding="utf-8")
        self.git(self.source, "add", ".")
        self.git(self.source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "undeclared runtime")
        before = self.fingerprint()
        result = self.install()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_CATALOG_INVALID", result.stderr)
        self.assertIn("skills/caveman/scripts/needed.py", result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_maintained_catalog_lists_bundle_roots_and_required_missing_workflows(self):
        checkout = SCRIPT.parent.parent
        catalog = json.loads(checkout.joinpath("distribution/catalog.json").read_bytes())
        for asset in catalog["assets"].values():
            for spec in asset["source_paths"]:
                path = self.source / spec["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(checkout.joinpath(spec["path"]).read_bytes())
        self.save_catalog(catalog)
        before = self.fingerprint()
        result = self.cli("list", "--source", str(self.source), "--client", "codex", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["bundles"], {"review": ["skill:code-review"],
                                             "security-hooks": ["hook:tool-guard", "hook:scan-secrets"],
                                             "required-context": ["hook:required-skills", "skill:caveman"]})
        self.assertIn("skill:domain-modeling", report["assets"])
        self.assertFalse(report["assets"]["skill:wayfinder"]["available"])
        self.assertIn(["skill:wayfinder", "skill:domain-modeling"],
                      [item["chain"] for item in report["assets"]["skill:wayfinder"]["missing"]])
        self.assertEqual(report["assets"]["skill:code-review"]["requires"], [
            "agent:addy-code-reviewer", "agent:addy-security-auditor", "agent:addy-test-engineer",
            "skill:addy-code-review-and-quality", "skill:addy-security-and-hardening", "skill:delegate-to-subagents",
            "notice:repository-license",
        ])
        self.assertIn("skill:caveman", report["assets"]["hook:required-skills"]["requires"])
        self.assertTrue(report["assets"]["hook:required-skills"]["installable"])
        self.assertEqual(self.fingerprint(), before)

    def test_shared_skill_paths_are_materialized_once_for_five_clients(self):
        catalog = self.catalog()
        catalog["assets"]["skill:caveman"]["clients"] = ["codex", "copilot", "gemini", "cursor", "opencode"]
        self.save_catalog(catalog)
        result = self.install("--client", "copilot", "--client", "gemini", "--client", "cursor", "--client", "opencode")
        self.assertEqual(result.returncode, 0, result.stderr)
        lock = json.loads(self.target.joinpath(".agent-assets/lock.json").read_bytes())
        self.assertEqual([item["destination"] for item in lock["items"]], [".agents/skills/caveman/SKILL.md"])

    def test_dependency_cycle_is_invalid_even_outside_selection(self):
        catalog = self.catalog()
        self.add_skill(catalog, "left", ["skill:right"])
        self.add_skill(catalog, "right", ["skill:left"])
        self.save_catalog(catalog)
        before = self.fingerprint()
        for command in [("list", "--source", str(self.source)),
                        ("install", "--source", str(self.source), "--client", "codex", "--asset", "skill:caveman")]:
            result = self.cli(*command, "--format", "json")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("Dependency cycle: skill:left -> skill:right -> skill:left", result.stderr)
            self.assertEqual(self.fingerprint(), before)

    def test_unknown_requested_asset_is_malformed_selection(self):
        before = self.fingerprint()
        result = self.install("--asset", "skill:typo")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_SELECTION_INVALID", result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_casefold_collision_across_assets_is_rejected_before_materialization(self):
        catalog = self.catalog()
        for asset_id, path in [("reference:first", "references/Case.md"), ("reference:second", "references/case.md")]:
            catalog["assets"][asset_id] = {"source_paths": [{"path": path, "content": "text", "line_endings": "lf"}],
                                         "requires": [], "clients": ["codex"], "rendering": "reference", "os": [], "runtime": []}
        self.source.joinpath("references").mkdir()
        self.source.joinpath("references/Case.md").write_text("case fixture\n", encoding="utf-8")
        self.save_catalog(catalog)
        before = self.fingerprint()
        result = self.install("--asset", "reference:first", "--asset", "reference:second")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_CATALOG_INVALID", result.stderr)
        self.assertIn("Case-colliding", result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_declared_missing_source_is_unavailable_with_dependency_chain(self):
        catalog = self.catalog()
        self.add_skill(catalog, "workflow", ["skill:caveman"])
        catalog["assets"]["skill:caveman"]["source_paths"].append({
            "path": "skills/caveman/references/required.md", "content": "text", "line_endings": "lf",
        })
        self.save_catalog(catalog)
        before = self.fingerprint()
        listed = self.cli("list", "--source", str(self.source), "--format", "json")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        entry = json.loads(listed.stdout)["assets"]["skill:workflow"]
        self.assertFalse(entry["available"])
        self.assertEqual(entry["missing"][0]["chain"], ["skill:workflow", "skill:caveman"])
        self.assertIn("skills/caveman/references/required.md", entry["missing"][0]["reason"])
        result = self.install("--asset", "skill:workflow")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_DEPENDENCY_MISSING", result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_explicit_repo_local_workflow_dependency_preserves_native_name_and_support(self):
        catalog = self.catalog()
        self.add_skill(catalog, "workflow", ["skill:exec-plans"])
        for relative, data in [("SKILL.md", b"Maintained execution plan skill.\n"),
                               ("references/requirements.md", b"Plan requirements.\n")]:
            path = self.source / ".agents/skills/exec-plans" / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        catalog["assets"]["skill:exec-plans"] = {
            "source_root": ".agents/skills/exec-plans", "source_paths": [
                {"path": ".agents/skills/exec-plans/SKILL.md", "content": "text", "line_endings": "lf"},
                {"path": ".agents/skills/exec-plans/references/requirements.md", "content": "text", "line_endings": "lf"},
            ], "requires": [], "clients": ["codex"], "rendering": "skill", "os": [], "runtime": [],
        }
        self.save_catalog(catalog)
        result = self.install("--asset", "skill:workflow")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.target.joinpath(".agents/skills/exec-plans/SKILL.md").read_bytes(), b"Maintained execution plan skill.\n")
        self.assertEqual(self.target.joinpath(".agents/skills/exec-plans/references/requirements.md").read_bytes(), b"Plan requirements.\n")

    def test_declared_os_restriction_refuses_before_any_write(self):
        catalog = self.catalog()
        catalog["assets"]["skill:caveman"]["os"] = ["linux" if sys.platform == "win32" else "windows"]
        self.save_catalog(catalog)
        before = self.fingerprint()
        result = self.install()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_PLATFORM_UNSUPPORTED", result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_repo_local_root_preflights_unlisted_filters_before_git_status(self):
        catalog = self.catalog()
        root = ".agents/skills/exec-plans"
        self.source.joinpath(root).mkdir(parents=True)
        self.source.joinpath(root, "SKILL.md").write_text("Execution plans.\n", encoding="utf-8")
        unlisted = self.source.joinpath(root, "unlisted.txt")
        unlisted.write_bytes(b"baseline\n")
        self.source.joinpath(".gitattributes").write_text(f"{root}/unlisted.txt filter=unsafe\n", encoding="utf-8")
        catalog["assets"]["skill:exec-plans"] = {
            "source_root": root, "source_paths": [{"path": root + "/SKILL.md", "content": "text", "line_endings": "lf"}],
            "requires": [], "clients": ["codex"], "rendering": "skill", "os": [], "runtime": [],
        }
        self.save_catalog(catalog)
        marker = self.root / "filter-executed"
        self.git(self.source, "config", "filter.unsafe.clean", f"touch '{marker}'; cat")
        unlisted.write_bytes(b"baseLINE\n")
        before = self.fingerprint()
        result = self.install("--asset", "skill:exec-plans")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_SOURCE_INVALID", result.stderr)
        self.assertFalse(marker.exists(), "Unlisted repo-local source file executed a Git filter")
        self.assertEqual(self.fingerprint(), before)

    def test_shared_declared_file_keeps_both_owners(self):
        catalog = self.catalog()
        path = "references/shared.md"
        self.source.joinpath("references").mkdir()
        self.source.joinpath(path).write_bytes(b"Shared support.\n")
        for name in ["first", "second"]:
            catalog["assets"]["reference:" + name] = {
                "source_paths": [{"path": path, "content": "text", "line_endings": "lf"}],
                "requires": [], "clients": ["codex"], "os": [], "runtime": [], "rendering": "reference",
            }
        self.save_catalog(catalog)
        result = self.install("--asset", "reference:first", "--asset", "reference:second")
        self.assertEqual(result.returncode, 0, result.stderr)
        lock = json.loads(self.target.joinpath(".agent-assets/lock.json").read_bytes())
        shared = next(item for item in lock["items"] if item["destination"] == ".agents/references/shared.md")
        self.assertEqual(shared["owners"], ["reference:first", "reference:second"])
        self.assertEqual(self.target.joinpath(shared["destination"]).read_bytes(), b"Shared support.\n")


class LifecycleTests(Fixture):
    def fingerprint(self):
        return {p.relative_to(self.target).as_posix(): (p.read_bytes(), p.stat().st_mode,
                p.stat().st_mtime_ns, p.stat().st_ino)
                for p in self.target.rglob("*") if p.is_file()}

    def advance(self, data):
        self.source.joinpath("skills/caveman/SKILL.md").write_bytes(data)
        self.git(self.source, "add", ".")
        self.git(self.source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "advance")
        return self.git(self.source, "rev-parse", "HEAD").strip()

    def lifecycle(self, command, *args):
        return self.cli(command, "--repo", str(self.target), "--format", "json", *args)

    def test_interrupted_update_is_read_only_error_then_recovers_before_new_plan(self):
        catalog_path = self.source / "distribution/catalog.json"
        catalog = json.loads(catalog_path.read_bytes())
        specs = catalog["assets"]["skill:caveman"]["source_paths"]
        for number in range(160):
            path = f"skills/caveman/file-{number:03}.txt"
            self.source.joinpath(path).write_bytes(b"A" * 32768)
            specs.append({"path": path, "content": "text", "line_endings": "lf"})
        catalog_path.write_text(json.dumps(catalog))
        self.advance(SKILL)
        self.assertEqual(self.install().returncode, 0)
        before_files = self.files()
        for number in range(160):
            self.source.joinpath(f"skills/caveman/file-{number:03}.txt").write_bytes(b"B" * 32768)
        self.advance(b"Revision B.\n")
        journal = Path(self.git(self.target, "rev-parse", "--path-format=absolute", "--git-path", "agent-assets-journal.json").strip())
        process = subprocess.Popen([sys.executable, str(SCRIPT), "update", "--repo", str(self.target), "--format", "json"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        deadline = time.monotonic() + 20
        interrupted = False
        while time.monotonic() < deadline and process.poll() is None:
            if journal.exists() and self.target.joinpath(".agents/skills/caveman/file-000.txt").read_bytes() == b"B" * 32768:
                process.kill()
                interrupted = True
                break
            time.sleep(0.001)
        stdout, stderr = process.communicate()
        self.assertTrue(interrupted, (stdout, stderr))
        before = self.fingerprint()
        result = self.lifecycle("status", "--check")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_INTERRUPTED", result.stderr)
        self.assertEqual(self.fingerprint(), before)
        changed = self.target / ".agents/skills/caveman/file-000.txt"
        changed.write_bytes(b"External edit during interruption.\n")
        before = self.fingerprint()
        result = self.lifecycle("update")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_INTERRUPTED", result.stderr)
        self.assertEqual(self.fingerprint(), before)
        changed.write_bytes(b"B" * 32768)
        outside = self.root / "external-recovery-file"
        outside.write_bytes(b"Do not touch.\n")
        changed.unlink()
        changed.symlink_to(outside)
        before = self.fingerprint()
        result = self.lifecycle("update")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_INTERRUPTED", result.stderr)
        self.assertEqual(self.fingerprint(), before)
        self.assertEqual(outside.read_bytes(), b"Do not touch.\n")
        changed.unlink()
        changed.write_bytes(b"B" * 32768)
        original_journal = journal.read_bytes()
        for destination in (".git/config", ".agent-assets/local/lock.json", "../victim"):
            forged = json.loads(original_journal)
            forged["entries"][0]["destination"] = destination
            journal.write_text(json.dumps(forged))
            before = self.fingerprint()
            result = self.lifecycle("update")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(self.fingerprint(), before)
        forged = json.loads(original_journal)
        forged["entries"][0]["after"]["digest"] = "0" * 64
        journal.write_text(json.dumps(forged))
        before = self.fingerprint()
        self.assertEqual(self.lifecycle("update").returncode, 2)
        self.assertEqual(self.fingerprint(), before)
        journal.write_bytes(original_journal)
        result = self.lifecycle("update", "--revision", "missing-ref")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_SOURCE_ERROR", result.stderr)
        self.assertEqual(self.files(), before_files)
        self.assertFalse(journal.exists())
        result = self.lifecycle("update")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.target.joinpath(".agents/skills/caveman/file-159.txt").read_bytes(), b"B" * 32768)
        self.assertFalse(journal.exists())

    @unittest.skipUnless(os.name == "posix", "POSIX process suspension and directory-descriptor race")
    def test_directory_swap_during_atomic_write_cannot_touch_external_files(self):
        catalog_path = self.source / "distribution/catalog.json"
        catalog = json.loads(catalog_path.read_bytes())
        catalog["assets"]["skill:caveman"]["source_paths"].append({
            "path": "skills/caveman/bulk.bin", "content": "binary", "line_endings": "none"})
        catalog_path.write_text(json.dumps(catalog))
        self.source.joinpath("skills/caveman/bulk.bin").write_bytes(b"A" * (32 * 1024 * 1024))
        self.advance(SKILL)
        self.assertEqual(self.install().returncode, 0)
        self.source.joinpath("skills/caveman/bulk.bin").write_bytes(b"B" * (32 * 1024 * 1024))
        self.advance(SKILL)
        directory = self.target / ".agents/skills/caveman"
        external = self.root / "external"
        external.mkdir()
        external.joinpath("bulk.bin").write_bytes(b"External file must survive.\n")
        process = subprocess.Popen([sys.executable, str(SCRIPT), "update", "--repo", str(self.target)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        deadline = time.monotonic() + 30
        staged = None
        try:
            while time.monotonic() < deadline and process.poll() is None:
                paths = list(directory.glob(".agent-assets-*"))
                if paths:
                    process.send_signal(signal.SIGSTOP)
                    _, stopped = os.waitpid(process.pid, os.WUNTRACED)
                    self.assertTrue(os.WIFSTOPPED(stopped))
                    staged = paths[0].name
                    break
                time.sleep(0.0001)
            self.assertIsNotNone(staged, "Update finished before the atomic-write race was exercised")
            directory.rename(self.root / "parked skill")
            directory.symlink_to(external, target_is_directory=True)
            external.joinpath(staged).write_bytes(b"External staging name must survive.\n")
            before = {p.name: (p.read_bytes(), p.stat().st_mode) for p in external.iterdir()}
            process.send_signal(signal.SIGCONT)
            stdout, stderr = process.communicate(timeout=30)
            self.assertEqual({p.name: (p.read_bytes(), p.stat().st_mode) for p in external.iterdir()}, before)
            self.assertNotEqual(process.returncode, 0, (stdout, stderr))
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()

    def test_forged_owned_item_cannot_authorize_pruning_a_personal_file(self):
        self.assertEqual(self.install().returncode, 0)
        private = self.target / ".agents/skills/personal/private.txt"
        private.parent.mkdir()
        private.write_bytes(b"Personal, never installed.\n")
        lock_path = self.target / ".agent-assets/lock.json"
        lock = json.loads(lock_path.read_bytes())
        forged = dict(lock["items"][0])
        forged["destination"] = ".agents/skills/personal/private.txt"
        forged["baseline_digest"] = hashlib.sha256(private.read_bytes()).hexdigest()
        forged["mode"] = private.stat().st_mode & 0o777
        lock["items"].append(forged)
        lock_path.write_text(json.dumps(lock))
        before = self.fingerprint()
        result = self.lifecycle("update")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_SOURCE_MISMATCH", result.stderr)
        self.assertEqual(self.fingerprint(), before)
        self.assertEqual(private.read_bytes(), b"Personal, never installed.\n")

    @unittest.skipUnless(os.name == "posix", "POSIX process suspension and directory identity")
    def test_regular_directory_swap_refuses_success_and_ambiguous_recovery(self):
        catalog_path = self.source / "distribution/catalog.json"
        catalog = json.loads(catalog_path.read_bytes())
        catalog["assets"]["skill:caveman"]["source_paths"].append({
            "path": "skills/caveman/bulk.bin", "content": "binary", "line_endings": "none"})
        catalog_path.write_text(json.dumps(catalog))
        self.source.joinpath("skills/caveman/bulk.bin").write_bytes(b"A" * (32 * 1024 * 1024))
        baseline = self.advance(SKILL)
        self.assertEqual(self.install().returncode, 0)
        self.source.joinpath("skills/caveman/bulk.bin").write_bytes(b"B" * (32 * 1024 * 1024))
        self.advance(SKILL)
        directory = self.target / ".agents/skills/caveman"
        external = self.root / "ordinary replacement"
        external.mkdir()
        external.joinpath("bulk.bin").write_bytes(b"A" * (32 * 1024 * 1024))
        external.joinpath("SKILL.md").write_bytes(SKILL)
        external.joinpath("personal.txt").write_bytes(b"Unrelated directory and files must survive.\n")
        journal = Path(self.git(self.target, "rev-parse", "--path-format=absolute", "--git-path", "agent-assets-journal.json").strip())
        process = subprocess.Popen([sys.executable, str(SCRIPT), "update", "--repo", str(self.target)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        deadline = time.monotonic() + 30
        try:
            while time.monotonic() < deadline and process.poll() is None:
                if list(directory.glob(".agent-assets-*")):
                    process.send_signal(signal.SIGSTOP)
                    _, stopped = os.waitpid(process.pid, os.WUNTRACED)
                    self.assertTrue(os.WIFSTOPPED(stopped))
                    break
                time.sleep(0.0001)
            else:
                self.fail("Update finished before directory substitution was exercised")
            directory.rename(self.root / "parked skill")
            external.rename(directory)
            before = {p.name: (p.read_bytes(), p.stat().st_mode, p.stat().st_ino) for p in directory.iterdir()}
            process.send_signal(signal.SIGCONT)
            stdout, stderr = process.communicate(timeout=30)
            self.assertEqual({p.name: (p.read_bytes(), p.stat().st_mode, p.stat().st_ino) for p in directory.iterdir()}, before)
            self.assertEqual(process.returncode, 2, (stdout, stderr))
            self.assertIn(b"ASSET_INTERRUPTED", stderr)
            self.assertTrue(journal.exists())
            lock = json.loads(self.target.joinpath(".agent-assets/lock.json").read_bytes())
            self.assertEqual(lock["source"]["commit"], baseline)
            before = self.fingerprint()
            recovered = self.lifecycle("update")
            self.assertEqual(recovered.returncode, 2, recovered.stderr)
            self.assertIn("ASSET_INTERRUPTED", recovered.stderr)
            self.assertEqual(self.fingerprint(), before)
            self.assertTrue(journal.exists())
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()

    def test_source_policy_disagreement_is_drift_and_blocks_mutation(self):
        self.assertEqual(self.install().returncode, 0)
        lock_path = self.target / ".agent-assets/lock.json"
        original = lock_path.read_bytes()
        for field, value in (("policy", {"kind": "branch", "value": "other"}),
                             ("location", str(self.root / "other source")),
                             ("kind", "git")):
            lock = json.loads(original)
            lock["source"][field] = value
            if field == "kind":
                lock["source"]["location"] = self.source.as_uri()
            lock_path.write_text(json.dumps(lock))
            before = self.fingerprint()
            result = self.lifecycle("status", "--check")
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("ASSET_DRIFT", result.stderr)
            self.assertEqual(self.fingerprint(), before)
            for command in ("update", "restore"):
                result = self.lifecycle(command)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("ASSET_RECORD_INVALID", result.stderr)
                self.assertEqual(self.fingerprint(), before)

    def test_recorded_origin_must_render_the_retained_baseline(self):
        self.advance(b"Different immutable baseline.\n")
        self.assertEqual(self.install().returncode, 0)
        lock_path = self.target / ".agent-assets/lock.json"
        lock = json.loads(lock_path.read_bytes())
        lock["items"][0]["origin_commit"] = self.commit
        lock_path.write_text(json.dumps(lock))
        before = self.fingerprint()
        result = self.lifecycle("update")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_SOURCE_MISMATCH", result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_owned_checkout_paths_still_refuse_unsupported_transforms(self):
        self.assertEqual(self.install().returncode, 0)
        self.advance(b"Changed upstream bytes.\n")
        info = self.target / ".git/info/attributes"
        for rule in ("filter=unsupported", "working-tree-encoding=UTF-8", "ident", "crlf"):
            with self.subTest(rule=rule):
                info.write_text(".agents/skills/caveman/SKILL.md " + rule + "\n")
                before = self.fingerprint()
                result = self.lifecycle("update")
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("ASSET_CONFLICT", result.stderr)
                self.assertEqual(self.fingerprint(), before)

    @unittest.skipUnless(os.name == "posix", "POSIX process suspension and final destination check")
    def test_concurrent_file_replacement_during_staging_is_preserved(self):
        catalog_path = self.source / "distribution/catalog.json"
        catalog = json.loads(catalog_path.read_bytes())
        catalog["assets"]["skill:caveman"]["source_paths"].append({
            "path": "skills/caveman/bulk.bin", "content": "binary", "line_endings": "none"})
        catalog_path.write_text(json.dumps(catalog))
        self.source.joinpath("skills/caveman/bulk.bin").write_bytes(b"A" * (32 * 1024 * 1024))
        baseline = self.advance(SKILL)
        self.assertEqual(self.install().returncode, 0)
        self.source.joinpath("skills/caveman/bulk.bin").write_bytes(b"B" * (32 * 1024 * 1024))
        self.advance(SKILL)
        directory = self.target / ".agents/skills/caveman"
        payload = directory / "bulk.bin"
        external = self.root / "unrelated file"
        external.write_bytes(b"Concurrent edit must survive.\n")
        external.chmod(0o600)
        journal = Path(self.git(self.target, "rev-parse", "--path-format=absolute", "--git-path", "agent-assets-journal.json").strip())
        process = subprocess.Popen([sys.executable, str(SCRIPT), "update", "--repo", str(self.target)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        deadline = time.monotonic() + 30
        try:
            while time.monotonic() < deadline and process.poll() is None:
                if list(directory.glob(".agent-assets-*")):
                    process.send_signal(signal.SIGSTOP)
                    _, stopped = os.waitpid(process.pid, os.WUNTRACED)
                    self.assertTrue(os.WIFSTOPPED(stopped))
                    break
                time.sleep(0.0001)
            else:
                self.fail("Update finished before destination substitution was exercised")
            parked = self.root / "parked payload"
            payload.rename(parked)
            payload.symlink_to(external)
            external_before = (external.read_bytes(), external.stat().st_mode, external.stat().st_ino)
            process.send_signal(signal.SIGCONT)
            stdout, stderr = process.communicate(timeout=30)
            self.assertEqual(process.returncode, 2, (stdout, stderr))
            self.assertIn(b"ASSET_INTERRUPTED", stderr)
            self.assertTrue(payload.is_symlink())
            self.assertEqual((external.read_bytes(), external.stat().st_mode, external.stat().st_ino), external_before)
            self.assertTrue(journal.exists())
            self.assertEqual(json.loads(self.target.joinpath(".agent-assets/lock.json").read_bytes())["source"]["commit"], baseline)
            before = self.fingerprint()
            self.assertEqual(self.lifecycle("update").returncode, 2)
            self.assertEqual(self.fingerprint(), before)
            payload.unlink()
            parked.rename(payload)
            result = self.lifecycle("update")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(payload.read_bytes(), b"B" * (32 * 1024 * 1024))
            self.assertFalse(journal.exists())
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()

    def test_offline_check_rejects_credential_bearing_record_without_echoing_it(self):
        self.assertEqual(self.install().returncode, 0)
        lock_path = self.target / ".agent-assets/lock.json"
        lock = json.loads(lock_path.read_bytes())
        lock["source"]["kind"] = "git"
        lock["source"]["location"] = "https://private-token@example.invalid/repo.git"
        lock_path.write_text(json.dumps(lock))
        before = self.fingerprint()
        result = self.lifecycle("status", "--check")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertNotIn("private-token", result.stdout + result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_saved_bundle_recalculates_membership_and_shared_dependency(self):
        catalog_path = self.source / "distribution/catalog.json"
        catalog = json.loads(catalog_path.read_bytes())
        for name in ("alpha", "beta", "shared"):
            path = self.source / f"skills/{name}/SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_bytes((name + " A\n").encode())
            catalog["assets"]["skill:" + name] = {
                "source_paths": [{"path": f"skills/{name}/SKILL.md", "content": "text", "line_endings": "lf"}],
                "requires": ["skill:shared"] if name != "shared" else [], "clients": ["codex"],
                "rendering": "skill", "os": [], "runtime": []}
        catalog["bundles"]["workflow"] = ["skill:alpha"]
        catalog_path.write_text(json.dumps(catalog))
        self.advance(SKILL)
        result = self.cli("install", "--repo", str(self.target), "--source", str(self.source),
                          "--client", "codex", "--bundle", "workflow", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        catalog["bundles"]["workflow"] = ["skill:beta"]
        catalog_path.write_text(json.dumps(catalog))
        self.source.joinpath("skills/shared/SKILL.md").write_bytes(b"shared B\n")
        self.advance(SKILL)
        before = self.fingerprint()
        preview = self.lifecycle("update", "--preview")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertEqual(json.loads(preview.stdout)["changes"], {"added": 1, "updated": 1, "removed": 1, "retained": 0})
        self.assertEqual(self.fingerprint(), before)
        result = self.lifecycle("update")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["resolved_assets"], ["skill:beta", "skill:shared"])
        self.assertFalse(self.target.joinpath(".agents/skills/alpha").exists())
        self.assertEqual(self.target.joinpath(".agents/skills/beta/SKILL.md").read_bytes(), b"beta A\n")
        self.assertEqual(self.target.joinpath(".agents/skills/shared/SKILL.md").read_bytes(), b"shared B\n")
        self.assertEqual(self.lifecycle("status", "--check").returncode, 0)

    def test_human_status_names_drift_without_running_a_git_filter(self):
        self.assertEqual(self.install().returncode, 0)
        path = self.target / ".agents/skills/caveman/SKILL.md"
        path.write_bytes(b"Edited.\n")
        marker = self.root / "filter-executed"
        self.git(self.target, "config", "filter.unsafe.clean", f"touch '{marker}'; cat")
        with self.target.joinpath(".gitattributes").open("ab") as output:
            output.write(b".agents/skills/caveman/SKILL.md filter=unsafe\n")
        before = self.fingerprint()
        result = self.cli("status", "--repo", str(self.target), "--check")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(".agents/skills/caveman/SKILL.md", result.stdout)
        self.assertIn("modified", result.stdout)
        self.assertIn(".gitattributes", result.stdout)
        self.assertFalse(marker.exists())
        self.assertEqual(self.fingerprint(), before)

    def test_future_scope_records_cannot_be_ignored_while_pruning(self):
        self.assertEqual(self.install().returncode, 0)
        local = self.target / ".agent-assets/local"
        local.mkdir()
        local.joinpath("lock.json").write_text('{"schema_version":99}')
        self.advance(b"Changed source.\n")
        before = self.fingerprint()
        result = self.lifecycle("update")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_RECORD_INVALID", result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_restore_refuses_rendered_baseline_tampering(self):
        self.assertEqual(self.install().returncode, 0)
        lock_path = self.target / ".agent-assets/lock.json"
        lock = json.loads(lock_path.read_bytes())
        lock["items"][0]["baseline_digest"] = "0" * 64
        lock_path.write_text(json.dumps(lock))
        before = self.fingerprint()
        result = self.lifecycle("restore")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_SOURCE_MISMATCH", result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_edited_removal_or_attribute_stops_whole_selection_change(self):
        catalog_path = self.source / "distribution/catalog.json"
        catalog = json.loads(catalog_path.read_bytes())
        catalog["assets"]["skill:next"] = {
            "source_paths": [{"path": "skills/next/SKILL.md", "content": "text", "line_endings": "lf"}],
            "requires": [], "clients": ["codex"], "rendering": "skill", "os": [], "runtime": []}
        self.source.joinpath("skills/next").mkdir()
        self.source.joinpath("skills/next/SKILL.md").write_bytes(b"Next skill.\n")
        catalog_path.write_text(json.dumps(catalog))
        self.advance(SKILL)
        self.assertEqual(self.install().returncode, 0)
        for relative, modified in ((".agents/skills/caveman/SKILL.md", b"Local edit.\n"),
                                   (".gitattributes", b"# edited owned rules\n")):
            path = self.target / relative
            original = path.read_bytes()
            path.write_bytes(modified)
            before = self.fingerprint()
            result = self.cli("install", "--repo", str(self.target), "--source", str(self.source),
                              "--client", "codex", "--asset", "skill:next", "--format", "json")
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("ASSET_CONFLICT", result.stderr)
            self.assertEqual(self.fingerprint(), before)
            path.write_bytes(original)

    def test_pins_branch_overrides_and_failed_policy_changes(self):
        self.assertEqual(self.install("--revision", self.commit).returncode, 0)
        newer = self.advance(b"Newer branch bytes.\n")
        result = self.lifecycle("update")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["source"]["commit"], self.commit)
        before = self.fingerprint()
        result = self.lifecycle("update", "--branch", "missing")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.fingerprint(), before)
        result = self.lifecycle("update", "--branch", "main")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["source"]["commit"], newer)
        self.assertEqual(json.loads(result.stdout)["selection"]["source"]["policy"], {"kind": "branch", "value": "main"})
        result = self.lifecycle("update", "--revision", self.commit)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.target.joinpath(".agents/skills/caveman/SKILL.md").read_bytes(), SKILL)
        self.assertEqual(json.loads(result.stdout)["selection"]["source"]["policy"], {"kind": "revision", "value": self.commit})

    def test_busy_mutex_refuses_without_changes_in_linked_worktree(self):
        self.assertEqual(self.install().returncode, 0)
        self.git(self.target, "add", ".")
        self.git(self.target, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "installation")
        linked = self.root / "linked target"
        self.git(self.target, "worktree", "add", "-b", "linked", str(linked))
        self.target = linked
        mutex = Path(self.git(linked, "rev-parse", "--path-format=absolute", "--git-path", "agent-assets.mutex").strip())
        mutex.write_bytes(b"0")
        script = """import os,sys
f=open(sys.argv[1], 'r+b')
if os.name == 'nt':
 import msvcrt
 msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
else:
 import fcntl
 fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
print('locked', flush=True)
sys.stdin.read()
"""
        holder = subprocess.Popen([sys.executable, "-c", script, str(mutex)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        try:
            self.assertEqual(holder.stdout.readline().strip(), "locked")
            self.advance(b"New desired bytes.\n")
            before = self.fingerprint()
            result = self.lifecycle("update")
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("ASSET_CONFLICT", result.stderr)
            self.assertEqual(self.fingerprint(), before)
        finally:
            holder.communicate("")
        result = self.lifecycle("update")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(linked.joinpath(".agents/skills/caveman/SKILL.md").read_bytes(), b"New desired bytes.\n")

    def test_tampered_ownership_never_authorizes_destructive_paths(self):
        self.assertEqual(self.install().returncode, 0)
        lock_path = self.target / ".agent-assets/lock.json"
        original = lock_path.read_bytes()
        for destination in (".git/config", ".agent-assets/selection.json", "README.md", ".agents/../victim", ".agents/skills/x/.git/config"):
            with self.subTest(destination=destination):
                lock = json.loads(original)
                lock["items"][0]["destination"] = destination
                lock_path.write_text(json.dumps(lock))
                before = self.fingerprint()
                for command in (("status", "--check"), ("update",), ("restore",)):
                    result = self.lifecycle(*command)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertIn("ASSET_RECORD_INVALID", result.stderr)
                    self.assertEqual(self.fingerprint(), before)
        lock_path.write_bytes(original)

    def test_check_distinguishes_selection_and_attribute_drift_from_invalid_records(self):
        self.assertEqual(self.install().returncode, 0)
        selection_path = self.target / ".agent-assets/selection.json"
        original = selection_path.read_bytes()
        selection = json.loads(original)
        selection["assets"] = ["skill:different"]
        selection_path.write_text(json.dumps(selection))
        before = self.fingerprint()
        result = self.lifecycle("status", "--check")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_DRIFT", result.stderr)
        self.assertEqual(self.fingerprint(), before)
        selection_path.write_bytes(original)
        attrs = self.target / ".gitattributes"
        original = attrs.read_bytes()
        attrs.write_bytes(original + b"*.png -text\n")
        self.assertEqual(self.lifecycle("status", "--check").returncode, 0)
        attrs.write_bytes(original.replace(b"eol=lf", b"eol=crlf"))
        before = self.fingerprint()
        result = self.lifecycle("status", "--check")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(self.fingerprint(), before)
        lock_path = self.target / ".agent-assets/lock.json"
        lock = json.loads(lock_path.read_bytes())
        lock["renderer_version"] = 999
        lock_path.write_text(json.dumps(lock))
        before = self.fingerprint()
        result = self.lifecycle("status", "--check")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_restore_uses_recorded_commit_and_digest_without_changing_policy(self):
        self.assertEqual(self.install().returncode, 0)
        before = self.files()
        self.advance(b"Unrequested newer revision.\n")
        self.target.joinpath(".agents/skills/caveman/SKILL.md").unlink()
        result = self.lifecycle("restore")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.files(), before)
        lock_path = self.target / ".agent-assets/lock.json"
        lock = json.loads(lock_path.read_bytes())
        lock["source"]["digest"] = "0" * 64
        lock_path.write_text(json.dumps(lock))
        before = self.fingerprint()
        result = self.lifecycle("restore")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_SOURCE_MISMATCH", result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_retained_edits_preserve_baseline_origin_and_later_conflict(self):
        self.assertEqual(self.install().returncode, 0)
        target = self.target / ".agents/skills/caveman/SKILL.md"
        target.write_bytes(b"Local edit.\n")
        self.source.joinpath("unrelated.md").write_bytes(b"Advance without payload change.\n")
        revision = self.advance(SKILL)
        result = self.lifecycle("update")
        self.assertEqual(result.returncode, 0, result.stderr)
        lock = json.loads(self.target.joinpath(".agent-assets/lock.json").read_bytes())
        self.assertEqual(lock["source"]["commit"], revision)
        self.assertEqual(lock["items"][0]["origin_commit"], self.commit)
        self.assertEqual(lock["items"][0]["baseline_digest"], hashlib.sha256(SKILL).hexdigest())
        self.assertEqual(target.read_bytes(), b"Local edit.\n")
        self.assertEqual(self.lifecycle("status", "--check").returncode, 1)
        self.advance(b"Upstream edit.\n")
        before = self.fingerprint()
        result = self.lifecycle("update")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(self.fingerprint(), before)
        target.write_bytes(b"Upstream edit.\n")
        result = self.lifecycle("update")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.lifecycle("status", "--check").returncode, 0)

    def test_strict_status_is_offline_read_only_and_reports_all_payload_drift(self):
        self.assertEqual(self.install().returncode, 0)
        moved = self.root / "unavailable source"
        self.source.rename(moved)
        before = self.fingerprint()
        result = self.lifecycle("status", "--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["verification"]["passed"])
        self.assertEqual(self.fingerprint(), before)
        for data in (b"Deliberate local edit.\n", None):
            path = self.target / ".agents/skills/caveman/SKILL.md"
            path.write_bytes(data) if data is not None else path.unlink()
            before = self.fingerprint()
            result = self.lifecycle("status", "--check")
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("ASSET_DRIFT", result.stderr)
            self.assertFalse(json.loads(result.stdout)["verification"]["passed"])
            self.assertEqual(self.fingerprint(), before)
        result = self.lifecycle("status")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_selection_change_prunes_only_unused_owned_paths_and_rules(self):
        catalog_path = self.source / "distribution/catalog.json"
        catalog = json.loads(catalog_path.read_bytes())
        for name in ("alpha", "beta", "shared"):
            path = self.source / f"skills/{name}/SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_bytes((name + "\n").encode())
            catalog["assets"]["skill:" + name] = {
                "source_paths": [{"path": f"skills/{name}/SKILL.md", "content": "text", "line_endings": "lf"}],
                "requires": ["skill:shared"] if name != "shared" else [], "clients": ["codex"],
                "rendering": "skill", "os": [], "runtime": []}
        catalog_path.write_text(json.dumps(catalog))
        self.advance(SKILL)
        self.target.joinpath(".gitattributes").write_bytes(b"*.png -text\n")
        result = self.install("--asset", "skill:alpha", "--asset", "skill:beta")
        self.assertEqual(result.returncode, 0, result.stderr)
        unrelated = self.target / ".agents/skills/alpha/personal.txt"
        unrelated.write_bytes(b"Keep me.\n")
        result = self.install("--asset", "skill:beta")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["changes"]["removed"], 1)
        self.assertFalse(self.target.joinpath(".agents/skills/alpha/SKILL.md").exists())
        self.assertEqual(unrelated.read_bytes(), b"Keep me.\n")
        self.assertEqual(self.target.joinpath(".agents/skills/shared/SKILL.md").read_bytes(), b"shared\n")
        rules = self.target.joinpath(".gitattributes").read_bytes()
        self.assertTrue(rules.startswith(b"*.png -text\n"))
        self.assertNotIn(b'alpha/SKILL.md', rules)
        self.assertIn(b'shared/SKILL.md', rules)

    def test_preview_and_update_follow_saved_remote_branch(self):
        remote = self.root / "remote.git"
        self.git(self.source, "clone", "--bare", str(self.source), str(remote))
        result = self.install("--source", remote.as_uri())
        self.assertEqual(result.returncode, 0, result.stderr)
        revision = self.advance(b"Revision B.\n")
        self.git(self.source, "push", str(remote), "main")
        before = self.fingerprint()
        preview = self.lifecycle("update", "--preview")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertEqual(json.loads(preview.stdout)["changes"]["updated"], 1)
        self.assertEqual(self.fingerprint(), before)
        result = self.lifecycle("update")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["source"]["commit"], revision)
        self.assertEqual(self.target.joinpath(".agents/skills/caveman/SKILL.md").read_bytes(), b"Revision B.\n")
        self.assertEqual(self.git(self.target, "ls-files"), "")


class ProviderTests(Fixture):
    catalog = SelectionTests.catalog
    save_catalog = SelectionTests.save_catalog
    fingerprint = SelectionTests.fingerprint

    def test_gemini_lifecycle_registrations_do_not_filter_on_a_literal_wildcard(self):
        self.maintained_source()
        result = self.hook_install("hook:required-skills", "hook:scan-secrets")
        self.assertEqual(result.returncode, 0, result.stderr)
        hooks = json.loads(self.target.joinpath(".gemini/settings.json").read_bytes())["hooks"]
        for event in ("SessionStart", "SessionEnd"):
            for group in hooks[event]:
                self.assertNotIn("matcher", group)

    def test_native_agent_preflight_refuses_invalid_unmanaged_toml_and_name_collisions(self):
        self.source.joinpath("agents").mkdir()
        self.source.joinpath("agents/reviewer.md").write_text('---\nname: reviewer\ndescription: Review code\n---\nReview carefully.\n')
        catalog = self.catalog()
        catalog["assets"]["agent:reviewer"] = {
            "source_paths": [{"path": "agents/reviewer.md", "content": "text", "line_endings": "lf"}],
            "requires": [], "clients": ["codex"], "os": [], "runtime": [], "rendering": "agent"}
        self.save_catalog(catalog)
        path = self.target / ".codex/agents/mine.toml"
        path.parent.mkdir(parents=True)
        for data in ['name = "broken', 'name = "REVIEWER"\ndescription = "Mine"\ndeveloper_instructions = "Mine"\n']:
            path.write_text(data)
            before = self.fingerprint()
            result = self.cli("install", "--repo", str(self.target), "--source", str(self.source),
                              "--client", "codex", "--asset", "agent:reviewer")
            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.fingerprint(), before)

    def test_copilot_owned_version_changes_drift_and_block_pruning(self):
        self.maintained_source()
        result = self.cli("install", "--repo", str(self.target), "--source", str(self.source),
                          "--client", "copilot", "--asset", "hook:required-skills")
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.target / ".github/hooks/agent-assets.json"
        original = json.loads(path.read_bytes())
        for version in (None, 2, True, 1.0):
            value = dict(original)
            value["unrelated"] = "preserve"
            if version is None:
                value.pop("version")
            else:
                value["version"] = version
            path.write_text(json.dumps(value))
            before = self.fingerprint()
            self.assertEqual(self.cli("status", "--repo", str(self.target), "--check").returncode, 1)
            self.assertEqual(self.fingerprint(), before)
            result = self.cli("update", "--repo", str(self.target), "--format", "json")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(any("Retained local edit" in warning for warning in json.loads(result.stdout)["warnings"]))
            self.assertEqual(self.fingerprint(), before)
            result = self.cli("install", "--repo", str(self.target), "--source", str(self.source),
                              "--client", "copilot", "--asset", "skill:caveman")
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(self.fingerprint(), before)

    def test_update_authenticates_old_hook_bytes_without_executing_old_generator(self):
        self.maintained_source()
        self.assertEqual(self.hook_install("hook:required-skills").returncode, 0)
        command = self.root / "updated command checkout"
        for directory in ("scripts", "hooks"):
            shutil.copytree(SCRIPT.parent.parent / directory, command / directory, ignore=shutil.ignore_patterns("__pycache__"))
        family = "hooks/families/required_skills.py"
        updated = self.source.joinpath(family).read_bytes() + b"\n# compatible canonical maintenance\n"
        self.source.joinpath(family).write_bytes(updated)
        command.joinpath(family).write_bytes(updated)
        self.source.joinpath("skills/caveman/SKILL.md").write_bytes(SKILL + b"Updated skill.\n")
        self.save_catalog(self.catalog())
        result = subprocess.run([sys.executable, str(command / "scripts/agent-assets.py"), "update", "--repo", str(self.target)],
                                text=True, capture_output=True, cwd=self.target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"Updated skill.", self.target.joinpath(".agents/skills/caveman/SKILL.md").read_bytes())

    def test_native_restore_repairs_missing_configuration_without_repeating_owned_handlers(self):
        self.maintained_source()
        self.assertEqual(self.hook_install("hook:required-skills").returncode, 0)
        config = self.target / ".gemini/settings.json"
        expected = json.loads(config.read_bytes())
        config.unlink()
        result = self.cli("restore", "--repo", str(self.target))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(config.read_bytes()), expected)
        before = self.fingerprint()
        result = self.cli("restore", "--repo", str(self.target))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def hook_install(self, *assets):
        return self.cli("install", "--repo", str(self.target), "--source", str(self.source),
                        "--client", "gemini", *[part for asset in assets for part in ("--asset", asset)])

    def test_native_config_hardlinks_are_replaced_without_changing_external_inode(self):
        self.maintained_source()
        external = self.root / "external settings.json"
        external.write_text('{"theme":"mine"}')
        external.chmod(0o640)
        config = self.target / ".gemini/settings.json"
        config.parent.mkdir()
        os.link(external, config)
        before = (external.read_bytes(), external.stat().st_mode, external.stat().st_ino)
        result = self.hook_install("hook:required-skills")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((external.read_bytes(), external.stat().st_mode, external.stat().st_ino), before)
        self.assertNotEqual(config.stat().st_ino, external.stat().st_ino)

        external.unlink()
        os.link(config, external)
        before = (external.read_bytes(), external.stat().st_mode, external.stat().st_ino)
        result = self.cli("update", "--repo", str(self.target))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((external.read_bytes(), external.stat().st_mode, external.stat().st_ino), before)
        self.assertNotEqual(config.stat().st_ino, external.stat().st_ino)

    def test_native_config_preflight_refuses_ambiguous_settings_and_inline_codex_hooks(self):
        self.maintained_source()
        for relative, content, client in [
                (".gemini/settings.json", '{"hooks":{},"hooks":{}}', "gemini"),
                (".gemini/settings.json", '{"hooks":', "gemini"),
                (".github/hooks/agent-assets.json", '{"version":true,"hooks":{}}', "copilot"),
                (".github/hooks/agent-assets.json", '{"version":1.0,"hooks":{}}', "copilot"),
                (".codex/config.toml", 'model = "unterminated', "codex"),
                (".codex/config.toml", '[hooks]\n', "codex")]:
            path = self.target / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            before = self.fingerprint()
            result = self.cli("install", "--repo", str(self.target), "--source", str(self.source),
                              "--client", client, "--asset", "hook:required-skills")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(self.fingerprint(), before)
            path.unlink()

    def test_acquired_generator_is_never_executed_and_stale_outputs_refuse_before_writes(self):
        self.maintained_source()
        path = self.source / "scripts/generate-hooks.py"
        original = path.read_bytes()
        marker = self.root / "acquired-code-executed"
        path.write_text("from pathlib import Path\nPath(" + repr(str(marker)) + ").write_text('executed')\n")
        self.save_catalog(self.catalog())
        before = self.fingerprint()
        result = self.hook_install("hook:required-skills")
        self.assertIn("compatible command checkout", result.stderr)
        self.assertFalse(marker.exists())
        self.assertEqual(self.fingerprint(), before)

        path.write_bytes(original)
        generated = self.source / ".gemini/hooks/scripts/skill-context-injector.py"
        generated.write_bytes(generated.read_bytes() + b"\n# stale\n")
        self.save_catalog(self.catalog())
        result = self.hook_install("hook:required-skills")
        self.assertIn("ASSET_SOURCE_STALE", result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_installed_hook_optional_capture_is_self_contained_and_external(self):
        self.maintained_source()
        self.assertEqual(self.hook_install("hook:required-skills").returncode, 0)
        state, home = self.root / "capture state", self.root / "capture home"
        home.mkdir()
        config = json.loads(self.target.joinpath(".gemini/settings.json").read_bytes())
        command = config["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        env = {**os.environ, "HOME": str(home), "USERPROFILE": str(home), "AGENT_ASSETS_STATE_DIR": str(state),
               "OBSERVABILITY_CAPTURE_EVENT": "true", "PATH": str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"]}
        completed = subprocess.run(["bash", "-c", command], input=json.dumps({"hook_event_name": "SessionStart", "session_id": "capture", "cwd": str(self.target)}),
                                   text=True, capture_output=True, cwd=self.target, env=env, timeout=20)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(list(state.rglob("observability_v1.db")), completed.stderr)
        self.assertEqual(list(home.iterdir()), [])

    def test_configuration_ownership_is_authenticated_before_pruning(self):
        self.maintained_source()
        self.assertEqual(self.hook_install("hook:required-skills").returncode, 0)
        config_path = self.target / ".gemini/settings.json"
        value = json.loads(config_path.read_bytes())
        unrelated = {"hooks": [{"type": "command", "command": "echo mine"}]}
        value["hooks"]["SessionStart"].append(unrelated)
        config_path.write_text(json.dumps(value))
        lock_path = self.target / ".agent-assets/lock.json"
        lock = json.loads(lock_path.read_bytes())
        item = next(item for item in lock["items"] if item["destination"] == ".gemini/settings.json")
        item["entries"] = {"hooks": {"SessionStart": [unrelated]}}
        data = json.dumps(item["entries"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode() + b"\n"
        item["baseline_digest"] = hashlib.sha256(data).hexdigest()
        lock_path.write_text(json.dumps(lock))
        before = self.fingerprint()
        result = self.hook_install("skill:caveman")
        self.assertIn("ASSET_SOURCE_MISMATCH", result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_native_configuration_retains_unrelated_settings_and_owned_edits_until_conflicting_change(self):
        self.maintained_source()
        self.assertEqual(self.hook_install("hook:required-skills").returncode, 0)
        path = self.target / ".gemini/settings.json"
        config = json.loads(path.read_bytes())
        config["theme"] = "my-theme"
        config["hooks"]["SessionStart"].insert(0, {"hooks": [{"type": "command", "command": "echo mine"}]})
        path.write_text(json.dumps(config))
        self.assertEqual(self.cli("status", "--repo", str(self.target), "--check").returncode, 0)
        self.assertEqual(self.cli("update", "--repo", str(self.target)).returncode, 0)
        config = json.loads(path.read_bytes())
        self.assertEqual(config["theme"], "my-theme")
        self.assertEqual(len(config["hooks"]["SessionStart"]), 2)
        config["hooks"]["SessionStart"][1]["hooks"][0]["timeout"] = 17000
        path.write_text(json.dumps(config))
        changed = path.read_bytes()
        result = self.cli("update", "--repo", str(self.target))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.read_bytes(), changed)
        self.assertEqual(self.cli("status", "--repo", str(self.target), "--check").returncode, 1)
        before = self.fingerprint()
        result = self.hook_install("skill:caveman")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(self.fingerprint(), before)
        config["hooks"]["SessionStart"][1]["hooks"][0]["timeout"] = 30000
        path.write_text(json.dumps(config))
        result = self.hook_install("skill:caveman")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(path.read_bytes()), {"theme": "my-theme", "hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "echo mine"}]}]}})

    def maintained_source(self):
        checkout = SCRIPT.parent.parent
        catalog = json.loads(checkout.joinpath("distribution/catalog.json").read_bytes())
        for path in [*checkout.joinpath("hooks").rglob("*.py"), checkout / "scripts/generate-hooks.py",
                     checkout / ".codex/global-hooks.json", checkout / ".copilot/hooks/hooks.json", checkout / ".gemini/global-settings.json"]:
            relative = path.relative_to(checkout)
            self.source.joinpath(relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, self.source / relative)
        for asset in catalog["assets"].values():
            for spec in asset["source_paths"]:
                relative = spec["path"]
                self.source.joinpath(relative).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(checkout / relative, self.source / relative)
        self.source.joinpath("skills/caveman/SKILL.md").write_bytes(SKILL)
        self.save_catalog(catalog)

    def test_installed_required_hooks_survive_clone_and_nested_start_without_personal_state(self):
        self.maintained_source()
        self.target.joinpath(".gemini").mkdir()
        self.target.joinpath(".gemini/settings.json").write_text('{"theme":"fixture","hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"echo unrelated"}]}]}}')
        result = self.cli("install", "--repo", str(self.target), "--source", str(self.source),
                          "--client", "codex", "--client", "copilot", "--client", "gemini", "--asset", "hook:required-skills")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.target.joinpath(".gemini/settings.json").read_bytes())["theme"], "fixture")
        self.git(self.target, "add", ".")
        self.git(self.target, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "installed")
        clone = self.root / "relocated clone 'quoted'"
        self.git(self.root, "clone", str(self.target), str(clone))
        shutil.rmtree(self.source)
        nested = clone / "nested directory"
        nested.mkdir()
        state, home = self.root / "state", self.root / "empty home"
        home.mkdir()
        env = {**os.environ, "HOME": str(home), "USERPROFILE": str(home), "AGENT_ASSETS_STATE_DIR": str(state),
               "PATH": str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"]}
        for provider, path, event in [("codex", ".codex/hooks.json", "SessionStart"),
                                      ("copilot", ".github/hooks/agent-assets.json", "sessionStart"),
                                      ("gemini", ".gemini/settings.json", "SessionStart")]:
            config = json.loads(clone.joinpath(path).read_bytes())
            entries = config["hooks"][event]
            hook = entries[-1] if provider == "copilot" else entries[-1]["hooks"][0]
            command = hook.get("bash", hook.get("command"))
            payload = {"hook_event_name": event, "source": "startup", "session_id": "fixture", "cwd": str(nested)}
            completed = subprocess.run(["bash", "-c", command], input=json.dumps(payload), text=True,
                                       capture_output=True, cwd=nested, env=env, timeout=20)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            response = json.loads(completed.stdout.splitlines()[-1])
            context = response.get("additionalContext") or response.get("hookSpecificOutput", {}).get("additionalContext")
            self.assertIn("Fixture skill.", context or "", completed.stdout + completed.stderr)
            self.assertTrue(any(state.joinpath(provider).rglob("audit.log")))
        self.assertEqual(list(home.iterdir()), [])
        self.assertEqual(self.git(clone, "status", "--porcelain"), "")
        self.assertEqual(self.cli("status", "--repo", str(clone), "--check").returncode, 0)

    def test_native_agents_use_strict_canonical_conversion_and_discovery_paths(self):
        source = b'---\nname: reviewer\ndescription: Review "quoted" code\n---\nReview carefully.\n'
        self.source.joinpath("agents").mkdir()
        self.source.joinpath("agents/reviewer.md").write_bytes(source)
        catalog = self.catalog()
        catalog["assets"]["agent:reviewer"] = {
            "source_paths": [{"path": "agents/reviewer.md", "content": "text", "line_endings": "lf"}],
            "requires": [], "clients": ["codex", "copilot", "gemini"], "os": [], "runtime": [], "rendering": "agent"}
        self.save_catalog(catalog)
        result = self.cli("install", "--repo", str(self.target), "--source", str(self.source),
                          "--client", "codex", "--client", "copilot", "--client", "gemini", "--asset", "agent:reviewer")
        self.assertEqual(result.returncode, 0, result.stderr)
        converted = tomllib.loads(self.target.joinpath(".codex/agents/reviewer.toml").read_text())
        self.assertEqual(converted, {"name": "reviewer", "description": 'Review "quoted" code',
                                     "developer_instructions": "Review carefully.\n"})
        self.assertEqual(self.target.joinpath(".github/agents/reviewer.agent.md").read_bytes(), source)
        self.assertEqual(self.target.joinpath(".gemini/agents/reviewer.md").read_bytes(), source)
        self.assertEqual(self.cli("status", "--repo", str(self.target), "--check").returncode, 0)

    def test_security_hooks_install_all_dependencies_and_native_tool_and_end_registrations(self):
        self.maintained_source()
        result = self.cli("install", "--repo", str(self.target), "--source", str(self.source),
                          "--client", "codex", "--client", "copilot", "--client", "gemini",
                          "--asset", "hook:tool-guard", "--asset", "hook:scan-secrets")
        self.assertEqual(result.returncode, 0, result.stderr)
        home, state = self.root / "home", self.root / "security state"
        home.mkdir()
        env = {**os.environ, "HOME": str(home), "USERPROFILE": str(home), "AGENT_ASSETS_STATE_DIR": str(state),
               "PATH": str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"]}
        nested = self.target / "nested"
        nested.mkdir()
        for provider, config_path, tool_event, stop_event in [
                ("codex", ".codex/hooks.json", "PreToolUse", "Stop"),
                ("copilot", ".github/hooks/agent-assets.json", "preToolUse", "agentStop"),
                ("gemini", ".gemini/settings.json", "BeforeTool", "SessionEnd")]:
            config = json.loads(self.target.joinpath(config_path).read_bytes())
            self.assertIn(stop_event, config["hooks"])
            tool_entries = config["hooks"][tool_event]
            for entry in tool_entries:
                hook = entry if provider == "copilot" else entry["hooks"][0]
                command = hook.get("bash", hook.get("command"))
                payload = {"hook_event_name": tool_event, "tool_name": "Bash" if provider != "gemini" else "run_shell_command",
                           "tool_input": {"command": "echo fixture"}, "cwd": str(nested), "session_id": "safe"}
                if "tool-guard" in command:
                    allowed = subprocess.run(["bash", "-c", command], input=json.dumps(payload), text=True,
                                             capture_output=True, cwd=nested, env=env, timeout=20)
                    self.assertEqual(allowed.returncode, 0, provider + allowed.stderr)
                    response = json.loads(allowed.stdout.splitlines()[-1])
                    decision = (response.get("permissionDecision") or response.get("decision")
                                or response.get("hookSpecificOutput", {}).get("permissionDecision")
                                or ("allow" if response == {} else None))
                    self.assertEqual(decision, "allow", provider + allowed.stdout)
                    payload["tool_input"]["command"] = "r" + "m -rf /"
                completed = subprocess.run(["bash", "-c", command], input=json.dumps(payload), text=True,
                                           capture_output=True, cwd=nested, env=env, timeout=20)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                response = json.loads(completed.stdout.splitlines()[-1])
                if "tool-guard" in command:
                    self.assertIn("deny", json.dumps(response), completed.stdout)
                else:
                    self.assertNotIn("incomplete", json.dumps(response), completed.stdout)
        self.assertEqual(list(home.iterdir()), [])


class ScopeTests(Fixture):
    maintained_source = ProviderTests.maintained_source
    catalog = SelectionTests.catalog
    save_catalog = SelectionTests.save_catalog

    def test_local_effective_ignore_negation_refuses_and_status_reports_privacy_drift(self):
        exclude = self.target / ".git/info/exclude"
        original = exclude.read_bytes()
        exclude.write_bytes(original + b"\n/.agents/skills/caveman/SKILL.md\n!/.agents/skills/caveman/SKILL.md\n")
        before = self.files(), exclude.read_bytes()
        result = self.install("--mode", "local")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_LOCAL_IGNORE_CONFLICT", result.stderr)
        self.assertEqual((self.files(), exclude.read_bytes()), before)
        exclude.write_bytes(original)
        ignore = self.target / ".gitignore"
        ignore.write_bytes(b"!/.agents/skills/caveman/SKILL.md\n")
        before = self.files(), exclude.read_bytes()
        result = self.install("--mode", "local")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_LOCAL_IGNORE_CONFLICT", result.stderr)
        self.assertEqual((self.files(), exclude.read_bytes()), before)
        ignore.unlink()
        result = self.install("--mode", "local")
        self.assertEqual(result.returncode, 0, result.stderr)
        ignore.write_bytes(b"!/.agents/skills/caveman/SKILL.md\n")
        before = self.files(), exclude.read_bytes()
        result = self.cli("status", "--mode", "local", "--check")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_DRIFT", result.stderr)
        self.assertEqual((self.files(), exclude.read_bytes()), before)
        ignore.unlink()
        self.git(self.target, "add", "--force", ".agents/skills/caveman/SKILL.md")
        index = self.target.joinpath(".git/index").read_bytes()
        before = self.files(), exclude.read_bytes()
        result = self.cli("status", "--mode", "local", "--check")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_DRIFT", result.stderr)
        self.assertEqual((self.files(), exclude.read_bytes()), before)
        self.assertEqual(self.target.joinpath(".git/index").read_bytes(), index)

    def test_codex_agents_borrow_and_promote_only_authenticated_companion_paths(self):
        self.source.joinpath("agents").mkdir()
        self.source.joinpath("agents/reviewer.md").write_text('---\nname: reviewer\ndescription: Review code\n---\nReview carefully.\n')
        catalog = self.catalog()
        catalog["assets"]["agent:reviewer"] = {"source_paths": [{"path": "agents/reviewer.md", "content": "text", "line_endings": "lf"}],
            "requires": [], "clients": ["codex"], "os": [], "runtime": [], "rendering": "agent"}
        self.save_catalog(catalog)
        for initial, following in (("team", "local"), ("local", "team")):
            target = self.root / (initial + " agents")
            target.mkdir()
            self.git(target, "init", "-b", "main")
            args = ("install", "--repo", str(target), "--source", str(self.source), "--client", "codex", "--asset", "agent:reviewer")
            result = self.cli(*args, "--mode", initial)
            self.assertEqual(result.returncode, 0, result.stderr)
            agent = target / ".codex/agents/reviewer.toml"
            before = agent.read_bytes(), agent.stat().st_ino, agent.stat().st_mtime_ns
            result = self.cli(*args, "--mode", following)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((agent.read_bytes(), agent.stat().st_ino, agent.stat().st_mtime_ns), before)
            self.assertEqual(self.cli("status", "--repo", str(target), "--mode", "local", "--check").returncode, 0)

    def test_tracked_local_native_config_and_different_shared_bytes_stop_whole_operation(self):
        self.maintained_source()
        config = self.target / ".gemini/settings.json"
        config.parent.mkdir()
        config.write_bytes(b'{"personal":true}\n')
        self.git(self.target, "add", ".")
        before = self.files(), self.target.joinpath(".git/info/exclude").read_bytes(), self.target.joinpath(".git/index").read_bytes()
        result = self.cli("install", "--mode", "local", "--source", str(self.source), "--client", "gemini", "--asset", "hook:required-skills")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_LOCAL_TRACKED_CONFLICT", result.stderr)
        self.assertEqual((self.files(), self.target.joinpath(".git/info/exclude").read_bytes(), self.target.joinpath(".git/index").read_bytes()), before)
        self.assertEqual(self.install().returncode, 0)
        self.source.joinpath("skills/caveman/SKILL.md").write_bytes(SKILL + b"changed\n")
        self.save_catalog(self.catalog())
        before = self.files(), self.target.joinpath(".git/info/exclude").read_bytes()
        result = self.install("--mode", "local")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_CONFLICT", result.stderr)
        self.assertEqual((self.files(), self.target.joinpath(".git/info/exclude").read_bytes()), before)

    def test_explicit_team_install_promotes_local_files_without_hiding_team_payload(self):
        self.assertEqual(self.install("--mode", "local").returncode, 0)
        before = self.target.joinpath(".agents/skills/caveman/SKILL.md").stat().st_ino
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.target.joinpath(".agents/skills/caveman/SKILL.md").stat().st_ino, before)
        self.assertIn(".agents/skills/caveman/SKILL.md", self.git(self.target, "status", "--porcelain", "--untracked-files=all"))
        local = json.loads(self.target.joinpath(".agent-assets/local/lock.json").read_bytes())
        team = json.loads(self.target.joinpath(".agent-assets/selection.json").read_bytes())
        self.assertEqual(local["items"][0]["borrowed_from"], team["installation_id"])
        self.assertNotIn(".agents/skills/caveman/SKILL.md", local["excludes"])
        self.assertEqual(self.cli("status", "--mode", "local", "--check").returncode, 0)


    def test_selected_rtk_prerequisite_is_checked_without_personal_configuration(self):
        tools = self.root / "tools"
        tools.mkdir()
        (tools / "git").symlink_to(shutil.which("git"))
        rtk = tools / "rtk"
        marker = self.root / "rtk invoked"
        rtk.write_text('#!/bin/sh\nprintf invoked >> "' + str(marker) + '"\nprintf "rtk 0.49.0\\n"\n')
        rtk.chmod(0o755)
        env = {**os.environ, "PATH": str(tools)}
        command = [sys.executable, str(SCRIPT), "install", "--repo", str(self.target), "--source", str(self.source), "--client", "codex", "--asset", "skill:caveman"]
        result = subprocess.run(command, env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists())
        catalog = self.catalog()
        catalog["assets"]["skill:caveman"]["runtime"] = ["rtk"]
        self.save_catalog(catalog)
        before = self.files()
        result = subprocess.run(command, env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_PREREQUISITE_MISSING", result.stderr)
        self.assertIn("configure-rtk.py", result.stderr)
        self.assertEqual(self.files(), before)
        self.assertTrue(marker.exists())


    def test_forged_local_excludes_and_other_scope_ownership_refuse_without_writes(self):
        self.assertEqual(self.install("--mode", "local").returncode, 0)
        lock_path = self.target / ".agent-assets/local/lock.json"
        original = lock_path.read_bytes()
        lock = json.loads(original)
        lock["excludes"].append(".agents/")
        lock_path.write_text(json.dumps(lock))
        before = self.files(), self.target.joinpath(".git/info/exclude").read_bytes()
        result = self.cli("update", "--mode", "local")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_RECORD_INVALID", result.stderr)
        self.assertEqual((self.files(), self.target.joinpath(".git/info/exclude").read_bytes()), before)
        lock = json.loads(original)
        lock["items"][0]["baseline_digest"] = "0" * 64
        lock_path.write_text(json.dumps(lock))
        before = self.files(), self.target.joinpath(".git/info/exclude").read_bytes()
        result = self.install()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_SOURCE_MISMATCH", result.stderr)
        self.assertEqual((self.files(), self.target.joinpath(".git/info/exclude").read_bytes()), before)


    def test_personal_adopts_known_legacy_config_and_preserves_unowned_values_and_backups(self):
        self.maintained_source()
        home = self.root / "legacy home"
        config = home / ".codex/hooks.json"
        config.parent.mkdir(parents=True)
        value = json.loads(self.source.joinpath(".codex/global-hooks.json").read_bytes())
        value["personal"] = {"keep": True}
        config.write_text(json.dumps(value))
        config.chmod(0o600)
        backup = config.with_suffix(".json.bak")
        backup.write_bytes(b"old preserved backup\n")
        args = ("install", "--scope", "user", "--home", str(home), "--source", str(self.source), "--client", "codex",
                "--asset", "hook:required-skills", "--asset", "hook:tool-guard", "--asset", "hook:scan-secrets", "--adopt")
        original = config.read_bytes()
        edited = json.loads(original)
        edited["hooks"]["Stop"][0]["hooks"][0]["timeout"] = 11
        config.write_text(json.dumps(edited))
        result = self.cli(*args)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse((home / ".agent-assets").exists())
        self.assertFalse((home / ".agents").exists())
        config.write_bytes(original)
        result = self.cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(config.read_bytes(), original)
        self.assertEqual(backup.read_bytes(), b"old preserved backup\n")
        result = self.cli("status", "--scope", "user", "--home", str(home), "--check")
        self.assertEqual(result.returncode, 0, result.stderr)


    def test_personal_codex_override_requires_explicit_matching_authority(self):
        self.source.joinpath("agents").mkdir()
        self.source.joinpath("agents/reviewer.md").write_text('---\nname: reviewer\ndescription: Review code\n---\nReview carefully.\n')
        catalog = self.catalog()
        catalog["assets"]["agent:reviewer"] = {"source_paths": [{"path": "agents/reviewer.md", "content": "text", "line_endings": "lf"}],
            "requires": [], "clients": ["codex"], "os": [], "runtime": [], "rendering": "agent"}
        self.save_catalog(catalog)
        home, override = self.root / "personal", self.root / "external codex"
        home.mkdir()
        args = ("--scope", "user", "--home", str(home), "--codex-home", str(override))
        result = self.cli("install", *args, "--source", str(self.source), "--client", "codex", "--asset", "agent:reviewer")
        self.assertEqual(result.returncode, 0, result.stderr)
        path = override / "agents/reviewer.toml"
        self.assertIn(b'Review carefully.', path.read_bytes())
        self.assertFalse((home / ".codex/agents").exists())
        path.unlink()
        result = self.cli("restore", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(path.is_file())
        before = path.read_bytes()
        result = self.cli("update", "--scope", "user", "--home", str(home))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ASSET_RECORD_INVALID", result.stderr)
        self.assertEqual(path.read_bytes(), before)


    def test_personal_adopts_exact_legacy_agents_and_rejects_edited_unknown_and_hardlinked_copies(self):
        self.source.joinpath("agents").mkdir()
        self.source.joinpath("agents/reviewer.md").write_text('---\nname: reviewer\ndescription: Review code\n---\nReview carefully.\n')
        catalog = self.catalog()
        catalog["assets"]["agent:reviewer"] = {"source_paths": [{"path": "agents/reviewer.md", "content": "text", "line_endings": "lf"}],
            "requires": [], "clients": ["codex", "copilot", "gemini"], "os": [], "runtime": [], "rendering": "agent"}
        self.save_catalog(catalog)
        home = self.root / "adopt home"
        home.mkdir()
        result = subprocess.run([sys.executable, str(SCRIPT.with_name("install-codex-agents.py")), "--source-dir", str(self.source / "agents"),
                                 "--destination-dir", str(home / ".codex/agents")], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        path = home / ".codex/agents/reviewer.toml"
        original = path.read_bytes()
        args = ("install", "--scope", "user", "--home", str(home), "--source", str(self.source), "--client", "codex", "--asset", "agent:reviewer", "--adopt")
        path.write_bytes(original + b"# edited\n")
        result = self.cli(*args)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse((home / ".agent-assets").exists())
        path.write_bytes(original)
        external = self.root / "linked copy"
        os.link(path, external)
        result = self.cli(*args)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse((home / ".agent-assets").exists())
        path.unlink()
        path.write_bytes(original)
        result = self.cli(*args, "--revision", "unknown")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((home / ".agent-assets").exists())
        result = self.cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((home / ".codex/agents/.skills-repo-agents.json").is_file())


    def test_wrappers_forward_scopes_and_saved_selection_refuses_tampering(self):
        for executable, script in (("bash", "install.sh"), ("pwsh", "install.ps1")):
            with self.subTest(wrapper=script):
                home = self.root / (script + " home")
                home.mkdir()
                env = {**os.environ, "HOME": str(home), "USERPROFILE": str(home),
                       **{name: str(self.root / (script + name)) for name in ("XDG_CACHE_HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME")}}
                command = [executable, *(["-NoProfile", "-File"] if executable == "pwsh" else []), str(SCRIPT.with_name(script))]
                result = subprocess.run([*command, "install", "--scope", "user", "--home", str(home), "--source", str(self.source), "--client", "codex", "--asset", "skill:caveman"],
                                        env=env, cwd=self.target, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                path = home / ".agents/skills/caveman/SKILL.md"
                path.unlink()
                result = subprocess.run(command, env=env, cwd=self.target, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(path.read_bytes(), SKILL)
                lock_path = home / ".agent-assets/lock.json"
                lock = json.loads(lock_path.read_bytes())
                lock["items"][0]["baseline_digest"] = "0" * 64
                lock_path.write_text(json.dumps(lock))
                before = {p.relative_to(home).as_posix(): p.read_bytes() for p in home.rglob("*") if p.is_file()}
                result = subprocess.run(command, env=env, cwd=self.target, text=True, capture_output=True)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("ASSET_SOURCE_MISMATCH", result.stderr)
                self.assertEqual({p.relative_to(home).as_posix(): p.read_bytes() for p in home.rglob("*") if p.is_file()}, before)

    def test_personal_hooks_use_native_home_paths_and_run_without_git_home(self):
        self.maintained_source()
        home = self.root / "personal home"
        home.mkdir()
        result = self.cli("install", "--scope", "user", "--home", str(home), "--source", str(self.source),
                          "--client", "codex", "--client", "copilot", "--client", "gemini", "--asset", "hook:tool-guard")
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in (".codex/hooks/tool-guard.py", ".copilot/hooks/scripts/tool-guard.py", ".gemini/hooks/scripts/tool-guard.py"):
            self.assertTrue(home.joinpath(name).is_file(), name)
        self.assertFalse(home.joinpath(".github").exists())
        for provider, path, event in (("codex", ".codex/hooks.json", "PreToolUse"), ("copilot", ".copilot/hooks/hooks.json", "preToolUse"), ("gemini", ".gemini/settings.json", "BeforeTool")):
            config = json.loads(home.joinpath(path).read_bytes())
            handler = config["hooks"][event][0] if provider == "copilot" else config["hooks"][event][0]["hooks"][0]
            command = handler.get("bash", handler.get("command"))
            allowed = subprocess.run(["bash", "-c", command], input=json.dumps({"tool_name": "Bash" if provider != "gemini" else "run_shell_command", "tool_input": {"command": "echo fixture"}, "cwd": str(self.target)}),
                                     env={**os.environ, "HOME": str(home), "USERPROFILE": str(home)}, cwd=self.target,
                                     text=True, capture_output=True, timeout=20)
            self.assertEqual(allowed.returncode, 0, provider + allowed.stderr)
            response = json.loads(allowed.stdout.splitlines()[-1])
            decision = (response.get("permissionDecision") or response.get("decision")
                        or response.get("hookSpecificOutput", {}).get("permissionDecision")
                        or ("allow" if response == {} else None))
            self.assertEqual(decision, "allow", provider + allowed.stdout)
            result = subprocess.run(["bash", "-c", command], input=json.dumps({"tool_name": "Bash" if provider != "gemini" else "run_shell_command", "tool_input": {"command": "r" + "m -rf /"}, "cwd": str(self.target)}),
                                    env={**os.environ, "HOME": str(home), "USERPROFILE": str(home)}, cwd=self.target,
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, provider + result.stderr)
            self.assertIn("deny", result.stdout)

    def test_personal_saved_selection_update_restore_and_verified_adoption(self):
        home = self.root / "personal home"
        home.mkdir()
        existing = home / ".agents/skills/caveman/SKILL.md"
        existing.parent.mkdir(parents=True)
        existing.write_bytes(SKILL)
        unrelated = home / "private-token-file"
        unrelated.write_bytes(b"preserve unrelated personal state\n")
        args = ("--scope", "user", "--home", str(home))
        result = self.cli("install", *args, "--source", str(self.source), "--client", "codex", "--asset", "skill:caveman")
        self.assertEqual(result.returncode, 1, result.stderr)
        result = self.cli("install", *args, "--source", str(self.source), "--client", "codex", "--asset", "skill:caveman", "--adopt")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(unrelated.read_bytes(), b"preserve unrelated personal state\n")
        self.assertFalse((home / ".gitattributes").exists())
        result = self.cli("status", *args, "--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        existing.unlink()
        result = self.cli("restore", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(existing.read_bytes(), SKILL)
        self.source.joinpath("skills/caveman/SKILL.md").write_bytes(SKILL + b"Updated upstream.\n")
        self.git(self.source, "add", ".")
        self.git(self.source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-m", "update")
        result = self.cli("update", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(existing.read_bytes(), SKILL + b"Updated upstream.\n")

    def test_team_local_share_and_prune_keeps_remaining_requirement(self):
        self.assertEqual(self.install().returncode, 0)
        before = self.target.joinpath(".agents/skills/caveman/SKILL.md").stat().st_mtime_ns
        result = self.install("--mode", "local")
        self.assertEqual(result.returncode, 0, result.stderr)
        lock = json.loads(self.target.joinpath(".agent-assets/local/lock.json").read_bytes())
        self.assertEqual(lock["items"][0]["borrowed_from"], json.loads(self.target.joinpath(".agent-assets/selection.json").read_bytes())["installation_id"])
        self.assertEqual(self.target.joinpath(".agents/skills/caveman/SKILL.md").stat().st_mtime_ns, before)
        path = self.source / "skills/other/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"Other selected skill.\n")
        catalog_path = self.source / "distribution/catalog.json"
        catalog = json.loads(catalog_path.read_bytes())
        catalog["assets"]["skill:other"] = {**catalog["assets"]["skill:caveman"], "source_paths": [{"path": "skills/other/SKILL.md", "content": "text", "line_endings": "lf"}]}
        catalog_path.write_text(json.dumps(catalog))
        self.git(self.source, "add", ".")
        self.git(self.source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-m", "other")
        result = self.cli("install", "--source", str(self.source), "--client", "codex", "--asset", "skill:other")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.target.joinpath(".agents/skills/caveman/SKILL.md").read_bytes(), SKILL)
        self.assertNotIn(".agents/skills/caveman/SKILL.md", self.git(self.target, "status", "--porcelain", "--untracked-files=all"))
        result = self.cli("status", "--mode", "local", "--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.cli("install", "--source", str(self.source), "--mode", "local", "--client", "codex", "--asset", "skill:other")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.target.joinpath(".agents/skills/caveman/SKILL.md").exists())
        self.assertTrue(self.target.joinpath(".agents/skills/other/SKILL.md").exists())

    def test_local_tracked_payload_refuses_before_any_target_or_exclude_change(self):
        path = self.target / ".agents/skills/caveman/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_bytes(SKILL)
        self.git(self.target, "add", ".")
        before = self.files(), (self.target / ".git/info/exclude").read_bytes(), (self.target / ".git/index").read_bytes()
        result = self.install("--mode", "local")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_LOCAL_TRACKED_CONFLICT", result.stderr)
        self.assertEqual((self.files(), (self.target / ".git/info/exclude").read_bytes(), (self.target / ".git/index").read_bytes()), before)

    def test_local_install_in_linked_worktree_preserves_other_worktree_excludes(self):
        self.target.joinpath("tracked.txt").write_text("baseline\n")
        self.git(self.target, "add", ".")
        self.git(self.target, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-m", "target")
        result = self.install("--mode", "local")
        self.assertEqual(result.returncode, 0, result.stderr)
        exclude = self.target / ".git/info/exclude"
        before = exclude.read_bytes()
        linked = self.root / "linked worktree"
        self.git(self.target, "worktree", "add", "-b", "linked", str(linked))
        result = self.cli("install", "--repo", str(linked), "--source", str(self.source), "--client", "codex", "--asset", "skill:caveman", "--mode", "local")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(exclude.read_bytes(), before)
        self.assertEqual(self.git(linked, "status", "--porcelain", "--untracked-files=all"), "")
        self.assertEqual(self.git(self.target, "status", "--porcelain", "--untracked-files=all"), "")
        before = self.files(), exclude.read_bytes()
        result = self.install()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ASSET_CONFLICT", result.stderr)
        self.assertEqual((self.files(), exclude.read_bytes()), before)
        self.assertEqual(self.git(linked, "status", "--porcelain", "--untracked-files=all"), "")

    def test_local_install_is_private_and_preserves_git_metadata_and_indexes(self):
        exclude = self.target / ".git/info/exclude"
        original = exclude.read_bytes() + b"\n# personal rule\nnotes.txt\n"
        exclude.write_bytes(original)
        source_index = (self.source / ".git/index").read_bytes()
        result = self.install("--mode", "local")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.target.joinpath(".agents/skills/caveman/SKILL.md").read_bytes(), SKILL)
        self.assertFalse(self.target.joinpath(".gitattributes").exists())
        self.assertEqual(self.git(self.target, "status", "--porcelain", "--untracked-files=all"), "")
        self.assertEqual((self.source / ".git/index").read_bytes(), source_index)
        self.assertFalse(self.target.joinpath(".git/index").exists())
        self.assertTrue(exclude.read_bytes().startswith(original))
        self.assertIn(b"/.agents/skills/caveman/SKILL.md\n", exclude.read_bytes())
        self.assertNotIn(b"/.agents/\n", exclude.read_bytes())
        before = self.files(), exclude.read_bytes()
        self.assertEqual(self.install("--mode", "local").returncode, 0)
        self.assertEqual((self.files(), exclude.read_bytes()), before)
        checked = self.cli("status", "--mode", "local", "--check")
        self.assertEqual(checked.returncode, 0, checked.stderr)


class CloneTests(Fixture):
    """Audit committed payloads before repair, including on read-only Windows."""

    catalog = SelectionTests.catalog
    save_catalog = SelectionTests.save_catalog
    maintained_source = ProviderTests.maintained_source

    def tearDown(self):
        # Native hook maintenance is detached and may finish opening its SQLite
        # files just after the launcher exits. Allow that real process to close.
        deadline = time.monotonic() + 5
        while True:
            try:
                super().tearDown()
                return
            except OSError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.05)

    def prepare_bundle(self, bundle):
        self.assertEqual(os.name, "posix", "Fixture installation requires the safe POSIX writer")
        self.maintained_source()
        catalog = self.catalog()
        specs = catalog["assets"]["skill:caveman"]["source_paths"]
        for name, data, content, endings in (
            ("literal.txt", b"first\nsecond\n", "text", "lf"),
            ("literal.cmd", b"@echo off\r\necho fixture\r\n", "text", "crlf"),
            ("literal.bin", b"\x00\xff\r\n\x80\n", "binary", "none"),
        ):
            path = "skills/caveman/" + name
            self.source.joinpath(path).write_bytes(data)
            specs.append({"path": path, "content": content, "line_endings": endings})
        self.save_catalog(catalog)
        result = self.cli("install", "--repo", str(self.target), "--source", self.source.as_uri(),
                          "--client", "codex", "--client", "copilot", "--client", "gemini",
                          "--asset", "hook:required-skills")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.git(self.target, "add", ".")
        self.git(self.target, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "committed payload")
        self.git(self.target, "bundle", "create", str(bundle), "HEAD")
        shutil.rmtree(self.source)

    def bundle(self):
        provided = os.environ.get("AGENT_ASSETS_CLONE_BUNDLE")
        if provided:
            bundle = Path(provided).resolve()
            self.assertTrue(bundle.is_file(), "The committed CI payload bundle is required")
            return bundle
        bundle = self.root / "payload.bundle"
        self.prepare_bundle(bundle)
        return bundle

    def clone(self, bundle, autocrlf):
        clone = self.root / ("relocated 'quoted' ü & payload " + autocrlf)
        self.git(self.root, "-c", "core.autocrlf=" + autocrlf, "clone", str(bundle), str(clone))
        self.git(clone, "config", "core.autocrlf", autocrlf)
        return clone

    def audit(self, clone, expected=0):
        before = {p.relative_to(clone).as_posix(): (p.stat().st_mtime_ns, p.read_bytes())
                  for p in clone.rglob("*") if p.is_file()}
        result = self.cli("status", "--repo", str(clone), "--check", "--format", "json")
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.assertEqual({p.relative_to(clone).as_posix(): (p.stat().st_mtime_ns, p.read_bytes())
                          for p in clone.rglob("*") if p.is_file()}, before)
        return json.loads(result.stdout)

    def test_committed_clone_audits_literal_bytes_then_runs_relocated_launchers(self):
        bundle = self.bundle()
        for autocrlf in ("true", "false"):
            with self.subTest(autocrlf=autocrlf):
                clone = self.clone(bundle, autocrlf)
                self.assertTrue(self.audit(clone)["verification"]["passed"])
                expected = {"SKILL.md": SKILL, "literal.txt": b"first\nsecond\n",
                            "literal.cmd": b"@echo off\r\necho fixture\r\n", "literal.bin": b"\x00\xff\r\n\x80\n"}
                lock = json.loads(clone.joinpath(".agent-assets/lock.json").read_bytes())
                recorded = {item["destination"]: item["baseline_digest"] for item in lock["items"]}
                for name, data in expected.items():
                    path = ".agents/skills/caveman/" + name
                    self.assertEqual(clone.joinpath(path).read_bytes(), data)
                    self.assertEqual(recorded[path], hashlib.sha256(data).hexdigest())
                self.run_launchers(clone, autocrlf)
                self.assertEqual(self.git(clone, "status", "--porcelain"), "")

    def run_launchers(self, clone, label):
        nested = clone / "nested directory"
        nested.mkdir()
        home, state = self.root / ("empty home " + label), self.root / ("state " + label)
        home.mkdir()
        env = {**os.environ, "HOME": str(home), "USERPROFILE": str(home),
               "AGENT_ASSETS_STATE_DIR": str(state), "PYTHONDONTWRITEBYTECODE": "1",
               "PATH": str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"]}
        for provider, path, event in (("codex", ".codex/hooks.json", "SessionStart"),
                                      ("copilot", ".github/hooks/agent-assets.json", "sessionStart"),
                                      ("gemini", ".gemini/settings.json", "SessionStart")):
            config = json.loads(clone.joinpath(path).read_bytes())
            entry = config["hooks"][event][-1]
            hook = entry if provider == "copilot" else entry["hooks"][0]
            if os.name == "nt":
                command = hook.get("powershell", hook.get("commandWindows", hook.get("command")))
                shell = ["pwsh", "-NoProfile", "-Command", command] if provider == "copilot" else ["cmd", "/d", "/s", "/c", command]
            else:
                command = hook.get("bash", hook.get("command"))
                shell = ["bash", "-c", command]
            payload = {"hook_event_name": event, "source": "startup", "session_id": "clone-fixture", "cwd": str(nested)}
            result = subprocess.run(shell, input=json.dumps(payload), text=True, capture_output=True,
                                    cwd=nested, env=env, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            response = json.loads(result.stdout.splitlines()[-1])
            context = response.get("additionalContext") or response.get("hookSpecificOutput", {}).get("additionalContext")
            self.assertIn("Fixture skill.", context or "", result.stdout + result.stderr)
            self.assertTrue(any(state.joinpath(provider).rglob("audit.log")))
        self.assertEqual(list(home.iterdir()), [])

    def test_committed_damage_fails_offline_audit_without_repair(self):
        bundle = self.bundle()
        for autocrlf in ("true", "false"):
            with self.subTest(autocrlf=autocrlf):
                clone = self.clone(bundle, autocrlf)
                path = ".agents/skills/caveman/literal.bin"
                clone.joinpath(path).write_bytes(b"intentional committed damage\x00")
                self.git(clone, "add", path)
                self.git(clone, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                         "-c", "commit.gpgsign=false", "commit", "-m", "damaged payload")
                report = self.audit(clone, expected=1)
                self.assertIn(path, [entry["destination"] for entry in report["verification"]["drift"]])
                self.assertEqual(self.git(clone, "status", "--porcelain"), "")


class WindowsBoundaryTests(Fixture):
    """Native refusal evidence only; this does not certify a Windows writer."""

    fingerprint = SelectionTests.fingerprint

    def setUp(self):
        self.assertEqual(os.name, "nt", "windows-boundary requires actual native Windows")
        super().setUp()

    def test_native_install_and_powershell_refuse_before_mutation(self):
        before = self.fingerprint()
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ASSET_PLATFORM_UNSUPPORTED", result.stderr)
        self.assertEqual(self.fingerprint(), before)
        result = subprocess.run(["pwsh", "-NoProfile", "-File", str(SCRIPT.with_name("install.ps1")),
                                 "install", "--repo", str(self.target), "--source", str(self.source),
                                 "--client", "codex", "--asset", "skill:caveman"],
                                text=True, capture_output=True, cwd=self.target, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ASSET_PLATFORM_UNSUPPORTED", result.stderr)
        self.assertEqual(self.fingerprint(), before)

    def test_native_pending_recovery_preserves_evidence_and_strict_check_never_recovers(self):
        journal = self.target / ".git/agent-assets-journal.json"
        journal.write_bytes(b'{"interrupted":"unverified Windows operation"}\n')
        before = self.fingerprint()
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ASSET_PLATFORM_UNSUPPORTED", result.stderr)
        self.assertEqual(self.fingerprint(), before)
        result = self.cli("status", "--repo", str(self.target), "--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ASSET_INTERRUPTED", result.stderr)
        self.assertEqual(self.fingerprint(), before)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    groups = {"team-install": TeamInstallTests, "selection": SelectionTests, "lifecycle": LifecycleTests,
              "providers": ProviderTests, "scopes": ScopeTests, "clone": CloneTests,
              "windows-boundary": WindowsBoundaryTests}
    parser.add_argument("--group", choices=tuple(groups))
    parser.add_argument("--export-clone-bundle", type=Path, help="Create a committed POSIX-installed payload for cross-OS read-only checks")
    args, remaining = parser.parse_known_args()
    if args.export_clone_bundle:
        fixture = CloneTests()
        fixture.setUp()
        try:
            fixture.prepare_bundle(args.export_clone_bundle.resolve())
        finally:
            fixture.tearDown()
        return
    selected = [groups[args.group].__name__] if args.group else [group.__name__ for name, group in groups.items()
                                                               if name != "windows-boundary" or os.name == "nt"]
    unittest.main(argv=[sys.argv[0], *selected, *remaining])


if __name__ == "__main__":
    main()
