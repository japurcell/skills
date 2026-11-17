---
name: verify-skills
description: Verify the Skills repository installer CLI and installed assets in disposable homes. Use when proving installation, category selection, generated agents, or provider hook configuration after changes.
---

# Verify Skills

The primary surface is `scripts/install.sh`, with `scripts/install.ps1` as the PowerShell entrypoint. Installed skills, agents, and provider hooks are secondary surfaces. No server, auth, port, or database is needed. Run from the checkout root in one dedicated Bash shell; keep its variables through cleanup. Read [the feature map](features/README.md), then the selected journey before driving it.

## Launch

Use real Bash, Python 3.11+ (for TOML evidence), Git, and stable RTK >=0.50.0. No dependency install or build is needed. Start a dedicated PTY with `bash --noprofile --norc`, then:

```bash
VERIFY_ROOT="$PWD"
VERIFY_RUN="$(rtk proxy mktemp -d /tmp/verify-skills.XXXXXX)"
VERIFY_HOME="$VERIFY_RUN/home"
VERIFY_EVIDENCE="$VERIFY_RUN/evidence"
rtk proxy mkdir -p "$VERIFY_HOME" "$VERIFY_EVIDENCE"
trap 'rtk proxy rm -rf -- "$VERIFY_RUN/home"' EXIT
rtk proxy git rev-parse HEAD > "$VERIFY_EVIDENCE/revision.txt"
rtk proxy git diff --binary > "$VERIFY_EVIDENCE/source.diff"
rtk proxy git status --short > "$VERIFY_EVIDENCE/status.txt"
rtk --version > "$VERIFY_EVIDENCE/rtk.txt"
printf '%s\n' "$VERIFY_RUN"
```

Ready means Doctor passes and the home is empty. Each concurrent run needs its own `VERIFY_RUN`; never share a home. Use command-scoped `env HOME=...`, never change the shell's HOME. Explicitly override inherited CODEX_HOME and category selection on installer commands. These commands do real installations, not dry-runs. Scratch home redirection is verification scaffolding; it requires no fake RTK or altered source assets.

## Doctor

Run this read-only check first when anything looks off. Exit 0 plus current generated outputs means the checkout and isolated destination are worth driving. Record every failure; do not regenerate sources merely to conceal a failed check.

```bash
rtk proxy bash -c '
  set -e
  test "$PWD" = "$1"
  test -d "$2/home" && test ! -L "$2/home"
  python3 -c "import sys,tomllib; assert sys.version_info >= (3,11)"
  bash -n scripts/install.sh
  python3 -B scripts/validate-skill-sources.py skills
  python3 -B scripts/generate-hooks.py --check
  python3 -B scripts/configure-rtk.py --home "$2/home" --check
' verify-doctor "$VERIFY_ROOT" "$VERIFY_RUN" > "$VERIFY_EVIDENCE/doctor.txt" 2>&1
```

## Drive

Use the public CLI, with raw stdout/stderr captured via `rtk proxy`. Start with [default installation](features/install.md); use [selection](features/selection.md), [agents](features/agents.md), or [hooks](features/hooks.md) for those changes. Each file defines its assertions and additional entrypoints. A single passing journey proves only that journey. Run all listed entrypoints when claiming the whole feature works.

## Evidence

Keep evidence in `$VERIFY_RUN/evidence`, outside the disposable home. Capture exact actions, exit codes, both streams, and file readback. A success message alone is insufficient. Record OS/tool versions and selected journey in the result. Preserve failed attempts in separate run directories. Assert real filesystem side effects; use mocks only at an existing external boundary and label their limits. For any future dry-run mode, observe file, network, and Git-ref effects before claiming it is side-effect free.

Installer evidence does not prove a provider loaded or trusted its hooks or an agent obeyed a skill. Native provider testing needs a separately isolated client profile and session evidence; refuse to double-drive a shared account session. POSIX PowerShell evidence does not establish native Windows behavior.

## Cleanup

On success or failure, in the same shell:

```bash
rtk proxy rm -rf -- "$VERIFY_RUN/home"
rtk proxy test ! -e "$VERIFY_RUN/home"
rtk proxy test -s "$VERIFY_EVIDENCE/doctor.txt"
rtk proxy ls -l "$VERIFY_EVIDENCE"
trap - EXIT
```

Confirm the selected journey's action logs and readback artifact also survive. Close the dedicated shell. There are no background processes; if an added journey launches one, record its PID and terminate only that owned process. Keep the evidence directory and report its absolute path.

## Helpers

No new helper is shipped. Reuse maintained installer suites for broader regression coverage: `rtk proxy bash scripts/tests/installers/test-install.sh` and `rtk proxy pwsh -NoProfile -File scripts/tests/installers/test-install.ps1`. These fixture suites supplement the real-asset journey; they do not replace it. Their fixture/mock and platform limits must remain visible.
