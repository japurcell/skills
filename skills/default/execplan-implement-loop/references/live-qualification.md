# Live Gemini qualification

Run this once on a macOS or Linux machine with Gemini CLI. This makes paid model calls in a disposable repository. It qualifies the real provider integration; the deterministic test suite uses a fake provider. Keep this project until its evidence has been reviewed.

## 1. Check prerequisites

Copy or check out this skill bundle on that machine. Set its absolute path below. These examples use a POSIX shell such as bash or zsh.

```sh
LOOP_SKILL="/absolute/path/to/execplan-implement-loop"
python3 --version
git --version
gemini --version
test -f "$LOOP_SKILL/scripts/run.py"
```

Python must be 3.12 or newer. Gemini must report **0.65.0** exactly; other versions are rejected. Authenticate Gemini using your normal setup. Make the real `exec-plans` and `tdd` skills available through `~/.agents/skills` or `~/.gemini/skills`, or the equivalent workspace directories. Do not use placeholder skill files. See [maintenance prerequisites](../README.md#provider-qualification).

## 2. Create the disposable project

```sh
QUALIFICATION_ROOT="$(mktemp -d)"
QUALIFICATION_ROOT="$(cd "$QUALIFICATION_ROOT" && pwd -P)"
mkdir "$QUALIFICATION_ROOT/project"
cd "$QUALIFICATION_ROOT/project"
git init
git config user.name "Loop qualification"
git config user.email "loop-qualification@example.invalid"
git config commit.gpgsign false
cp "$LOOP_SKILL/evals/fixtures/live-qualification.md" ExecPlan.md
git add ExecPlan.md
git commit -m "test: prepare live loop qualification"
printf 'Keep this evidence directory: %s\n' "$QUALIFICATION_ROOT"
```

These Git settings apply only to this disposable repository. The plan asks Gemini to write two failing Python tests, implement a greeting function, and return a typed result. The runner performs task, milestone, and final acceptance checks and owns all three completion commits.

Before running the loop, open `gemini` interactively in this directory. Establish folder trust and confirm both real skills are discoverable and permitted to activate. Then exit Gemini. Configure a policy that allows the fixture's file edits and test commands without interactive input. The runner's child stdin is EOF. A permission failure is a useful blocked result, but it does not qualify successful execution. Do not assume authentication or trust alone grants tool permissions. The runner inherits your policy; it never silently enables `yolo`.

Run `git status --short` afterward. It must be empty before launch. If setup created workspace configuration, inspect and commit only the approved fixture configuration first. The next step records that clean baseline.

## 3. Validate and run

Keep reports outside the project so they do not dirty its Git worktree.

```sh
python3 "$LOOP_SKILL/scripts/run.py" "$PWD/ExecPlan.md" --validate-only
git rev-parse HEAD > "$QUALIFICATION_ROOT/baseline-head.txt"
gemini --version > "$QUALIFICATION_ROOT/gemini-version.txt"
python3 "$LOOP_SKILL/scripts/run.py" "$PWD/ExecPlan.md" \
  --max-runtime 600 --iteration-timeout 300 \
  > "$QUALIFICATION_ROOT/live-report.json" \
  2> "$QUALIFICATION_ROOT/progress.jsonl"
LOOP_EXIT=$?
printf 'Runner exit: %s\n' "$LOOP_EXIT"
cat "$QUALIFICATION_ROOT/live-report.json"
git status --short
git log --oneline > "$QUALIFICATION_ROOT/git-log.txt"
git status --porcelain > "$QUALIFICATION_ROOT/git-status.txt"
```

Allow up to ten minutes total and five minutes per Gemini iteration. This replaces the normal one-hour/twenty-minute defaults only for qualification. A timed-out iteration retries while the total budget allows. To watch progress from a second terminal, run `tail -f /absolute/evidence/directory/progress.jsonl` using the printed directory.

## 4. Check acceptance

A successful qualification has all of these results:

- Exit code `0`, report status `completed`, three completed tasks, and one completed milestone.
- Three runner completion commits after `baseline-head.txt`, with SHAs matching the report.
- Empty `git status --short`, correct greeting behavior, and passing declared verification records, including final acceptance.
- Reported Gemini session ID(s), a successful terminal provider result, and honest usage fields. Missing usage remains unknown.
- Gemini's own session history confirms activation of `exec-plans` and `tdd`, failing tests before implementation, and passing tests afterward. The worker did not stage or commit files. A successful runner report alone does not prove skill activation or test-first behavior.

Use the session IDs to inspect Gemini's existing transcript through its normal session tooling. The runner intentionally does not duplicate raw provider transcripts. If any item fails, retain the artifacts and report the failure; do not mark live acceptance complete.

## 5. Handle a blocked or timed-out run

Read `reason_code`, `detail`, and `run_directory` in the report. Fix missing authentication, skill discovery, or policy prerequisites before retrying. If a run directory exists, preserve the project and resume that same run:

```sh
python3 "$LOOP_SKILL/scripts/run.py" "$PWD/ExecPlan.md" \
  --resume "/absolute/run_directory/from/report" \
  --max-runtime 600 --iteration-timeout 300 \
  > "$QUALIFICATION_ROOT/resume-report.json" \
  2> "$QUALIFICATION_ROOT/resume-progress.jsonl"
```

Do not start a fresh run over partial changes, reset files, or delete Git locks. A commit failure resumes the prepared transaction after its cause is fixed. `unclean_execution_requires_reconciliation` requires stopping the old child tree and inspecting Git and task state before explicitly acknowledging reconciliation. Follow [recovery guidance](../README.md#recovery-and-limits); do not add acknowledgement blindly. A preflight failure without a run directory may be retried with the original command after its cause is fixed.

## 6. Return evidence

Provide `live-report.json`, `progress.jsonl`, `gemini-version.txt`, `baseline-head.txt`, `git-log.txt`, and `git-status.txt`. Include resume reports if used. Confirm whether actual skill activation and the failing-then-passing test sequence were visible in the reported session. Include a short relevant excerpt if needed, after checking it for private data. Full raw session logs are unnecessary. Refresh Git evidence after a resumed run.

The implementation plan's live-provider gate stays pending until this evidence passes review or the owner explicitly waives that gate.
