#!/usr/bin/env python3
"""Compare public hook processes to revision 069b3f22 on identical byte streams.

Run from any directory: python3 scripts/tests/hooks/test-input-baseline.py [candidate-root]
Requires Git and Python 3.12+. Run separately on each supported platform.
"""
import errno
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[3]
CANDIDATE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT
REVISION = "069b3f22"
HOOKS = {
    "common": (".codex/hooks/inject-brain.py", ["--provider", "codex"]),
    "rtk": (".copilot/hooks/scripts/rtk-hook-copilot.py", []),
    "codex": (".codex/hooks/load-required-skills.py", []),
}
BASE = b'{"hook_event_name":"SessionStart","source":"startup"'
def sized_object(size):
    prefix, suffix = BASE + b',"x":"', b'"}'
    body = b"a" * (size - len(prefix) - len(suffix))
    return [prefix] + [body[i:i + 4096] for i in range(0, len(body), 4096)] + [suffix]


CASES = {
    # Each tuple is (chunks, pause between chunks, hold pipe open after writing).
    "ascii-whitespace": ([b" \t" + BASE + b"}\r\n"], 0, True),
    "nbsp-both-sides": ([b"\xc2\xa0" + BASE + b"}\xc2\xa0"], 0, True),
    "split-utf8": ([BASE + b',"x":"\xc3', b'\xa9"}'], .05, True),
    "buffered-trailing": ([BASE + b"}x"], 0, True),
    "delayed-final": ([BASE, b"}"], .1, True),
    "incomplete": ([BASE], 0, True),
    "non-object": ([b"[]"], 0, True),
    "buffered-number": ([b" " * 4095 + b"12"], 0, True),
    "invalid-utf8": ([BASE + b',"x":"\xff"}'], 0, True),
    "depth-65": ([BASE + b',"x":' + b"[" * 65 + b"0" + b"]" * 65 + b"}"], 0, False),
    "large-fragmented": ([BASE + b',"x":"'] + [b"a" * 4096] * 256 + [b'"}'], 0, False),
    "codex-limit": (sized_object(1_000_000), 0, False),
    "codex-limit-plus-one": (sized_object(1_000_001), 0, False),
    "common-limit": (sized_object(2 * 1024 * 1024), 0, False),
    "common-limit-plus-one": (sized_object(2 * 1024 * 1024 + 1), 0, False),
    "over-common-limit": ([BASE + b',"x":"'] + [b"a" * 65536] * 33 + [b'"}'], 0, False),
}


REJECTED_INPUTS = {
    "common": {"nbsp-both-sides", "buffered-trailing", "incomplete", "non-object",
               "buffered-number", "invalid-utf8", "depth-65", "common-limit-plus-one",
               "over-common-limit"},
    "rtk": {"buffered-trailing", "incomplete", "non-object", "buffered-number", "invalid-utf8"},
    "codex": {"buffered-trailing", "incomplete", "non-object", "buffered-number", "invalid-utf8",
              "large-fragmented", "codex-limit-plus-one", "common-limit", "common-limit-plus-one",
              "over-common-limit"},
}

RTK_ACCEPTED = {
    "ascii-whitespace", "nbsp-both-sides", "split-utf8", "delayed-final",
    "depth-65", "large-fragmented", "codex-limit", "codex-limit-plus-one",
    "common-limit", "common-limit-plus-one", "over-common-limit",
}


def run(root, hook, case, work):
    rel, args = HOOKS[hook]
    home = work / "home"
    (home / ".agents/skills/caveman").mkdir(parents=True, exist_ok=True)
    (home / ".agents/skills/caveman/SKILL.md").write_text("baseline skill\n")
    bindir = work / "bin"
    bindir.mkdir(exist_ok=True)
    capture = work / "forwarded"
    capture.unlink(missing_ok=True)
    recorder = "import os,sys\nopen(os.environ['CAPTURE'], 'wb').write(sys.stdin.buffer.read())\nprint('{\"mock\":true}')\n"
    if os.name == "nt":
        (bindir / "record.py").write_text(recorder)
        (bindir / "rtk.cmd").write_text('@echo off\n"' + sys.executable + '" "%~dp0record.py"\n')
    else:
        mock = bindir / "rtk"
        mock.write_text("#!" + sys.executable + "\n" + recorder)
        mock.chmod(0o755)
    env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), CAPTURE=str(capture), PATH=str(bindir) + os.pathsep + os.environ.get("PATH", ""))
    proc = subprocess.Popen([sys.executable, str(root / rel), *args], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, cwd=work, bufsize=0)
    chunks, delay, hold = case
    writer_errors = []
    def writer():
        try:
            for i, chunk in enumerate(chunks):
                if i and delay:
                    time.sleep(delay)
                remaining = memoryview(chunk)
                while remaining:
                    remaining = remaining[os.write(proc.stdin.fileno(), remaining):]
            if not hold:
                proc.stdin.close()
        except Exception as error:
            writer_errors.append(error)
    thread = threading.Thread(target=writer, daemon=True)
    thread.start()
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        raise AssertionError(f"{hook} did not finish within 8 seconds")
    thread.join(timeout=2)
    if thread.is_alive():
        raise AssertionError(f"{hook}/{work.name}: writer did not finish")
    if writer_errors:
        error = writer_errors[0]
        closed_pipe = isinstance(error, BrokenPipeError) or (
            os.name == "nt" and isinstance(error, OSError) and error.errno == errno.EINVAL
        )
        expected_rejection = work.name in REJECTED_INPUTS[hook]
        if not (closed_pipe and expected_rejection):
            raise AssertionError(f"{hook}/{work.name}: unexpected writer error") from error
    # A still-open writer establishes that the consumer completed without EOF.
    pipe_open = hold and not proc.stdin.closed
    try:
        proc.stdin.close()
    except BrokenPipeError:
        pass
    stdout, stderr = proc.stdout.read(), proc.stderr.read()
    forwarded = capture.read_bytes() if capture.exists() else None
    assert proc.returncode == 0, (hook, proc.returncode, stderr)
    return stdout, stderr, forwarded, pipe_open


def main():
    with tempfile.TemporaryDirectory(prefix="hook-input-baseline-") as tmp:
        temp = Path(tmp)
        reference = temp / "reference"
        reference.mkdir()
        archive = subprocess.check_output(["git", "-C", str(ROOT), "archive", REVISION])
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(reference, filter="data")
        # Verify the executable bytes against the repository object, independently of the archive.
        for rel, _ in HOOKS.values():
            blob = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{REVISION}:{rel}"])
            assert (reference / rel).read_bytes() == blob, rel
        for name, case in CASES.items():
            for hook in HOOKS:
                a = temp / "old" / hook / name
                b = temp / "new" / hook / name
                a.mkdir(parents=True)
                b.mkdir(parents=True)
                old = run(reference, hook, case, a)
                new = run(CANDIDATE, hook, case, b)
                assert old == new, f"{name}/{hook}: reference={old!r}, candidate={new!r}"
                stdout, stderr, forwarded, pipe_open = old
                if hook == "rtk" and name in RTK_ACCEPTED:
                    assert forwarded == b"".join(case[0]) and forwarded, f"{name}: RTK did not receive the exact bytes"
                elif hook == "rtk":
                    assert forwarded is None, f"{name}: invalid input reached RTK"
                print(f"{name}/{hook}: stdout={stdout.decode().strip()} stderr={stderr.decode().strip()!r} forwarded={len(forwarded) if forwarded is not None else None} pipe_open={pipe_open}")
    print("Public hook input parity passed")


if __name__ == "__main__":
    main()
