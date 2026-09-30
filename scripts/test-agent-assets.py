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
        self.assertFalse(report["assets"]["hook:required-skills"]["installable"])
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=("team-install", "selection", "lifecycle", "providers", "scopes"))
    args, remaining = parser.parse_known_args()
    if args.group not in (None, "team-install", "selection"):
        parser.error(f"group {args.group} has no implemented cases yet")
    groups = {"team-install": TeamInstallTests, "selection": SelectionTests}
    unittest.main(argv=[sys.argv[0], *([groups[args.group].__name__] if args.group else []), *remaining])


if __name__ == "__main__":
    main()
