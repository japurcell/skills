"""Exercise the size fixture and verifier through their public CLIs."""

import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unittest
from tempfile import TemporaryDirectory


HERE = Path(__file__).parent


def prepare(case, root):
    subprocess.run([sys.executable, str(HERE / "prepare_size_case.py"), case, str(root)], check=True)


class SizeFixtureTests(unittest.TestCase):
    def test_boundary_is_utf8_bytes_with_lf(self):
        with TemporaryDirectory() as temporary:
            for case, size in [("create-exact", 12288), ("create-over", 12289), ("resume-over", 12289)]:
                root = Path(temporary) / case
                prepare(case, root)
                source = root / ("draft.md" if case.startswith("create") else "AtlasPlan.md")
                self.assertEqual(len(source.read_bytes()), size)
                self.assertLess(len(source.read_text(encoding="utf-8")), size)
                for file in root.iterdir():
                    self.assertNotIn(b"\r", file.read_bytes())

    def test_late_index_pages_need_both_local_and_cross_page_prerequisites(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary) / "case"
            prepare("large-index", root)
            source = (root / "AtlasPlan.md").read_text(encoding="utf-8")
            edges = {int(task): int(parent) for task, parent in re.findall(
                r"^- T(\d+) .*?prerequisite T(\d+)\.", source, re.MULTILINE
            )}
            self.assertEqual(set(edges), set(range(2, 193)))
            self.assertTrue(all(0 < parent < task for task, parent in edges.items()))
            for start in (97, 145, 177):
                page = {v for k, v in edges.items() if k >= start}
                self.assertGreater(len({p for p in page if p < start}), 2)
                self.assertGreater(len({p for p in page if p >= start}), 2)


class SizeVerificationTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def split(self, case):
        self.initial = self.root / "initial"
        self.run = self.root / "run"
        prepare(case, self.initial)
        shutil.copytree(self.initial, self.run)
        self.pages = self.run / "AtlasPlan"
        self.pages.mkdir()
        self.task = self.pages / "T001.md"
        self.decision = self.pages / "milestone-1.md"
        self.history = self.pages / "history.md"
        self.task.write_text("# T001: First label\nMara owns this pending assignment. Prerequisite: "
                             "[D1](milestone-1.md#catalog-encoding). Run `head -n 1 labels.txt` from the "
                             "project root; compare with `café-001`, record the result and stop.\n", encoding="utf-8")
        self.decision.write_text("# Milestone 1\nStatus: done\nAcceptance: met\n\n## Catalog encoding\n"
                                 "D1 approved UTF-8. Receipt ATLAS-7104.\n", encoding="utf-8")
        self.history.write_text("# Historical Records\nRetired catalog receipt HIST-194C.\n", encoding="utf-8")
        (self.run / "AtlasPlan.md").write_text(
            "# Atlas\n## Concrete Steps\nMara's next task is [T001](AtlasPlan/T001.md).\n"
            "## Progress\n- [ ] [milestone-2] T001\n## Plan of Work\n[Verify labels](AtlasPlan/milestone-2.md)\n"
            "## Historical Records\n[Catalog history](AtlasPlan/history.md)\n", encoding="utf-8")
        milestone = self.pages / "milestone-2.md"
        milestone.write_text("# Milestone 2\nStatus: open\nAcceptance: not met\n[T001](T001.md)\n", encoding="utf-8")
        if case == "large-index":
            rows = [s for s in (self.initial / "AtlasPlan.md").read_text(encoding="utf-8").splitlines()
                    if re.match(r"^- T\d+", s)]
            for name, records in [("early", rows[:95]), ("late", rows[95:])]:
                (self.pages / f"{name}.md").write_text(f"# {name}\n" + "\n".join(records), encoding="utf-8")
                with milestone.open("a", encoding="utf-8") as file:
                    file.write(f"[{name}]({name}.md)\n")

    def grade(self, case, previous=None):
        command = [sys.executable, str(HERE / "verify_size_case.py"), case, str(self.initial), str(self.run)]
        if previous:
            command += ["--previous", str(previous)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertIn(result.returncode, (0, 1), result.stderr)
        errors = json.loads(result.stdout)["failures"]
        self.assertEqual(bool(errors), result.returncode == 1)
        return errors

    def test_only_the_linked_assignment_and_its_cited_decision_can_supply_worker_context(self):
        self.split("resume-over")
        self.assertFalse(self.grade("resume-over"))
        task = self.task.read_text(encoding="utf-8")
        self.history.write_text(self.history.read_text(encoding="utf-8") + task, encoding="utf-8")
        self.task.write_text("# T001: First label\nMara owns this pending assignment.\n", encoding="utf-8")
        self.assertTrue(self.grade("resume-over"))
        self.task.write_text(task.replace("#catalog-encoding", "#other"), encoding="utf-8")
        with self.decision.open("a", encoding="utf-8") as file:
            file.write("\n## Other\nDoc formatting decision.\n")
        self.assertTrue(self.grade("resume-over"))

    def test_repeat_detects_duplicate_records_inside_existing_files(self):
        self.split("resume-over")
        before = self.root / "previous"
        shutil.copytree(self.run, before)
        self.assertFalse(self.grade("repeat", before))
        for path in [self.task, self.history]:
            with self.subTest(path=path.name):
                original = path.read_bytes()
                path.write_bytes(original + original)
                self.assertTrue(self.grade("repeat", before))
                path.write_bytes(original)
        with (self.pages / "milestone-2.md").open("a", encoding="utf-8") as page:
            page.write("\n" + self.task.read_text(encoding="utf-8"))
        self.assertTrue(self.grade("repeat", before))
        shutil.copyfile(before / "AtlasPlan/milestone-2.md", self.pages / "milestone-2.md")
        shutil.copyfile(self.history, self.pages / "obsolete.md")
        self.assertTrue(self.grade("repeat", before))

    def test_worker_can_use_entry_and_plain_assignment_link(self):
        self.split("resume-over")
        entry = self.run / "AtlasPlan.md"
        entry.write_text(entry.read_text(encoding="utf-8").replace(
            "## Concrete Steps\nMara's next task is [T001]", "## Release queue\n"
            "Mara's next task is T001. Use `head -n 1 labels.txt` to check `café-001`. Read the [assignment]"
        ), encoding="utf-8")
        task = self.task.read_text(encoding="utf-8").replace(
            "# T001: First label", "# First label"
        ).replace("Run `head -n 1 labels.txt` from the project root; compare with `café-001`,", "From the project root,")
        self.task.write_text(task.replace("[D1]", "[approved encoding]"), encoding="utf-8")
        self.assertFalse(self.grade("resume-over"))

    def test_unrelated_open_progress_cannot_mask_completed_first_label(self):
        self.split("resume-over")
        entry = self.run / "AtlasPlan.md"
        entry.write_text(entry.read_text(encoding="utf-8").replace(
            "- [ ] [milestone-2] T001", "- [x] [milestone-2] T001\n- [ ] [milestone-2] Other labels"
        ), encoding="utf-8")
        self.assertTrue(self.grade("resume-over"))

    def test_progress_link_cannot_rescue_a_wrong_next_assignment(self):
        self.split("resume-over")
        entry = self.run / "AtlasPlan.md"
        entry.write_text(entry.read_text(encoding="utf-8").replace(
            "next task is [T001](AtlasPlan/T001.md)", "next task is [T001](AtlasPlan/history.md)"
        ).replace("[milestone-2] T001", "[milestone-2] [T001](AtlasPlan/T001.md)"), encoding="utf-8")
        self.assertTrue(self.grade("resume-over"))

    def test_page_prerequisites_and_all_rows_must_match_source(self):
        self.split("large-index")
        late = self.pages / "late.md"
        records = late.read_text(encoding="utf-8")
        late.write_text(records.replace("# late", "# late\nThe first prerequisite is [T096](early.md)."), encoding="utf-8")
        self.assertFalse(self.grade("large-index"))
        late.write_text(records.replace("# late", "# late\nThe first prerequisite is [T096](T001.md)."), encoding="utf-8")
        self.assertTrue(self.grade("large-index"))

        late.write_text(records.replace("# late", "# late\nThe first prerequisite is [T001](T001.md)."), encoding="utf-8")
        self.assertTrue(self.grade("large-index"))
        late.write_text(records.replace("prerequisite T096.", "prerequisite T001.", 1), encoding="utf-8")
        self.assertTrue(self.grade("large-index"))

    def test_linked_fields_preserve_semantic_edges_and_check_the_destination(self):
        self.split("large-index")
        with (self.pages / "milestone-2.md").open("a", encoding="utf-8") as milestone:
            milestone.write("- [T001](T001.md) (open, Mara). Its prerequisite D1 is met.\n")
        path = self.pages / "late.md"
        source = path.read_text(encoding="utf-8")
        linked = source.replace("- T097 (open, release editor):", "* **T097** (open, release editor):", 1).replace(
            "prerequisite T096.", "prerequisite [T096](early.md).", 1)
        path.write_text(linked, encoding="utf-8")
        self.assertFalse(self.grade("large-index"))
        for invalid in [linked.replace("T096](early.md)", "T096](T001.md)", 1),
                        linked.replace("T096](early.md)", "T001](T001.md)", 1),
                        linked + "\n- T097 (closed): prerequisite T001."]:
            path.write_text(invalid, encoding="utf-8")
            self.assertTrue(self.grade("large-index"))

    def test_next_action_declarations_must_agree_on_owner_and_task(self):
        self.split("large-index")
        entry = self.run / "AtlasPlan.md"
        initial = entry.read_text(encoding="utf-8")
        for note, error in [
            ("Mara's next authorized action is [T001](AtlasPlan/T001.md).", False),
            ("Mara is blocked. Jo's next authorized action is [T110](AtlasPlan/late.md).", True),
            ("Jo's next task is [T001](AtlasPlan/T001.md).", True),
        ]:
            with self.subTest(note=note):
                entry.write_text(initial.replace("## Progress", f"## Next authorized action\n{note}\n## Progress"), encoding="utf-8")
                self.assertEqual(bool(self.grade("large-index")), error)

    def test_close_requires_both_milestones_done_accepted_and_checked(self):
        self.initial, self.run = self.root / "original", self.root / "run"
        prepare("close-only", self.initial)
        shutil.copytree(self.initial, self.run)
        entry = self.run / "AtlasPlan.md"
        current = entry.read_text(encoding="utf-8").replace("Status: open", "Status: done").replace(
            "Acceptance: not met", "Acceptance: met").replace("- [ ]", "- [X]").replace(
            "Label verification remains open.", "Mara verified café-001. Jo accepted under CLOSE-7104.")
        entry.write_text(current, encoding="utf-8")
        self.assertFalse(self.grade("close-only"))
        for invalid in [current.replace("Status: done", "Status: open"),
                        current.replace("Status: done", "Status: done\nStatus: open", 1),
                        current.replace("Acceptance: met", "Acceptance: not met", 1),
                        current.replace("[milestone-1] D1", "[milestone-2] D1", 1),
                        current.replace("- [X]", "- [ ]", 1)]:
            entry.write_text(invalid, encoding="utf-8")
            self.assertTrue(self.grade("close-only"))



if __name__ == "__main__":
    unittest.main()
