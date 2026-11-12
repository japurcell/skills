#!/usr/bin/env python3
"""Public CLI tests; fake providers never perform inference."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI = Path(__file__).with_name("scheduler_pilot.py")

class PilotTests(unittest.TestCase):
    def call(self, *args):
        return subprocess.run([sys.executable, str(CLI), *map(str,args)], capture_output=True, text=True)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.skill = self.root / "source"
        (self.skill / "scripts").mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("Selected unique body")
        (self.skill / "scripts/scheduler.py").write_text("print('fixture')")
        self.provider = self.root / "provider"
        self.provider.write_text("#!/usr/bin/env python3\nimport sys\nprint('fake 1 --json --model --sandbox --output-format --allow-tool --session-id --cd --add-dir --output-last-message --reasoning-effort --share --usage-output-file --log-dir --no-auto-update --no-custom-instructions --prompt')\n")
        self.provider.chmod(0o700)
        self.config = self.root / "config.json"
        self.config.write_text(json.dumps({"providers": {name: {"executable": str(self.provider), "model": "test-model", "effort": "medium"} for name in ("codex", "copilot")}, "timeout_seconds": 2}))
        self.run = self.root / "run"
        self.manifest = self.run / "manifest.json"

    def prepare(self):
        result = self.call("prepare", "--run-root", self.run, "--baseline", self.skill,
                           "--candidate", self.skill, "--config", self.config)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(self.manifest.read_text())

    def test_prepare_freezes_absolute_paths_and_refuses_reuse(self):
        manifest = self.prepare()
        self.assertEqual(len(manifest["cells"]), 4)
        self.assertEqual(self.run.stat().st_mode & 0o777, 0o700)
        cell = manifest["cells"]["codex-candidate"]
        prompt = Path(cell["prompts"]["smoke"]).read_text()
        self.assertIn("Selected unique body", prompt)
        self.assertIn(str(Path(cell["repo"]) / "outputs/smoke.json"), prompt)
        duplicate = self.call("prepare", "--run-root", self.run, "--baseline", self.skill,
                              "--candidate", self.skill, "--config", self.config)
        self.assertEqual(duplicate.returncode, 2)

    def test_preflight_records_no_inference_and_drift_fails_closed(self):
        self.prepare()
        result = self.call("preflight", "--manifest", self.manifest, "--provider", "codex")
        self.assertEqual(result.returncode, 0, result.stderr)
        evidence = json.loads((self.run / "preflight/codex.json").read_text())
        self.assertEqual([x["argv"][-1] for x in evidence["probes"]], ["--version", "--help"])
        (self.run / "snapshots/baseline/SKILL.md").chmod(0o600)
        (self.run / "snapshots/baseline/SKILL.md").write_text("drift")
        result = self.call("preflight", "--manifest", self.manifest, "--provider", "codex")
        self.assertEqual(result.returncode, 2)
        self.assertIn("drift", result.stderr)

    def fake_execution(self, mode="good"):
        self.provider.write_text("""#!/usr/bin/env python3
import builtins, json, os, pathlib, sys, time
raw_print = builtins.print
def print(value):
    if '--output-format' not in sys.argv:
        return raw_print(value)
    try: row = json.loads(value)
    except ValueError: return raw_print(value)
    if row.get('type') == 'item.completed':
        item = row['item']
        raw_print(json.dumps({'type':'tool.execution_start','data':{'toolCallId':item['command'],'arguments':{'command':item['command']}}}))
        raw_print(json.dumps({'type':'tool.execution_complete','data':{'toolCallId':item['command'],'success':item['exit_code']==0,'result':item.get('aggregated_output','')}}))
    else: raw_print(value)
if '--version' in sys.argv or '--help' in sys.argv:
    print('fake 1 --json --model --sandbox --output-format --allow-tool --session-id --cd --add-dir --output-last-message --reasoning-effort --share --usage-output-file --log-dir --no-auto-update --no-custom-instructions --prompt')
    raise SystemExit
mode = MODE
if mode == 'timeout':
    time.sleep(10)
repo = pathlib.Path.cwd()
phase = 'smoke' if not (repo / 'outputs/smoke.json').exists() else 'scenario'
script = next(repo.parents[2].glob('snapshots/candidate/scripts/scheduler.py'))
if 'baseline' in str(repo):
    script = next(repo.parents[2].glob('snapshots/baseline/scripts/scheduler.py'))
if mode != 'missing':
    target = repo / 'outputs' / ('smoke.json' if phase == 'smoke' else 'result.json')
    if mode == 'wrong': target = repo / 'wrong.json'
    target.write_text(json.dumps({'smoke': True}) if mode != 'malformed' else '{')
if phase == 'scenario' and mode == 'good':
    actions = []
    for name, assignment, at in [('stop','A',105),('extend','B',103),('stop','B',200),('transfer-rejected','B',201),('confirm-stopped','B',202),('transfer','B',203),('parent-update','B',204),('confirm-transfer','B',205)]:
        command = 'python3 ' + str(script) + ' --state scenario-state.json ' + name.replace('stop', 'tick') + ' ' + assignment + ' --now ' + str(at)
        if name == 'confirm-transfer': command = 'python3 ' + str(script) + ' confirm-transfer B'
        code = 2 if name == 'transfer-rejected' else 0
        evidence = 'outputs/' + name + '-' + str(at) + '.json'
        (repo / evidence).write_text(json.dumps({'command': command, 'exit_code': code}))
        actions.append({'action': name, 'assignment': assignment, 'at': at, 'evidence': evidence})
        print(json.dumps({'type':'item.completed','item':{'type':'command_execution','command':command,'exit_code':code}}))
    state = {'assignments': {'A': {'phase':'stop'}, 'B': {'phase':'stop','extension_used':True,'deadline':200,'stop_confirmed':True,'transfer_authorized':True,'transferred':True,'transfer_completed':True,'transfer_receipt':{'owner':'agent-new','evidence':'outputs/ownership.json'}}, 'C':{'status':'completed'}}}
    (repo / 'outputs/state.json').write_text(json.dumps(state))
    (repo / 'outputs/ownership.json').write_text(json.dumps({'owner':'agent-new','previous_owner':'agent-old','updated_at':204}))
    final = {'old_owner':'agent-old','new_owner':'agent-new','worker_stopped':True,'writes_stopped':True,'transfer_authorized':True,'parent_record':'outputs/ownership.json','scheduler_state':'outputs/state.json'}
    (repo / 'outputs/result.json').write_text(json.dumps({'actions':actions,'final_state':final}))
    print(json.dumps({'type':'item.completed','item':{'type':'command_execution','command':'python3 ' + str(script) + ' complete C','exit_code':0}}))
command = 'python3 ' + str(script) + ' --state ' + str(repo / 'smoke-state.json') + ' register smoke'
for cmd in (command, command.replace('register smoke', 'complete smoke'), 'python3 ' + str(script.parent.parent / 'io_fixture.py') + ' ' + str(repo)):
    item = {'type': 'command_execution', 'command': cmd, 'status': 'completed', 'exit_code': 1 if mode == 'denied' else 0, 'aggregated_output': 'permission denied' if mode == 'denied' else ''}
    print(json.dumps({'type': 'item.completed', 'item': item}))
print(json.dumps({'type': 'turn.completed', 'usage': {'input_tokens': 1, 'output_tokens': 1}}))
""".replace("MODE", repr(mode)))
        self.provider.chmod(0o700)

    def start(self, provider="codex", mode="good"):
        self.fake_execution(mode)
        self.prepare()
        result = self.call("preflight", "--manifest", self.manifest, "--provider", provider)
        self.assertEqual(result.returncode, 0, result.stderr)
        return provider + "-candidate"

    def test_explicit_run_freezes_argv_and_preserves_smoke_evidence(self):
        cell = self.start()
        result = self.call("run", "--manifest", self.manifest, "--cell", cell, "--phase", "smoke")
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertTrue(receipt["smoke_valid"])
        self.assertIn("--sandbox", receipt["argv"])
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", receipt["argv"])
        retry = self.call("run", "--manifest", self.manifest, "--cell", cell, "--phase", "smoke")
        self.assertEqual(retry.returncode, 2)
        self.assertEqual(json.loads((self.run / "cells" / cell / "evidence/smoke/run.json").read_text()), receipt)

    def test_grade_separates_invalid_setup_and_valid_output_failure(self):
        cell = self.start()
        result = self.call("grade", "--manifest", self.manifest, "--cell", cell)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["setup_status"], "invalid")
        smoke = self.call("run", "--manifest", self.manifest, "--cell", cell, "--phase", "smoke")
        self.assertEqual(smoke.returncode, 0, smoke.stderr)
        scenario = self.call("run", "--manifest", self.manifest, "--cell", cell, "--phase", "scenario")
        self.assertEqual(scenario.returncode, 0, scenario.stderr)
        (self.run / "cells" / cell / "repo/outputs/result.json").write_text('{"smoke":true}')
        grade = self.call("grade", "--manifest", self.manifest, "--cell", cell)
        self.assertEqual(grade.returncode, 0, grade.stderr)
        report = json.loads(grade.stdout)
        self.assertEqual(report["setup_status"], "valid")
        self.assertEqual(report["behavior_status"], "fail")
        self.assertEqual(report["output_contract_status"], "fail")
        self.assertIn("candidate_acknowledgment", report["candidate_only"])

    def test_smoke_negative_outputs_and_denial_preserve_evidence(self):
        for mode in ("denied", "missing", "wrong", "malformed"):
            with self.subTest(mode=mode):
                self.run = self.root / ("run-" + mode)
                self.manifest = self.run / "manifest.json"
                cell = self.start(mode=mode)
                result = self.call("run", "--manifest", self.manifest, "--cell", cell, "--phase", "smoke")
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertTrue((self.run / "cells" / cell / "evidence/smoke/stdout.jsonl").exists())
                grade = json.loads(self.call("grade", "--manifest", self.manifest, "--cell", cell).stdout)
                self.assertEqual(grade["setup_status"], "invalid")
                self.assertEqual(grade["behavior_status"], "not_evaluated")

    def test_timeout_and_missing_usage_are_explicit(self):
        cell = self.start(mode="timeout")
        result = self.call("run", "--manifest", self.manifest, "--cell", cell, "--phase", "smoke")
        self.assertEqual(result.returncode, 124, result.stderr)
        directory = self.run / "cells" / cell / "evidence/smoke"
        self.assertTrue((directory / "usage-missing.json").exists())
        self.assertEqual(json.loads((directory / "run.json").read_text())["exit_code"], 124)

    def test_symlink_output_escape_and_arbitrary_flags_rejected(self):
        manifest = self.prepare()
        output = Path(manifest["cells"]["codex-candidate"]["repo"]) / "outputs/result.json"
        outside = self.root / "outside.json"
        outside.write_text('{}')
        output.symlink_to(outside)
        result = self.call("grade", "--manifest", self.manifest, "--cell", "codex-candidate")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(outside.read_text(), '{}')
        config = json.loads(self.config.read_text())
        config["providers"]["codex"]["flags"] = ["--dangerously-bypass-approvals-and-sandbox"]
        self.config.write_text(json.dumps(config))
        result = self.call("prepare", "--run-root", self.root / "bad", "--baseline", self.skill, "--candidate", self.skill, "--config", self.config)
        self.assertEqual(result.returncode, 2, result.stderr)

    def test_copilot_scoped_grants_and_fresh_sessions(self):
        cell = self.start(provider="copilot")
        result = self.call("run", "--manifest", self.manifest, "--cell", cell, "--phase", "smoke")
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        argv = record["argv"]
        self.assertIn("--no-custom-instructions", argv)
        self.assertFalse(any(arg in argv for arg in ("--allow-all", "--allow-all-tools", "--allow-all-paths")))
        self.assertFalse(any(arg == "--allow-tool=write" for arg in argv))
        manifest = json.loads(self.manifest.read_text())
        self.assertNotEqual(manifest["cells"][cell]["session_ids"]["smoke"], manifest["cells"][cell]["session_ids"]["scenario"])

    def test_known_good_and_each_common_assertion_failure(self):
        cell = self.start()
        for phase in ("smoke", "scenario"):
            result = self.call("run", "--manifest", self.manifest, "--cell", cell, "--phase", phase)
            self.assertEqual(result.returncode, 0, result.stderr)
        result = self.call("grade", "--manifest", self.manifest, "--cell", cell)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["behavior_status"], "pass", report)
        output = self.run / "cells" / cell / "repo/outputs/result.json"
        original = json.loads(output.read_text())
        for assertion, action_name in (("stop_timing","stop"), ("single_extension","extend"), ("exclusive_pending_shutdown","transfer-rejected"), ("parent_transfer","parent-update")):
            damaged = json.loads(json.dumps(original))
            damaged["actions"] = [action for action in damaged["actions"] if action["action"] != action_name]
            output.write_text(json.dumps(damaged))
            result = json.loads(self.call("grade", "--manifest", self.manifest, "--cell", cell).stdout)
            self.assertFalse(result["assertions"][assertion]["passed"], assertion)
        output.write_text(json.dumps(original))
        state_path = self.run / "cells" / cell / "repo/outputs/state.json"
        state = json.loads(state_path.read_text())
        state["assignments"]["B"]["transfer_completed"] = False
        state_path.write_text(json.dumps(state))
        report = json.loads(self.call("grade", "--manifest", self.manifest, "--cell", cell).stdout)
        self.assertFalse(report["candidate_only"]["candidate_acknowledgment"]["passed"])

    def test_interrupt_retains_partial_evidence(self):
        import signal
        import time
        cell = self.start(mode="timeout")
        process = subprocess.Popen([sys.executable, str(CLI), "run", "--manifest", str(self.manifest), "--cell", cell, "--phase", "smoke"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        evidence = self.run / "cells" / cell / "evidence/smoke/run.json"
        for _ in range(100):
            if evidence.exists(): break
            time.sleep(0.01)
        time.sleep(0.1)
        process.send_signal(signal.SIGINT)
        stdout, stderr = process.communicate(timeout=5)
        self.assertEqual(process.returncode, 130, stderr)
        self.assertEqual(json.loads(evidence.read_text())["exit_code"], 130)

    def test_wrapped_immutable_execution_is_valid(self):
        import shlex
        cell = self.start()
        for phase in ("smoke", "scenario"):
            result = self.call("run", "--manifest", self.manifest, "--cell", cell, "--phase", phase)
            self.assertEqual(result.returncode, 0, result.stderr)
        raw = self.run / "cells" / cell / "evidence/scenario/stdout.jsonl"
        rows = [json.loads(line) for line in raw.read_text().splitlines()]
        for row in rows:
            event = row.get("item", {})
            if "complete C" in event.get("command", ""):
                event["command"] = shlex.join(["python3", "-c", "import subprocess; subprocess.run(" + repr(shlex.split(event["command"])) + ", check=True)"])
        raw.write_text("\n".join(json.dumps(row) for row in rows))
        report = json.loads(self.call("grade", "--manifest", self.manifest, "--cell", cell).stdout)
        self.assertTrue(report["assertions"]["independent_progress"]["passed"])

    def test_help_is_offline_and_describes_contract(self):
        result = self.call("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for word in ("prepare", "preflight", "run", "grade", "124", "130"):
            self.assertIn(word, result.stdout)

if __name__ == "__main__":
    unittest.main()
