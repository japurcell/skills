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
        return subprocess.run([sys.executable, str(CLI), *map(str,args)], capture_output=True, text=True, env={**os.environ, **getattr(self,"child_env",{})})

    def prepare(self):
        baseline = self.root / "v2"
        (baseline / "scripts").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / "SKILL.md", baseline / "SKILL.md")
        shutil.copyfile(CLI.parent / "fixtures/v2-scheduler.py", baseline / "scripts/scheduler.py")
        result = self.call("prepare", "--run-root", self.run, "--baseline", baseline, "--candidate", SOURCE, "--config", self.config)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.data = json.loads(self.manifest.read_text())

    def fixture(self, provider="codex", variant="candidate", omit=None, ordering="normal", smoke_case="normal", smoke_only=False, ack_reference="outputs/ownership.json", second_extension=("--eta", "250")):
        if variant == "candidate":
            baseline_evidence = Path(self.data["cells"][provider + "-baseline"]["repo"]).parent / "evidence/smoke/stdout.jsonl"
            if not baseline_evidence.exists():
                self.fixture(provider, "baseline", smoke_case=smoke_case, smoke_only=True)
        cell_id = provider + "-" + variant
        cell = self.data["cells"][cell_id]
        repo = Path(cell["repo"])
        evidence = repo.parent / "evidence"
        rows = []
        def invoke(args):
            argv = cell["helper_prefix"] + args
            command = shlex.join(argv)
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
            (directory / "run.json").write_text(json.dumps({"exit_code":0,"smoke_valid":phase=="smoke", "delivered_prompt_sha256":hashlib.sha256(Path(cell["prompts"].get(phase,self.data["cells"][provider+"-baseline"]["prompts"][phase])).read_bytes()).hexdigest()}))
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

    def test_prompt_hash_drift_fails_closed(self):
        self.prepare()
        cell,_=self.fixture()
        path=Path(self.data["cells"]["codex-baseline"]["prompts"]["smoke"])
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
        cell,repo=self.fixture(variant="baseline")
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
        shutil.copyfile(CLI.parent / "fixtures/copilot-native-envelopes.json", self.root / "native-samples.json")
        fake=self.root / "fake-provider"
        fake.write_text("#!"+sys.executable+"\n"+r"""
import json,pathlib,shlex,subprocess,sys
if '--version' in sys.argv:
 print('GitHub Copilot CLI 1.0.109.');raise SystemExit
if '--help' in sys.argv:
 print('--available-tools --sync-session --trust-folder --output-format --allow-tool --session-id --add-dir --model --reasoning-effort --share --usage-output-file --log-dir --no-auto-update --no-custom-instructions --prompt --disallow-temp-dir --disable-builtin-mcps --no-bash-env --secret-env-vars')
 raise SystemExit
if '--trust-folder' in sys.argv and '--session-id' in sys.argv:
 print('error: --session-id cannot be combined with --trust-folder',file=sys.stderr);raise SystemExit(2)
if '--new-session-id' in sys.argv:
 import uuid
 if any(flag in sys.argv for flag in ('--session-id','--resume','--continue')):
  print('error: conflicting new-session-id option',file=sys.stderr);raise SystemExit(2)
 try:uuid.UUID(sys.argv[sys.argv.index('--new-session-id')+1])
 except ValueError:print('error: invalid session UUID',file=sys.stderr);raise SystemExit(2)
repo=pathlib.Path.cwd()
mode=(repo.parents[3]/'copilot-mode').read_text()
samples=json.loads((repo.parents[3]/'native-samples.json').read_text())['events']
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
session_flag='--new-session-id' if '--new-session-id' in sys.argv else '--session-id'
session_id=sys.argv[sys.argv.index(session_flag)+1]
if session_flag=='--new-session-id':
 sessions=repo.parents[3]/'copilot-sessions';sessions.mkdir(exist_ok=True)
 marker=sessions/session_id
 try:marker.open('x').close()
 except FileExistsError:print('error: session already exists or is in use',file=sys.stderr);raise SystemExit(2)
phase='smoke' if session_id==cell['session_ids'].get('smoke') else 'scenario'
mode=(repo.parents[3]/'copilot-mode').read_text()
if mode=='malformed': print('{')
if mode=='unknown': print(json.dumps({'type':'tool.unrecognized','data':['opaque-observation']}))
start=samples['session.start']
start['data'].update(sessionId='wrong' if mode=='wrong-session' else cell['session_ids'][phase],context={'cwd':repo.as_uri()},selectedModel='wrong' if mode=='wrong-model' else 'gpt-6.1-sol',reasoningEffort=None if mode=='missing-effort' else 'medium')
print(json.dumps(start))
for name in ('session.extensions_loaded','session.tools_updated','session.mcp_servers_loaded','session.usage_checkpoint'):
 if name in samples:print(json.dumps(samples[name]))

def write_artifact(relative,value):
 text=('{"neutral_patch":true}' if relative=='outputs/smoke-patch.json' else json.dumps(value))+'\n'
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
 child=subprocess.CompletedProcess(argv,1,'','') if mode=='actual-denied' else subprocess.run(argv,capture_output=True,text=True)
 if mode=='actual-denied':
  start=samples['tool.execution_start'];start['data']['arguments']['command']=shlex.join(argv);start['data']['toolCallId']=str(number)
  complete=samples['tool.execution_complete'];complete['data']['toolCallId']=str(number)
  print(json.dumps(start));print(json.dumps(complete));continue
 print(json.dumps({'type':'tool.execution_start','data':{'toolCallId':str(number),'toolName':'write_stdin' if mode=='unknown-tool' else 'bash','model':'wrong' if mode=='tool-model' else 'gpt-6.1-sol','turnId':'0','arguments':{'command':shlex.join(argv)}}}))
 if mode!='missing-completion': print(json.dumps({'type':'tool.execution_complete','data':{'toolCallId':str(number),'turnId':'0','success':child.returncode==0,'result':{'content':child.stdout}}}))
 if mode=='duplicate': print(json.dumps({'type':'tool.execution_complete','data':{'toolCallId':str(number),'turnId':'0','success':True,'result':{'content':child.stdout}}}))
if cell.get('authentication',{}).get('mode')=='native-existing-login' and mode!='native-skip-patch':write_artifact('outputs/smoke-patch.json',{'neutral_patch':True})
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

    def test_public_smoke_retains_unknown_observational_telemetry(self):
        self.copilot_setup(mode="unknown")
        self.assertEqual(sum(len(cell["argv"]) for cell in self.data["cells"].values()), 6)
        cell = self.data["cells"]["copilot-baseline"]
        helper = Path(cell["helper_prefix"][0])
        self.assertEqual(helper.read_text().splitlines()[0], "#!" + cell["python_identity"]["path"])
        self.assertEqual(helper.name, "invoke-scheduler")
        for prompt in cell["prompts"].values():
            text = Path(prompt).read_text()
            self.assertIn("directly executable", text)
            self.assertIn("without prepending Python", text)
            self.assertIn(str(helper) + " --state ", text)
        self.assertEqual(helper.stat().st_mode & 0o777, 0o500)
        self.assertIn("--allow-tool=shell(" + str(helper) + ":*)", cell["argv"]["smoke"])
        result = self.provider_call("run", "--manifest", self.manifest,
                                    "--cell", "copilot-baseline", "--phase", "smoke")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        record = json.loads(result.stdout)
        self.assertTrue(record["smoke_valid"], record)

    def test_public_actual_copilot_denied_helper_remains_invalid(self):
        self.copilot_setup(mode="actual-denied")
        result = self.provider_call("run", "--manifest", self.manifest,
                                    "--cell", "copilot-baseline", "--phase", "smoke")
        self.assertEqual(result.returncode, 2, result.stdout)
        record = json.loads(result.stdout)
        self.assertIn("missing-real-child-receipt", record["invalid_reasons"])
        self.assertFalse(record["smoke_valid"])
        repo = Path(self.data["cells"]["copilot-baseline"]["repo"])
        self.assertFalse((repo / "outputs/smoke-state.json").exists())

    def test_public_native_login_uses_standard_lookup_without_process_tokens(self):
        settings=Path.home()/'.copilot/settings.json'
        before=settings.read_bytes() if settings.exists() else None
        self.copilot_setup(native=True)
        for variant in ('baseline',):
            cell=self.data['cells']['copilot-'+variant]
            self.assertEqual(cell['authentication']['mode'],'native-existing-login')
            self.assertEqual(cell['environment']['HOME'],str(Path.home().resolve()))
            self.assertNotIn('--no-bash-env',cell['argv']['smoke'])
            self.assertIn('--trust-folder',cell['argv']['smoke'])
            self.assertIn('--sync-session=off',cell['argv']['smoke'])
            self.assertIn('--available-tools',cell['argv']['smoke'])
            override=json.loads((Path(cell['repo'])/'.github/copilot/settings.json').read_text())
            self.assertTrue(override['disableAllHooks'])
            result=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-'+variant,'--phase','smoke')
            self.assertEqual(result.returncode,0,result.stderr+result.stdout)
            self.assertNotIn('--session-id',cell['argv']['smoke'])
            index=cell['argv']['smoke'].index('--new-session-id')
            self.assertEqual(cell['argv']['smoke'][index+1],cell['session_ids']['smoke'])
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
        self.assertIn('nonsecret_environment_hashes',context)
        self.assertEqual(settings.read_bytes() if settings.exists() else None,before)

    def test_public_native_status_failures_stay_closed(self):
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

    def test_public_native_status_interruption_reaps_descendant(self):
        self.copilot_setup(native=True)
        (self.root / "copilot-mode").write_text("native-timeout")
        process = subprocess.Popen([sys.executable, str(CLI), "preflight", "--manifest", str(self.manifest), "--provider", "copilot"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        pid_file = self.run / "cells/copilot-baseline/repo/outputs/status-child.pid"
        for _ in range(300):
            if pid_file.exists():
                break
            time.sleep(.01)
        self.assertTrue(pid_file.exists())
        process.send_signal(signal.SIGINT)
        stdout, stderr = process.communicate(timeout=5)
        self.assertEqual(process.returncode, 130, stderr)
        with self.assertRaises(ProcessLookupError):
            os.kill(int(pid_file.read_text()), 0)

    def test_public_copilot_fake_smoke_uses_real_children_and_preserves_attempt(self):
        self.copilot_setup()
        call=self.provider_call
        result=call("preflight","--manifest",self.manifest,"--provider","copilot")
        self.assertEqual(result.returncode,0,result.stderr)
        result=call("run","--manifest",self.manifest,"--cell","copilot-baseline","--phase","smoke")
        self.assertEqual(result.returncode,0,result.stderr)
        record=json.loads(result.stdout)
        self.assertTrue(record["smoke_valid"],record)
        self.assertEqual(record["acceptance_contract"],"verified-observed-run")
        self.assertEqual(record["schema_version"],1)
        self.assertEqual(json.loads((self.run / "cells/copilot-baseline/repo/outputs/smoke.json").read_text()),{"smoke":True})
        self.assertNotIn("offline-fixture-token",result.stdout)
        directory=self.run / "cells/copilot-baseline/evidence/smoke"
        self.assertTrue((directory / "usage-missing.json").exists())
        original=(directory / "run.json").read_bytes()
        retry=call("run","--manifest",self.manifest,"--cell","copilot-baseline","--phase","smoke")
        self.assertEqual(retry.returncode,2)
        self.assertEqual((directory / "run.json").read_bytes(),original)

    def test_public_copilot_malformed_authoritative_evidence_stays_invalid(self):
        for mode in ('malformed','wrong-session','wrong-model','missing-effort','unknown-tool','missing-completion','duplicate','tool-model'):
            with self.subTest(mode=mode):
                self.run=self.root / ('copilot-'+mode)
                self.manifest=self.run / 'manifest.json'
                self.copilot_setup(mode)
                failed=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-baseline','--phase','smoke')
                self.assertEqual(failed.returncode,2,failed.stderr)
                receipt=json.loads(failed.stdout)
                self.assertFalse(receipt['smoke_valid'])
                self.assertTrue(receipt['invalid_reasons'])
                blocked=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-baseline','--phase','smoke')
                self.assertEqual(blocked.returncode,2)
                self.assertIn('File exists',blocked.stderr)
                self.assertTrue((self.run/'cells/copilot-baseline/evidence/smoke').exists())


    def test_public_copilot_scenario_replay_bindings_and_raw_regrading(self):
        self.copilot_setup()
        for variant in ('baseline','candidate'):
            scenario=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-'+variant,'--phase','scenario')
            self.assertEqual(scenario.returncode,0,scenario.stderr+scenario.stdout)
            report=self.grade('copilot-'+variant)
            self.assertEqual(report['setup_status'],'valid',report)
            self.assertEqual(report['behavior_status'],'pass',report)
            self.assertTrue(report['comparison_eligible'],report)
            self.assertTrue(all(claim['passed'] for claim in report['assertions'].values()),report)
        directory=self.run/'cells/copilot-candidate/evidence/scenario'
        record=json.loads((directory/'run.json').read_text())
        self.assertEqual(len(record['approved_payload_sha256']),64)
        self.assertEqual(record['provider'],'copilot')
        for key in ('attempt_id','caller_sources','selected_sources','environment','executable','python','provider_version','raw_stdout_sha256','native_events_sha256'):
            self.assertIn(key,record)
        raw=directory/'stdout.jsonl'
        original=raw.read_text()
        raw.write_text(original+'{\n')
        report=self.grade('copilot-candidate')
        self.assert_invalid_diagnostics(report)
        self.assertIn('raw-evidence-drift',report['invalid_reasons'])
        blocked=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-candidate','--phase','scenario')
        self.assertEqual(blocked.returncode,2)
        self.assertIn('File exists',blocked.stderr)
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
(pathlib.Path.cwd().parents[3]/'native-inference').touch()
import datetime,shlex,subprocess
repo=pathlib.Path.cwd();manifest=json.loads((repo.parents[2]/'manifest.json').read_text());cell=manifest['cells'][repo.parent.name]
prompt=sys.stdin.read();phase=pathlib.Path(sys.argv[sys.argv.index('--output-last-message')+1]).parent.name
session=cell['session_ids'][phase];turn='turn-'+session
rollout=pathlib.Path(os.environ['CODEX_HOME'])/'sessions'/('rollout-'+session+'.jsonl');rollout.parent.mkdir(parents=True,exist_ok=True)
rows=[{'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'type':'session_meta','payload':{'id':'wrong' if mode=='wrong-session' else session,'cwd':repo.as_uri(),'originator':'codex_exec','cli_version':'0.167.1','model_provider':'openai'}},{'type':'turn_context','payload':{'turn_id':turn,'cwd':str(repo),'approval_policy':'never','sandbox_policy':dict(type='workspace-write',**cell['safe_config']['sandbox_workspace_write']),'model':'wrong' if mode=='wrong-model' else 'gpt-6.1-sol','effort':None if mode=='missing-effort' else 'medium'}}]
if mode=='missing-context':rows=rows[:1]
if mode=='wrong-cwd':rows[0]['payload']['cwd']='file:///wrong/repo'
native_stdout=[];emit=print
def print(value):native_stdout.append(value)
print(json.dumps({'type':'thread.started','thread_id':session}))
number=0
def identities():
 global number
 number+=1
 return 'call_'+str(number),'item_'+str(number),'exec-'+str(number)
def raw_call(key,source):
 rows.append({'type':'response_item','payload':{'type':'custom_tool_call','call_id':key,'name':'exec','input':source,'internal_chat_message_metadata_passthrough':{'turn_id':turn}}})
def raw_output(key,value):
 rows.append({'type':'response_item','payload':{'type':'custom_tool_call_output','call_id':key,'output':value}})
def write_artifact(relative,value):
 text=('{"neutral_patch":true}' if relative=='outputs/smoke-patch.json' else json.dumps(value))+'\n'
 patch='*** Begin Patch\n*** Add File: '+relative+'\n'+''.join('+'+line+'\n' for line in text.splitlines())+'*** End Patch\n'
 call,item,exec_id=identities();path=repo/relative
 changes=[{'path':str(path),'kind':'add'}]
 print(json.dumps({'type':'item.started','item':{'id':item,'type':'file_change','changes':changes,'status':'in_progress'}}))
 raw_call(call,'text(await tools.apply_patch('+json.dumps(patch)+'));')
 path.write_text(text)
 rows.append({'type':'event_msg','payload':{'type':'item_completed','thread_id':session,'turn_id':turn,'item':{'id':exec_id,'type':'FileChange','changes':{str(path):{'type':'add','content':text}},'status':'completed','stdout':'Success. Updated the following files:\nA '+relative+'\n','stderr':''}}})
 raw_output(call,[{'type':'input_text','text':'Script completed'}])
 print(json.dumps({'type':'item.completed','item':{'id':item,'type':'file_change','changes':changes,'status':'completed'}}))
def invoke(args,label=None,assignment=None,at=None):
 argv=cell['helper_prefix']+args
 if mode in ('python-prefix','wrong-interpreter'):
  argv=['python3']+argv
 elif mode=='absolute-prefix':
  argv=[cell['python_identity']['path']]+argv
 command=shlex.join(argv)
 if mode=='wrong-interpreter':command=shlex.join(['/usr/bin/python3',*argv[1:]])
 if mode=='wrong-helper-argv':command=command.replace('--deadline 100','--deadline 101')
 call,item,_=identities()
 child=subprocess.run(argv,capture_output=True,text=True)
 display=shlex.join(['/bin/zsh','-c',command])
 print(json.dumps({'type':'item.started','item':{'id':item,'type':'command_execution','command':display}}))
 print(json.dumps({'type':'item.completed','item':{'id':item,'type':'command_execution','command':display,'exit_code':child.returncode,'aggregated_output':child.stdout}}))
 raw_call(call,'text(await tools.exec_command({cmd:'+json.dumps(command)+',login:false,tty:false}));');raw_output(call,child.stdout)
 if label:
  relative='outputs/'+label+'-'+str(at)+'.json';write_artifact(relative,{'command':command,'exit_code':child.returncode})
  actions.append({'action':label,'assignment':assignment,'at':at,'evidence':relative})
if phase=='smoke':
 state=str(repo/'outputs/smoke-state.json')
 for args in (['--state',state,'register','smoke','smoke-agent','neutral','--deadline','100','--checkpoint','300','--now','0'],['--state',state,'complete','smoke','--now','1'],['smoke-write']):invoke(args)
 write_artifact('outputs/smoke-patch.json',{'neutral_patch':True})
else:
 state=str(repo/'outputs/scenario-state.json');actions=[]
 def op(command,assignment=None,at=0,extra=(),label=None):
  invoke(['--state',state,command]+([assignment] if assignment else [])+list(extra)+['--now',str(at)],label,assignment or ('A' if at==105 else 'B'),at)
 for assignment,agent in (('A','agent-a'),('B','agent-old'),('C','agent-c')):op('register',assignment,extra=[agent,'task','--deadline','100','--checkpoint','300','--grace','5'])
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
 if cell['variant']=='candidate':op('confirm-transfer','B',205,['--owner','agent-new','--evidence','outputs/ownership.json','--confirmation','parent-ownership-updated'],'confirm-transfer')
 write_artifact('outputs/result.json',{'actions':actions,'final_state':{'old_owner':'agent-old','new_owner':'agent-new','worker_stopped':True,'writes_stopped':True,'transfer_authorized':True,'parent_record':'outputs/ownership.json','scheduler_state':'outputs/scenario-state.json'}})
rollout.write_text(''.join(json.dumps(r)+'\n' for r in rows))
if mode=='proof-overlap':native_stdout[2],native_stdout[3]=native_stdout[3],native_stdout[2]
if mode=='proof-patch-overlap':
 index=next(i for i,line in enumerate(native_stdout) if json.loads(line).get('item',{}).get('type')=='file_change')
 native_stdout[index-1],native_stdout[index]=native_stdout[index],native_stdout[index-1]
for line in native_stdout:emit(line)
raise SystemExit
''')
        fake.chmod(0o700)
        config=json.loads(self.config.read_text())
        config['providers']['codex'].update(executable=str(fake),authentication={'mode':'native-existing-login'})
        self.config.write_text(json.dumps(config))
        self.prepare()




    def test_public_codex_pinned_python_prefix_has_real_child_receipts(self):
        for mode, expected in (("python-prefix", 0), ("absolute-prefix", 0), ("wrong-interpreter", 2), ("wrong-helper-argv", 2)):
            with self.subTest(mode=mode):
                self.run = self.root / mode
                self.manifest = self.run / "manifest.json"
                self.child_env = {"CODEX_HOME": str(self.root / "standard-codex")}
                self.native_codex_setup(mode)
                self.assertEqual(self.call("preflight", "--manifest", self.manifest, "--provider", "codex").returncode, 0)
                result = self.call("run", "--manifest", self.manifest, "--cell", "codex-baseline", "--phase", "smoke")
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                record = json.loads(result.stdout)
                self.assertEqual(record["smoke_valid"], expected == 0)
                if expected:
                    self.assertIn("receipt-from-unmatched-command" if mode == "wrong-interpreter" else "missing-real-child-receipt", record["invalid_reasons"])

    def test_public_codex_companion_context_qualifies_real_helper_smokes(self):
        self.child_env={'CODEX_HOME':str(self.root/'standard-codex')}
        self.native_codex_setup('proof')
        result=self.call('preflight','--manifest',self.manifest,'--provider','codex')
        self.assertEqual(result.returncode,0,result.stderr)
        for variant in ('baseline',):
            result=self.call('run','--manifest',self.manifest,'--cell','codex-'+variant,'--phase','smoke')
            self.assertEqual(result.returncode,0,result.stderr+result.stdout)
            record=json.loads(result.stdout)
            self.assertTrue(record['smoke_valid'],record)


    def test_public_codex_required_identity_remains_invalid(self):
        for mode in ("wrong-session", "wrong-model", "missing-effort", "missing-context", "wrong-cwd"):
            with self.subTest(mode=mode):
                self.run = self.root / mode
                self.manifest = self.run / "manifest.json"
                self.child_env = {"CODEX_HOME": str(self.root / "standard-codex")}
                self.native_codex_setup(mode)
                self.assertEqual(self.call("preflight", "--manifest", self.manifest, "--provider", "codex").returncode, 0)
                result = self.call("run", "--manifest", self.manifest, "--cell", "codex-baseline", "--phase", "smoke")
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertFalse(json.loads(result.stdout)["smoke_valid"])

    def test_public_copilot_create_only_identity_rejects_conflicts_and_reuse(self):
        self.copilot_setup(native=True)
        cell=self.data['cells']['copilot-baseline']
        argv=cell['argv']['smoke']
        for option in ('--session-id','--resume','--continue'):
            extra=[option,cell['session_ids']['smoke']] if option!='--continue' else [option]
            result=subprocess.run(argv+extra,cwd=cell['repo'],env=cell['environment'],capture_output=True,text=True)
            self.assertEqual(result.returncode,2,result.stdout)
            self.assertIn('--session-id cannot be combined' if option=='--session-id' else 'conflicting new-session-id',result.stderr)
        invalid=list(argv)
        invalid[invalid.index('--new-session-id')+1]='invalid'
        result=subprocess.run(invalid,cwd=cell['repo'],env=cell['environment'],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('invalid session UUID',result.stderr)
        result=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-baseline','--phase','smoke')
        self.assertEqual(result.returncode,0,result.stderr+result.stdout)
        result=subprocess.run(argv,cwd=cell['repo'],env=cell['environment'],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('session already exists or is in use',result.stderr)

    def test_public_codex_native_complete_both_version_scenarios(self):
        self.child_env={'CODEX_HOME':str(self.root/'standard-codex')}
        self.native_codex_setup('proof')
        result=self.call('preflight','--manifest',self.manifest,'--provider','codex')
        self.assertEqual(result.returncode,0,result.stderr)
        for variant in ('baseline','candidate'):
            cell_id='codex-'+variant
            result=self.call('run','--manifest',self.manifest,'--cell',cell_id,'--phase','scenario')
            self.assertEqual(result.returncode,0,result.stderr+result.stdout)
            report=self.grade(cell_id)
            self.assertEqual(report['setup_status'],'valid',report)
            self.assertEqual(report['behavior_status'],'pass',report)
            self.assertTrue(report['comparison_eligible'],report)
            cell=self.data['cells'][cell_id]
            raw=json.loads((Path(cell['repo']).parent/'evidence/scenario/native-events.json').read_text())
            patches=[call for call in raw['calls'] if call['tool_type']=='apply_patch']
            self.assertTrue(patches)
            self.assertTrue(all(call['exit_code'] is None for call in patches))
            self.assertTrue(any(call['exit_code']==2 for call in raw['calls'] if call['tool_type']=='command_execution'))


    def test_public_codex_overlapping_stdout_intervals_rejected(self):
        for mode in ('proof-overlap','proof-patch-overlap'):
            with self.subTest(mode=mode):
                self.run=self.root/mode;self.manifest=self.run/'manifest.json'
                self.child_env={'CODEX_HOME':str(self.root/'standard-codex')}
                self.native_codex_setup(mode)
                self.assertEqual(self.call('preflight','--manifest',self.manifest,'--provider','codex').returncode,0)
                result=self.call('run','--manifest',self.manifest,'--cell','codex-baseline','--phase','smoke')
                record=json.loads(result.stdout)
                self.assertEqual(result.returncode,2,result.stdout)
                self.assertFalse(record['smoke_valid'])
                self.assertTrue(any('overlap' in reason for reason in record['invalid_reasons']),record)




    def test_public_setup_binding_drift_blocks_launch_before_child(self):
        for mode in ('executable','provider-receipt'):
            with self.subTest(mode=mode):
                self.run=self.root/('binding-'+mode)
                self.manifest=self.run/'manifest.json'
                self.child_env={'CODEX_HOME':str(self.root/'standard-codex')}
                self.native_codex_setup('proof')
                preflight=self.call('preflight','--manifest',self.manifest,'--provider','codex')
                self.assertEqual(preflight.returncode,0,preflight.stderr)
                cell=self.data['cells']['codex-candidate']
                if mode=='executable':
                    fake=Path(cell['requested_settings']['executable']);fake.write_text(fake.read_text()+'\n# drift\n')
                if mode=='provider-receipt':
                    p=self.run/'preflight/codex.json';receipt=json.loads(p.read_text());receipt['provider']='copilot';p.write_text(json.dumps(receipt))
                result=self.call('run','--manifest',self.manifest,'--cell','codex-baseline','--phase','smoke')
                self.assertEqual(result.returncode,2)
                self.assertFalse((Path(cell['repo'])/'outputs/launch.json').exists())


    def test_public_partial_attempt_cannot_be_replayed(self):
        self.copilot_setup()
        partial=self.run/'cells/copilot-baseline/evidence/smoke'
        partial.mkdir()
        (partial/'attempt.json').write_text('{}')
        blocked=self.provider_call('run','--manifest',self.manifest,'--cell','copilot-baseline','--phase','smoke')
        self.assertEqual(blocked.returncode,2)
        self.assertIn('File exists',blocked.stderr)
        self.assertFalse((self.run/'cells/copilot-baseline/repo/outputs/smoke.json').exists())

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

    def test_public_canonical_scheduler_state_cannot_be_hidden_by_detached_copy(self):
        for variant in ("baseline", "candidate"):
            self.run = self.root / ("canonical-state-" + variant)
            self.manifest = self.run / "manifest.json"
            self.copilot_setup(native=True)
            smoke = self.provider_call("run", "--manifest", self.manifest, "--cell", "copilot-baseline", "--phase", "smoke")
            self.assertEqual(smoke.returncode, 0, smoke.stderr)
            cell_id = "copilot-" + variant
            scenario = self.provider_call("run", "--manifest", self.manifest, "--cell", cell_id, "--phase", "scenario")
            self.assertEqual(scenario.returncode, 0, scenario.stderr)
            self.assertEqual(self.grade(cell_id)["behavior_status"], "pass")
            repo = Path(self.data["cells"][cell_id]["repo"])
            canonical = repo / "outputs/scenario-state.json"
            detached = repo / "outputs/detached-state.json"
            detached.write_bytes(canonical.read_bytes())
            output = repo / "outputs/result.json"
            result = json.loads(output.read_text())
            result["final_state"]["scheduler_state"] = "outputs/detached-state.json"
            output.write_text(json.dumps(result))
            altered = json.loads(canonical.read_text())
            altered["assignments"]["B"]["agent_id"] = "agent-compromised"
            canonical.write_text(json.dumps(altered))
            report = self.grade(cell_id)
            self.assert_invalid_diagnostics(report)
            self.assertIn("scenario-state-or-output-invalid", report["invalid_reasons"])

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
        self.assertIn("prerequisites", result.stderr)

    def test_help(self):
        self.assertEqual(self.call("--help").returncode, 0)

if __name__ == "__main__":
    unittest.main()
