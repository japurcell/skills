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

    def assert_invalid_diagnostics(self, report):
        self.assertEqual(report["setup_status"], "invalid", report)
        self.assertEqual(report["behavior_status"], "not_evaluated", report)
        self.assertFalse(report["comparison_eligible"], report)
        self.assertTrue(report["invalid_reasons"], report)

    def assert_behavior_diagnostics(self, report, expected):
        self.assert_invalid_diagnostics(report)
        claims=list(report["assertions"].values()) + list(report["candidate_only"].values())
        passed=all(claim["passed"] for claim in claims) and report.get("execution_status")=="success"
        self.assertEqual(passed, expected=="pass", report)

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
                    self.assert_behavior_diagnostics(report, "pass")

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
                        self.assert_invalid_diagnostics(report)
                        self.assertEqual(report["assertions"]["single_extension"]["passed"], expected, report)
                        self.assert_behavior_diagnostics(report, "pass" if expected else "fail")
                        self.assertEqual(report["output_contract_status"], "pass", report)
                        self.assertFalse(report["comparison_eligible"], report)

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
                self.assert_behavior_diagnostics(self.grade(cell),"fail")
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
        self.assert_behavior_diagnostics(report, "fail")
        self.assertFalse(report["assertions"]["immutable_execution"]["passed"])

    def test_smoke_gate_and_hash_drift_fail_closed(self):
        self.prepare()
        cell,_=self.fixture()
        result=self.call("run","--manifest",self.manifest,"--cell",cell,"--phase","scenario")
        self.assertEqual(result.returncode,2)
        self.assertIn("qualification",result.stderr)
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
                self.assert_behavior_diagnostics(report, "fail")
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
                self.assert_behavior_diagnostics(self.grade(cell),"fail")
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
        self.assertNotIn("--ignore-user-config",self.data["cells"]["codex-candidate"]["argv"]["scenario"])
        self.assertEqual(self.data["cells"]["codex-candidate"]["environment"]["CODEX_HOME"],str(Path(self.data["cells"]["codex-candidate"]["environment"]["HOME"])/".codex"))
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
        self.assertFalse(report["diagnostic_smoke_checks"]["register"])
        self.assertFalse(report["diagnostic_smoke_checks"]["complete"])
        raw.write_text(original)
        output=repo / "outputs/smoke.json"
        for content in ("{",'{"wrong":true}'):
            output.write_text(content)
            report=self.grade(cell)
            self.assertEqual(report["setup_status"],"invalid")
            self.assertFalse(report["diagnostic_smoke_checks"]["exact_output"])
        output.unlink()
        self.assertEqual(self.grade(cell)["setup_status"],"invalid")

    def copilot_setup(self, mode="normal", native=False):
        (self.root / "copilot-mode").write_text(mode)
        fake=self.root / "fake-provider"
        fake.write_text("#!"+sys.executable+"\n"+r"""
import json,pathlib,shlex,subprocess,sys
if '--version' in sys.argv:
 print('GitHub Copilot CLI 1.0.109.');raise SystemExit
if '--help' in sys.argv:
 print('--headless --stdio --available-tools --sync-session --trust-folder --output-format --allow-tool --session-id --add-dir --model --reasoning-effort --share --usage-output-file --log-dir --no-auto-update --no-custom-instructions --prompt --disallow-temp-dir --disable-builtin-mcps --no-bash-env --secret-env-vars')
 raise SystemExit
repo=pathlib.Path.cwd()
mode=(repo.parents[3]/'copilot-mode').read_text()
if sys.argv[1:3]==['config','--list']:
 print(json.dumps({'memory':False,'modelProviderId':'copilot',**({'allowAllTools':True} if mode=='native-unsafe-setting' else {})}));raise SystemExit
if sys.argv[1:3]==['skill','list']:
 print(json.dumps([{'name':'inherited' if mode!='native-skill-drift' else 'changed','path':str(pathlib.Path.home()/'.agents/skills/inherited'),'source':'personal-agents','enabled':True,'description':'excluded'}]));raise SystemExit
if sys.argv[1:3]==['config','--repo']:
 settings=json.loads((repo/'.github/copilot/settings.json').read_text())
 print(json.dumps(dict(settings,customAgents={'defaultLocalOnly':True})));raise SystemExit
manifest=json.loads((repo.parents[2]/'manifest.json').read_text())
cell=manifest['cells'][repo.parent.name]
if '--headless' in sys.argv:
 import os,time,signal
 (repo/'outputs/status-server.pid').write_text(str(os.getpid()))
 if mode=='native-timeout':
  child=subprocess.Popen([sys.executable,'-c','import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(30)'])
  (repo/'outputs/status-child.pid').write_text(str(child.pid));time.sleep(30)
 while True:
  header=sys.stdin.buffer.readline()
  if not header:break
  length=int(header.split(b':')[1]);sys.stdin.buffer.readline()
  request=json.loads(sys.stdin.buffer.read(length));method=request['method']
  result={'version':'1.0.109','protocolVersion':3}
  if method=='auth.getStatus': result={'isAuthenticated':mode!='native-unavailable','authType':'user','login':'private-account-never-retain','host':'private-host-never-retain','statusMessage':'private-status-never-retain'}
  if method=='models.list': result={'models':[{'id':'gpt-6.1-sol','supportedReasoningEfforts':['medium']} ]}
  row={'jsonrpc':'2.0','id':99 if mode=='native-wrong-id' else request['id'],'result':result}
  if mode=='native-malformed': row={'id':request['id'],'result':'invalid'}
  raw=json.dumps(row).encode();sys.stdout.buffer.write(('Content-Length: '+str(len(raw))+'\r\n\r\n').encode()+raw);sys.stdout.buffer.flush()
 raise SystemExit
if cell.get('authentication',{}).get('mode')=='native-existing-login':
 import os
 (repo/'outputs/native-environment.json').write_text(json.dumps({'HOME':os.environ.get('HOME'),'COPILOT_HOME':os.environ.get('COPILOT_HOME'),'auth_names':[k for k in ('GH_TOKEN','GITHUB_TOKEN','COPILOT_GITHUB_TOKEN') if k in os.environ]}))
phase='smoke'  if sys.argv[sys.argv.index('--session-id')+1]==cell['session_ids']['smoke'] else 'scenario'
mode=(repo.parents[3]/'copilot-mode').read_text()
if mode=='malformed': print('{')
if mode=='unknown': print(json.dumps({'type':'tool.unrecognized','data':{}}))
print(json.dumps({'type':'session.start','data':{'sessionId':'wrong' if mode=='wrong-session' else cell['session_ids'][phase],'context':{'cwd':str(repo)},'selectedModel':'wrong' if mode=='wrong-model' else 'gpt-6.1-sol','reasoningEffort':None if mode=='missing-effort' else 'medium'}}))

def write_artifact(relative,value):
 text=json.dumps(value)+'\n'
 path=repo/relative
 patch='*** Begin Patch\n*** Add File: '+relative+'\n'+''.join('+'+line+'\n' for line in text.splitlines())+'*** End Patch\n'
 if mode=='traversal': patch=patch.replace('*** Add File: outputs/','*** Add File: outputs/../outputs/',1)
 if mode=='absolute-patch': patch=patch.replace('*** Add File: '+relative,'*** Add File: '+str(path),1)
 if mode=='nonoutputs-patch': patch=patch.replace('*** Add File: outputs/','*** Add File: ./outputs/',1)
 key='patch-'+relative
 print(json.dumps({'type':'tool.execution_start','data':{'toolCallId':key,'toolName':'apply_patch','turnId':'0','arguments':patch}}))
 path.write_text(text)
 print(json.dumps({'type':'tool.execution_complete','data':{'toolCallId':key,'turnId':'0','success':True,'fileEdits':[{'path':str(repo/relative.replace('outputs/','outputs/../outputs/',1)) if mode=='traversal' else str(path),'kind':'create'}],'result':{'content':'Patch applied'}}}))
if phase=='scenario':
 state=str(repo/'outputs/scenario-state.json')
 actions=[]
 number=0
 def invoke(args,label=None,assignment=None,at=None):
  global number
  argv=cell['helper_prefix']+args
  command=shlex.join(argv)
  key='scenario-'+str(number);number+=1
  print(json.dumps({'type':'tool.execution_start','data':{'toolCallId':key,'toolName':'bash','turnId':'0','arguments':{'command':command}}}))
  child=subprocess.run(argv,capture_output=True,text=True)
  print(json.dumps({'type':'tool.execution_complete','data':{'toolCallId':key,'turnId':'0','success':child.returncode==0,'result':{'content':child.stdout}}}))
  if label:
   relative='outputs/'+label+'-'+str(at)+'.json'
   write_artifact(relative,{'command':command,'exit_code':child.returncode})
   actions.append({'action':label,'assignment':assignment,'at':at,'evidence':relative})
 def op(command,assignment=None,at=0,extra=(),label=None):
  invoke(['--state',state,command]+([assignment] if assignment else [])+list(extra)+['--now',str(at)],label,assignment or ('A' if at==105 else 'B'),at)
 for assignment,agent in (('A','agent-a'),('B','agent-old'),('C','agent-c')):
  op('register',assignment,extra=[agent,'task','--deadline','100','--checkpoint','300','--grace','5'])
 op('tick',at=100)
 op('checkpoint','B',102,['--eta','200'])
 op('checkpoint','C',102)
 op('extend','B',103,['--eta','200'],'extend')
 op('complete','C',104)
 op('tick',at=105,label='stop')
 op('checkpoint','B',150)
 op('extend','B',151,['--eta','250'])
 op('tick',at=200,label='stop')
 op('transfer','B',201,label='transfer-rejected')
 op('confirm-stopped','B',202,['--confirmation','worker-and-writes-stopped'],'confirm-stopped')
 op('transfer','B',203,label='transfer')
 invoke(['parent-update','agent-old','agent-new','204'],'parent-update','B',204)
 if cell['variant']=='candidate': op('confirm-transfer','B',205,['--owner','agent-new','--evidence','outputs/ownership.json','--confirmation','parent-ownership-updated'],'confirm-transfer')
 write_artifact('outputs/result.json',{'actions':actions,'final_state':{'old_owner':'agent-old','new_owner':'agent-new','worker_stopped':True,'writes_stopped':True,'transfer_authorized':True,'parent_record':'outputs/ownership.json','scheduler_state':'outputs/scenario-state.json'}})
 raise SystemExit

state=str(repo/'outputs/smoke-state.json')
operations=[['--state',state,'register','smoke','smoke-agent','neutral','--deadline','100','--checkpoint','300','--now','0'],['--state',state,'complete','smoke','--now','1'],['smoke-write']]
for number,args in enumerate(operations):
 argv=cell['helper_prefix']+args
 child=subprocess.run(argv,capture_output=True,text=True)
 print(json.dumps({'type':'tool.execution_start','data':{'toolCallId':str(number),'toolName':'write_stdin' if mode=='unknown-tool' else 'bash','model':'wrong' if mode=='tool-model' else 'gpt-6.1-sol','turnId':'0','arguments':{'command':shlex.join(argv)}}}))
 if mode!='missing-completion': print(json.dumps({'type':'tool.execution_complete','data':{'toolCallId':str(number),'turnId':'0','success':child.returncode==0,'result':{'content':child.stdout}}}))
 if mode=='duplicate': print(json.dumps({'type':'tool.execution_complete','data':{'toolCallId':str(number),'turnId':'0','success':True,'result':{'content':child.stdout}}}))
print(json.dumps({'type':'tool.execution_start','data':{'toolCallId':'denied','toolName':'bash','turnId':'0','arguments':{'command':cell['control']['denied_probe']}}}))
print(json.dumps({'type':'tool.execution_complete','data':{'toolCallId':'denied','turnId':'0','success':False,'result':{'content':'Permission denied by native grant fixture'}}}))
""")
        fake.chmod(0o700)
        config=json.loads(self.config.read_text());config["providers"]["copilot"]["executable"]=str(fake)
        if native: config["providers"]["copilot"]["authentication"]={"mode":"native-existing-login"}
        self.config.write_text(json.dumps(config))
        self.prepare()
        result=self.provider_call("preflight","--manifest",self.manifest,"--provider","copilot")
        self.assertEqual(result.returncode,2 if mode in ("native-unavailable","native-malformed","native-wrong-id","native-timeout") else 0,result.stderr)

    def provider_call(self, *args):
        return subprocess.run([sys.executable,str(CLI),*map(str,args)],env={**os.environ,"GH_TOKEN":"offline-fixture-token"},capture_output=True,text=True)

    def test_public_native_login_uses_standard_lookup_without_process_tokens(self):
        settings=Path.home()/'.copilot/settings.json'
        before=settings.read_bytes() if settings.exists() else None
        self.copilot_setup(native=True)
        for variant in ('baseline','candidate'):
            cell=self.data['cells']['copilot-'+variant]
            self.assertEqual(cell['authentication']['mode'],'native-existing-login')
            self.assertEqual(cell['environment']['HOME'],str(Path.home().resolve()))
            self.assertNotIn('--no-bash-env',cell['argv']['smoke'])
            self.assertIn('--trust-folder',cell['argv']['smoke'])
            self.assertIn('--sync-session=off',cell['argv']['smoke'])
            self.assertIn('--available-tools',cell['argv']['smoke'])
            override=json.loads((Path(cell['repo'])/'.github/copilot/settings.json').read_text())
            self.assertTrue(override['disableAllHooks'])
            self.assertEqual(override['disabledSkills'],['inherited'])
            result=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-'+variant,'--phase','smoke')
            self.assertEqual(result.returncode,0,result.stderr+result.stdout)
            record=json.loads(result.stdout)
            self.assertEqual(record['auth_environment_names'],[])
            env=json.loads((Path(cell['repo'])/'outputs/native-environment.json').read_text())
            self.assertEqual(env['auth_names'],[])
        for variant in ('baseline','candidate'):
            result=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-'+variant,'--phase','scenario')
            self.assertEqual(result.returncode,0,result.stderr+result.stdout)
            self.assertEqual(self.grade('copilot-'+variant)['behavior_status'],'pass')
        receipt=(self.run/'preflight/copilot.json').read_text()
        for private in ('private-account-never-retain','private-host-never-retain','private-status-never-retain','offline-fixture-token',hashlib.sha256(b'offline-fixture-token').hexdigest()):
            self.assertNotIn(private,receipt)
        for variant in ('baseline','candidate'):
            self.assertNotIn('--trust-folder',json.loads(receipt)['cells']['copilot-'+variant]['argv'])
        context=json.loads((self.run/'provider-context.json').read_text())
        self.assertFalse(any(path.endswith('/.copilot/config.json') for path in context['config_hashes']))
        self.assertEqual(settings.read_bytes() if settings.exists() else None,before)

    def test_public_native_status_failures_and_skill_drift_stay_closed(self):
        for mode in ('native-unavailable','native-malformed','native-wrong-id','native-timeout'):
            with self.subTest(mode=mode):
                self.run=self.root/mode;self.manifest=self.run/'manifest.json'
                self.copilot_setup(mode,native=True)
                receipt=json.loads((self.run/'preflight/copilot.json').read_text())
                self.assertFalse(receipt['smoke_ready'])
                self.assertFalse(receipt['scenario_ready'])
                if mode=='native-timeout':
                    for variant in ('baseline','candidate'):
                        pid=int((self.run/('cells/copilot-'+variant+'/repo/outputs/status-child.pid')).read_text())
                        with self.assertRaises(ProcessLookupError):os.kill(pid,0)
        self.run=self.root/'native-drift';self.manifest=self.run/'manifest.json'
        self.copilot_setup(native=True)
        for mode in ('native-skill-drift','native-unsafe-setting'):
            (self.root/'copilot-mode').write_text(mode)
            result=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-candidate','--phase','smoke')
            self.assertEqual(result.returncode,2)
            self.assertFalse((self.run/'cells/copilot-candidate/evidence/smoke').exists())

    def test_public_native_status_interruption_and_repo_layer_rejection(self):
        self.copilot_setup(native=True)
        (self.root/'copilot-mode').write_text('native-timeout')
        process=subprocess.Popen([sys.executable,str(CLI),'preflight','--manifest',str(self.manifest),'--provider','copilot'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        pid_file=self.run/'cells/copilot-baseline/repo/outputs/status-child.pid'
        for _ in range(300):
            if pid_file.exists():break
            time.sleep(.01)
        self.assertTrue(pid_file.exists())
        process.send_signal(signal.SIGINT)
        stdout,stderr=process.communicate(timeout=5)
        self.assertEqual(process.returncode,130,stderr)
        with self.assertRaises(ProcessLookupError):os.kill(int(pid_file.read_text()),0)
        (self.root/'copilot-mode').write_text('normal')
        repo=Path(self.data['cells']['copilot-candidate']['repo'])
        extra=repo/'.github/instructions/unsafe.md';extra.parent.mkdir();extra.write_text('extra instructions')
        rejected=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-candidate','--phase','smoke')
        self.assertEqual(rejected.returncode,2)
        self.assertIn('unexpected repository',rejected.stderr)
        extra.unlink();extra.parent.rmdir()
        override=repo/'.github/copilot/settings.json';override.chmod(0o600)
        settings=json.loads(override.read_text());settings['disabledSkills']=[];override.write_text(json.dumps(settings))
        rejected=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-candidate','--phase','smoke')
        self.assertEqual(rejected.returncode,2)
        self.assertIn('drift',rejected.stderr)

    def test_public_copilot_fake_smoke_uses_real_children_and_preserves_attempt(self):
        self.copilot_setup()
        call=self.provider_call
        result=call("preflight","--manifest",self.manifest,"--provider","copilot")
        self.assertEqual(result.returncode,0,result.stderr)
        result=call("run","--manifest",self.manifest,"--cell","copilot-candidate","--phase","smoke")
        self.assertEqual(result.returncode,0,result.stderr)
        record=json.loads(result.stdout)
        self.assertTrue(record["smoke_valid"],record)
        self.assertEqual(record["acceptance_contract"],"verified-observed-run")
        self.assertEqual(record["schema_version"],1)
        self.assertEqual(json.loads((self.run / "cells/copilot-candidate/repo/outputs/smoke.json").read_text()),{"smoke":True})
        self.assertNotIn("offline-fixture-token",result.stdout)
        directory=self.run / "cells/copilot-candidate/evidence/smoke"
        self.assertTrue((directory / "usage-missing.json").exists())
        original=(directory / "run.json").read_bytes()
        retry=call("run","--manifest",self.manifest,"--cell","copilot-candidate","--phase","smoke")
        self.assertEqual(retry.returncode,2)
        self.assertEqual((directory / "run.json").read_bytes(),original)

    def test_public_copilot_malformed_and_unsupported_events_stop_remaining_calls(self):
        for mode in ('malformed','unknown','wrong-session','wrong-model','missing-effort','unknown-tool','missing-completion','duplicate','tool-model'):
            with self.subTest(mode=mode):
                self.run=self.root / ('copilot-'+mode)
                self.manifest=self.run / 'manifest.json'
                self.copilot_setup(mode)
                failed=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-candidate','--phase','smoke')
                self.assertEqual(failed.returncode,2,failed.stderr)
                receipt=json.loads(failed.stdout)
                self.assertFalse(receipt['smoke_valid'])
                self.assertTrue(receipt['invalid_reasons'])
                blocked=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-baseline','--phase','smoke')
                self.assertEqual(blocked.returncode,2)
                self.assertIn('remaining provider calls stopped',blocked.stderr)
                self.assertFalse((self.run/'cells/copilot-baseline/evidence/smoke').exists())

    def test_public_copilot_patch_lexical_traversal_invalidates_qualification(self):
        for mode in ('traversal','absolute-patch','nonoutputs-patch'):
            with self.subTest(mode=mode):
                self.run=self.root/('patch-'+mode)
                self.manifest=self.run/'manifest.json'
                self.copilot_setup(mode)
                for variant in ('baseline','candidate'):
                    smoke=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-'+variant,'--phase','smoke')
                    self.assertEqual(smoke.returncode,0,smoke.stderr)
                scenario=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-candidate','--phase','scenario')
                self.assertEqual(scenario.returncode,2,scenario.stdout+scenario.stderr)
                record=json.loads(scenario.stdout)
                self.assertTrue(any('lexical' in reason for reason in record['invalid_reasons']),record)
                report=self.grade('copilot-candidate')
                self.assert_invalid_diagnostics(report)
                self.assertTrue(all(claim['passed'] for claim in report['assertions'].values()),report)
                self.assertTrue(all(claim['passed'] for claim in report['candidate_only'].values()),report)

    def test_public_copilot_both_smokes_replay_bindings_and_raw_regrading(self):
        self.copilot_setup()
        early=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-candidate','--phase','scenario')
        self.assertEqual(early.returncode,2)
        for variant in ('baseline','candidate'):
            smoke=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-'+variant,'--phase','smoke')
            self.assertEqual(smoke.returncode,0,smoke.stderr)
        for variant in ('baseline','candidate'):
            scenario=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-'+variant,'--phase','scenario')
            self.assertEqual(scenario.returncode,0,scenario.stderr+scenario.stdout)
            report=self.grade('copilot-'+variant)
            self.assertEqual(report['setup_status'],'valid',report)
            self.assertEqual(report['behavior_status'],'pass',report)
            self.assertTrue(report['comparison_eligible'],report)
            self.assertTrue(all(claim['passed'] for claim in report['assertions'].values()),report)
        directory=self.run/'cells/copilot-candidate/evidence/smoke'
        record=json.loads((directory/'run.json').read_text())
        self.assertEqual(len(record['approved_payload_sha256']),64)
        self.assertEqual(record['provider'],'copilot')
        for key in ('attempt_id','caller_sources','selected_sources','environment','executable','python','provider_version','audit_interval','raw_stdout_sha256','native_events_sha256'):
            self.assertIn(key,record)
        raw=directory/'stdout.jsonl'
        original=raw.read_text()
        raw.write_text(original+'{\n')
        report=self.grade('copilot-candidate')
        self.assert_invalid_diagnostics(report)
        self.assertIn('raw-evidence-drift',report['invalid_reasons'])
        blocked=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-candidate','--phase','scenario')
        self.assertEqual(blocked.returncode,2)
        self.assertIn('two-smoke',blocked.stderr)
        raw.write_text(original)
        data=json.loads((directory/'run.json').read_text())
        data['cell']='copilot-baseline'
        (directory/'run.json').write_text(json.dumps(data))
        self.assertIn('phase-bindings-drift',self.grade('copilot-candidate')['invalid_reasons'])

    def test_public_codex_native_mode_requires_metadata(self):
        config=json.loads(self.config.read_text())
        config['providers']['codex']['authentication']={'mode':'native-existing-login'}
        self.config.write_text(json.dumps(config))
        baseline=self.root/'v2'
        (baseline/'scripts').mkdir(parents=True)
        shutil.copyfile(SOURCE/'SKILL.md',baseline/'SKILL.md')
        shutil.copyfile(CLI.parent/'fixtures/v2-scheduler.py',baseline/'scripts/scheduler.py')
        result=self.call('prepare','--run-root',self.run,'--baseline',baseline,'--candidate',SOURCE,'--config',self.config)
        self.assertEqual(result.returncode,2)
        self.assertNotIn('authentication mode',result.stderr)
        self.assertIn('unsupported native Codex version',result.stderr)

    def native_codex_setup(self, mode="normal"):
        (self.root/"native-mode").write_text(mode)
        fake=self.root/'native-codex'
        fake.write_text('#!'+sys.executable+'\n'+r'''
import json,sys,tomllib,pathlib,os
with (pathlib.Path.cwd().parents[3]/'native-pids').open('a') as log:log.write(str(os.getpid())+'\n')
if '--version' in sys.argv:print('codex-cli 0.167.1');raise SystemExit
if '--help' in sys.argv:print('--json --model --sandbox --cd --add-dir --output-last-message --enable');raise SystemExit
if sys.argv[1:]==['login','status']:print('Logged in using ChatGPT');raise SystemExit
mode=(pathlib.Path.cwd().parents[3]/'native-mode').read_text()
config={'mcp_servers':{'fixture':{'enabled':True,'required':True,'env':{'TOKEN':'fixture-sensitive'}}},'plugins':{'fixture@bundle':{'enabled':True}},'features':{}}
def merge(target,source):
 for key,value in source.items():
  if isinstance(value,dict):merge(target.setdefault(key,{}),value)
  else:target[key]=value
for i,arg in enumerate(sys.argv):
 if arg=='-c':
  key,value=sys.argv[i+1].split('=',1)
  merge(config,tomllib.loads('.'.join(json.dumps(part) for part in key.split('.'))+'='+value))
for line in sys.stdin:
 q=json.loads(line);method=q['method']
 if method=='initialized':continue
 result={}
 if method=='config/read':result={'config':config,'layers':[{'name':{'type':'user','file':str(pathlib.Path.home()/'.codex/config.toml')}},{'name':{'type':'project','dotCodexFolder':str(pathlib.Path.cwd()/'.codex')},'disabledReason':None if mode=='trusted' else 'untrusted project'}]}
 if method=='skills/list':result={'data':[{'cwd':str(pathlib.Path.cwd()),'errors':[],'skills':[{'path':'/fixture/SKILL.md','scope':'user','enabled':not bool(config.get('skills',{}).get('config'))}]}]}
 if method=='hooks/list':result={'data':[{'cwd':str(pathlib.Path.cwd()),'errors':[],'warnings':[],'hooks':[{'source':'user','sourcePath':'/fixture/hooks.json','key':'disabled','eventName':'sessionStart','handlerType':'command','enabled':False,'currentHash':'sha256:fixture','trustStatus':'trusted'}]}]}
 if method=='model/list':result={'data':[{'id':'gpt-6.1-sol','supportedReasoningEfforts':[{'reasoningEffort':'medium'}]}]}
 if method=='hooks/list' and mode=='trusted':
  path=pathlib.Path.cwd()/'.codex/hooks.json';hook=json.loads(path.read_text())['hooks']['PreToolUse'][0]['hooks'][0]
  result['data'][0]['hooks'].append(dict(source='project',sourcePath=str(path),key=str(path)+':pre_tool_use:0:0',eventName='preToolUse',handlerType='command',enabled=True,currentHash='sha256:project-fixture',trustStatus='trusted',command=hook['command'],timeoutSec=3,**{'async':False}))
 if method=='config/read' and mode=='enabled-mcp':result['config']['mcp_servers']['fixture']['enabled']=True
 if method=='config/read' and mode=='new-plugin':result['config']['plugins']['extra@bundle']={'enabled':False}
 if method=='config/read' and mode=='wrong-sandbox':result['config']['sandbox_mode']='danger-full-access'
 if method=='config/read' and mode=='wrong-approval':result['config']['approval_policy']='on-request'
 if method=='config/read' and mode=='unknown-key':result['config']['unknown_instructions']='unsafe'
 if method=='skills/list' and mode=='skill-drift':result['data'][0]['skills'][0]['path']='/changed/SKILL.md'
 if method=='hooks/list' and mode=='hook-hash':result['data'][0]['hooks'][0]['currentHash']='sha256:changed'
 if method=='config/read' and mode=='new-mcp':result['config']['mcp_servers']['extra']={'enabled':False}
 if method=='config/read' and mode=='unsafe-instructions':result['config']['instructions']='unsafe'
 if method=='config/read' and mode=='unknown-layer':result['layers'].append({'name':{'type':'unknown'}})
 if method=='config/read' and mode=='wrong-provider':result['config']['model_provider']='other'
 if method=='hooks/list' and mode=='active-user-hook':result['data'][0]['hooks'][0]['enabled']=True
 print(json.dumps({'id':q['id'],'result':result}),flush=True)
''')
        fake.chmod(0o700)
        config=json.loads(self.config.read_text())
        config['providers']['codex'].update(executable=str(fake),authentication={'mode':'native-existing-login'})
        self.config.write_text(json.dumps(config))
        self.prepare()

    def test_public_codex_native_freezes_disabled_components_and_blocks_untrusted_policy(self):
        self.native_codex_setup()
        for variant in ('baseline','candidate'):
            cell=self.data['cells']['codex-'+variant]
            self.assertEqual(cell['environment']['HOME'],str(Path.home().resolve()))
            self.assertEqual(cell['native_inventory']['mcp_servers'],['fixture'])
            self.assertFalse(cell['safe_config']['mcp_servers']['fixture']['enabled'])
            self.assertFalse(cell['safe_config']['plugins']['fixture@bundle']['enabled'])
            shell=Path(cell['shell_home'])
            self.assertEqual(list(shell.iterdir()),[])
            self.assertFalse(shell.stat().st_mode & 0o222)
            self.assertEqual(cell['safe_config']['shell_environment_policy']['set']['HOME'],str(shell))
            self.assertNotIn('fixture-sensitive',self.manifest.read_text())
            self.assertFalse(cell['native_preparation']['setup_ready'])
        result=self.call('preflight','--manifest',self.manifest,'--provider','codex')
        self.assertEqual(result.returncode,2,result.stdout)
        self.assertIn('hook',result.stderr)
        shell=Path(self.data['cells']['codex-candidate']['shell_home'])
        shell.chmod(0o700)
        (shell/'.zshenv').write_text('unsafe')
        drift=self.call('preflight','--manifest',self.manifest,'--provider','codex')
        self.assertIn('shell startup directory drift',drift.stderr)

    def test_public_codex_native_ready_metadata_and_drift_fail_closed(self):
        self.native_codex_setup()
        (self.root/'native-mode').write_text('trusted')
        result=self.call('preflight','--manifest',self.manifest,'--provider','codex')
        self.assertEqual(result.returncode,0,result.stderr)
        receipt=json.loads(result.stdout)
        self.assertTrue(receipt['setup_ready'])
        self.assertFalse(receipt['scenario_ready'])
        for mode in ('new-mcp','enabled-mcp','new-plugin','wrong-sandbox','wrong-approval','unknown-key','skill-drift','hook-hash','unsafe-instructions','unknown-layer','wrong-provider','active-user-hook'):
            with self.subTest(mode=mode):
                (self.root/'native-mode').write_text(mode)
                result=self.call('preflight','--manifest',self.manifest,'--provider','codex')
                self.assertEqual(result.returncode,2,result.stdout)
        for pid in (self.root/'native-pids').read_text().splitlines():
            with self.assertRaises(ProcessLookupError):
                os.kill(int(pid),0)

    def test_public_codex_native_tmp_root_disables_implicit_sandbox_grants(self):
        temporary=tempfile.TemporaryDirectory(dir='/private/tmp')
        self.addCleanup(temporary.cleanup)
        config=json.loads(self.config.read_text())
        self.root=Path(temporary.name)
        self.config=self.root/'config.json'
        self.config.write_text(json.dumps(config))
        self.run=self.root/'run'
        self.manifest=self.run/'manifest.json'
        self.native_codex_setup()
        for cell_id in ('codex-baseline','codex-candidate'):
            cell=self.data['cells'][cell_id]
            sandbox=cell['safe_config']['sandbox_workspace_write']
            self.assertTrue(sandbox['exclude_slash_tmp'])
            self.assertTrue(sandbox['exclude_tmpdir_env_var'])
            self.assertEqual(sandbox['writable_roots'],cell['write_roots'])
            self.assertFalse(any(Path(cell['shell_home']).is_relative_to(root) for root in cell['write_roots']))

    def codex_setup(self, mode="normal"):
        (self.root / "discovery-mode").write_text(mode)
        fake = self.root / "fake-codex"
        fake.write_text("#!" + sys.executable + "\n" + r"""
import json,os,pathlib,shlex,subprocess,sys
if '--version' in sys.argv:
 print('offline-codex 1'); raise SystemExit
if '--help' in sys.argv:
 print('--json --model --sandbox --cd --add-dir --output-last-message --ignore-user-config --ignore-rules --enable'); raise SystemExit
repo=pathlib.Path.cwd()
manifest=json.loads((repo.parents[2]/'manifest.json').read_text())
cell=manifest['cells'][repo.parent.name]
mode=(repo.parents[3]/'discovery-mode').read_text()
if 'app-server' in sys.argv:
 for line in sys.stdin:
  request=json.loads(line); method=request['method']
  if method=='initialized': continue
  result={}
  if mode=='eof': raise SystemExit
  if mode=='timeout' or (mode=='notification-timeout' and method=='hooks/list'):
   if mode=='notification-timeout': print(json.dumps({'method':'remoteControl/status/changed','params':{'status':'disabled'}}),flush=True)
   import time,signal
   child=subprocess.Popen([sys.executable,'-c','import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(30)'])
   (repo/'outputs/discovery-child.pid').write_text(str(child.pid))
   time.sleep(30)
  if mode=='malformed': print('{',flush=True);continue
  if mode=='rpc-error': print(json.dumps({'id':request['id'],'error':{'code':-1,'message':'offline'}}),flush=True);continue
  if method=='hooks/list' and mode in ('notification-active','notification-unknown','notification-malformed','notification-bad-timestamp','wrong-reply','duplicate-reply'):
   if mode=='wrong-reply': print(json.dumps({'id':99,'result':{}}),flush=True)
   elif mode=='duplicate-reply': print(json.dumps({'id':1,'result':{}}),flush=True)
   else: print(json.dumps({'method':'unknown/native/event' if mode=='notification-unknown' else 'remoteControl/status/changed','params':[] if mode=='notification-malformed' else {'status':'enabled' if mode=='notification-active' else 'disabled'},'emittedAtMs':{} if mode=='notification-bad-timestamp' else 0}),flush=True)
  if method=='hooks/list' and mode in ('notification-disabled','configuration-warning','notification-truncated-eof'):
   if mode=='configuration-warning': print(json.dumps({'method':'configWarning','params':{'summary':'offline-auth-adjacent-sensitive-summary','details':None},'emittedAtMs':0}),flush=True)
   print(json.dumps({'method':'remoteControl/status/changed','params':{'status':'disabled','serverName':None,'installationId':None,'environmentId':None},'emittedAtMs':0}),flush=True)
  if method=='hooks/list':
   hook=json.loads(pathlib.Path(cell['control']['hook_config']).read_text())['hooks']['PreToolUse'][0]['hooks'][0]
   result={'data':[{'cwd':str(repo),'errors':[],'warnings':[],'hooks':[dict(handlerType='command',command=hook['command'],timeoutSec=3,enabled=True,eventName='preToolUse',source='project',sourcePath=cell['control']['hook_config'],currentHash='sha256:offline-native-definition',trustStatus='trusted',key=cell['control']['hook_config']+':pre_tool_use:0:0',**{'async':False})]}]}
  if method=='config/read':
   result={'config':cell['safe_config'],'layers':[{'name':{'type':'system','file':'/etc/codex/config.toml'},'config':{}}],'origins':{}}
  if method=='hooks/list':
   h=result['data'][0]['hooks'][0]
   if mode in ('untrusted','modified'): h['trustStatus']=mode
   if mode=='disabled': h['enabled']=False
   if mode=='unexpected': result['data'][0]['hooks'].append(dict(h))
   if mode=='wrong-source': h['sourcePath']='/outside/hooks.json'
   if mode=='changed-hash': h['currentHash']='sha256:changed-native-definition'
  if method=='config/read' and mode=='wrong-model': result['config']['model']='wrong'
  if method=='config/read' and mode=='notification-truncated-eof':
   (repo/'outputs/discovery-server.pid').write_text(str(os.getpid()))
   sys.stdout.write(json.dumps({'id':request['id'],'result':result})+'\n'+json.dumps({'method':'remoteControl/status/changed','params':{'status':'enabled'}}))
   sys.stdout.flush();os.close(1)
   import time;time.sleep(30)
   raise SystemExit
  print(json.dumps({'id':request['id'],'result':result}),flush=True)
  if method=='config/read' and mode=='duplicate-final': print(json.dumps({'id':request['id'],'result':result}),flush=True)
 raise SystemExit
if sys.argv[1:]==['login','status']:
 print('Logged in using ChatGPT');raise SystemExit
prompt=sys.stdin.read()
print(json.dumps({'type':'thread.started','thread_id':'offline-exec-thread'}))
(repo/'outputs/launch.json').write_text(json.dumps({'stdin':prompt,'env':dict(os.environ),'argv':sys.argv}))
state=str(repo/'outputs/smoke-state.json')
for number,args in enumerate((['--state',state,'register','smoke','smoke-agent','neutral','--deadline','100','--checkpoint','300','--now','0'],['--state',state,'complete','smoke','--now','1'],['smoke-write'])):
 argv=cell['helper_prefix']+args
 command=shlex.join(argv)
 event={'hook_event_name':'PreToolUse','tool_use_id':'offline-native-tool-'+str(number),'cwd':cell['repo'],'tool_name':'Bash','tool_input':{'command':command}}
 verdict=subprocess.run([sys.executable,cell['control']['script'],'--manifest',manifest['root']+'/manifest.json','--cell',repo.parent.name],input=json.dumps(event),capture_output=True,text=True)
 child=subprocess.run(argv,capture_output=True,text=True)
 item={'id':'item_'+str(number),'type':'command_execution','command':command}
 print(json.dumps({'type':'item.started','item':item}))
 print(json.dumps({'type':'item.completed','item':dict(item,exit_code=child.returncode,aggregated_output=child.stdout)}))
command=cell['control']['denied_probe']
event={'hook_event_name':'PreToolUse','tool_use_id':'offline-denied','cwd':cell['repo'],'tool_name':'Bash','tool_input':{'command':command}}
verdict=subprocess.run([sys.executable,cell['control']['script'],'--manifest',manifest['root']+'/manifest.json','--cell',repo.parent.name],input=json.dumps(event),capture_output=True,text=True)
item={'id':'item_denied','type':'command_execution','command':command}
print(json.dumps({'type':'item.started','item':item}))
print(json.dumps({'type':'item.completed','item':dict(item,exit_code=verdict.returncode,aggregated_output=verdict.stdout)}))
""")
        fake.chmod(0o700)
        config=json.loads(self.config.read_text())
        config['providers']['codex']['executable']=str(fake)
        self.config.write_text(json.dumps(config))
        self.prepare()

    def test_public_codex_setup_opens_only_unqualified_smoke_with_frozen_stdin(self):
        self.codex_setup()
        preflight=self.call('preflight','--manifest',self.manifest,'--provider','codex')
        launch=self.call('run','--manifest',self.manifest,'--cell','codex-candidate','--phase','smoke')
        self.assertEqual(preflight.returncode,0,preflight.stderr + launch.stderr)
        receipt=json.loads(preflight.stdout)
        self.assertTrue(receipt['setup_ready'])
        self.assertTrue(receipt['smoke_ready'])
        self.assertFalse(receipt['scenario_ready'])
        cell=self.data['cells']['codex-candidate']
        delivered=json.loads((Path(cell['repo'])/'outputs/launch.json').read_text())
        self.assertEqual(delivered['stdin'],Path(cell['prompts']['smoke']).read_text())
        self.assertEqual(delivered['env']['CODEX_HOME'],str(Path(cell['environment']['HOME'])/'.codex'))
        self.assertFalse(set(delivered['env']) & {'GH_TOKEN','GITHUB_TOKEN','COPILOT_GITHUB_TOKEN'})
        record=json.loads(launch.stdout)
        self.assertFalse(record['smoke_valid'])
        self.assertEqual(launch.returncode,2)
        self.assertEqual(json.loads((Path(cell['repo'])/'outputs/smoke.json').read_text()),{'smoke':True})
        scenario=self.call('run','--manifest',self.manifest,'--cell','codex-candidate','--phase','scenario')
        self.assertEqual(scenario.returncode,2)
        self.assertIn('qualification',scenario.stderr)

    def test_public_codex_disabled_startup_notification_preserves_reply_correlation(self):
        self.codex_setup('notification-disabled')
        result=self.call('preflight','--manifest',self.manifest,'--provider','codex')
        self.assertEqual(result.returncode,0,result.stderr)
        receipt=json.loads(result.stdout)
        self.assertTrue(receipt['setup_ready'])
        self.assertFalse(receipt['scenario_ready'])
        for variant in ('baseline','candidate'):
            discovery=receipt['cells']['codex-'+variant]
            self.assertEqual(discovery['notifications'],[{'method':'remoteControl/status/changed','status':'disabled'}])
            self.assertEqual([row['id'] for row in discovery['safe_responses']],[1,2,3])

    def test_public_codex_eof_with_pending_notification_invalidates_setup(self):
        self.codex_setup('notification-truncated-eof')
        result=self.call('preflight','--manifest',self.manifest,'--provider','codex')
        self.assertEqual(result.returncode,2,result.stderr)
        receipt=json.loads((self.run/'preflight/codex.json').read_text())
        self.assertFalse(receipt['setup_ready'])
        self.assertFalse(receipt['smoke_ready'])
        self.assertFalse(receipt['scenario_ready'])
        self.assertIn('truncated trailing discovery notification',result.stderr)
        for variant in ('baseline','candidate'):
            self.assertEqual(receipt['cells']['codex-'+variant]['notifications'],[{'method':'remoteControl/status/changed','status':'disabled'}])
            pid=int((self.run/('cells/codex-'+variant+'/repo/outputs/discovery-server.pid')).read_text())
            with self.assertRaises(ProcessLookupError): os.kill(pid,0)

    def test_public_codex_startup_notification_failures_are_safe_and_closed(self):
        for mode in ('configuration-warning','notification-active','notification-unknown','notification-malformed','notification-bad-timestamp','wrong-reply','duplicate-reply','duplicate-final','rpc-error','notification-timeout'):
            with self.subTest(mode=mode):
                self.run=self.root/('startup-'+mode)
                self.manifest=self.run/'manifest.json'
                self.codex_setup(mode)
                result=self.call('preflight','--manifest',self.manifest,'--provider','codex')
                self.assertEqual(result.returncode,2,result.stdout)
                receipt=json.loads((self.run/'preflight/codex.json').read_text())
                self.assertFalse(receipt['setup_ready'])
                self.assertFalse(receipt['smoke_ready'])
                self.assertFalse(receipt['scenario_ready'])
                self.assertNotIn('offline-auth-adjacent-sensitive-summary',result.stderr+(self.run/'preflight/codex.json').read_text())
                if mode=='configuration-warning':
                    self.assertIn('configuration-warning',result.stderr)
                    self.assertEqual(receipt['cells']['codex-baseline']['notifications'],[{'method':'configWarning','classification':'configuration-warning','summary_present':True,'details_present':True}])
                if mode=='notification-timeout':
                    for variant in ('baseline','candidate'):
                        pid=int((self.run/('cells/codex-'+variant+'/repo/outputs/discovery-child.pid')).read_text())
                        with self.assertRaises(ProcessLookupError): os.kill(pid,0)

    def test_public_codex_notification_wait_interruption_reaps_descendant(self):
        self.codex_setup('notification-timeout')
        process=subprocess.Popen([sys.executable,str(CLI),'preflight','--manifest',str(self.manifest),'--provider','codex'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        pid_file=self.run/'cells/codex-baseline/repo/outputs/discovery-child.pid'
        for _ in range(200):
            if pid_file.exists(): break
            time.sleep(.01)
        self.assertTrue(pid_file.exists())
        process.send_signal(signal.SIGINT)
        stdout,stderr=process.communicate(timeout=5)
        self.assertEqual(process.returncode,130,stderr)
        with self.assertRaises(ProcessLookupError): os.kill(int(pid_file.read_text()),0)

    def test_public_codex_discovery_rejects_incomplete_untrusted_and_unexpected_setup(self):
        for mode in ('eof','malformed','rpc-error','untrusted','modified','disabled','unexpected','wrong-source','wrong-model','timeout'):
            with self.subTest(mode=mode):
                self.run=self.root / ('run-' + mode)
                self.manifest=self.run / 'manifest.json'
                self.codex_setup(mode)
                result=self.call('preflight','--manifest',self.manifest,'--provider','codex')
                self.assertEqual(result.returncode,2,result.stdout)
                receipt=json.loads((self.run/'preflight/codex.json').read_text())
                self.assertFalse(receipt['smoke_ready'])
                self.assertFalse(receipt['scenario_ready'])
                launch=self.call('run','--manifest',self.manifest,'--cell','codex-candidate','--phase','smoke')
                self.assertEqual(launch.returncode,2)
                self.assertFalse((self.run/'cells/codex-candidate/repo/outputs/launch.json').exists())
                if mode=='timeout':
                    for variant in ('baseline','candidate'):
                        pid=int((self.run/('cells/codex-'+variant+'/repo/outputs/discovery-child.pid')).read_text())
                        with self.assertRaises(ProcessLookupError):
                            os.kill(pid,0)

    def test_public_codex_receipt_audit_intervals_and_unsupported_native_evidence(self):
        self.codex_setup()
        preflight=self.call('preflight','--manifest',self.manifest,'--provider','codex')
        self.assertEqual(preflight.returncode,0,preflight.stderr)
        # A real preexisting audit prefix must be preserved and independently hashed.
        self.assertEqual(self.hook('codex-candidate').returncode,0)
        launched=self.call('run','--manifest',self.manifest,'--cell','codex-candidate','--phase','smoke')
        self.assertEqual(launched.returncode,2,launched.stderr)
        record=json.loads(launched.stdout)
        self.assertTrue(any('native-evidence-unsupported' in reason for reason in record['invalid_reasons']))
        self.assertNotIn('audit-command-count-mismatch',record['invalid_reasons'])
        self.assertGreater(record['audit_interval']['start'],0)
        self.assertGreater(record['audit_interval']['end'],record['audit_interval']['start'])
        self.assertTrue(all(record['smoke_checks'][key] for key in ('control_loaded','control_denial','register','complete','write_readback')))
        audit=Path(self.data['cells']['codex-candidate']['control']['audit'])
        original=audit.read_bytes()
        changed=bytearray(original);changed[10]=ord('X')
        audit.write_bytes(changed)
        report=self.grade('codex-candidate')
        self.assertIn('audit-prefix-or-range-drift',report['invalid_reasons'])
        audit.write_bytes(original+b'{}\n')
        self.assertIn('audit-records-outside-phase',self.grade('codex-candidate')['invalid_reasons'])
        audit.write_bytes(original)

    def test_public_setup_binding_drift_blocks_launch_before_child(self):
        for mode in ('private-home','executable','provider-receipt','current-hash'):
            with self.subTest(mode=mode):
                self.run=self.root/('binding-'+mode)
                self.manifest=self.run/'manifest.json'
                self.codex_setup()
                preflight=self.call('preflight','--manifest',self.manifest,'--provider','codex')
                self.assertEqual(preflight.returncode,0,preflight.stderr)
                cell=self.data['cells']['codex-candidate']
                if mode=='private-home': Path(cell['environment']['CODEX_HOME']).rmdir()
                if mode=='executable':
                    fake=Path(cell['requested_settings']['executable']);fake.write_text(fake.read_text()+'\n# drift\n')
                if mode=='provider-receipt':
                    p=self.run/'preflight/codex.json';receipt=json.loads(p.read_text());receipt['provider']='copilot';p.write_text(json.dumps(receipt))
                if mode=='current-hash': (self.root/'discovery-mode').write_text('changed-hash')
                result=self.call('run','--manifest',self.manifest,'--cell','codex-candidate','--phase','smoke')
                self.assertEqual(result.returncode,2)
                self.assertFalse((Path(cell['repo'])/'outputs/launch.json').exists())

    def test_public_discovery_interruption_reaps_server_and_descendant(self):
        self.codex_setup('timeout')
        process=subprocess.Popen([sys.executable,str(CLI),'preflight','--manifest',str(self.manifest),'--provider','codex'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        pid_file=self.run/'cells/codex-baseline/repo/outputs/discovery-child.pid'
        for _ in range(200):
            if pid_file.exists(): break
            time.sleep(.01)
        self.assertTrue(pid_file.exists())
        process.send_signal(signal.SIGINT)
        stdout,stderr=process.communicate(timeout=5)
        self.assertEqual(process.returncode,130,stderr)
        with self.assertRaises(ProcessLookupError): os.kill(int(pid_file.read_text()),0)

    def test_public_partial_attempt_blocks_provider_without_child(self):
        self.copilot_setup()
        partial=self.run/'cells/copilot-baseline/evidence/smoke'
        partial.mkdir()
        (partial/'attempt.json').write_text('{}')
        blocked=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-candidate','--phase','smoke')
        self.assertEqual(blocked.returncode,2)
        self.assertIn('remaining provider calls stopped',blocked.stderr)
        self.assertFalse((self.run/'cells/copilot-candidate/repo/outputs/smoke.json').exists())

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
        report=self.grade(cell)
        self.assertEqual(report["setup_status"],"invalid")
        self.assertFalse(report["diagnostic_smoke_checks"]["control_loaded"])
        audit.write_text(original)
        (repo / "outputs/control-forbidden.json").write_text("unexpected execution")
        report=self.grade(cell)
        self.assertEqual(report["setup_status"],"invalid")
        self.assertFalse(report["diagnostic_smoke_checks"]["forbidden_write_absent"])

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
                        self.assert_invalid_diagnostics(report)
                        expected=ordering=="swap-equal"
                        self.assertEqual(report["assertions"]["independent_progress"]["passed"],expected,report)
                        self.assert_behavior_diagnostics(report, "pass" if expected else "fail")
                        self.assertFalse(report["comparison_eligible"], report)

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
                    self.assert_invalid_diagnostics(report)
                    self.assert_behavior_diagnostics(report, "fail")
                    self.assertFalse(report["assertions"]["parent_transfer"]["passed"],report)
                    if variant=="candidate":
                        self.assertFalse(report["candidate_only"]["candidate_acknowledgment"]["passed"],report)
                    self.assertFalse(report["comparison_eligible"], report)

    def test_r2_acknowledgment_reads_same_target_in_causal_order(self):
        for provider in ("codex","copilot"):
            for label, ordering, reference, expected in (("early-ack","ack-first","outputs/ownership.json",False),("detached-ack","normal","outputs/detached-ack.json",False),("same-target-alias","normal","outputs/./ownership.json",True)):
                with self.subTest(provider=provider,case=label):
                    self.matrix_root(label,provider,"candidate")
                    cell,_=self.fixture(provider,"candidate",ordering=ordering,ack_reference=reference)
                    report=self.grade(cell)
                    self.assert_invalid_diagnostics(report)
                    self.assertEqual(report["candidate_only"]["candidate_acknowledgment"]["passed"],expected,report)
                    self.assertEqual(report["assertions"]["parent_transfer"]["passed"],expected,report)
                    self.assert_behavior_diagnostics(report, "pass" if expected else "fail")
                    self.assertFalse(report["comparison_eligible"], report)

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
                        self.assertFalse(report["diagnostic_smoke_checks"]["register"])
                        self.assertFalse(report["diagnostic_smoke_checks"]["complete"])

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
