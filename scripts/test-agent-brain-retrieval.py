#!/usr/bin/env python3
"""Public process tests for agent-brain metadata retrieval."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CLI = Path(__file__).parents[1] / "skills" / "agent-brain" / "scripts" / "agent-brain.py"
STARTUP_ID = "11111111-1111-4111-8111-111111111111"
SOURCE_ID = "22222222-2222-4222-8222-222222222222"
DEPLOY_ID = "33333333-3333-4333-8333-333333333333"


class AgentBrainRetrievalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(prefix="agent-brain-retrieval-")
        self.repository = Path(self.temporary_directory.name)
        self.guidance = self.repository / "guidance"
        self.guidance.mkdir()
        self.config_path = self.repository / ".agents" / "context" / "config.json"
        self.config_path.parent.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_config(self, startup_id: str = STARTUP_ID) -> None:
        self.write_config_document({
            "schema_version": 1,
            "repository_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "knowledge_roots": [{"path": "guidance", "ownership": "read_only"}],
            "mapped_units": [
                {"id": STARTUP_ID, "path": "guidance/startup.md", "unit": "whole"}
            ],
            "startup": [{"id": startup_id, "loading_mode": "whole"}],
        })
        (self.guidance / "startup.md").write_text(
            "# Startup\n\nKeep mandatory startup policy available.\n", encoding="utf-8"
        )

    def write_config_document(self, config: dict[str, object]) -> None:
        self.config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    def read_config_document(self) -> dict[str, object]:
        return json.loads(self.config_path.read_text(encoding="utf-8"))

    def annotation(self, unit_id: str, *, paths: list[str], concepts: list[str]) -> str:
        return "<!-- agent-brain " + json.dumps(
            {
                "schema_version": 1,
                "id": unit_id,
                "kind": "policy",
                "status": "established",
                "applies": {"paths": paths, "concepts": concepts},
                "requires": [],
                "evidence": {},
            },
            separators=(",", ":"),
        ) + " -->\n"

    def metadata_comment(self, metadata: dict[str, object]) -> str:
        return "<!-- agent-brain " + json.dumps(metadata, separators=(",", ":")) + " -->\n"

    def record(self, unit_id: str, *, kind: str = "policy", status: str = "established",
               applies: dict[str, list[str]] | None = None, requires: list[dict[str, str]] | None = None,
               evidence: dict[str, object] | None = None) -> dict[str, object]:
        return {
            "schema_version": 1,
            "id": unit_id,
            "kind": kind,
            "status": status,
            "applies": applies or {},
            "requires": requires or [],
            "evidence": evidence or {},
        }

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), *arguments],
            cwd=self.repository,
            text=True,
            capture_output=True,
            check=False,
            env=os.environ.copy(),
            stdin=subprocess.DEVNULL,
            timeout=5,
        )

    def test_known_path_and_concept_route_before_read_only_use(self) -> None:
        self.write_config()
        source = self.guidance / "source.md"
        source.write_text(
            self.annotation(SOURCE_ID, paths=["src/**"], concepts=["python"])
            + "# Python source\n\nUse the established source policy.\n",
            encoding="utf-8",
        )
        deploy = self.guidance / "deploy.md"
        deploy.write_text(
            self.annotation(DEPLOY_ID, paths=["deploy/*"], concepts=["release"])
            + "# Deployment\n\nUse the release guidance.\n",
            encoding="utf-8",
        )

        result = self.run_cli(
            "--json", "recall", "--path", "src/main.py", "--concept", "python"
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        ids = [unit["id"] for unit in record["units"]]
        self.assertEqual(ids, [STARTUP_ID, SOURCE_ID])
        self.assertEqual(record["units"][1]["path"], "guidance/source.md")
        self.assertTrue(record["informational_only"])
        self.assertEqual(result.stderr, "")

    def test_section_inherits_defaults_and_keeps_unannotated_exception(self) -> None:
        self.write_config()
        core_id = "44444444-4444-4444-8444-444444444444"
        child_id = "55555555-5555-4555-8555-555555555555"
        defaults = {
            "schema_version": 1,
            "defaults": {
                "kind": "policy",
                "status": "established",
                "applies": {"paths": ["src/**"]},
                "requires": [],
                "evidence": {
                    "sources": [{"source": "policy.md", "revision": "r1", "note": "verified"}]
                },
            },
        }
        guide = (
            "---\ntitle: Guidance\n---\n"
            + self.metadata_comment(defaults)
            + "# Guide\n\n"
            + "## Core rules\n"
            + self.metadata_comment({"schema_version": 1, "id": core_id,
                                     "applies": {"concepts": ["core"]},
                                     "evidence": {"sources": [{
                                         "source": "policy.md", "revision": "r1",
                                         "note": "SECTION-ONLY-SENSITIVE-DETAIL",
                                     }]}})
            + "Follow the core rule.\n\n"
            + "### Exception\nPreserve the exception for generated files.\n\n"
            + "### Child unit\n"
            + self.metadata_comment({"schema_version": 1, "id": child_id,
                                     "applies": {"concepts": ["child"]}})
            + "Child-specific guidance must remain a separate unit.\n\n"
            + "## Neighbor\nUnrelated neighbor guidance.\n"
        )
        (self.guidance / "guide.md").write_text(guide, encoding="utf-8")

        result = self.run_cli("--json", "recall", "--path", "src/main.py", "--concept", "core")

        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        core = next(unit for unit in record["units"] if unit["id"] == core_id)
        self.assertEqual(core["kind"], "policy")
        self.assertEqual(core["status"], "established")
        self.assertEqual(core["applies"]["paths"], ["src/**"])
        self.assertEqual(core["applies"]["concepts"], ["core"])
        self.assertEqual(core["evidence"], {
            "available": True,
            "sources": [{"source": "policy.md", "revision": "r1"}],
        })
        self.assertNotIn("SECTION-ONLY-SENSITIVE-DETAIL", result.stdout)
        artifact = next(item for item in record["artifacts"] if item["id"] == core_id)
        self.assertEqual(artifact["applies"]["paths"], ["src/**"])
        self.assertEqual(artifact["applies"]["concepts"], ["core"])
        self.assertIn("Preserve the exception for generated files.", artifact["content"])
        self.assertNotIn("Child-specific guidance", artifact["content"])
        self.assertNotIn("SECTION-ONLY-SENSITIVE-DETAIL", artifact["content"])
        self.assertFalse(artifact["evidence_details_included"])
        self.assertEqual(artifact["content_bytes"], len(artifact["content"].encode("utf-8")))
        self.assertEqual(
            artifact["content_revision"],
            hashlib.sha256(artifact["content"].encode("utf-8")).hexdigest(),
        )
        self.assertNotIn("Unrelated neighbor guidance", artifact["content"])
        self.assertEqual(result.stderr, "")

        detailed = self.run_cli(
            "--json", "recall", "--path", "src/main.py", "--concept", "core", "--show-evidence"
        )
        detail_record = json.loads(detailed.stdout)
        detail_core = next(unit for unit in detail_record["units"] if unit["id"] == core_id)
        self.assertEqual(detail_core["evidence"]["sources"][0]["note"], "SECTION-ONLY-SENSITIVE-DETAIL")

        human = self.run_cli("recall", "--all-guidance")
        self.assertEqual(human.returncode, 0, human.stderr)
        self.assertIn("Applies: paths=src/**; concepts=core", human.stdout)
        self.assertNotIn("SECTION-ONLY-SENSITIVE-DETAIL", human.stdout)
        self.assertEqual(human.stdout.count(f"Evidence for {core_id}:"), 1)
        self.assertEqual(human.stdout.count(f"Evidence for {child_id}:"), 1)

    def test_nested_units_partition_parent_without_dropping_later_exception(self) -> None:
        self.write_config()
        parent_id = "19191919-1919-4919-8919-191919191919"
        child_id = "20202020-2020-4020-8020-202020202020"
        (self.guidance / "nested.md").write_text(
            "# Guide\n\n## Parent\n"
            + self.metadata_comment(self.record(parent_id))
            + "Parent first rule.\n\n### Child unit\n"
            + self.metadata_comment(self.record(child_id))
            + "Child-specific rule.\n\n### Later exception\nPreserve this parent exception.\n\n## Next\nNeighbor.\n",
            encoding="utf-8",
        )

        result = self.run_cli("--json", "recall", "--all-guidance")

        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        parent = next(item for item in record["artifacts"] if item["id"] == parent_id)
        child = next(item for item in record["artifacts"] if item["id"] == child_id)
        self.assertIn("Parent first rule.", parent["content"])
        self.assertIn("Preserve this parent exception.", parent["content"])
        self.assertNotIn("Child-specific rule.", parent["content"])
        self.assertIn("Child-specific rule.", child["content"])
        self.assertNotIn("Preserve this parent exception.", child["content"])

    def test_text_search_keeps_universal_policy_and_routes_matching_facts(self) -> None:
        self.write_config()
        policy_id = "66666666-6666-4666-8666-666666666666"
        fact_id = "77777777-7777-4777-8777-777777777777"
        unrelated_id = "88888888-8888-4888-8888-888888888888"
        (self.guidance / "policy.md").write_text(
            self.metadata_comment(self.record(policy_id)) + "# Manifest rule\nDo not change the package manifest.\n",
            encoding="utf-8",
        )
        (self.guidance / "fact.md").write_text(
            self.metadata_comment(self.record(fact_id, kind="fact"))
            + "# Selenium runner\nThe selenium runner writes its trace beneath the fixture home.\n",
            encoding="utf-8",
        )
        (self.guidance / "unrelated.md").write_text(
            self.metadata_comment(self.record(unrelated_id, kind="fact"))
            + "# Packaging\nBuild the package after editing the manifest.\n",
            encoding="utf-8",
        )

        result = self.run_cli("--json", "recall", "--query", "selenium runner")

        self.assertEqual(result.returncode, 0, result.stderr)
        ids = [unit["id"] for unit in json.loads(result.stdout)["units"]]
        self.assertEqual(ids, [STARTUP_ID, policy_id, fact_id])

    def test_code_examples_are_ignored_without_swallowing_real_annotation(self) -> None:
        self.write_config()
        unit_id = "99999999-9999-4999-8999-999999999999"
        guide = (
            "# Guide\n\n"
            "    <!-- agent-brain {not valid json} -->\n\n"
            "## Real unit\n"
            + self.metadata_comment(self.record(
                unit_id, kind="fact", applies={"concepts": ["unmatched ` tick"]}
            ))
            + "Use `literal` text as an example.\n"
        )
        (self.guidance / "guide.md").write_text(guide, encoding="utf-8")

        result = self.run_cli("--json", "recall", "--concept", "unmatched ` tick")

        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        self.assertEqual([unit["id"] for unit in record["units"]], [STARTUP_ID, unit_id])
        self.assertTrue(record["complete"])
        self.assertEqual(record["gaps"], [])

    def test_path_globs_have_segment_bounded_star_question_and_recursive_star(self) -> None:
        self.write_config()
        ids = {
            "star": "aaaaaaaa-1111-4111-8111-111111111111",
            "question": "bbbbbbbb-2222-4222-8222-222222222222",
            "recursive": "cccccccc-3333-4333-8333-333333333333",
        }
        for name, pattern in (("star", "src/*"), ("question", "src/?pp.py"),
                              ("recursive", "src/**/app.py")):
            (self.guidance / f"{name}.md").write_text(
                self.metadata_comment(self.record(ids[name], kind="fact", applies={"paths": [pattern]}))
                + f"# {name}\nGuidance for {name}.\n",
                encoding="utf-8",
            )

        root_path = self.run_cli("--json", "recall", "--path", "src/app.py")
        nested_path = self.run_cli("--json", "recall", "--path", "src/lib/app.py")
        self.assertEqual(root_path.returncode, 0, root_path.stderr)
        self.assertEqual(nested_path.returncode, 0, nested_path.stderr)
        root_ids = {unit["id"] for unit in json.loads(root_path.stdout)["units"]}
        nested_ids = {unit["id"] for unit in json.loads(nested_path.stdout)["units"]}
        self.assertEqual(root_ids, {STARTUP_ID, ids["star"], ids["question"], ids["recursive"]})
        self.assertEqual(nested_ids, {STARTUP_ID, ids["recursive"]})

    def test_duplicate_ids_and_unresolved_references_are_incomplete(self) -> None:
        self.write_config()
        repeated_id = "dddddddd-4444-4444-8444-444444444444"
        (self.guidance / "one.md").write_text(
            self.metadata_comment(self.record(repeated_id, kind="fact")) + "# One\nFirst.\n",
            encoding="utf-8",
        )
        (self.guidance / "two.md").write_text(
            self.metadata_comment(self.record(repeated_id, kind="fact")) + "# Two\nSecond.\n",
            encoding="utf-8",
        )
        unresolved_id = "eeeeeeee-5555-4555-8555-555555555555"
        missing_target = "ffffffff-6666-4666-8666-666666666666"
        (self.guidance / "reference.md").write_text(
            self.metadata_comment(self.record(
                unresolved_id, requires=[{"id": missing_target, "loading_mode": "unit"}]
            )) + "# Reference\nRequires missing guidance.\n",
            encoding="utf-8",
        )

        duplicate_result = self.run_cli("--json", "recall", "--concept", "missing")
        self.assertEqual(duplicate_result.returncode, 1)
        duplicate_record = json.loads(duplicate_result.stdout)
        self.assertFalse(duplicate_record["complete"])
        self.assertTrue(any(gap["code"] == "ABM002" for gap in duplicate_record["gaps"]))

        reference = self.run_cli("--json", "recall", "--concept", "reference")
        self.assertEqual(reference.returncode, 1)
        self.assertIn("CONTEXT_GAP", reference.stderr)
        reference_record = json.loads(reference.stdout)
        self.assertFalse(reference_record["complete"])
        self.assertTrue(any(missing_target in gap["message"] for gap in reference_record["gaps"]))

    def test_stable_id_survives_move_while_path_bound_input_revision_changes(self) -> None:
        self.write_config()
        moved_id = "12121212-1212-4212-8212-121212121212"
        old_path = self.guidance / "before.md"
        old_path.write_text(
            self.metadata_comment(self.record(moved_id, kind="fact", applies={"concepts": ["move"]}))
            + "# Stable guidance\nSame content.\n",
            encoding="utf-8",
        )
        before = self.run_cli("--json", "recall", "--concept", "move")
        old_path.rename(self.guidance / "after.md")
        after = self.run_cli("--json", "recall", "--concept", "move")
        self.assertEqual(before.returncode, 0, before.stderr)
        self.assertEqual(after.returncode, 0, after.stderr)
        old_unit = next(unit for unit in json.loads(before.stdout)["units"] if unit["id"] == moved_id)
        new_unit = next(unit for unit in json.loads(after.stdout)["units"] if unit["id"] == moved_id)
        self.assertEqual(old_unit["content_revision"], new_unit["content_revision"])
        self.assertNotEqual(old_unit["input_revision"], new_unit["input_revision"])
        self.assertEqual(new_unit["path"], "guidance/after.md")

    def test_unavailable_mapped_artifact_is_reported_as_incomplete(self) -> None:
        self.write_config()
        startup = self.read_config_document()
        startup["mapped_units"] = [
            {"id": STARTUP_ID, "path": "guidance/missing.md", "unit": "whole"}
        ]
        self.write_config_document(startup)

        result = self.run_cli("--json", "recall")

        self.assertEqual(result.returncode, 1)
        record = json.loads(result.stdout)
        self.assertFalse(record["complete"])
        self.assertTrue(any(gap["code"] == "ABM004" for gap in record["gaps"]))

    def test_malformed_mapped_record_keeps_structured_usage_error(self) -> None:
        self.write_config()
        config = self.read_config_document()
        config["mapped_units"] = [{}]
        self.write_config_document(config)

        result = self.run_cli("--json", "recall")

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        record = json.loads(result.stdout)
        self.assertEqual(record["error"]["code"], "CONFIGURATION_INVALID")
        self.assertIn("mapped_units[0] is missing field(s)", record["error"]["cause"])
        self.assertIn("CONFIGURATION_INVALID", result.stderr)

    def test_duplicate_document_selector_is_rejected(self) -> None:
        self.write_config()
        config = self.read_config_document()
        config["mapped_units"].append({
            "id": "35353535-3535-4535-8535-353535353535",
            "path": "guidance/startup.md",
            "selector": {"type": "document"},
            "kind": "policy",
            "status": "established",
        })
        self.write_config_document(config)

        result = self.run_cli("--json", "recall")

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        record = json.loads(result.stdout)
        self.assertEqual(record["error"]["code"], "CONFIGURATION_INVALID")
        self.assertIn("duplicate mapped document", record["error"]["cause"])

    def test_closed_output_pipe_reports_incomplete_delivery(self) -> None:
        self.write_config()
        (self.guidance / "startup.md").write_text(
            "# Large startup\n\n" + ("Required startup content.\n" * 300_000), encoding="utf-8"
        )
        process = subprocess.Popen(
            [sys.executable, str(CLI), "--json", "recall"],
            cwd=self.repository,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
        )
        assert process.stdout is not None
        assert process.stderr is not None
        try:
            self.assertEqual(process.stdout.read(1), b"{")
            process.stdout.close()
            return_code = process.wait(timeout=10)
            stderr = process.stderr.read().decode("utf-8")
        except BaseException:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=10)
            raise
        finally:
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()

        self.assertEqual(return_code, 1, stderr)
        self.assertIn("DELIVERY_INCOMPLETE", stderr)
        self.assertFalse((self.repository / ".agents/context/state").exists())

    def test_external_section_mapping_is_read_only_and_keeps_scope(self) -> None:
        self.write_config()
        external_id = "13131313-1313-4313-8313-131313131313"
        source = "# Protected notes\n\n## Protected\nKeep this policy.\n\n### Exception\nKeep this exception.\n\n## Other\nDo not deliver the neighbor.\n"
        external_path = self.guidance / "protected.md"
        external_path.write_text(source, encoding="utf-8")
        config = self.read_config_document()
        config["mapped_units"].append({
            "id": external_id,
            "path": "guidance/protected.md",
            "selector": {"type": "section", "heading": "Protected"},
            "kind": "policy",
            "status": "established",
            "applies": {"concepts": ["protected"]},
            "requires": [],
            "evidence": {"sources": [{"source": "contract.md", "revision": "r2"}]},
        })
        config["startup"].append({"id": external_id, "loading_mode": "unit"})
        self.write_config_document(config)

        result = self.run_cli("--json", "recall")

        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        external = next(unit for unit in record["units"] if unit["id"] == external_id)
        artifact = next(item for item in record["artifacts"] if item["id"] == external_id)
        self.assertEqual(external["source"], "mapping")
        self.assertEqual(external["applies"]["concepts"], ["protected"])
        self.assertIn("Keep this exception.", artifact["content"])
        self.assertNotIn("Do not deliver the neighbor.", artifact["content"])
        self.assertEqual(external_path.read_text(encoding="utf-8"), source)

    def test_whole_artifact_expands_contained_section_references_transitively(self) -> None:
        self.write_config()
        child_id = "14141414-1414-4414-8414-141414141414"
        whole_id = "15151515-1515-4515-8515-151515151515"
        contained_id = "16161616-1616-4616-8616-161616161616"
        nested_id = "17171717-1717-4717-8717-171717171717"
        (self.guidance / "startup.md").write_text(
            "# Startup\n\n## Contained policy\n"
            + self.metadata_comment(self.record(child_id, requires=[{"id": whole_id, "loading_mode": "whole"}]))
            + "Follow contained policy.\n",
            encoding="utf-8",
        )
        (self.guidance / "whole.md").write_text(
            self.metadata_comment(self.record(whole_id, kind="policy"))
            + "# Required whole artifact\n\n## Nested policy\n"
            + self.metadata_comment(self.record(
                contained_id, requires=[{"id": nested_id, "loading_mode": "unit"}]
            ))
            + "Follow nested policy.\n",
            encoding="utf-8",
        )
        (self.guidance / "nested.md").write_text(
            self.metadata_comment(self.record(nested_id, kind="fact"))
            + "# Nested reference\nPreserve the transitive required fact.\n",
            encoding="utf-8",
        )

        result = self.run_cli("--json", "recall")

        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        artifacts = record["artifacts"]
        self.assertEqual([artifact["path"] for artifact in artifacts], [
            "guidance/startup.md", "guidance/whole.md", "guidance/nested.md"
        ])
        startup_artifact = next(item for item in artifacts if item["path"] == "guidance/startup.md")
        whole_artifact = next(item for item in artifacts if item["path"] == "guidance/whole.md")
        self.assertIn(child_id, startup_artifact["contained_unit_ids"])
        self.assertIn(whole_id, whole_artifact["contained_unit_ids"])
        self.assertIn(contained_id, whole_artifact["contained_unit_ids"])
        self.assertTrue(whole_artifact["evidence_details_included"])
        self.assertEqual(
            whole_artifact["content_revision"],
            hashlib.sha256(whole_artifact["content"].encode("utf-8")).hexdigest(),
        )
        self.assertEqual(len([item for item in artifacts if item["path"] == "guidance/whole.md"]), 1)
        self.assertEqual({unit["id"] for unit in record["units"]}, {
            STARTUP_ID, child_id, whole_id, contained_id, nested_id
        })

    def test_late_whole_reference_upgrade_reopens_contained_closure(self) -> None:
        self.write_config()
        whole_id = "25252525-2525-4525-8525-252525252525"
        requiring_id = "26262626-2626-4626-8626-262626262626"
        contained_id = "27272727-2727-4727-8727-272727272727"
        nested_id = "28282828-2828-4828-8828-282828282828"
        (self.guidance / "whole-late.md").write_text(
            self.metadata_comment(self.record(whole_id))
            + "# Late whole\n\n## Contained child\n"
            + self.metadata_comment(self.record(
                contained_id,
                applies={"concepts": ["unrelated-conditional-child"]},
                requires=[{"id": nested_id, "loading_mode": "unit"}],
            ))
            + "This child is part of the whole read.\n",
            encoding="utf-8",
        )
        (self.guidance / "requiring.md").write_text(
            self.metadata_comment(self.record(
                requiring_id, requires=[{"id": whole_id, "loading_mode": "whole"}]
            ))
            + "# Requiring policy\nThe later whole read is mandatory.\n",
            encoding="utf-8",
        )
        (self.guidance / "nested-required.md").write_text(
            self.metadata_comment(self.record(nested_id, kind="fact"))
            + "# Nested dependency\nRead after the late whole upgrade.\n",
            encoding="utf-8",
        )
        config = self.read_config_document()
        config["startup"] = [
            {"id": whole_id, "loading_mode": "unit"},
            {"id": requiring_id, "loading_mode": "unit"},
        ]
        self.write_config_document(config)

        result = self.run_cli("--json", "recall")

        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        whole = next(unit for unit in record["units"] if unit["id"] == whole_id)
        self.assertEqual(whole["loading_mode"], "whole")
        paths = [artifact["path"] for artifact in record["artifacts"]]
        self.assertEqual(paths, [
            "guidance/whole-late.md", "guidance/requiring.md", "guidance/startup.md",
            "guidance/nested-required.md",
        ])
        self.assertIn(contained_id, next(item for item in record["artifacts"]
                                         if item["path"] == "guidance/whole-late.md")["contained_unit_ids"])

    def test_whole_reference_revisions_bind_unannotated_document_content(self) -> None:
        self.write_config()
        target_id = "36363636-3636-4636-8636-363636363636"
        requiring_id = "37373737-3737-4737-8737-373737373737"
        contained_id = "38383838-3838-4838-8838-383838383838"
        dependency_id = "39393939-3939-4939-8939-393939393939"
        source_path = self.guidance / "target.md"
        source_path.write_text(
            "# Target\n\n## Required section\n" + self.metadata_comment(self.record(target_id))
            + "Keep this section stable.\n\n## Dependent contained section\n"
            + self.metadata_comment(self.record(contained_id,
                requires=[{"id": dependency_id, "loading_mode": "unit"}]))
            + "This contained section depends on another file.\n\n## Unannotated neighbor\nVersion one.\n",
            encoding="utf-8",
        )
        (self.guidance / "requiring.md").write_text(
            self.metadata_comment(self.record(requiring_id,
                requires=[{"id": target_id, "loading_mode": "whole"}]))
            + "# Requiring\nRead the whole target.\n", encoding="utf-8")
        dependency_path = self.guidance / "dependency.md"
        dependency_path.write_text(
            self.metadata_comment(self.record(dependency_id, kind="fact"))
            + "# Dependency\nVersion one.\n", encoding="utf-8")
        config = self.read_config_document()
        config["startup"] = [{"id": requiring_id, "loading_mode": "unit"}]
        self.write_config_document(config)
        before_result = self.run_cli("--json", "recall")
        self.assertEqual(before_result.returncode, 0, before_result.stderr)
        before = json.loads(before_result.stdout)
        dependency_path.write_text(dependency_path.read_text(encoding="utf-8").replace(
            "Version one.", "Version two."), encoding="utf-8")
        after_result = self.run_cli("--json", "recall")
        self.assertEqual(after_result.returncode, 0, after_result.stderr)
        after = json.loads(after_result.stdout)
        before_target = next(item for item in before["artifacts"] if item["path"] == "guidance/target.md")
        after_target = next(item for item in after["artifacts"] if item["path"] == "guidance/target.md")
        before_requiring = next(item for item in before["units"] if item["id"] == requiring_id)
        after_requiring = next(item for item in after["units"] if item["id"] == requiring_id)
        self.assertNotEqual(before_target["input_revision"], after_target["input_revision"])
        self.assertEqual(before_target["content_revision"], after_target["content_revision"])
        self.assertNotEqual(before_requiring["input_revision"], after_requiring["input_revision"])
        config["startup"] = [
            {"id": requiring_id, "loading_mode": "unit"},
            {"id": contained_id, "loading_mode": "unit"},
        ]
        self.write_config_document(config)
        first_order = self.run_cli("--json", "recall")
        config["startup"].reverse()
        self.write_config_document(config)
        second_order = self.run_cli("--json", "recall")
        self.assertEqual(first_order.returncode, 0, first_order.stderr)
        self.assertEqual(second_order.returncode, 0, second_order.stderr)
        first_revision = next(item for item in json.loads(first_order.stdout)["units"]
                              if item["id"] == requiring_id)["input_revision"]
        second_revision = next(item for item in json.loads(second_order.stdout)["units"]
                               if item["id"] == requiring_id)["input_revision"]
        self.assertEqual(first_revision, second_revision)
        neighbor_before = json.loads(second_order.stdout)
        source_path.write_text(source_path.read_text(encoding="utf-8").replace(
            "Version one.", "Version two."), encoding="utf-8")
        neighbor_result = self.run_cli("--json", "recall")
        self.assertEqual(neighbor_result.returncode, 0, neighbor_result.stderr)
        neighbor_after = json.loads(neighbor_result.stdout)
        whole_before = next(item for item in neighbor_before["artifacts"]
                            if item["path"] == "guidance/target.md")
        whole_after = next(item for item in neighbor_after["artifacts"]
                           if item["path"] == "guidance/target.md")
        requiring_after = next(item for item in neighbor_after["units"] if item["id"] == requiring_id)
        self.assertNotEqual(whole_before["input_revision"], whole_after["input_revision"])
        self.assertNotEqual(second_revision, requiring_after["input_revision"])
        self.assertNotEqual(whole_before["content_revision"], whole_after["content_revision"])

    def test_duplicate_annotation_ids_inside_whole_read_are_structured_gaps(self) -> None:
        self.write_config()
        duplicate_id = "40404040-4040-4040-8040-404040404040"
        (self.guidance / "startup.md").write_text(
            "# Startup\n\n## First\n" + self.metadata_comment(self.record(duplicate_id))
            + "First section.\n\n## Second\n" + self.metadata_comment(self.record(duplicate_id))
            + "Second section.\n", encoding="utf-8")

        result = self.run_cli("--json", "recall")

        self.assertEqual(result.returncode, 1, result.stderr)
        record = json.loads(result.stdout)
        self.assertFalse(record["complete"])
        self.assertTrue(any(gap["code"] == "ABM002" for gap in record["gaps"]))

    def test_investigated_candidate_still_cannot_satisfy_required_policy(self) -> None:
        self.write_config()
        candidate_id = "29292929-2929-4929-8929-292929292929"
        policy_id = "30303030-3030-4030-8030-303030303030"
        (self.guidance / "candidate-target.md").write_text(
            self.metadata_comment(self.record(candidate_id, kind="policy", status="candidate",
                                              applies={"concepts": ["candidate-target"]}))
            + "# Candidate target\nThis remains a proposal.\n",
            encoding="utf-8",
        )
        (self.guidance / "established.md").write_text(
            self.metadata_comment(self.record(
                policy_id, requires=[{"id": candidate_id, "loading_mode": "unit"}],
                applies={"concepts": ["established-policy"]},
            ))
            + "# Established policy\nA candidate cannot satisfy this.\n",
            encoding="utf-8",
        )
        config = self.read_config_document()
        config["startup"] = [{"id": candidate_id, "loading_mode": "unit"}]
        self.write_config_document(config)

        result = self.run_cli(
            "--json", "recall", "--concept", "established-policy", "--investigate"
        )

        self.assertEqual(result.returncode, 1)
        record = json.loads(result.stdout)
        self.assertFalse(record["complete"])
        self.assertIn(candidate_id, {unit["id"] for unit in record["units"]})
        self.assertTrue(any(
            gap["path"] == "guidance/established.md"
            and "cannot satisfy mandatory established guidance" in gap["message"]
            for gap in record["gaps"]
        ))

    def test_candidate_cannot_satisfy_startup_without_investigation(self) -> None:
        self.write_config()
        candidate_id = "18181818-1818-4818-8818-181818181818"
        (self.guidance / "candidate.md").write_text(
            self.metadata_comment(self.record(candidate_id, kind="policy", status="candidate"))
            + "# Candidate rule\nThis rule is not established.\n",
            encoding="utf-8",
        )
        config = self.read_config_document()
        config["startup"] = [{"id": candidate_id, "loading_mode": "unit"}]
        self.write_config_document(config)

        ordinary = self.run_cli("--json", "recall")
        investigated = self.run_cli("--json", "recall", "--investigate")

        self.assertEqual(ordinary.returncode, 1)
        ordinary_record = json.loads(ordinary.stdout)
        self.assertFalse(ordinary_record["complete"])
        self.assertNotIn(candidate_id, {unit["id"] for unit in ordinary_record["units"]})
        self.assertTrue(any("candidate" in gap["message"] for gap in ordinary_record["gaps"]))
        self.assertEqual(investigated.returncode, 1)
        candidate = next(unit for unit in json.loads(investigated.stdout)["units"] if unit["id"] == candidate_id)
        self.assertEqual(candidate["status"], "candidate")

    def test_unknown_task_shows_startup_and_universal_policy_only(self) -> None:
        self.write_config()
        universal_id = "23232323-2323-4323-8323-232323232323"
        conditional_id = "24242424-2424-4424-8424-242424242424"
        (self.guidance / "universal.md").write_text(
            self.metadata_comment(self.record(universal_id)) + "# Universal\nKeep all work read-only.\n",
            encoding="utf-8",
        )
        (self.guidance / "conditional.md").write_text(
            self.metadata_comment(self.record(conditional_id, kind="fact",
                                              applies={"concepts": ["specific-tool"]}))
            + "# Conditional fact\nThis fact is relevant only for one tool.\n",
            encoding="utf-8",
        )

        result = self.run_cli("--json", "recall")

        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        self.assertEqual(record["scope_status"], "task_unknown")
        self.assertEqual({unit["id"] for unit in record["units"]}, {STARTUP_ID, universal_id})
        self.assertTrue(record["complete"])

    def test_uncertain_selector_broadens_and_reports_incomplete_scope(self) -> None:
        self.write_config()
        known_id = "21212121-2121-4121-8121-212121212121"
        (self.guidance / "known.md").write_text(
            self.metadata_comment(self.record(known_id, kind="fact", applies={"concepts": ["known"]}))
            + "# Known fact\nRetain this broad guidance.\n",
            encoding="utf-8",
        )

        result = self.run_cli("--json", "recall", "--concept", "unindexed-concept")

        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        self.assertFalse(record["complete"])
        self.assertIn(known_id, {unit["id"] for unit in record["units"]})
        self.assertTrue(any(gap["code"] == "ABM010" for gap in record["gaps"]))

    def test_published_metadata_schema_and_example_match_runtime_parser(self) -> None:
        bundle = CLI.parents[1]
        for path in (*bundle.joinpath("schemas").glob("*.json"),
                     *bundle.joinpath("examples").glob("*.json")):
            with self.subTest(path=path.name):
                json.loads(path.read_text(encoding="utf-8"))
        schema = json.loads((bundle / "schemas/metadata-v1.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(set(schema["$defs"]), {
            "defaultsComment", "unitComment", "fields", "applies", "selectorList", "requires"
        })
        self.assertEqual(schema["$defs"]["selectorList"]["items"]["pattern"], r"\S")
        self.write_config()
        metadata = json.loads((bundle / "examples/metadata-v1.json").read_text(encoding="utf-8"))
        self.assertEqual(set(metadata), {"schema_version", "id", "kind", "status", "applies", "requires", "evidence"})
        (self.guidance / "example.md").write_text(
            self.metadata_comment(metadata) + "# Python source policy\nUse the example policy.\n",
            encoding="utf-8",
        )
        target_id = metadata["requires"][0]["id"]
        (self.guidance / "target.md").write_text(
            self.metadata_comment(self.record(target_id, kind="policy"))
            + "# Required whole policy\nRead this closure target.\n",
            encoding="utf-8",
        )

        result = self.run_cli("--json", "recall", "--path", "src/main.py", "--concept", "python")

        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        self.assertTrue(record["complete"])
        self.assertIn(target_id, {unit["id"] for unit in record["units"]})
        self.assertNotIn("Detailed support note", result.stdout)


if __name__ == "__main__":
    unittest.main()
