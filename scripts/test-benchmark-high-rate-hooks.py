#!/usr/bin/env python3
"""Exercise the benchmark CLI using inert temporary guardian entrypoints."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tool_guard_corpus import PROVIDERS, decision, encode, envelope, fixtures, script_path

BENCHMARK = Path(__file__).with_name("benchmark-high-rate-hooks.py")


class BenchmarkCliTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "darwin", "benchmark execution is macOS only")
    def test_guard_only_uses_script_root_and_preserves_raw_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for provider in PROVIDERS:
                expectations = {encode(envelope(provider,f)).decode().strip():f.expected("baseline",provider) for f in fixtures()}
                # Existing cases retain their exact legacy benchmark envelopes.
                path = script_path(root,provider)
                path.parent.mkdir(parents=True)
                script = "import json,sys\nexpected="+repr(expectations)+"\nraw=sys.stdin.read().strip()\n"
                script += "try:\n p=json.loads(raw)\n value=p.get('toolArgs',p.get('tool_input',{}))\n text=value if isinstance(value,str) else value.get('command','')\n outcome=expected.get(raw, 'deny' if '--force' in text else 'allow')\nexcept ValueError:\n outcome='deny'\n"
                if provider == "codex":
                    script += "print(json.dumps({} if outcome=='allow' else {'hookSpecificOutput':{'permissionDecision':'deny'}}))\n"
                elif provider == "copilot":
                    script += "print(json.dumps({'permissionDecision':outcome,'hookSpecificOutput':{'permissionDecision':outcome}}))\n"
                else:
                    script += "print(json.dumps({'decision':outcome}))\n"
                path.write_text(script,encoding="utf-8")
            output = root/"report.json"
            result = subprocess.run([sys.executable,str(BENCHMARK),"--guard-only","--script-root",str(root),"--expected-behavior","baseline","--samples","5","--warmups","0","--output",str(output)],capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stderr)
            report=json.loads(output.read_text())
            names={row["case"] for row in report["results"]}
            for provider in PROVIDERS:
                self.assertIn(provider+".guard.clean",names)
                self.assertIn(provider+".guard.finding",names)
                self.assertIn(provider+".guard.large",names)
                self.assertIn(provider+".guard.failure",names)
                self.assertIn(provider+".guard.patch.bytes-46899",names)
            for row in report["results"]:
                self.assertEqual(len(row["samples_ms"]),5)
                self.assertIn(row["expected_decision"],("allow","deny"))
                self.assertEqual(row["actual_decision"],row["expected_decision"])
                self.assertGreater(row["first_run_ms"],0)
            self.assertEqual(len(report["concurrency"]),3)
            self.assertEqual(report["method"]["expected_behavior"],"baseline")
            # Changing the expected mode must reject these same baseline fixtures.
            candidate=subprocess.run([sys.executable,str(BENCHMARK),"--guard-only","--script-root",str(root),"--expected-behavior","candidate","--samples","5","--warmups","0"],capture_output=True,text=True,timeout=15)
            self.assertNotEqual(candidate.returncode,0)
            self.assertIn("expected allow",candidate.stderr)

    def test_public_flags_validate_usage_before_running(self) -> None:
        for args in (("--help",),("--expected-behavior","unknown"),("--guard-only","--script-root","/nonexistent/guardian-fixture")):
            result=subprocess.run([sys.executable,str(BENCHMARK),*args],capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,0 if args==("--help",) else 2,result.stderr)


if __name__ == "__main__":
    unittest.main()
