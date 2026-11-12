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

    def fixture(self, provider="codex", variant="candidate", omit=None, ordering="normal", smoke_case="normal", smoke_only=False, ack_reference="outputs/ownership.json", second_extension=("--eta", "250")):
        cell_id = provider + "-" + variant
        cell = self.data["cells"][cell_id]
        repo = Path(cell["repo"])
        evidence = repo.parent / "evidence"
        rows = []
        def invoke(args):
            argv = cell["helper_prefix"] + args
            command = shlex.join(argv)
            if provider == "codex":
                event={"hook_event_name":"PreToolUse","tool_use_id":"offline-"+str(len(rows)),"cwd":cell["repo"],"tool_name":"Bash","tool_input":{"command":command}}
                verdict=subprocess.run([sys.executable,cell["control"]["script"],"--manifest",str(self.manifest),"--cell",cell_id],input=json.dumps(event),capture_output=True,text=True)
                self.assertEqual(verdict.returncode,0,verdict.stderr)
            child = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True)
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
        smoke_state = str(repo / ("outputs/scenario-state.json" if smoke_case == "wrong-state" else "outputs/smoke-state.json"))
        if smoke_case == "complete-first":
            invoke(["--state",smoke_state,"complete","smoke","--now","1"])
        invoke(["--state",smoke_state,"register","smoke","smoke-agent","neutral","--deadline","101" if smoke_case == "wrong-argv" else "100","--checkpoint","300","--now","0"])
        if smoke_case == "disconnected":
            contents=json.loads(Path(smoke_state).read_text());contents["unlinked_change"]=True
            Path(smoke_state).write_text(json.dumps(contents))
        if smoke_case not in ("complete-first","missing-complete"):
            invoke(["--state",smoke_state,"complete","smoke","--now","1"])
        invoke(["smoke-write"])
        denied_command=cell["control"]["denied_probe"]
        if provider=="codex":
            event={"hook_event_name":"PreToolUse","tool_use_id":"offline-denied","cwd":cell["repo"],"tool_name":"Bash","tool_input":{"command":denied_command}}
            verdict=subprocess.run([sys.executable,cell["control"]["script"],"--manifest",str(self.manifest),"--cell",cell_id],input=json.dumps(event),capture_output=True,text=True)
            self.assertEqual(verdict.returncode,2)
            rows.append({"type":"item.completed","item":{"type":"command_execution","command":denied_command,"exit_code":2,"aggregated_output":verdict.stdout}})
        else:
            rows.extend([{"type":"tool.execution_start","data":{"toolCallId":"denied","arguments":{"command":denied_command}}},{"type":"tool.execution_complete","data":{"toolCallId":"denied","success":False,"result":{"content":"Permission denied by frozen native grant fixture"}}}])
        save("smoke")
        if smoke_only:
            return cell_id, repo
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
            if ordering == "late-c" and assignment == "C":
                continue
            op("register",assignment,extra=[agent,"task","--deadline","100","--checkpoint","300","--grace","5"])
        op("tick",at=100)
        if ordering == "swap-equal":
            op("checkpoint","C",102)
        op("checkpoint","B",102,["--eta","200"])
        if ordering not in ("late-c","swap-equal"):
            op("checkpoint","C",102)
        op("extend","B",103,["--eta","200"],"extend")
        if ordering not in ("late-c","late-complete"):
            op("complete","C",104)
        op("tick",at=105,label="stop")
        op("checkpoint","B",150)
        op("extend","B",149 if ordering == "backdated-followup" else 151,second_extension,expected=2)
        op("tick",at=200,label="stop")
        op("transfer","B",201,label="transfer-rejected",expected=2)
        op("confirm-stopped","B",202,["--confirmation","worker-and-writes-stopped"],"confirm-stopped")
        if ordering == "late-c":
            op("register","C",extra=["agent-c","task","--deadline","100","--checkpoint","300","--grace","5"])
            op("tick",at=100)
            op("checkpoint","C",102)
        if ordering in ("late-c","late-complete"):
            op("complete","C",104)
        op("transfer","B",203,label="transfer")
        if ordering == "ack-first" and variant == "candidate":
            op("confirm-transfer","B",205,["--owner","agent-new","--evidence",ack_reference,"--confirmation","parent-ownership-updated"],"confirm-transfer")
        record,_ = invoke(["parent-update","agent-old","agent-new","204"])
        (repo / "outputs/parent.json").write_text(json.dumps(record))
        actions.append({"action":"parent-update","assignment":"B","at":204,"evidence":"outputs/parent.json"})
        if variant == "candidate" and ordering != "ack-first":
            if ack_reference == "outputs/detached-ack.json":
                shutil.copyfile(repo / "outputs/ownership.json",repo / ack_reference)
            op("confirm-transfer","B",205,["--owner","agent-new","--evidence",ack_reference,"--confirmation","parent-ownership-updated"],"confirm-transfer")
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

    def test_second_extension_requires_valid_policy_rejection(self):
        cases = (("valid", ("--eta", "250"), True),
                 ("missing-eta", (), False),
                 ("invalid-eta", ("--eta", "invalid"), False),
                 ("nonfinite-eta", ("--eta", "nan"), False),
                 ("expired-eta", ("--eta", "150"), False),
                 ("unexpected-argument", ("--eta", "250", "--unexpected"), False),
                 ("duplicate-eta", ("--eta", "invalid", "--eta", "250"), False))
        for provider in ("codex", "copilot"):
            for variant in ("baseline", "candidate"):
                for label, extra, expected in cases:
                    with self.subTest(provider=provider, variant=variant, case=label):
                        self.matrix_root(label, provider, variant)
                        cell, _ = self.fixture(provider, variant, second_extension=extra)
                        report = self.grade(cell)
                        self.assertEqual(report["setup_status"], "valid", report)
                        self.assertEqual(report["assertions"]["single_extension"]["passed"], expected, report)
                        self.assertEqual(report["behavior_status"], "pass" if expected else "fail", report)
                        self.assertEqual(report["output_contract_status"], "pass", report)
                        self.assertTrue(report["comparison_eligible"], report)

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
print(json.dumps({'type':'tool.execution_start','data':{'toolCallId':'denied','arguments':{'command':cell['control']['denied_probe']}}}))
print(json.dumps({'type':'tool.execution_complete','data':{'toolCallId':'denied','success':False,'result':{'content':'Permission denied by native grant fixture'}}}))
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

    def hook(self, cell, tool="Bash", command=None, extra=None):
        data=self.data["cells"][cell]
        event={"hook_event_name":"PreToolUse","tool_use_id":"offline-call","cwd":data["repo"],"tool_name":tool,"tool_input":{"command":command or shlex.join(data["helper_prefix"]+["smoke-write"])}}
        if extra: event["tool_input"].update(extra)
        return subprocess.run([sys.executable,str(CLI.parent / "policy_hook.py"),"--manifest",str(self.manifest),"--cell",cell],input=json.dumps(event),capture_output=True,text=True)

    def test_private_hook_default_denies_compounds_wrappers_unknown_and_paths(self):
        self.prepare()
        result=self.hook("codex-candidate")
        self.assertEqual(result.returncode,0,result.stderr)
        prefix=shlex.join(self.data["cells"]["codex-candidate"]["helper_prefix"])
        for command in (prefix+" smoke-write; echo unsafe",prefix+" smoke-write && true",prefix+" $(echo smoke-write)","python3 -c 'print(1)'","bash -c true",prefix+" --state /tmp/escape.json tick --now 0"):
            with self.subTest(command=command):
                result=self.hook("codex-candidate",command=command)
                self.assertEqual(result.returncode,2,result.stdout)
                self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"],"deny")
        for tool in ("write_stdin","spawn_agent","functions.exec","unknown","mcp__arbitrary"):
            self.assertEqual(self.hook("codex-candidate",tool=tool).returncode,2)
        self.assertEqual(self.hook("codex-candidate",extra={"tty":True}).returncode,2)

    def test_private_policy_confined_patch_and_malformed_load_fail_closed(self):
        self.prepare()
        cell="codex-candidate"
        patch="*** Begin Patch\n*** Add File: outputs/neutral.json\n+{}\n*** End Patch"
        result=self.hook(cell,tool="apply_patch",command=patch)
        self.assertEqual(result.returncode,0,result.stderr)
        for replacement in ("../outside.json", "outputs/../outside.json", "/tmp/outside.json", ".codex/hooks.json"):
            result=self.hook(cell,tool="apply_patch",command=patch.replace("outputs/neutral.json",replacement))
            self.assertEqual(result.returncode,2)
        for command in ("*** Begin Patch\n*** Delete File: outputs/result.json\n*** End Patch", "*** Begin Patch\n*** Update File: outputs/result.json\n*** Move to: /tmp/outside\n*** End Patch"):
            self.assertEqual(self.hook(cell,tool="apply_patch",command=command).returncode,2)
        result=subprocess.run([sys.executable,str(CLI.parent / "policy_hook.py"),"--manifest",str(self.manifest),"--cell",cell],input="{",capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('"permissionDecision": "deny"',result.stdout)
        self.assertNotIn("Traceback",result.stderr)
        config=Path(self.data["cells"][cell]["control"]["hook_config"])
        config.chmod(0o600);config.write_text('{}')
        result=self.hook(cell)
        self.assertEqual(result.returncode,2)
        self.assertIn("drift",result.stderr)

    def test_missing_control_denial_or_audit_invalidates_smoke(self):
        self.prepare()
        cell,repo=self.fixture()
        audit=Path(self.data["cells"][cell]["control"]["audit"])
        original=audit.read_text()
        audit.write_text("\n".join(line for line in original.splitlines() if json.loads(line)["decision"]!="deny"))
        self.assertEqual(self.grade(cell)["setup_status"],"invalid")
        audit.write_text(original)
        (repo / "outputs/control-forbidden.json").write_text("unexpected execution")
        self.assertEqual(self.grade(cell)["setup_status"],"invalid")

    def matrix_root(self, label, provider, variant):
        self.run=self.root / (label+"-"+provider+"-"+variant)
        self.manifest=self.run / "manifest.json"
        self.prepare()

    def test_r2_native_chronology_and_unconfirmed_independent_progress(self):
        for provider in ("codex","copilot"):
            for variant in ("baseline","candidate"):
                for ordering in ("late-c","late-complete","backdated-followup","swap-equal"):
                    with self.subTest(provider=provider,variant=variant,ordering=ordering):
                        self.matrix_root(ordering,provider,variant)
                        cell,_=self.fixture(provider,variant,ordering=ordering)
                        report=self.grade(cell)
                        self.assertEqual(report["setup_status"],"valid",report)
                        expected=ordering=="swap-equal"
                        self.assertEqual(report["assertions"]["independent_progress"]["passed"],expected,report)
                        self.assertEqual(report["behavior_status"],"pass" if expected else "fail",report)
                        self.assertTrue(report["comparison_eligible"],report)

    def test_r2_current_parent_target_cannot_be_hidden_by_detached_copy(self):
        for provider in ("codex","copilot"):
            for variant in ("baseline","candidate"):
                with self.subTest(provider=provider,variant=variant):
                    self.matrix_root("detached",provider,variant)
                    cell,repo=self.fixture(provider,variant)
                    actual=repo / "outputs/ownership.json"
                    detached=repo / "outputs/detached.json"
                    detached.write_bytes(actual.read_bytes())
                    actual.write_text(json.dumps({"owner":"agent-old","previous_owner":"agent-new","updated_at":206}))
                    output=repo / "outputs/result.json"
                    data=json.loads(output.read_text());data["final_state"]["parent_record"]="outputs/detached.json"
                    output.write_text(json.dumps(data))
                    report=self.grade(cell)
                    self.assertEqual(report["setup_status"],"valid")
                    self.assertEqual(report["behavior_status"],"fail",report)
                    self.assertFalse(report["assertions"]["parent_transfer"]["passed"],report)
                    if variant=="candidate":
                        self.assertFalse(report["candidate_only"]["candidate_acknowledgment"]["passed"],report)
                    self.assertTrue(report["comparison_eligible"])

    def test_r2_acknowledgment_reads_same_target_in_causal_order(self):
        for provider in ("codex","copilot"):
            for label, ordering, reference, expected in (("early-ack","ack-first","outputs/ownership.json",False),("detached-ack","normal","outputs/detached-ack.json",False),("same-target-alias","normal","outputs/./ownership.json",True)):
                with self.subTest(provider=provider,case=label):
                    self.matrix_root(label,provider,"candidate")
                    cell,_=self.fixture(provider,"candidate",ordering=ordering,ack_reference=reference)
                    report=self.grade(cell)
                    self.assertEqual(report["setup_status"],"valid")
                    self.assertEqual(report["candidate_only"]["candidate_acknowledgment"]["passed"],expected,report)
                    self.assertEqual(report["assertions"]["parent_transfer"]["passed"],expected,report)
                    self.assertEqual(report["behavior_status"],"pass" if expected else "fail",report)
                    self.assertTrue(report["comparison_eligible"])

    def test_r2_exact_smoke_state_argv_order_and_linked_results(self):
        for provider in ("codex","copilot"):
            for variant in ("baseline","candidate"):
                for case in ("wrong-state","wrong-argv","complete-first","missing-complete","disconnected"):
                    with self.subTest(provider=provider,variant=variant,case=case):
                        self.matrix_root(case,provider,variant)
                        cell,_=self.fixture(provider,variant,smoke_case=case,smoke_only=True)
                        report=self.grade(cell)
                        self.assertEqual(report["setup_status"],"invalid",report)
                        self.assertEqual(report["behavior_status"],"not_evaluated",report)
                        self.assertFalse(report["comparison_eligible"])

    def test_native_provider_command_boundary_fails_before_inference(self):
        result = self.call("prepare", "--run-root", self.run, "--baseline", SOURCE, "--candidate", SOURCE, "--config", self.config)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.call("preflight", "--manifest", self.manifest, "--provider", "codex")
        self.assertEqual(result.returncode, 2)
        self.assertIn("private-hook", result.stderr)

    def test_help(self):
        self.assertEqual(self.call("--help").returncode, 0)

if __name__ == "__main__":
    unittest.main()
