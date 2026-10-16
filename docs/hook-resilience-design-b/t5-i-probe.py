#!/usr/bin/env python3
"""T5-I combined public-process proof. Run serially; no product writes.

Usage: python3 docs/hook-resilience-design-b/t5-i-probe.py --root CHECKOUT
All credentials are constructed unmistakably fake runtime fixtures. Output is
allowlisted metadata only. Fixture dispatchers are not the T7 gate installer.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

BUILD = "09c5d1e64561b2c42789f95eaee3fa031fa743b84ef40f085e01f0bfddff9fab"
MODULES = ("scan_types", "scan_reporting", "scan_allowlist", "scan_stream", "scan_git", "scan_engine", "scan_native_file", "scan_audit", "scan_budget", "scan_repository", "scan_gate", "scan_transaction", "scan_publication")
ASSETS = ("scripts/scan-secrets.py", "hooks/runtime/scan_cli.py", "hooks/runtime/scan_status.py", *("hooks/runtime/" + name + ".py" for name in MODULES))
BUDGET = {"schema_version": 1,
    "checkpoint": dict(max_objects=4096, max_candidate_bytes=67108864, max_seconds=30, max_capture_bytes=134217728, max_temp_bytes=268435456),
    "publication": dict(max_objects=20000, max_candidate_bytes=268435456, max_seconds=120, max_capture_bytes=536870912, max_temp_bytes=805306368)}
BUDGET_ID = hashlib.sha256(json.dumps(BUDGET, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
GIT = shutil.which("git")


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


# Public caller admission belongs to the fixture, separate from scanner output.
# Expected build/budget are literal accepted contract values, repository/index
# are captured by this caller, and destination/transaction use actual Git stdin.
DISPATCHER = r"""import hashlib,json,os,subprocess,sys
from pathlib import Path
sys.path.insert(0, VALIDATOR_ROOT)
from hooks.runtime.scan_gate import validate_result
control=json.loads(Path(CONTROL).read_text())
action=Path(sys.argv[0]).name
raw=sys.stdin.buffer.read(1048577) if action=='pre-push' else None
expected=dict(action=action,build=BUILD,repository_identity=REPOSITORY,budget_identity=BUDGET_ID)
args=COMMAND+['gate',action,'--json','--repo',REPO]
if control.get('budget'):
 args+=['--budget-file',control['budget']]
 expected['budget_identity']=hashlib.sha256(Path(control['budget']).read_bytes()).hexdigest()
if action=='pre-push':
 args+=['--remote',sys.argv[1],'--url',sys.argv[2]]
 destination=hashlib.sha256(b'publication-destination-v1\0'+os.fsencode(sys.argv[1])+b'\0'+os.fsencode(sys.argv[2])).hexdigest()
 expected.update(destination_identity=destination,transaction_identity=hashlib.sha256(b'publication-transaction-v1\0'+bytes.fromhex(destination)+b'\0'+raw).hexdigest())
else:
 index=Path(os.environ.get('GIT_INDEX_FILE','.git/index'))
 expected['index_identity']=hashlib.sha256(b'selected-index-v1\0'+(index.read_bytes() if index.exists() else b'absent')).hexdigest()
p=subprocess.run(args,input=raw,capture_output=True,timeout=40)
response=p.stdout
if control.get('mutation')=='missing': response=b''
elif control.get('mutation')=='status': response=subprocess.run(COMMAND+['status','--repo',REPO,'--json'],capture_output=True,timeout=5).stdout
elif control.get('mutation')=='build':
 v=json.loads(response);v['build']='0'*64;response=json.dumps(v).encode()
try:
 value=validate_result(response,p.returncode,**expected)
except Exception:
 Path(RECEIPT).write_text(json.dumps(dict(action=action,admitted=False,exit_code=p.returncode)))
 sys.exit(2)
# Retain only safe structured results; never child stderr.
Path(RECEIPT).write_bytes(response)
sys.exit(p.returncode)
"""


class Workflow:
    def __init__(self, root, base, mode):
        self.root, self.base, self.mode = root, base, mode
        self.repo = base / "repo"
        self.repo.mkdir()
        self.env = {k:v for k,v in os.environ.items() if not k.startswith(("GIT_", "SCAN_", "PYTHON"))}
        for key, name in (("HOME","home"),("USERPROFILE","home"),("XDG_CONFIG_HOME","config"),("XDG_DATA_HOME","data"),("APPDATA","appdata"),("LOCALAPPDATA","localappdata"),("CODEX_HOME","codex"),("TMPDIR","temp")):
            path = base / name
            path.mkdir(mode=0o700, exist_ok=True)
            self.env[key] = str(path)
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", TERM="dumb", NO_COLOR="1")
        self.secret = ("gh" + "p_" + "A" * 36).encode()
        self.control, self.receipt = base / "control.json", base / "receipt.json"
        self.control.write_text("{}")
        self.events = []
        self.git("init", "--quiet")
        self.git("symbolic-ref", "HEAD", "refs/heads/main")
        self.remote = base / "remote.git"
        self.git("init", "--quiet", "--bare", str(self.remote))
        self.git("remote", "add", "fixture", str(self.remote))
        self.command = [sys.executable,"-I","-S","-B",str(root / "scripts/scan-secrets.py")]
        self.validator_root = root
        if mode == "installed":
            source = base / "disposable-source"
            for relative in (*ASSETS,"scripts/install-scan-secrets.py","scripts/scan_install_windows.py"):
                path = source / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / relative, path)
            destination = base / "installed"
            p = self.run([sys.executable,"-I","-S","-B",str(source / "scripts/install-scan-secrets.py"),"install","--source-dir",str(source),"--destination",str(destination),"--json"])
            require(p.returncode == 0, "real neutral installer succeeds")
            manifest = json.loads((destination / "installation.json").read_bytes())
            require(set(manifest["files"]) == set(ASSETS), "exact installed 16-file closure")
            require(manifest["interpreter"] == str(Path(sys.executable).resolve()), "pinned interpreter")
            require(Path(manifest["data"]).is_relative_to(base), "disposable installed data")
            owned = {**manifest["files"], **manifest["launchers"]}
            actual = {str(p.relative_to(destination)) for p in destination.rglob("*") if p.is_file()}
            require(actual == set(owned) | {"installation.json"}, "no extra installed file")
            for relative, expected in owned.items():
                require(digest((destination / relative).read_bytes()) == expected, "installed ownership digest")
            for relative in ASSETS:
                require((destination / relative).read_bytes() == (root / relative).read_bytes(), "installed runtime equals accepted source")
            shutil.rmtree(source)
            require(not source.exists(), "copied source removed before launch")
            self.command = [str(destination / "scan-secrets")]
            self.validator_root = destination
        repository = digest(b"\0".join(os.fsencode(p) for p in (self.repo,self.repo / ".git",self.repo / ".git")))
        constants = dict(VALIDATOR_ROOT=str(self.validator_root), CONTROL=str(self.control), BUILD=BUILD, REPOSITORY=repository, BUDGET_ID=BUDGET_ID, REPO=str(self.repo), COMMAND=self.command, RECEIPT=str(self.receipt))
        for action in ("pre-commit","pre-push"):
            hook = self.repo / ".git/hooks" / action
            hook.write_text("#!" + sys.executable + " -I\n" + "\n".join(k+"="+repr(v) for k,v in constants.items()) + "\n" + DISPATCHER)
            hook.chmod(0o755)

    def run(self, command, data=None, env=None):
        p = subprocess.run(command,cwd=self.repo,env=env or self.env,input=data,capture_output=True,timeout=50)
        require(self.secret not in p.stdout+p.stderr, "runtime fixture redacted at process boundary")
        require(b"Traceback" not in p.stderr, "no traceback at process boundary")
        return p

    def git(self, *args, data=None, expected=0):
        p = self.run([GIT,"-c","commit.gpgsign=false","-c","user.name=Fixture","-c","user.email=fixture@example.invalid",*args],data)
        if expected is not None:
            require(p.returncode == expected, "git " + args[0] + " expected exit " + str(expected))
        return p

    def oid(self, ref="HEAD"):
        return self.git("rev-parse",ref).stdout.strip().decode()

    def transaction(self):
        return ("refs/heads/main " + self.oid() + " refs/heads/new " + "0"*40 + "\n").encode()

    def cli(self, action, code, data=None, extra=(), env=None):
        p = self.run(self.command+["gate",action,"--repo",str(self.repo),"--json",*extra],data,env)
        require(p.returncode == code, action + " expected exit " + str(code))
        v = json.loads(p.stdout)
        require(v["exit_code"] == code, "truthful result exit")
        return v

    def log(self, label, value=None):
        event = dict(label=label)
        if value is not None:
            for key in ("action","elapsed_seconds","outcome","reason","coverage_complete","security_outcome","audit_outcome","status_outcome","build","policy_version","scope","scope_description","scope_identity","repository_identity","index_identity","budget_identity","transaction_identity","destination_identity","budget_profile","accounting_units","counts","limits","diagnostic","exit_code"):
                if key in value: event[key] = value[key]
        self.events.append(event)

    def absent(self, oid, ref):
        require(self.git("--git-dir="+str(self.remote),"cat-file","-e",oid,expected=None).returncode != 0, "blocked object never delivered")
        require(self.git("--git-dir="+str(self.remote),"rev-parse","--verify",ref,expected=None).returncode != 0, "blocked ref absent")

    def execute(self):
        path = self.repo / "selected.txt"
        path.write_text("safe base\n")
        self.git("add",".")
        self.git("commit","--quiet","-m","base")
        base_oid = self.oid()
        self.log("real clean commit admitted",json.loads(self.receipt.read_bytes()))
        self.git("push","fixture","HEAD:refs/heads/main")
        require(self.oid_remote("main") == base_oid, "checked root received")
        self.log("real clean push admitted; remote OID matched",json.loads(self.receipt.read_bytes()))
        path.write_bytes(self.secret+b"\n")
        self.git("add",".")
        path.write_text("clean worktree hiding staged fixture\n")
        require(self.git("commit","--quiet","-m","blocked",expected=None).returncode != 0, "staged finding blocks real commit")
        require(self.oid() == base_oid, "blocked commit leaves HEAD unchanged")
        self.log("staged secret hidden by worktree denied",json.loads(self.receipt.read_bytes()))
        path.write_text("repaired staged version\n")
        self.git("add",".")
        self.git("commit","--quiet","-m","repair staged content")
        repair_base = self.oid()
        # Import pre-existing unsafe history using Git's public plumbing while
        # both fixture dispatchers remain present and unchanged.
        path.write_bytes(self.secret+b"\n")
        self.git("add",".")
        unsafe_tree = self.git("write-tree").stdout.strip().decode()
        intermediate = self.git("commit-tree",unsafe_tree,"-p",repair_base,data=b"imported intermediate fixture\n").stdout.strip().decode()
        path.write_text("latest tree is safe\n")
        self.git("add",".")
        clean_tree = self.git("write-tree").stdout.strip().decode()
        latest = self.git("commit-tree",clean_tree,"-p",intermediate,data=b"removed fixture from latest tree\n").stdout.strip().decode()
        self.git("update-ref","refs/heads/main",latest,repair_base)
        (self.repo / "unrelated.txt").write_text("safe unrelated commit\n")
        self.git("add","unrelated.txt")
        self.git("commit","--quiet","-m","safe unrelated change")
        staged = json.loads(self.receipt.read_bytes())
        require(staged["counts"]["candidates"] == 1, "staged feedback selects one changed file")
        self.log("clean staged feedback over unsafe outgoing ancestry",staged)
        status = json.loads(self.run(self.command+["status","--repo",str(self.repo),"--json"]).stdout)
        require(status["last_scan"]["outcome"] == "complete_clean" and not status["authorizes_publication"], "clean last scan informational")
        hidden_oid = self.oid()
        require(self.git("push","fixture","HEAD:refs/heads/hidden",expected=None).returncode != 0, "outgoing intermediate secret blocks push")
        value = json.loads(self.receipt.read_bytes())
        require(value["outcome"] == "complete_findings" and value["coverage_complete"], "history detection complete")
        require(value["budget_profile"] == "publication" and value["policy_version"] == "publication_v1", "independent publication policy")
        self.absent(hidden_oid,"refs/heads/hidden")
        self.absent(intermediate,"refs/heads/hidden")
        self.log("clean latest tree and old clean status cannot waive history",value)
        # Rebuild the outgoing branch from the checked safe parent, retaining
        # the clean working tree and index, then retry normal commit and push.
        self.git("reset","--soft",repair_base)
        self.git("commit","--quiet","-m","repair outgoing ancestry")
        checked = self.oid()
        self.git("push","fixture","HEAD:refs/heads/main")
        require(self.oid_remote("main") == checked, "repaired checked OID actually received")
        self.log("history repair and actual push retry; received OID matched",json.loads(self.receipt.read_bytes()))
        self.events.append(dict(label="OID receipt",checked_oid=checked,received_oid=self.oid_remote("main"),blocked_intermediate_oid=intermediate))
        # Current unchanged fixture elsewhere must not block unrelated commits.
        path.write_bytes(self.secret+b"\n")
        self.git("add","selected.txt")
        fixture_tree = self.git("write-tree").stdout.strip().decode()
        imported = self.git("commit-tree",fixture_tree,"-p",checked,data=b"import old fixture\n").stdout.strip().decode()
        self.git("update-ref","refs/heads/main",imported,checked)
        (self.repo / "unrelated.txt").write_text("another unrelated change\n")
        self.git("add","unrelated.txt")
        self.git("commit","--quiet","-m","unrelated change with unchanged fixture")
        self.log("unchanged fixture outside staged selection permits unrelated commit",json.loads(self.receipt.read_bytes()))
        path.write_bytes(self.secret+b"\nnew safe line\n")
        self.git("add","selected.txt")
        require(self.git("commit","--quiet","-m","changed whole file",expected=None).returncode != 0, "unchanged secret line within changed file blocks")
        self.log("full changed file detects unchanged secret line",json.loads(self.receipt.read_bytes()))
        require(self.git("push","fixture","HEAD:refs/heads/fixture",expected=None).returncode != 0, "staged selection never exempts publication")
        self.absent(self.oid(),"refs/heads/fixture")
        # Restore safe public history before infrastructure/control checks.
        self.git("reset","--hard",checked)
        self.controls()
        return dict(mode=self.mode,python=sys.version.split()[0],build=BUILD,events=self.events)

    def oid_remote(self, name):
        return self.git("--git-dir="+str(self.remote),"rev-parse","refs/heads/"+name).stdout.strip().decode()

    def controls(self):
        # Display failure is separate from required audit failure for each action.
        data_root = self.base / "data/scan-secrets"
        status = data_root / "status"
        shutil.rmtree(status)
        status.write_text("display failure fixture")
        for action in ("pre-commit","pre-push"):
            extra = ("--remote","fixture","--url",str(self.remote)) if action == "pre-push" else ()
            value = self.cli(action,0,self.transaction() if extra else None,extra)
            require(value["status_outcome"] == "failed" and value["audit_outcome"] == "written", "display failure preserves clean enforcement")
            self.log(action+" display failure stays separate",value)
        status.unlink()
        audit = data_root / "audit.jsonl"
        records = [json.loads(row) for row in audit.read_text().splitlines()]
        require({"pre-commit","pre-push"}.issubset({r["action"] for r in records}), "both actions written to required audit")
        audit.unlink(); audit.mkdir()
        for action in ("pre-commit","pre-push"):
            extra = ("--remote","fixture","--url",str(self.remote)) if action == "pre-push" else ()
            value = self.cli(action,2,self.transaction() if extra else None,extra)
            require(value["audit_outcome"] == "failed", "required audit fail closed")
            self.log(action+" required audit failure",value)
        require(self.git("commit","--allow-empty","--quiet","-m","audit block",expected=None).returncode != 0, "audit failure blocks actual commit")
        require(self.git("push","fixture","HEAD:refs/heads/audit",expected=None).returncode != 0, "audit failure blocks actual push")
        require(self.git("--git-dir="+str(self.remote),"rev-parse","--verify","refs/heads/audit",expected=None).returncode != 0,"audit failure leaves no new ref")
        audit.rmdir()
        # An independently invalid caller response cannot reuse old status.
        for mutation in ("missing","status","build"):
            self.control.write_text(json.dumps(dict(mutation=mutation)))
            before = self.oid()
            require(self.git("commit","--allow-empty","--quiet","-m","invalid caller response",expected=None).returncode != 0,"invalid response blocks commit")
            require(self.oid() == before,"invalid commit unchanged")
            require(self.git("push","fixture","HEAD:refs/heads/invalid",expected=None).returncode != 0,"invalid response blocks push")
            require(self.git("--git-dir="+str(self.remote),"rev-parse","--verify","refs/heads/invalid",expected=None).returncode != 0,"invalid push unchanged")
            require(not json.loads(self.receipt.read_bytes())["admitted"],"caller rejected invalid result")
            self.log("both actual actions reject "+mutation+" response")
        self.control.write_text("{}")
        budget = self.base / "budget.json"
        document = json.loads(json.dumps(BUDGET))
        document["checkpoint"]["max_objects"] = 1
        document["publication"]["max_objects"] = 1
        budget.write_text(json.dumps(document))
        (self.repo / "a.txt").write_text("safe a\n")
        (self.repo / "b.txt").write_text("safe b\n")
        self.git("add",".")
        for action in ("pre-commit","pre-push"):
            extra = ("--remote","fixture","--url",str(self.remote)) if action == "pre-push" else ()
            value = self.cli(action,2,self.transaction() if extra else None,extra+("--budget-file",str(budget)))
            require(not value["coverage_complete"],"capacity failure is incomplete")
            self.log(action+" bounded incomplete inspection",value)
        self.control.write_text(json.dumps(dict(budget=str(budget))))
        require(self.git("commit","--quiet","-m","capacity block",expected=None).returncode != 0,"incomplete real commit blocked")
        require(self.git("push","fixture","HEAD:refs/heads/capacity",expected=None).returncode != 0,"incomplete real push blocked")
        self.control.write_text("{}")
        budget.write_text('{"schema_version":true}')
        for action in ("pre-commit","pre-push"):
            extra = ("--remote","fixture","--url",str(self.remote)) if action == "pre-push" else ()
            value = self.cli(action,3,self.transaction() if extra else None,extra+("--budget-file",str(budget)))
            self.log(action+" invalid configuration",value)
        # Open transaction stdin is a public acquisition boundary. Cancellation
        # is sent only after the process is running and still awaiting input.
        p = subprocess.Popen(self.command+["gate","pre-push","--repo",str(self.repo),"--remote","fixture","--url",str(self.remote),"--json"],cwd=self.repo,env=self.env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            p.stdin.write(b"refs/heads/"); p.stdin.flush()
            time.sleep(.2)
            require(p.poll() is None,"open partial transaction activated")
            p.send_signal(signal.SIGINT)
            stdout, stderr = p.communicate(timeout=4)
            require(p.returncode == 130 and self.secret not in stdout+stderr and b"Traceback" not in stderr,"cancellation contract")
            value = json.loads(stdout)
            require(value["reason"] == "cancelled", "cancelled reason")
            self.log("open transaction cancelled with exit 130",value)
        finally:
            if p.poll() is None:
                p.kill(); p.communicate(timeout=4)
        self.git("reset","--hard","HEAD")
        require(list((self.base / "temp").iterdir()) == [], "private scratch cleaned before fixture cleanup")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    evidence = (root / "docs/hook-resilience-design-b/t5b-composed-evidence.md").read_text()
    expected = dict(re.findall(r"`((?:scripts|hooks)/[^`]+\.py)` \| `([0-9a-f]{64})`",evidence))
    require(set(expected) == set(ASSETS), "composed evidence exact closure")
    h = hashlib.sha256()
    for relative in ASSETS:
        raw = (root / relative).read_bytes()
        require(digest(raw) == expected[relative], "accepted composed runtime hash")
        h.update(Path(relative).name.encode()+b"\0"+raw)
    require(h.hexdigest() == BUILD, "independent accepted build identity")
    results = []
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="t5-i-") as temporary:
        base = Path(temporary).resolve()
        for mode in ("source","installed"):
            run_root = base / mode
            run_root.mkdir(mode=0o700)
            results.append(Workflow(root,run_root,mode).execute())
    print(json.dumps(dict(schema="t5_i_probe_v1",python=sys.version.split()[0],build=BUILD,elapsed_seconds=time.monotonic()-started,results=results),sort_keys=True))


if __name__ == "__main__":
    main()
