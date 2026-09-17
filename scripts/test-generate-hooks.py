#!/usr/bin/env python3
"""Public CLI and transaction tests for the checked-in hook generator."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "generate-hooks.py"
OWNERSHIP = "# Generated from hooks/families/send_event.py by scripts/generate-hooks.py. Do not edit.\n"
PILOT_RUNTIME_BODY = '''
from __future__ import annotations

import os
import sys

from helpers.common import emit_json, read_json_input


def main() -> int:
    if "--include-transcript" in sys.argv[1:]:
        os.environ["OBSERVABILITY_INCLUDE_TRANSCRIPT"] = "true"

    read_json_input()
    emit_json({})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
TARGETS = (
    ".copilot/hooks/scripts/send-event.py",
    ".gemini/hooks/scripts/send-event.py",
)


def load_generator():
    specification = importlib.util.spec_from_file_location("generate_hooks", SCRIPT)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def snapshot(root: Path) -> dict[str, tuple[bytes, int]]:
    return {
        path.relative_to(root).as_posix(): (path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
        for path in root.rglob("*")
        if path.is_file()
    }


class GenerateHooksTests(unittest.TestCase):
    def run_cli(self, *arguments: str, cwd: Path | None = None, environment: dict[str, str] | None = None):
        variables = os.environ.copy()
        if environment:
            variables.update(environment)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=cwd or ROOT,
            text=True,
            capture_output=True,
            check=False,
            env=variables,
        )

    def restore_checked_in_outputs(self) -> None:
        subprocess.run(
            [sys.executable, str(SCRIPT), "--write"], cwd=ROOT,
            text=True, capture_output=True, check=True,
        )

    def tearDown(self) -> None:
        self.restore_checked_in_outputs()

    def test_help_and_usage_are_explicit_and_non_mutating(self) -> None:
        before = snapshot(ROOT)
        for flag in ("-h", "--help"):
            with self.subTest(flag=flag):
                result = self.run_cli(flag)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Examples:", result.stdout)
                self.assertEqual(result.stderr, "")
                self.assertNotRegex(result.stdout + result.stderr, re.compile("\\x1b"))
        bare = self.run_cli()
        self.assertEqual(bare.returncode, 2)
        self.assertIn("Examples:", bare.stdout)
        self.assertIn("choose exactly one", bare.stderr)
        conflicting = self.run_cli("--check", "--write")
        self.assertEqual(conflicting.returncode, 2)
        self.assertEqual(before, snapshot(ROOT))

    def test_check_is_read_only_and_reports_missing_stale_and_undeclared_outputs(self) -> None:
        self.restore_checked_in_outputs()
        before = snapshot(ROOT)
        fresh = self.run_cli("--check")
        self.assertEqual(fresh.returncode, 0, fresh.stderr)
        self.assertEqual(fresh.stdout, "Generated hooks are current (2 files).\n")
        self.assertEqual(fresh.stderr, "")
        self.assertEqual(before, snapshot(ROOT))

        stale = ROOT / TARGETS[0]
        stale.write_text("stale\n", encoding="utf-8")
        expected_after_manual_edit = snapshot(ROOT)
        result = self.run_cli("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn(TARGETS[0], result.stdout)
        self.assertEqual(result.stderr, "")
        self.assertEqual(expected_after_manual_edit, snapshot(ROOT))

        undeclared = ROOT / ".copilot/hooks/scripts/obsolete-generated.py"
        undeclared.write_text("#!/usr/bin/env python3\n" + OWNERSHIP, encoding="utf-8")
        result = self.run_cli("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn(undeclared.relative_to(ROOT).as_posix(), result.stdout)
        undeclared.unlink()

    def test_write_repairs_outputs_and_is_idempotent_from_any_directory(self) -> None:
        target = ROOT / TARGETS[0]
        target.write_text("stale\n", encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli("--write", cwd=Path(directory))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(TARGETS[0], result.stdout)
        self.assertEqual(result.stderr, "")
        after_first_write = snapshot(ROOT)
        second = self.run_cli("--write")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(second.stdout, "Generated hooks already current (2 files).\n")
        self.assertEqual(after_first_write, snapshot(ROOT))
        for target_path in TARGETS:
            content = (ROOT / target_path).read_text(encoding="utf-8")
            self.assertTrue(content.startswith("#!/usr/bin/env python3\n" + OWNERSHIP))
            self.assertEqual(stat.S_IMODE((ROOT / target_path).stat().st_mode), 0o755)

    def test_rendered_pilot_preserves_the_pre_generation_runtime_body(self) -> None:
        generator = load_generator()
        outputs = generator.render_all(ROOT)
        self.assertEqual(tuple(output.target.output_path.as_posix() for output in outputs), TARGETS)
        for target in TARGETS:
            expected = "#!/usr/bin/env python3\n" + OWNERSHIP + PILOT_RUNTIME_BODY
            rendered = next(output.content.decode("utf-8") for output in outputs if output.target.output_path.as_posix() == target)
            self.assertEqual(rendered, expected)

    def test_rendering_rejects_unsafe_paths_and_invalid_python_before_writing(self) -> None:
        generator = load_generator()
        original = snapshot(ROOT)
        bad_path = generator.GeneratedTarget("send_event", "copilot", Path("outside.py"))
        with self.assertRaises(generator.GenerateError):
            generator.validate_target(ROOT, bad_path)
        bad_render = generator.RenderedOutput(
            generator.targets()[0], b"#!/usr/bin/env python3\nnot python !\n"
        )
        with self.assertRaises(generator.GenerateError):
            generator.validate_rendered_output(ROOT, bad_render)
        self.assertEqual(original, snapshot(ROOT))

    def test_rejects_symbolic_links_without_following_them(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symbolic links are unavailable")
        target = ROOT / TARGETS[0]
        original = target.read_bytes()
        mode = stat.S_IMODE(target.stat().st_mode)
        outside = Path(tempfile.mkdtemp()) / "outside.py"
        outside.write_bytes(original)
        target.unlink()
        target.symlink_to(outside)
        try:
            result = self.run_cli("--check")
            self.assertEqual(result.returncode, 2)
            self.assertIn(TARGETS[0], result.stderr)
            self.assertEqual(outside.read_bytes(), original)
        finally:
            target.unlink()
            target.write_bytes(original)
            target.chmod(mode)
            shutil.rmtree(outside.parent)

    def test_lock_and_injected_write_failure_leave_outputs_unchanged(self) -> None:
        generator = load_generator()
        target = ROOT / TARGETS[0]
        target.write_text("stale\n", encoding="utf-8")
        before = snapshot(ROOT)
        lock = ROOT / generator.LOCK_NAME
        lock.write_text("held\n", encoding="utf-8")
        try:
            result = self.run_cli("--write")
            self.assertEqual(result.returncode, 2)
            self.assertIn("lock", result.stderr.lower())
            self.assertEqual(before | {lock.relative_to(ROOT).as_posix(): (b"held\n", stat.S_IMODE(lock.stat().st_mode))}, snapshot(ROOT))
        finally:
            lock.unlink()
        result = self.run_cli("--write", environment={"GENERATE_HOOKS_TEST_FAIL_AFTER_REPLACEMENTS": "1"})
        self.assertEqual(result.returncode, 2)
        self.assertIn("rollback", result.stderr.lower())
        self.assertEqual(before, snapshot(ROOT))
        self.assertFalse(lock.exists())
        result = self.run_cli("--write", environment={"GENERATE_HOOKS_TEST_INTERRUPT_AFTER_REPLACEMENTS": "1"})
        self.assertEqual(result.returncode, 130)
        self.assertEqual(before, snapshot(ROOT))
        self.assertFalse(lock.exists())


if __name__ == "__main__":
    unittest.main()
