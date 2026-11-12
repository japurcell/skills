#!/usr/bin/env python3
"""Public CLI and transaction tests for the checked-in hook generator."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
SCRIPT = ROOT / "scripts" / "generate-hooks.py"
OWNERSHIP = "# Generated from hooks/families/rtk.py by scripts/generate-hooks.py. Do not edit.\n"
TARGETS = (
    ".copilot/hooks/scripts/rtk-hook-copilot.py",
    ".gemini/hooks/scripts/rtk-hook-gemini.py",
)
RTK_TARGETS = TARGETS
OBSERVABILITY_TARGETS = (
    ".copilot/hooks/scripts/helpers/observability.py",
    ".gemini/hooks/scripts/helpers/observability.py",
)
OBSERVABILITY_ALLOWED_DIFFERENCES = (
    ('OBSERVABILITY_RUNTIME = "copilot"', 'OBSERVABILITY_RUNTIME = "gemini"'),
    ('_truthy_env("COPILOT_OBSERVABILITY_DISABLE", "OBSERVABILITY_DISABLE")',
     '_truthy_env("GEMINI_OBSERVABILITY_DISABLE", "OBSERVABILITY_DISABLE")'),
    ('_truthy_env("OBSERVABILITY_CAPTURE_EVENT", "COPILOT_OBSERVABILITY_CAPTURE_EVENT")',
     '_truthy_env("OBSERVABILITY_CAPTURE_EVENT", "GEMINI_OBSERVABILITY_CAPTURE_EVENT")'),
    ('_truthy_env("OBSERVABILITY_INCLUDE_TRANSCRIPT", "COPILOT_OBSERVABILITY_INCLUDE_TRANSCRIPT")',
     '_truthy_env("OBSERVABILITY_INCLUDE_TRANSCRIPT", "GEMINI_OBSERVABILITY_INCLUDE_TRANSCRIPT")'),
    ('os.environ.get("COPILOT_OBSERVABILITY_LOG_PATH")',
     'os.environ.get("GEMINI_OBSERVABILITY_LOG_PATH")'),
    ('Path.home() / ".copilot" / "hooks" / "logs"',
     'Path.home() / ".gemini" / "hooks" / "logs"'),
    ('os.environ.get("COPILOT_OBSERVABILITY_LOCK_WAIT_MS")',
     'os.environ.get("GEMINI_OBSERVABILITY_LOCK_WAIT_MS")'),
    ('os.environ.get("COPILOT_OBSERVABILITY_SOURCE_EVENT_NAME")',
     'os.environ.get("GEMINI_OBSERVABILITY_SOURCE_EVENT_NAME")'),
)
BRAIN_BUNDLE_TARGETS = (
    "skills/default/brain-install/assets/skills/brain/scripts/auto-index-brain.py",
    "skills/default/brain-install/assets/hooks/inject-brain.py",
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

    def rendered_text_outputs(self) -> dict[str, str]:
        return {
            output.target.output_path.as_posix(): output.content.decode("utf-8")
            for output in load_generator().render_all(ROOT)
        }


    def test_rtk_targets_share_runtime_body_outside_explicit_provider_adapters(self) -> None:
        rendered = self.rendered_text_outputs()
        self.assertTrue(set(RTK_TARGETS).issubset(rendered))

        shared_sections = []
        for target, provider in zip(RTK_TARGETS, ("copilot", "gemini"), strict=True):
            with self.subTest(target=target):
                source = rendered[target]
                self.assertTrue(source.startswith(
                    "#!/usr/bin/env python3\n"
                    "# Generated from hooks/families/rtk.py by scripts/generate-hooks.py. Do not edit.\n"
                ))
                self.assertEqual(stat.S_IMODE((ROOT / target).stat().st_mode), 0o755)
                self.assertIn(f'RTK_PROVIDER = "{provider}"', source)
                self.assertIn('[rtk_bin, "hook", RTK_PROVIDER]', source)
                self.assertIn("from helpers.audit import audit_log_event", source)
                self.assertIn("from helpers.common import emit_json, sanitize_log_field", source)
                self.assertIn("from helpers.observability import begin_hook_capture", source)
                self.assertNotIn(".copilot.hooks", source)
                self.assertNotIn(".gemini.hooks", source)
                sections = re.split(
                    r"# BEGIN PROVIDER ADAPTER\n.*?# END PROVIDER ADAPTER\n",
                    source,
                    flags=re.DOTALL,
                )
                self.assertEqual(len(sections), 2, f"Expected one provider adapter in {target}.")
                shared_sections.append(sections)

        self.assertEqual(
            shared_sections[0],
            shared_sections[1],
            "RTK outputs diverged outside their explicit provider adapters.",
        )
        self.assertIn('rewritten["permissionDecision"] = "allow"', rendered[RTK_TARGETS[0]])
        self.assertIn('hook_out["permissionDecision"] = "allow"', rendered[RTK_TARGETS[0]])
        self.assertNotIn('permissionDecision"] = "allow"', rendered[RTK_TARGETS[1]])

    def test_rtk_renderer_rejects_swapped_and_undeclared_target_paths(self) -> None:
        load_generator()
        from hooks.families import rtk
        from hooks.manifest import GeneratedTarget
        from hooks.providers import PROVIDERS

        invalid_targets = (
            (
                "swapped",
                GeneratedTarget("rtk", "copilot", Path(RTK_TARGETS[1])),
            ),
            (
                "undeclared",
                GeneratedTarget(
                    "rtk",
                    "copilot",
                    Path(".copilot/hooks/scripts/rtk-hook-undeclared.py"),
                ),
            ),
        )
        for case, target in invalid_targets:
            with self.subTest(case=case):
                with self.assertRaisesRegex(ValueError, "Unsupported RTK target/provider"):
                    rtk.render(PROVIDERS["copilot"], target)

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
        self.assertEqual(fresh.stdout, "Generated hooks are current (16 files).\n")
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

    def test_bundle_helpers_are_checked_repaired_and_match_provider_outputs(self) -> None:
        self.restore_checked_in_outputs()
        for relative in BRAIN_BUNDLE_TARGETS:
            with self.subTest(target=relative):
                path = ROOT / relative
                original = path.read_bytes()
                mode = stat.S_IMODE(path.stat().st_mode)
                try:
                    path.write_bytes(original + b"\n# bundle drift probe\n")
                    before = snapshot(ROOT)
                    stale = self.run_cli("--check")
                    self.assertEqual(stale.returncode, 1, stale.stdout + stale.stderr)
                    self.assertIn(relative, stale.stdout)
                    self.assertEqual(before, snapshot(ROOT))
                    repaired = self.run_cli("--write")
                    self.assertEqual(repaired.returncode, 0, repaired.stderr)
                    self.assertIn(relative, repaired.stdout)
                    canonical = ROOT / ".github/hooks/scripts" / path.name
                    self.assertEqual(path.read_bytes(), canonical.read_bytes())
                    if os.name != "nt":
                        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o755)
                    current = self.run_cli("--check")
                    self.assertEqual(current.returncode, 0, current.stdout + current.stderr)
                finally:
                    path.write_bytes(original)
                    path.chmod(mode)

    def test_check_reads_canonical_sources_as_utf8_in_legacy_locales(self) -> None:
        # Inventory generated Python bytes and modes, excluding interpreter caches.
        paths = tuple(path for name in (".codex/hooks", ".copilot/hooks/scripts",
                                        ".gemini/hooks/scripts", ".github/hooks/scripts")
                      for path in (ROOT / name).rglob("*.py"))
        before = {path: (path.read_bytes(), stat.S_IMODE(path.stat().st_mode)) for path in paths}
        result = self.run_cli(
            "--check",
            environment={"LC_ALL": "C", "PYTHONUTF8": "0", "PYTHONCOERCECLOCALE": "0"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Generated hooks are current (16 files).\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(before, {path: (path.read_bytes(), stat.S_IMODE(path.stat().st_mode)) for path in paths})

    def test_windows_check_ignores_posix_executable_mode(self) -> None:
        generator = load_generator()
        outputs = generator.render_all(ROOT)
        target = ROOT / TARGETS[0]
        target.chmod(0o644)

        self.assertIn(PurePosixPath(TARGETS[0]), generator.check_outputs(ROOT, outputs).stale_paths)
        with mock.patch.object(generator.os, "name", "nt"):
            self.assertTrue(generator.check_outputs(ROOT, outputs).is_current)

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
        self.assertEqual(second.stdout, "Generated hooks already current (16 files).\n")
        self.assertEqual(after_first_write, snapshot(ROOT))
        for target_path in TARGETS:
            content = (ROOT / target_path).read_text(encoding="utf-8")
            self.assertTrue(content.startswith("#!/usr/bin/env python3\n" + OWNERSHIP))
            self.assertEqual(stat.S_IMODE((ROOT / target_path).stat().st_mode), 0o755)

    def test_observability_renderings_have_only_named_provider_differences(self) -> None:
        rendered = self.rendered_text_outputs()
        copilot = rendered[OBSERVABILITY_TARGETS[0]]
        gemini = rendered[OBSERVABILITY_TARGETS[1]]
        self.assertTrue(copilot.startswith("#!/usr/bin/env python3\n"))
        self.assertTrue(gemini.startswith("#!/usr/bin/env python3\n"))
        normalized = copilot
        for copilot_value, gemini_value in OBSERVABILITY_ALLOWED_DIFFERENCES:
            self.assertEqual(copilot.count(copilot_value), 1)
            self.assertEqual(gemini.count(gemini_value), 1)
            normalized = normalized.replace(copilot_value, gemini_value)
        self.assertEqual(normalized, gemini, "Observability outputs diverged outside their named provider differences.")

    def test_rendering_rejects_unsafe_paths_and_invalid_python_before_writing(self) -> None:
        generator = load_generator()
        original = snapshot(ROOT)
        bad_path = generator.GeneratedTarget("rtk", "copilot", Path("outside.py"))
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


class ReadyIdeasWindowsWorkflowTests(unittest.TestCase):
    def test_provider_hook_changes_trigger_push_and_pull_request_checks(self) -> None:
        workflow = (ROOT / ".github/workflows/ready-ideas-windows.yml").read_text(
            encoding="utf-8"
        )
        for event in ("push", "pull_request"):
            with self.subTest(event=event):
                match = re.search(
                    rf"(?m)^  {event}:\n    paths:\n((?:      - '[^']+'\n)+)",
                    workflow,
                )
                self.assertIsNotNone(match, f"{event} needs a paths filter")
                paths = set(re.findall(r"^      - '([^']+)'$", match.group(1), re.MULTILINE))
                self.assertTrue({".copilot/**", ".gemini/**"} <= paths)


if __name__ == "__main__":
    unittest.main()
