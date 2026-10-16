#!/usr/bin/env python3
"""Disposable I3-P public-process production integration and capacity evidence.

No production modules are imported. Optional profiling is a separate invocation
of the same public CLI under cProfile, outside unprofiled acceptance timing.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import pstats
import re
import runpy
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

GIT = "/Library/Developer/CommandLineTools/usr/bin/git"
ZERO = "0" * 40
SIZES = [3611602, 3131324, 2495842, 3340075, 3319151, 4128480]
DEFAULTS = {"schema_version": 1,
    "checkpoint": dict(max_objects=4096, max_candidate_bytes=67108864, max_seconds=30, max_capture_bytes=134217728, max_temp_bytes=268435456),
    "publication": dict(max_objects=20000, max_candidate_bytes=268435456, max_seconds=120, max_capture_bytes=536870912, max_temp_bytes=805306368)}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def credential():
    return b"gh" + b"p_" + b"A" * 36


class Lab:
    def __init__(self, root, source, python):
        self.root, self.source, self.python = root.resolve(), source, python
        self.home, self.repo, self.remote = (self.root / name for name in ("home", "repo", "remote.git"))
        self.home.mkdir(parents=True)
        self.tmp = self.root / "temporary"
        self.tmp.mkdir()
        self.env = {key: value for key, value in os.environ.items() if not key.startswith(("GIT_", "SCAN_", "PYTHON"))}
        self.env.update(HOME=str(self.home), USERPROFILE=str(self.home), XDG_CONFIG_HOME=str(self.home / "config"),
            XDG_DATA_HOME=str(self.home / "data"), GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
            GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1", GIT_NO_REPLACE_OBJECTS="1", TMPDIR=str(self.tmp))
        self.run([GIT, "init", "-qb", "main", str(self.repo)])
        self.run([GIT, "init", "--bare", "-q", str(self.remote)])
        for repo in (self.repo, self.remote):
            self.git("config", "gc.auto", "0", cwd=repo)
            self.git("config", "maintenance.auto", "false", cwd=repo)
        self.git("remote", "add", "origin", str(self.remote))
        self.entry = [python, "-I", "-S", "-B", str(source / "scripts/scan-secrets.py")]
        self.budget = self.home / "budget.json"
        self.save_budget(DEFAULTS)
        self.marker = self.root / "downstream"
        hook = self.repo / ".git/hooks/pre-push"
        hook.write_text("#!/bin/sh\nprintf 'ran\\n' >> '" + str(self.marker) + "'\ncat > '" + str(self.root / "hook-input") + "'\n")
        hook.chmod(0o755)

    def save_budget(self, values):
        self.budget.write_text(json.dumps(values, sort_keys=True))
        self.budget.chmod(0o600)

    def run(self, command, *, data=None, expected=0, cwd=None, timeout=180):
        start = time.monotonic()
        result = subprocess.run(command, input=data, cwd=cwd or self.root, env=self.env, capture_output=True, timeout=timeout)
        result.elapsed = time.monotonic() - start
        assert credential() not in result.stdout + result.stderr, "raw credential leaked"
        if expected is not None:
            assert result.returncode == expected, (command, result.returncode, result.stdout[:2000], result.stderr[:2000])
        return result

    def git(self, *args, **kw):
        return self.run([GIT, "--no-replace-objects", "-c", "user.name=D0 fixture", "-c", "user.email=d0@example.invalid", "-c", "commit.gpgsign=false", *args], cwd=kw.pop("cwd", self.repo), **kw)

    def cli(self, *args, data=None, expected=0):
        result = self.run([*self.entry, *args, "--json"], data=data, expected=expected)
        value = json.loads(result.stdout)
        return dict(value=value, wall_seconds=result.elapsed, stdout_bytes=len(result.stdout), stderr_bytes=len(result.stderr))

    def install(self, *extra):
        return self.cli("hooks", "install", "--repo", str(self.repo), "--git", GIT, "--budget-file", str(self.budget), *extra)

    def neutral(self, legacy=False):
        copy = self.root / "source-copy"
        if legacy:
            copy.mkdir()
            fixture = self.source / "scripts/fixtures/scan-secrets-releases/t6.tar.gz"
            if fixture.exists():
                archive = fixture.read_bytes()
                assert digest(archive) == "04d1d01ca62b0d6ac0e1a6cf7c8b72c8315c867e515a11b62ba4dba1d3191258"
            else:
                archive = self.run([GIT, "-C", str(self.source), "archive", "342287dde89ec772293b4c3df24a7a80cb216a22",
                    "hooks", "scripts/scan-secrets.py", "scripts/install-scan-secrets.py", "scripts/scan_install_windows.py"]).stdout
            with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
                bundle.extractall(copy, filter="data")
        else:
            shutil.copytree(self.source / "hooks", copy / "hooks", ignore=shutil.ignore_patterns("__pycache__"))
            (copy / "scripts").mkdir()
            for name in ("scan-secrets.py", "scan_install_windows.py"):
                shutil.copy2(self.source / "scripts" / name, copy / "scripts" / name)
        dest = self.home / "neutral"
        receipt = self.run([self.python, "-I", "-S", "-B", str((copy if legacy else self.source) / "scripts/install-scan-secrets.py"),
            "install", "--source-dir", str(copy), "--destination", str(dest), "--json"])
        shutil.rmtree(copy)
        self.entry = [str(dest / "scan-secrets")]
        return json.loads(receipt.stdout)

    def commit(self, name=None, data=None, *, bypass=False, message="fixture", expected=0):
        if name is not None:
            (self.repo / name).write_bytes(data)
        self.git("add", "--all")
        return self.git(*(["-c", "core.hooksPath=" + os.devnull] if bypass else []), "commit", "-qm", message, expected=expected)

    def head(self):
        return self.git("rev-parse", "HEAD").stdout.decode().strip()

    def refs(self):
        return self.git("show-ref", cwd=self.remote, expected=None).stdout

    def gate(self, refs):
        rows = []
        for ref in refs:
            oid = self.git("rev-parse", ref).stdout.decode().strip()
            rows.append(f"{ref} {oid} refs/heads/{ref} {ZERO}\n")
        return self.cli("gate", "pre-push", "--repo", str(self.repo), "--git", GIT,
            "--budget-file", str(self.budget), "--remote", "origin", "--url", str(self.remote), data="".join(rows).encode(), expected=None)

    def instrument(self, refs):
        raw = b"".join(f"{ref} {self.git('rev-parse', ref).stdout.decode().strip()} refs/heads/{ref} {ZERO}\n".encode() for ref in refs)
        command = [self.python, "-I", "-S", "-B", str(self.source / "scripts/scan-secrets.py"),
            "gate", "pre-push", "--repo", str(self.repo), "--git", GIT, "--budget-file", str(self.budget),
            "--remote", "origin", "--url", str(self.remote), "--json"]
        path = self.root / "profile"
        profiled = self.run([*command[:4], "-m", "cProfile", "-o", str(path), *command[4:]], data=raw)
        stats = pstats.Stats(str(path)).stats
        functions = []
        for (file, line, name), (primitive, total, own, cumulative, _) in stats.items():
            if name in {"walk_graph", "capture", "acquire", "scan_line_events", "occurrence_tree"} and "scan_" in file:
                functions.append(dict(module=Path(file).name, function=name, calls=total, own_seconds=own, inclusive_seconds=cumulative))
        phases_path = self.root / "boundary-phases.json"
        phases = self.run([self.python, "-I", "-S", "-B", str(Path(__file__).resolve()), "--profile-child", str(phases_path), *command[4:]], data=raw)
        native = self.run(["/usr/bin/time", "-l", *command], data=raw, expected=None)
        rss = re.search(rb"(\d+)\s+maximum resident set size", native.stderr)
        return dict(label="separate profiler and separate native-RSS launches; excluded from capacity timings",
            profile_wall_seconds=profiled.elapsed, profile_counts=json.loads(profiled.stdout)["counts"], functions=functions,
            boundary_profile_wall_seconds=phases.elapsed, boundary_profile=json.loads(phases_path.read_bytes()),
            boundary_profile_counts=json.loads(phases.stdout)["counts"],
            native_exit_code=native.returncode, native_wall_seconds=native.elapsed,
            native_peak_rss_bytes=int(rss[1]) if rss else None,
            native_collector_available=native.returncode == 0 and b"Operation not permitted" not in native.stderr and rss is not None,
            native_outcome=json.loads(native.stdout)["outcome"] if native.stdout else None,
            native_stdout_bytes=len(native.stdout),
            native_stderr_bytes=len(native.stderr))

    def push(self, refs, *, clean):
        before = self.refs()
        old_marker = self.marker.read_bytes() if self.marker.exists() else b""
        result = self.git("push", "-q", "origin", *refs, expected=None)
        assert (result.returncode == 0) == clean, (result.returncode, result.stdout, result.stderr)
        if not clean:
            assert self.refs() == before, "blocked push changed remote refs"
            assert (self.marker.read_bytes() if self.marker.exists() else b"") == old_marker, "blocked push ran downstream"
        delivery = None
        if clean:
            tips = []
            for ref in refs:
                local, _, remote = ref.partition(":")
                remote = remote or "refs/heads/" + local
                source_oid = self.git("rev-parse", local).stdout.strip()
                assert self.git("rev-parse", remote, cwd=self.remote).stdout.strip() == source_oid
                tips.append(source_oid)
            ids = self.git("rev-list", "--objects", "--no-object-names", "--stdin", data=b"\n".join(tips) + b"\n").stdout
            ids = b"\n".join(sorted(set(ids.splitlines()))) + b"\n"
            acquired = self.git("cat-file", "--batch", data=ids).stdout
            delivered = self.git("cat-file", "--batch", data=ids, cwd=self.remote).stdout
            assert acquired == delivered, "published object bytes differ"
            delivery = dict(object_batch_sha256=digest(delivered), object_batch_bytes=len(delivered), objects=len(ids.splitlines()), checked_delivered_equal=True)
        return dict(exit_code=result.returncode, wall_seconds=result.elapsed, stdout_bytes=len(result.stdout), stderr_bytes=len(result.stderr), delivery=delivery,
                    blocked_remote_unchanged=not clean, blocked_downstream_zero=not clean)


def workflow(lab, upgraded):
    receipts = {"kind": "upgraded" if upgraded else "fresh", "neutral": lab.neutral(legacy=upgraded)}
    lab.receipts = receipts
    if upgraded:
        receipts["upgrade"] = lab.neutral()
    receipts["install"] = lab.install()
    receipts["clean_commit"] = lab.commit("content.txt", b"safe\n").returncode
    installed_entry = lab.entry
    lab.entry = [lab.python, "-I", "-S", "-B", str(lab.source / "scripts/scan-secrets.py")]
    receipts["source_cli_publication"] = lab.gate(["main"])
    assert receipts["source_cli_publication"]["value"]["outcome"] == "complete_clean"
    lab.entry = installed_entry
    receipts["clean_push"] = lab.push(["HEAD:refs/heads/main"], clean=True)
    lab.budget.chmod(0o666)
    receipts["current_budget_trust_rejected"] = lab.push(["HEAD:refs/heads/untrusted-budget"], clean=False)
    lab.budget.chmod(0o600)
    receipts["identity_repaired_retry"] = lab.push(["HEAD:refs/heads/identity-retry"], clean=True)
    receipts["historical_clean_status"] = lab.cli("status", "--repo", str(lab.repo))
    rejected = lab.commit("content.txt", credential() + b"\n", expected=None)
    assert rejected.returncode != 0 and b"content.txt" in rejected.stderr
    receipts["late_staged_rejected"] = rejected.returncode
    receipts["repaired_commit"] = lab.commit("content.txt", b"repaired\n").returncode
    shutil.rmtree(lab.home / "neutral")
    receipts["repaired_push"] = lab.push(["HEAD:refs/heads/main"], clean=True)
    receipts["repaired_push"]["source_copy_and_external_neutral_removed"] = True
    # Full-file staged policy: the credential is unchanged by the safe edit.
    lab.commit("content.txt", credential() + b"\nsafe\n", bypass=True)
    rejected = lab.commit("content.txt", credential() + b"\nchanged safe line\n", expected=None)
    assert rejected.returncode != 0 and b"content.txt" in rejected.stderr
    receipts["unchanged_staged_credential_rejected"] = rejected.returncode
    lab.commit("content.txt", b"safe repaired tip\n")
    receipts["intermediate_history_rejected"] = lab.push(["HEAD:refs/heads/main"], clean=False)
    # Ownership binds metadata including ctime; restoring bytes is insufficient.
    # Keep this destructive fixture-only control last and discard the fixture.
    owner = json.loads((lab.repo / ".git/scan-secrets/repository-installation.json").read_bytes())
    owned = Path(owner["installed_value"]).parent / "bundle/hooks/runtime/scan_engine.py"
    owned.write_bytes(owned.read_bytes() + b"\n# disposable drift control\n")
    receipts["current_owned_bytes_rejected"] = lab.push(["HEAD:refs/heads/drift"], clean=False)
    return receipts


def capacity(lab, case, instrumentation=False):
    # These constructions copy D0 shapes, never D0's prototype scanner/policy.
    refs = ["main"]
    if case == "first-publication":
        for number, size in enumerate(SIZES):
            (lab.repo / f"image-{number}.png").write_bytes(b"\0" * size)
    elif case == "merge-sized":
        size, remainder = divmod(9453698, 223)
        for number in range(223):
            body = (f"safe snapshot {number:03}\n".encode() * 4096)[:size + (number < remainder)]
            (lab.repo / f"snapshot-{number:03}").write_bytes(body)
    elif case == "repeated-blobs":
        for number in range(128):
            (lab.repo / f"shared-{number:03}").write_bytes(b"\0" * 262144)
    elif case == "large-blob":
        (lab.repo / "large.bin").write_bytes(b"\0" * 67108864)
    elif case == "multi-ref":
        lab.commit("base", b"safe base\n", bypass=True)
        base = lab.head()
        refs = []
        for number in range(12):
            ref = f"branch-{number}"
            lab.git("checkout", "-qB", ref, base)
            lab.commit(f"payload-{number}", bytes([number]) * 1048576, bypass=True)
            refs.append(ref)
    elif case == "long-history":
        lab.commit("shared", b"\0" * 262144, bypass=True)
        for number in range(512):
            lab.commit("version", f"safe version {number:04}\n".encode() * 64, bypass=True)
        assert int(lab.git("rev-list", "--count", "HEAD").stdout) == 513
        lab.git("fsck", "--full")
    else:
        raise ValueError(case)
    if case not in {"multi-ref", "long-history"}:
        lab.commit(bypass=True, message="capacity fixture")
    lab.neutral()
    installed = lab.install()
    clean = lab.gate(refs)
    assert clean["value"]["outcome"] == "complete_clean", clean
    counts = clean["value"]["counts"]
    # Production charges commit/tag MESSAGE bytes. D0 charged whole bodies.
    expected = {"first-publication": (20026491, 6), "merge-sized": (9453715, 223),
        "repeated-blobs": (33554449, 128), "large-blob": (67108881, 1),
        "multi-ref": (12583146, 25), "long-history": (135073800, 1025)}
    logical, paths = expected[case]
    assert counts["candidate_bytes"] == logical, (case, counts, expected[case])
    assert counts["path_occurrences"] == paths, (case, counts)
    if instrumentation:
        return dict(kind=case, supplemental_clean=clean, separate_instrumentation=lab.instrument(refs))
    clean_push = lab.push(refs, clean=True)
    # One-byte-under exact fixture logical requirement, within approved ranges.
    limited = json.loads(json.dumps(DEFAULTS))
    limited["publication"]["max_candidate_bytes"] = logical - 1
    lab.save_budget(limited)
    over = lab.gate(refs)
    assert over["value"]["outcome"] == "incomplete" and over["value"]["reason"] == "total_bytes_limit", over
    over_push = lab.push([ref + ":refs/heads/over-" + ref for ref in refs], clean=False)
    lab.save_budget(DEFAULTS)
    repaired = lab.push([ref + ":refs/heads/retry-" + ref for ref in refs], clean=True)
    # Bad history is constructed explicitly; ordinary installed commits reject it.
    if case == "multi-ref":
        lab.git("checkout", "-q", "main")
    lab.commit("zz-late-control", credential() + b"\n", bypass=True)
    late_refs = refs + ["HEAD"] if case == "multi-ref" else ["HEAD"]
    late = lab.gate(late_refs)
    assert late["value"]["outcome"] == "complete_findings", late
    assert late["value"]["counts"]["candidate_bytes"] >= logical
    late_push = lab.push([ref + ":refs/heads/late-" + str(i) for i, ref in enumerate(late_refs)], clean=False)
    return dict(kind=case, installed=installed, clean=clean, clean_push=clean_push, expected_logical_bytes=logical,
        d0_prototype_logical_bytes={"first-publication": 20026653, "merge-sized": 9453877, "repeated-blobs": 33554611,
            "large-blob": 67109043, "multi-ref": 12585828, "long-history": 135181482}[case],
        expected_path_occurrences=paths, over_limit=over, over_limit_push=over_push, repaired_retry_push=repaired,
        late_findings=late, late_push=late_push)


def checkpoint(lab, merge):
    if merge:
        shutil.rmtree(lab.repo)
        lab.run([GIT, "clone", "--shared", "--no-checkout", "-q", str(lab.source), str(lab.repo)])
        lab.git("-c", "core.hooksPath=" + os.devnull, "checkout", "-q", "e5c2be2095ba30626559adae7fb2c49ba691734e")
        conflict = lab.git("-c", "core.hooksPath=" + os.devnull, "merge", "--no-commit", "--no-ff", "5f3948c92e5037fb066321e9c9e5b03419410671", expected=None)
        assert conflict.returncode == 1
        expected = 9453698
    else:
        for number, size in enumerate(SIZES):
            (lab.repo / f"image-{number}.png").write_bytes(b"\x89PNG\x00" + b"\0" * (size - 5))
        (lab.repo / "repair.txt").write_bytes(b"safe pending input\n")
        expected = 20026493
    lab.neutral()
    historical = None
    if merge:
        historical = lab.cli("check", "--repo", str(lab.repo), expected=1)
        assert historical["value"]["outcome"] == "complete_findings"
        assert historical["value"]["counts"]["candidate_bytes"] == 9453698
        finding = historical["value"]["findings"]
        assert len(finding) == 1 and finding[0]["pattern"] == "stripe_live_key" and finding[0]["path"] == "scripts/test-codex-hooks-windows.ps1"
        target = finding[0]["path"]
        assert lab.git("ls-files", "-u", "--", target).stdout == b""
        path = lab.repo / target
        raw = path.read_bytes()
        safe, replaced = re.subn(rb"sk_live_[A-Za-z0-9]{16,}", lambda match: b"Z" * len(match[0]), raw)
        assert replaced == 2 and len(safe) == len(raw)
        path.write_bytes(safe)
        lab.git("add", "--", target)
    clean = lab.cli("check", "--repo", str(lab.repo), "--budget-file", str(lab.budget))
    assert clean["value"]["outcome"] == "complete_clean", clean
    assert clean["value"]["counts"]["candidate_bytes"] == expected, clean
    limited = json.loads(json.dumps(DEFAULTS))
    limited["checkpoint"]["max_candidate_bytes"] = expected - 1
    lab.save_budget(limited)
    over = lab.cli("check", "--repo", str(lab.repo), "--budget-file", str(lab.budget), expected=2)
    assert over["value"]["reason"] == "total_bytes_limit", over
    lab.save_budget(DEFAULTS)
    control = lab.repo / "zz-late-control"
    control.write_bytes(credential() + b"\n")
    late = lab.cli("check", "--repo", str(lab.repo), expected=1)
    assert late["value"]["outcome"] == "complete_findings", late
    control.write_bytes(b"repaired\n")
    retry = lab.cli("check", "--repo", str(lab.repo))
    assert retry["value"]["outcome"] == "complete_clean"
    return dict(kind="unresolved-merge" if merge else "six-binaries-checkpoint", expected_candidate_bytes=expected,
                exact_historical_replay=historical, size_preserving_test_credential_repair=merge,
                clean=clean, over_limit=over, late_findings=late, repaired_retry=retry)


def lfs_capacity(lab, binary, instrumentation=False):
    endpoint = runpy.run_path(str(lab.source / "scripts/test-scan-secrets-lfs.py"))["RecordingEndpoint"]()
    try:
        # Replace only the fixture-owned ordinary hook with real standard LFS.
        (lab.repo / ".git/hooks/pre-push").unlink()
        lab.run([str(binary), "install", "--local"], cwd=lab.repo)
        lab.neutral()
        installed = lab.install("--lfs", str(binary), "--lfs-endpoint", endpoint.url)
        data = b"\0" * 67108864
        oid = digest(data)
        store = lab.repo / ".git/lfs/objects" / oid[:2] / oid[2:4] / oid
        store.parent.mkdir(parents=True)
        store.write_bytes(data)
        pointer = f"version https://git-lfs.github.com/spec/v1\noid sha256:{oid}\nsize 67108864\n".encode()
        lab.commit("large.bin", pointer)
        clean = lab.gate(["main"])
        assert clean["value"]["outcome"] == "complete_clean", clean
        assert clean["value"]["counts"]["lfs_payload_bytes"] == 67108864
        if instrumentation:
            observation = dict(kind="large-lfs", supplemental_clean=clean, separate_instrumentation=lab.instrument(["main"]))
            assert endpoint.received_bytes == 0 and endpoint.batches == []
            return observation
        pushed = lab.push(["main"], clean=True)
        assert endpoint.received_bytes == 67108864 and endpoint.payloads == {oid: data}
        received, batches = endpoint.received_bytes, len(endpoint.batches)
        clean_head = lab.head()
        lab.commit("zz-late-control", credential() + b"\n", bypass=True)
        late = lab.gate(["main"])
        assert late["value"]["outcome"] == "complete_findings"
        denied = lab.push(["main:refs/heads/late"], clean=False)
        assert endpoint.received_bytes == received and len(endpoint.batches) == batches
        # Restore the previously checked clean tip, then bound it by one byte.
        lab.git("reset", "--hard", clean_head)
        # Inspect an embedded payload credential AFTER the first 64 MiB.
        bad = data + credential() + b"\n"
        bad_oid = digest(bad)
        bad_store = lab.repo / ".git/lfs/objects" / bad_oid[:2] / bad_oid[2:4] / bad_oid
        bad_store.parent.mkdir(parents=True, exist_ok=True)
        bad_store.write_bytes(bad)
        (lab.repo / "large.bin").write_bytes(f"version https://git-lfs.github.com/spec/v1\noid sha256:{bad_oid}\nsize 67108905\n".encode())
        lab.git("add", "large.bin")
        lab.git("commit", "--amend", "-qm", "fixture")
        embedded = lab.gate(["main"])
        assert embedded["value"]["outcome"] == "complete_findings", embedded
        embedded_push = lab.push(["main:refs/heads/embedded-payload-late"], clean=False)
        assert endpoint.received_bytes == received and len(endpoint.batches) == batches
        lab.git("reset", "--hard", clean_head)
        limited = json.loads(json.dumps(DEFAULTS))
        limited["publication"]["max_candidate_bytes"] = clean["value"]["counts"]["candidate_bytes"] - 1
        lab.save_budget(limited)
        over = lab.gate(["main"])
        assert over["value"]["outcome"] == "incomplete" and over["value"]["reason"] == "total_bytes_limit"
        over_push = lab.push(["main:refs/heads/over"], clean=False)
        assert endpoint.received_bytes == received and len(endpoint.batches) == batches
        lab.save_budget(DEFAULTS)
        retry = lab.push(["main:refs/heads/retry"], clean=True)
        assert endpoint.payloads[oid] == data
        return dict(kind="large-lfs", installed=installed, clean=clean, clean_push=pushed, late_findings=late,
            late_push=denied, over_limit=over, over_limit_push=over_push, repaired_retry_push=retry,
            embedded_after_64mib_findings=embedded, embedded_after_64mib_push=embedded_push,
            delivered_sha256=oid, delivered_size=67108864, rejected_additional_batch_requests=0, rejected_additional_payload_bytes=0)
    finally:
        endpoint.close()


def profile_child():
    """External process profiler; invoke the unchanged public source CLI.

    Attribute each measured wall interval once by active function boundary.
    Matching takes priority over acquisition, then graph traversal. The other
    bucket includes startup, audit/status, repository discovery and SQL outside
    those boundaries. This is a separately labeled instrumented diagnostic.
    """
    output, entry, *arguments = sys.argv[2:]
    frames = {}
    counts = {"enumeration": 0, "acquisition": 0, "matching": 0}
    seconds = dict(enumeration=0., acquisition=0., matching=0., other=0.)
    calls = dict(enumeration=0, acquisition=0, matching=0)
    last = time.monotonic()

    def category():
        return next((name for name in ("matching", "acquisition", "enumeration") if counts[name]), "other")

    def observe(frame, event, arg):
        nonlocal last
        now = time.monotonic()
        seconds[category()] += now - last
        last = now
        if event == "call":
            module = Path(frame.f_code.co_filename).name
            name = frame.f_code.co_name
            selected = ("matching" if module == "scan_stream.py" and name == "scan_line_events" else
                "acquisition" if (module == "scan_publication.py" and name == "capture" or module == "scan_lfs.py" and name == "acquire") else
                "enumeration" if module == "scan_publication.py" and name in {"walk_graph", "occurrence_tree"} else None)
            if selected:
                frames[id(frame)] = selected
                counts[selected] += 1
                calls[selected] += 1
        elif event == "return" and id(frame) in frames:
            counts[frames.pop(id(frame))] -= 1

    sys.argv = [entry, *arguments]
    code = 0
    sys.setprofile(observe)
    try:
        runpy.run_path(entry, run_name="__main__")
    except SystemExit as exc:
        code = exc.code
    finally:
        sys.setprofile(None)
        seconds[category()] += time.monotonic() - last
        Path(output).write_text(json.dumps(dict(seconds=seconds, calls=calls,
            method="disjoint wall intervals by active function boundary; matching > ObjectStore.capture > graph traversal; includes profiler overhead")))
    raise SystemExit(code)


def default_boundary(lab, publication):
    lab.neutral()
    if publication:
        for number in range(255):
            (lab.repo / f"shared-{number:03}").write_bytes(b"\0" * 1048576)
        (lab.repo / "tail.bin").write_bytes(b"\0" * 1048559)
        lab.commit(bypass=True, message="capacity fixture")
        lab.install()
        check = lambda: lab.gate(["main"])
        expected = 268435456
    else:
        (lab.repo / "large.bin").write_bytes(b"\0" * 67108864)
        (lab.repo / "tail.bin").write_bytes(b"")
        check = lambda: lab.cli("check", "--repo", str(lab.repo), expected=None)
        expected = 67108864
    clean = check()
    assert clean["value"]["outcome"] == "complete_clean" and clean["value"]["counts"]["candidate_bytes"] == expected, clean
    clean_push = lab.push(["main"], clean=True) if publication else None
    tail = lab.repo / "tail.bin"
    original = tail.read_bytes()
    tail.write_bytes(original + b"\0")
    if publication:
        lab.git("add", "tail.bin")
        lab.git("-c", "core.hooksPath=" + os.devnull, "commit", "--amend", "-qm", "capacity fixture")
    over = check()
    assert over["value"]["outcome"] == "incomplete" and over["value"]["reason"] == "total_bytes_limit", over
    assert over["value"]["diagnostic"]["measured"] == expected + 1, over
    denied = lab.push(["main:refs/heads/over-default"], clean=False) if publication else None
    tail.write_bytes(original)
    if publication:
        lab.git("add", "tail.bin")
        lab.git("-c", "core.hooksPath=" + os.devnull, "commit", "--amend", "-qm", "capacity fixture")
    retry = check()
    assert retry["value"]["outcome"] == "complete_clean"
    target = tail if publication else lab.repo / "large.bin"
    with target.open("r+b") as handle:
        handle.seek(-41, os.SEEK_END)
        handle.write(credential() + b"\n")
    if publication:
        lab.git("add", "tail.bin")
        lab.git("-c", "core.hooksPath=" + os.devnull, "commit", "--amend", "-qm", "capacity fixture")
    late = check()
    assert late["value"]["outcome"] == "complete_findings" and late["value"]["counts"]["candidate_bytes"] == expected, late
    late_push = lab.push(["main:refs/heads/late-default"], clean=False) if publication else None
    return dict(kind="publication-default-boundary" if publication else "checkpoint-default-boundary",
        expected_limit=expected, clean=clean, clean_push=clean_push, one_byte_over=over, blocked_push=denied, repaired_retry=retry,
        embedded_late_findings=late, embedded_late_push=late_push)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--instrumentation", action="store_true")
    parser.add_argument("--lfs", type=Path, default=Path("/tmp/design-b-lfs-3.8.0/git-lfs-3.8.0/git-lfs"))
    args = parser.parse_args()
    source = args.source.resolve()
    result = dict(status="in_progress", python=sys.version, platform=platform.platform(), commands=sys.argv,
                  git=subprocess.check_output([GIT, "--version"]).decode().strip(), observations=[],
                  source_revision=subprocess.check_output([GIT, "-C", str(source), "rev-parse", "HEAD"]).decode().strip(),
                  fingerprints={str(p.relative_to(source)): digest(p.read_bytes()) for p in sorted((source / "hooks/runtime").glob("*.py"))},
                  probe_sha256=digest(Path(__file__).read_bytes()), profiles=DEFAULTS)
    for name in ("scan-secrets.py", "install-scan-secrets.py", "scan_install_windows.py"):
        result["fingerprints"]["scripts/" + name] = digest((source / "scripts" / name).read_bytes())
    def retain():
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    retain()
    try:
        with tempfile.TemporaryDirectory(prefix="i3-p-") as temp:
            root = Path(temp).resolve()
            for case in args.case or ["fresh", "upgraded"]:
                lab = Lab(root / case, source, str(Path(sys.executable).resolve()))
                if case in {"fresh", "upgraded"}:
                    observation = workflow(lab, case == "upgraded")
                elif case in {"unresolved-merge", "six-binaries-checkpoint"}:
                    observation = checkpoint(lab, case == "unresolved-merge")
                elif case == "large-lfs":
                    observation = lfs_capacity(lab, args.lfs.resolve(), args.instrumentation)
                elif case in {"publication-default-boundary", "checkpoint-default-boundary"}:
                    observation = default_boundary(lab, case == "publication-default-boundary")
                else:
                    observation = capacity(lab, case, args.instrumentation)
                result["observations"].append(observation)
                retain()
                print(case + ": passed", flush=True)
        assert all(digest((source / path).read_bytes()) == sha for path, sha in result["fingerprints"].items()), "frozen source changed"
        result["status"] = "passed"
    except Exception as exc:
        result.update(status="failed", failure=repr(exc)[:4000])
        if hasattr(lab, "receipts"):
            result["partial_workflow"] = lab.receipts
        retain()
        raise
    retain()


if __name__ == "__main__":
    if sys.argv[1:2] == ["--profile-child"]:
        profile_child()
    else:
        main()
