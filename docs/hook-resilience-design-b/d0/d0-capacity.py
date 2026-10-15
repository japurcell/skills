#!/usr/bin/env python3
"""Run frozen D0 capacity experiments serially, retaining raw safe metrics."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import shutil
import subprocess
import sys
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--lfs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case", action="append", help="Run only the named workload; repeat for multiple workloads")
    parser.add_argument("--prepared-history", type=Path, help="Reuse a prebuilt history fixture without reconstructing it during measurement")
    args = parser.parse_args()
    probe = runpy.run_path(str(Path(__file__).with_name("d0-probe.py")))
    Lab, git, Endpoint = (probe[key] for key in ("Lab", "git", "Endpoint"))
    observations = []
    paths = [Path(__file__), Path(__file__).with_name("d0-probe.py"), Path(__file__).with_name("d0-test.py")]
    paths += sorted((args.source / ".codex/hooks").rglob("*.py"))
    fingerprint = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    result = dict(platform=platform.platform(), python=sys.version, git=subprocess.check_output(["git", "--version"]).decode().strip(), lfs=subprocess.check_output([str(args.lfs), "version"]).decode().strip(), source_revision=subprocess.check_output(["git", "-C", str(args.source), "rev-parse", "HEAD"]).decode().strip(), fingerprints=fingerprint, observations=observations, status="in-progress")
    publication = dict(max_objects=20000, max_candidate_bytes=268435456, max_seconds=120, max_capture_bytes=536870912, max_temp_bytes=805306368)
    result["publication_profile"] = publication
    def retain():
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    retain()
    with tempfile.TemporaryDirectory(prefix="d0-capacity-") as temp:
        root = Path(temp)
        for case in ("first-publication", "merge-sized", "repeated-blobs", "multi-ref", "long-history", "large-blob", "large-lfs"):
            if args.case and case not in args.case:
                continue
            workspace = root / case
            workspace.mkdir()
            if case == "long-history" and args.prepared_history:
                lab = Lab.__new__(Lab)
                lab.root = args.prepared_history.resolve()
                lab.source = args.source.resolve()
                lab.home = lab.root / "home"
                lab.env = probe["clean_env"](lab.home)
                lab.repo, lab.remote, lab.scratch = (lab.root / name for name in ("repo", "remote.git", "scratch"))
                lab.config = lab.root / "config.json"
                lab.cfg = json.loads(lab.config.read_bytes())
            else:
                lab = Lab(workspace, args.source)
            lab.cfg.update(publication)
            lab.save()
            refs = ["main"]
            if case == "first-publication":
                for n, size in enumerate([3611602, 3131324, 2495842, 3340075, 3319151, 4128480]):
                    (lab.repo / f"image-{n}.png").write_bytes(b"\0" * size)
            elif case == "merge-sized":
                size, remainder = divmod(9453698, 223)
                for n in range(223):
                    # Distinct contents prevent accidental blob deduplication.
                    body = (f"safe snapshot {n:03}\n".encode() * 4096)[:size + (n < remainder)]
                    (lab.repo / f"snapshot-{n:03}").write_bytes(body)
            elif case == "repeated-blobs":
                data = b"\0" * (256 * 1024)
                for n in range(128):
                    (lab.repo / f"shared-{n:03}").write_bytes(data)
            elif case == "multi-ref":
                base = lab.commit("base", b"safe base\n")
                refs = []
                for n in range(12):
                    git(lab.repo, lab.env, "checkout", "-qB", f"branch-{n}", base)
                    lab.commit(f"payload-{n}", bytes([n]) * (1024 * 1024))
                    refs.append(f"branch-{n}")
            elif case == "long-history":
                if not args.prepared_history:
                    lab.commit("shared", b"\0" * (256 * 1024))
                    for n in range(512):
                        lab.commit("version", (f"safe version {n:04}\n".encode() * 64))
            elif case == "large-blob":
                (lab.repo / "large.bin").write_bytes(b"\0" * (64 * 1024 * 1024))
            else:
                endpoint = Endpoint()
                data = b"\0" * (64 * 1024 * 1024)
                oid = hashlib.sha256(data).hexdigest()
                store = lab.repo / ".git/lfs/objects" / oid[:2] / oid[2:4] / oid
                store.parent.mkdir(parents=True)
                store.write_bytes(data)
                (lab.repo / "large.bin").write_text(f"version https://git-lfs.github.com/spec/v1\noid sha256:{oid}\nsize {len(data)}\n")
                lab.cfg.update(lfs_binary=str(args.lfs), lfs_url=endpoint.url, mutate_original=True)
                lab.save()
            if case not in {"multi-ref", "long-history"}:
                git(lab.repo, lab.env, "add", "--all")
                git(lab.repo, lab.env, "commit", "-qm", "capacity fixture")
            try:
                measured = lab.push(*refs)
            except AssertionError:
                result.update(status="failed", failed_case=case)
                artifact = Path(lab.cfg["result"])
                result["failed_result"] = json.loads(artifact.read_bytes()) if artifact.exists() else {"outcome": "unavailable"}
                retain()
                raise
            assert measured["outcome"] == "clean", measured
            if case == "large-lfs":
                assert endpoint.uploads == [(oid, data)]
                measured.update(uploaded_objects=1, uploaded_bytes=len(data), delivered_snapshot_matches=True)
                endpoint.close()
                # The source is deliberately corrupted after the clean proof.
                store.write_bytes(data)
            # First-publication late controls always use an unknown remote ref,
            # so the clean previous push cannot subtract the workload.
            lab.cfg.pop("mutate_original", None)
            lab.save()
            if case == "multi-ref":
                git(lab.repo, lab.env, "checkout", "-q", "main")
            lab.commit("zz-late-control", b"ghp_" + b"A" * 32 + b"FAKE\n")
            controls = ([ref + ":refs/heads/control-" + ref for ref in refs] if case == "multi-ref" else [])
            control = lab.push(*controls, "HEAD:refs/heads/late-control", expect=False)
            assert control["outcome"] == "findings", control
            assert control["metrics"]["logical_candidate_bytes"] >= measured["metrics"]["logical_candidate_bytes"], "credential control omitted the measured workload"
            observations.append(dict(case=case, clean=measured, late_control=control))
            retain()
            print(case + ": clean and late control verified", file=sys.stderr, flush=True)
        # Checkpoint measurements use the real generated process in a copied
        # bundle. Only constants change; the live/source assets stay untouched.
        for case in ("checkpoint-images", "checkpoint-merge"):
            if args.case and case not in args.case:
                continue
            workspace = root / case
            workspace.mkdir()
            lab = Lab(workspace, args.source)
            directory = workspace / "candidate-hook"
            shutil.copytree(args.source / ".codex/hooks", directory)
            entry = directory / "scan-secrets.py"
            content = entry.read_text().replace("MAX_FILES = 256\n", "MAX_FILES = 4096\n").replace("MAX_TOTAL_BYTES = 8388608\n", "MAX_TOTAL_BYTES = 67108864\n").replace("MAX_GIT_OUTPUT_BYTES = 8388608\n", "MAX_GIT_OUTPUT_BYTES = 134217728\n").replace("MAX_SCAN_SECONDS = 8.0\n", "MAX_SCAN_SECONDS = 30.0\n")
            entry.write_text(content)
            sizes = [3611602, 3131324, 2495842, 3340075, 3319151, 4128480] if case.endswith("images") else [9453698 // 223 + (n < 9453698 % 223) for n in range(223)]
            for n, size in enumerate(sizes):
                (lab.repo / f"snapshot-{n:03}").write_bytes(b"\0" * size)
            logs = workspace / "logs"
            logs.mkdir()
            env = {**lab.env, "SCAN_MODE": "block", "SCAN_SCOPE": "diff", "SECRETS_LOG_DIR": str(logs), "AUDIT_LOG": str(logs / "audit.log"), "AUDIT_LOCK": str(logs / "audit.lock"), "OBSERVABILITY_LOG_PATH": str(logs / "observability.jsonl"), "OBSERVABILITY_TESTING": "1", "TMPDIR": str(workspace)}
            payload = json.dumps(dict(tool_name="exec_command", tool_input=dict(cmd="rtk read repair.txt", login=False), cwd=str(lab.repo))).encode()
            start = time.monotonic()
            clean = subprocess.run(["/usr/bin/time", "-l", sys.executable, "-I", "-S", "-B", str(entry)], cwd=lab.repo, env=env, input=payload, capture_output=True, timeout=35)
            elapsed = time.monotonic() - start
            record = json.loads((logs / "scan.log").read_text().splitlines()[-1])
            assert clean.returncode == 0 and record["status"] == "clean", (clean.stderr, record)
            (lab.repo / "zz-control").write_bytes(b"ghp_" + b"A" * 32 + b"FAKE\n")
            late = subprocess.run([sys.executable, "-I", "-S", "-B", str(entry)], cwd=lab.repo, env=env, input=payload, capture_output=True, timeout=35)
            late_record = json.loads((logs / "scan.log").read_text().splitlines()[-1])
            assert late.returncode == 0 and late_record["status"] == "findings"
            observations.append(dict(case=case, candidate_entry_sha256=hashlib.sha256(entry.read_bytes()).hexdigest(), logical_candidate_bytes=sum(sizes), snapshots=len(sizes), elapsed_seconds=elapsed, stdout_bytes=len(clean.stdout), time_stderr=clean.stderr.decode(), clean_status=record["status"], late_status=late_record["status"]))
            retain()
            print(case + ": clean and late control verified", file=sys.stderr, flush=True)
    assert fingerprint == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}, "frozen files changed during measurement"
    result["status"] = "passed"
    retain()


if __name__ == "__main__":
    main()
