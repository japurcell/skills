#!/usr/bin/env python3
"""Offline public CLI checks using real frozen scheduler subprocesses."""
import json
import hashlib
import os
import shlex
import shutil
import signal
import time
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).with_name("scheduler_pilot.py")
SOURCE = CLI.parent.parent

class PilotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = self.root / "config.json"
        self.config.write_text(json.dumps({"providers": {p: {"executable": sys.executable, "model": "gpt-6.1-sol", "effort": "medium"} for p in ("codex", "copilot")}, "timeout_seconds": 2}))
        self.run = self.root / "run"
        self.manifest = self.run / "manifest.json"

    def call(self, *args):
        return subprocess.run([sys.executable, str(CLI), *map(str,args)], capture_output=True, text=True)

    def prepare(self):
        baseline = self.root / "v2"
        (baseline / "scripts").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / "SKILL.md", baseline / "SKILL.md")
        shutil.copyfile(CLI.parent / "fixtures/v2-scheduler.py", baseline / "scripts/scheduler.py")
        result = self.call("prepare", "--run-root", self.run, "--baseline", baseline, "--candidate", SOURCE, "--config", self.config)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.data = json.loads(self.manifest.read_text())

    def fixture(self, provider="codex", variant="candidate", omit=None):
        cell_id = provider + "-" + variant
        cell = self.data["cells"][cell_id]
        repo = Path(cell["repo"])
        evidence = repo.parent / "evidence"
        rows = []
        def invoke(args):
            argv = cell["helper_prefix"] + args
            child = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True)
            command = shlex.join(argv)
            if provider == "codex":
                rows.append({"type":"item.completed", "item":{"type":"command_execution", "command":command, "exit_code":child.returncode, "aggregated_output":child.stdout}})
            else:
                key = str(len(rows))
                rows.extend([{"type":"tool.execution_start", "data":{"toolCallId":key,"arguments":{"command":command}}}, {"type":"tool.execution_complete", "data":{"toolCallId":key,"success":child.returncode==0,"result":{"content":child.stdout}}}])
            return {"command":command, "exit_code":child.returncode}, json.loads(child.stdout)["pilot_child"]
        def save(phase):
            directory = evidence / phase
            directory.mkdir(exist_ok=True)
            if provider == "copilot":
                rows.insert(0,{"type":"session.start","data":{"selectedModel":"gpt-6.1-sol","reasoningEffort":"medium"}})
            (directory / "stdout.jsonl").write_text("\n".join(json.dumps(row) for row in rows))
            (directory / "run.json").write_text(json.dumps({"exit_code":0,"smoke_valid":phase=="smoke", "delivered_prompt_sha256":hashlib.sha256(Path(cell["prompts"][phase]).read_bytes()).hexdigest()}))
            rows.clear()
        smoke_state = str(repo / "outputs/smoke-state.json")
        invoke(["--state",smoke_state,"register","smoke","smoke-agent","neutral","--deadline","100","--checkpoint","300","--now","0"])
        invoke(["--state",smoke_state,"complete","smoke","--now","1"])
        invoke(["smoke-write"])
        save("smoke")
        state = str(repo / "outputs/scenario-state.json")
        actions = []
        def op(command, assignment=None, at=0, extra=(), label=None, expected=0):
            args=["--state",state,command] + ([assignment] if assignment else []) + list(extra) + ["--now",str(at)]
            if omit is not None and label == omit:
                return
            record, receipt = invoke(args)
            self.assertEqual(record["exit_code"], expected, receipt)
            if label:
                path="outputs/"+label+"-"+str(at)+".json"
                (repo/path).write_text(json.dumps(record))
                actions.append({"action":label,"assignment":assignment or ("A" if at==105 else "B"),"at":at,"evidence":path})
        for assignment, agent in (("A","agent-a"),("B","agent-old"),("C","agent-c")):
            op("register",assignment,extra=[agent,"task","--deadline","100","--checkpoint","300","--grace","5"])
        op("tick",at=100)
        op("checkpoint","B",102,["--eta","200"])
        op("checkpoint","C",102)
        op("extend","B",103,["--eta","200"],"extend")
        op("complete","C",104)
        op("tick",at=105,label="stop")
        op("checkpoint","B",150)
        op("extend","B",151,["--eta","250"],expected=2)
        op("tick",at=200,label="stop")
        op("transfer","B",201,label="transfer-rejected",expected=2)
        op("confirm-stopped","B",202,["--confirmation","worker-and-writes-stopped"],"confirm-stopped")
        op("transfer","B",203,label="transfer")
        record,_ = invoke(["parent-update","agent-old","agent-new","204"])
        (repo / "outputs/parent.json").write_text(json.dumps(record))
        actions.append({"action":"parent-update","assignment":"B","at":204,"evidence":"outputs/parent.json"})
        if variant == "candidate":
            op("confirm-transfer","B",205,["--owner","agent-new","--evidence","outputs/ownership.json","--confirmation","parent-ownership-updated"],"confirm-transfer")
        output={"actions":actions,"final_state":{"old_owner":"agent-old","new_owner":"agent-new","worker_stopped":True,"writes_stopped":True,"transfer_authorized":True,"parent_record":"outputs/ownership.json","scheduler_state":"outputs/scenario-state.json"}}
        (repo / "outputs/result.json").write_text(json.dumps(output))
        save("scenario")
        return cell_id, repo

    def grade(self, cell):
        result=self.call("grade","--manifest",self.manifest,"--cell",cell)
        self.assertEqual(result.returncode,0,result.stderr)
        return json.loads(result.stdout)

    def test_both_providers_real_v2_v3_good_cases(self):
        self.prepare()
        for provider in ("codex","copilot"):
            for variant in ("baseline","candidate"):
                with self.subTest(provider=provider,variant=variant):
                    cell,_=self.fixture(provider,variant)
                    report=self.grade(cell)
                    self.assertEqual(report["behavior_status"],"pass",report)

    def test_each_semantic_negative_fails(self):
        self.prepare()
        cell,repo=self.fixture()
        output=repo / "outputs/result.json"
        original=json.loads(output.read_text())
        for name in ("stop","extend","transfer-rejected","confirm-stopped","transfer","parent-update","confirm-transfer"):
            with self.subTest(action=name):
                damaged=json.loads(json.dumps(original))
                for action in damaged["actions"]:
                    if action["action"]==name: action["at"]+=1
                output.write_text(json.dumps(damaged))
                self.assertEqual(self.grade(cell)["behavior_status"],"fail")
        output.write_text(json.dumps(original))
        state=repo / "outputs/scenario-state.json"
        state.write_text('{"assignments":[]}')
        self.assertEqual(self.grade(cell)["output_contract_status"],"fail")

    def test_output_traversal_and_symlink_are_not_evidence(self):
        self.prepare()
        cell,repo=self.fixture()
        output=repo / "outputs/result.json"
        original=json.loads(output.read_text())
        artifact=repo / original["actions"][0]["evidence"]
        outside=repo.parent / "evidence/outside.json"
        shutil.copyfile(artifact,outside)
        original["actions"][0]["evidence"]="outputs/../../evidence/outside.json"
        output.write_text(json.dumps(original))
        self.assertEqual(self.grade(cell)["output_contract_status"],"fail")
        original["actions"][0]["evidence"]="outputs/link.json"
        (repo / "outputs/link.json").symlink_to(outside)
        output.write_text(json.dumps(original))
        self.assertEqual(self.grade(cell)["output_contract_status"],"fail")

    def test_dead_wrapper_and_forged_state_do_not_count(self):
        self.prepare()
        cell,repo=self.fixture()
        raw=repo.parent / "evidence/scenario/stdout.jsonl"
        rows=[json.loads(line) for line in raw.read_text().splitlines()]
        for row in rows:
            item=row.get("item",{})
            if item.get("type")=="command_execution":
                item["command"]=shlex.join(["python3","-c","import subprocess\nif False: subprocess.run("+repr(shlex.split(item["command"]))+", check=True)"])
        raw.write_text("\n".join(json.dumps(row) for row in rows))
        report=self.grade(cell)
        self.assertEqual(report["behavior_status"],"fail")
        self.assertFalse(report["assertions"]["immutable_execution"]["passed"])

    def test_smoke_gate_and_hash_drift_fail_closed(self):
        self.prepare()
        cell,_=self.fixture()
        result=self.call("run","--manifest",self.manifest,"--cell",cell,"--phase","scenario")
        self.assertEqual(result.returncode,2)
        self.assertIn("two-smoke",result.stderr)
        path=Path(self.data["cells"][cell]["prompts"]["smoke"])
        path.chmod(0o600);path.write_text("drift")
        result=self.call("grade","--manifest",self.manifest,"--cell",cell)
        self.assertEqual(result.returncode,2)
        self.assertIn("drift",result.stderr)

    def test_helper_timeout_success_and_interrupt_kill_detached_pipe_descendants(self):
        for mode in ("timeout","success","interrupt"):
            with self.subTest(mode=mode):
                directory=self.root / ("helper-"+mode)
                (directory / "repo/outputs").mkdir(parents=True)
                helper=directory / "invoke_scheduler.py"
                shutil.copyfile(CLI.parent / "invoke_scheduler.py",helper)
                scheduler=directory / "scheduler.py"
                script="import subprocess,sys,time,pathlib\nchild=subprocess.Popen([sys.executable,'-c','import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(30)'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\npathlib.Path('child.pid').write_text(str(child.pid))\n"
                scheduler.write_text(script + ("time.sleep(30)\n" if mode!="success" else ""))
                (directory / "invocation.json").write_text(json.dumps({"repo":str((directory / "repo").resolve()),"scheduler":str(scheduler),"timeout_seconds":.3 if mode=="timeout" else 10}))
                argv=[sys.executable,str(helper),"--state",str(directory / "repo/outputs/scenario-state.json"),"tick","--now","0"]
                process=subprocess.Popen(argv,cwd=directory,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
                for _ in range(100):
                    if (directory / "child.pid").exists(): break
                    time.sleep(.01)
                if mode=="interrupt": process.send_signal(signal.SIGINT)
                stdout,stderr=process.communicate(timeout=4)
                (directory / "retained-stdout.json").write_text(stdout)
                (directory / "retained-stderr.txt").write_text(stderr)
                self.assertEqual(process.returncode,{"timeout":124,"success":0,"interrupt":130}[mode],stderr)
                pid=int((directory / "child.pid").read_text())
                for _ in range(100):
                    try: os.kill(pid,0)
                    except ProcessLookupError: break
                    time.sleep(.01)
                else:
                    os.kill(pid,signal.SIGKILL)
                    self.fail("TERM-ignoring descendant survived cleanup")

    def test_missing_wrong_malformed_outputs_and_failed_evidence_retained(self):
        self.prepare()
        cell,repo=self.fixture()
        output=repo / "outputs/result.json"
        original=output.read_text()
        raw=repo.parent / "evidence/scenario/stdout.jsonl"
        retained=raw.read_bytes()
        for mode in ("missing","wrong","malformed"):
            with self.subTest(mode=mode):
                if output.exists(): output.unlink()
                if mode=="wrong": (repo / "wrong.json").write_text(original)
                if mode=="malformed": output.write_text("{")
                report=self.grade(cell)
                self.assertEqual(report["behavior_status"],"fail")
                self.assertEqual(report["output_contract_status"],"fail")
                self.assertEqual(report["usage_status"],"unavailable")
                self.assertTrue((raw.parent / "usage-missing.json").exists())
                self.assertEqual(raw.read_bytes(),retained)

    def test_missing_execution_and_followup_are_behavior_failures(self):
        self.prepare()
        cell,repo=self.fixture()
        raw=repo.parent / "evidence/scenario/stdout.jsonl"
        original=raw.read_text()
        for marker in ("complete C", "checkpoint B --now 150", "extend B --eta 250 --now 151", "confirm-transfer B"):
            with self.subTest(marker=marker):
                rows=[json.loads(line) for line in original.splitlines()]
                rows=[row for row in rows if marker not in row.get("item",{}).get("command","")]
                raw.write_text("\n".join(json.dumps(row) for row in rows))
                self.assertEqual(self.grade(cell)["behavior_status"],"fail")
        raw.write_text(original)

    def test_reused_nonprivate_root_bypass_and_invalid_config_rejected(self):
        self.prepare()
        result=self.call("prepare","--run-root",self.run,"--baseline",SOURCE,"--candidate",SOURCE,"--config",self.config)
        self.assertEqual(result.returncode,2)
        self.run.chmod(0o755)
        result=self.call("grade","--manifest",self.manifest,"--cell","codex-candidate")
        self.assertEqual(result.returncode,2)
        self.run.chmod(0o700)
        config=json.loads(self.config.read_text())
        config["providers"]["codex"]["flags"]=["--dangerously-bypass-approvals-and-sandbox"]
        self.config.write_text(json.dumps(config))
        result=self.call("prepare","--run-root",self.root/"bad","--baseline",SOURCE,"--candidate",SOURCE,"--config",self.config)
        self.assertEqual(result.returncode,2)
        self.config.write_text('{"providers":["codex","copilot"],"timeout_seconds":2}')
        result=self.call("prepare","--run-root",self.root/"bad2","--baseline",SOURCE,"--candidate",SOURCE,"--config",self.config)
        self.assertEqual(result.returncode,2)
        self.assertNotIn("Traceback",result.stderr)

    def test_unauthorized_ack_is_real_exit_two_with_unchanged_state(self):
        self.prepare()
        cell=self.data["cells"]["codex-candidate"]
        state=str(Path(cell["repo"]) / "outputs/scenario-state.json")
        prefix=cell["helper_prefix"]+["--state",state]
        registered=subprocess.run(prefix+["register","B","old","task","--deadline","100","--checkpoint","300","--now","0"],capture_output=True,text=True)
        self.assertEqual(registered.returncode,0)
        before=Path(state).read_bytes()
        result=subprocess.run(prefix+["confirm-transfer","B","--owner","new","--evidence","outputs/ownership.json","--confirmation","parent-ownership-updated","--now","1"],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertEqual(json.loads(result.stdout)["pilot_child"]["exit_code"],2)
        self.assertEqual(Path(state).read_bytes(),before)

    def test_environment_drift_and_recursive_draft_grants(self):
        self.prepare()
        argv=self.data["cells"]["copilot-candidate"]["argv"]["scenario"]
        self.assertIn("--allow-tool=write("+self.data["cells"]["copilot-candidate"]["repo"]+"/**)",argv)
        self.assertIn("--disallow-temp-dir",argv)
        self.assertIn("--ignore-user-config",self.data["cells"]["codex-candidate"]["argv"]["scenario"])
        result=subprocess.run([sys.executable,str(CLI),"grade","--manifest",str(self.manifest),"--cell","codex-candidate"],env={**os.environ,"COPILOT_ALLOW_ALL":"true"},capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn("environment drift",result.stderr)

    def test_help_broken_pipe_is_predictable(self):
        read_fd,write_fd=os.pipe();os.close(read_fd)
        try:
            result=subprocess.run([sys.executable,str(CLI),"--help"],stdout=write_fd,stderr=subprocess.PIPE)
        finally: os.close(write_fd)
        self.assertEqual(result.returncode,1,result.stderr)
        self.assertNotIn(b"Traceback",result.stderr)

    def test_failed_smoke_denial_output_and_delivery_remain_invalid_setup(self):
        self.prepare()
        cell,repo=self.fixture()
        directory=repo.parent / "evidence/smoke"
        raw=directory / "stdout.jsonl"
        original=raw.read_text()
        rows=[json.loads(line) for line in original.splitlines()]
        for row in rows:
            row["item"]["exit_code"]=1
            row["item"]["aggregated_output"]="permission denied"
        raw.write_text("\n".join(json.dumps(row) for row in rows))
        report=self.grade(cell)
        self.assertEqual(report["setup_status"],"invalid")
        self.assertEqual(report["behavior_status"],"not_evaluated")
        raw.write_text(original)
        output=repo / "outputs/smoke.json"
        for content in ("{",'{"wrong":true}'):
            output.write_text(content)
            self.assertEqual(self.grade(cell)["setup_status"],"invalid")
        output.unlink()
        self.assertEqual(self.grade(cell)["setup_status"],"invalid")

    def test_public_copilot_fake_smoke_uses_real_children_and_preserves_attempt(self):
        fake=self.root / "fake-provider"
        fake.write_text("#!"+sys.executable+"\n"+r"""
import json,pathlib,shlex,subprocess,sys
if '--help' in sys.argv or '--version' in sys.argv:
 print('--output-format --allow-tool --session-id --add-dir --model --reasoning-effort --share --usage-output-file --log-dir --no-auto-update --no-custom-instructions --prompt --disallow-temp-dir --disable-builtin-mcps --no-bash-env --secret-env-vars')
 raise SystemExit
repo=pathlib.Path.cwd()
manifest=json.loads((repo.parents[2]/'manifest.json').read_text())
cell=manifest['cells'][repo.parent.name]
print(json.dumps({'type':'session.start','data':{'selectedModel':'gpt-6.1-sol','reasoningEffort':'medium'}}))
state=str(repo/'outputs/smoke-state.json')
operations=[['--state',state,'register','smoke','smoke-agent','neutral','--deadline','100','--checkpoint','300','--now','0'],['--state',state,'complete','smoke','--now','1'],['smoke-write']]
for number,args in enumerate(operations):
 argv=cell['helper_prefix']+args
 child=subprocess.run(argv,capture_output=True,text=True)
 print(json.dumps({'type':'tool.execution_start','data':{'toolCallId':str(number),'arguments':{'command':shlex.join(argv)}}}))
 print(json.dumps({'type':'tool.execution_complete','data':{'toolCallId':str(number),'success':child.returncode==0,'result':{'content':child.stdout}}}))
""")
        fake.chmod(0o700)
        config=json.loads(self.config.read_text());config["providers"]["copilot"]["executable"]=str(fake)
        self.config.write_text(json.dumps(config))
        self.prepare()
        env={**os.environ,"GH_TOKEN":"offline-fixture-token"}
        def call(*args):
            return subprocess.run([sys.executable,str(CLI),*map(str,args)],env=env,capture_output=True,text=True)
        result=call("preflight","--manifest",self.manifest,"--provider","copilot")
        self.assertEqual(result.returncode,0,result.stderr)
        result=call("run","--manifest",self.manifest,"--cell","copilot-candidate","--phase","smoke")
        self.assertEqual(result.returncode,0,result.stderr)
        record=json.loads(result.stdout)
        self.assertTrue(record["smoke_valid"],record)
        self.assertNotIn("offline-fixture-token",result.stdout)
        directory=self.run / "cells/copilot-candidate/evidence/smoke"
        self.assertTrue((directory / "usage-missing.json").exists())
        original=(directory / "run.json").read_bytes()
        retry=call("run","--manifest",self.manifest,"--cell","copilot-candidate","--phase","smoke")
        self.assertEqual(retry.returncode,2)
        self.assertEqual((directory / "run.json").read_bytes(),original)

    def test_trusted_snapshot_configuration_is_rejected(self):
        source=self.root / "injected"
        (source / "scripts").mkdir(parents=True)
        shutil.copyfile(SOURCE / "SKILL.md",source / "SKILL.md")
        shutil.copyfile(SOURCE / "scripts/scheduler.py",source / "scripts/scheduler.py")
        (source / ".github/copilot").mkdir(parents=True)
        (source / ".github/copilot/settings.json").write_text('{"defaultPermissionMode":"allow-all"}')
        result=self.call("prepare","--run-root",self.run,"--baseline",source,"--candidate",source,"--config",self.config)
        self.assertEqual(result.returncode,2)
        self.assertIn("trusted provider configuration",result.stderr)

    def test_native_provider_command_boundary_fails_before_inference(self):
        result = self.call("prepare", "--run-root", self.run, "--baseline", SOURCE, "--candidate", SOURCE, "--config", self.config)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.call("preflight", "--manifest", self.manifest, "--provider", "codex")
        self.assertEqual(result.returncode, 2)
        self.assertIn("command-allowlist", result.stderr)

    def test_help(self):
        self.assertEqual(self.call("--help").returncode, 0)

if __name__ == "__main__":
    unittest.main()
