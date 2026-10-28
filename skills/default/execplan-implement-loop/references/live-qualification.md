# Owner-run Gemini qualification

This procedure makes live Gemini calls in a disposable repository. Use it only after the owner has explicitly authorized paid provider use. The `--authorize-paid-run` flag records that authorization; the flag alone does not grant it.

## Historical evidence and scope

The original adapter completed an owner-run qualification on 2026-10-27 with Gemini CLI 0.65.0. That is historical evidence for the original adapter flow. It does not establish readiness on this machine or qualify the follow-up doctor, reviewed-policy, blocker, observation, and helper behavior. The follow-up has no live provider proof as of 2026-10-28. Local tests and fake-provider runs are not live evidence.

A fresh run records the exact bundle digest, current local doctor result, provider session identifiers, runner reports, and disposable Git history. It documents only what this machine and observed attempt did. It does not turn unknown authentication, trust, or effective permission into a general readiness claim.

The historical qualification used the user-level policy file `~/.gemini/policies/qualification.toml`. If it remains on a machine, its owner should review whether it is still needed through their normal configuration process before a fresh provider attempt. If the owner decides it is no longer needed, they may remove it through that same process. An explicit `--policy` file does not disable or erase inherited user policy. The runner and this guide never edit or delete the historical global file; any cleanup is an owner-managed configuration action.

## Prerequisites

Use macOS or Linux with Python 3.12 or newer, Git, Gemini CLI 0.65.0, authentication configured through the owner's normal process, and the real `exec-plans` and `tdd` skills discoverable to Gemini. The runner checks the version and required skill files. It does not install skills, establish project trust, write policy, or prompt to discover permissions.

Choose an absolute path to the installed bundle and a new absolute qualification root whose parent already exists. Replace the example paths below with those literal paths. Use the same literal paths in every command, quoting a literal path if it contains spaces. The root must not already exist. If setup stops after creating it, preserve the partial files and choose a different new root for a retry.

An explicit policy is optional. If the owner has already reviewed a single UTF-8 TOML file, it can be supplied with `--policy` to doctor and run. The file must be a regular file no larger than 1 MiB; symlink path components and commas in the path are rejected. The selected path and exact-byte hash are recorded and checked before provider spawn. This file supplements other provider policies and does not prove effective permissions. Gemini CLI 0.65.0 disables implicit workspace `.gemini/policies` discovery. Do not create or edit global policy or add blanket grants for this qualification.

## Create the disposable project

Run setup from the copied or installed bundle. It creates a new owner-only root containing `project/`, `evidence/`, and an owner-only manifest; copies the bundled fixture to `project/ExecPlan.md`; and configures Git identity and signing only in that disposable repository. Setup makes no Gemini call and changes no trust, skills, policy, or user configuration. It prints the physical root, baseline commit, manifest path, and a suggested next argument vector as JSON. Review the output; setup does not start the paid run.

```sh
python3 /absolute/path/to/execplan-implement-loop/scripts/qualify.py setup --root /tmp/execplan-loop-qualification-2026-10-28
```

## Inspect local readiness

Doctor is local diagnosis. It can call only bounded local checks and `gemini --version`; it sends no prompt and does not activate skills. It emits one JSON object. Exit 0 means no known local blocker, not `ready`: `readiness.status` is `blocked` or `unknown`, and `can_attempt: true` means only that the local checks found no known blocker. Authentication, project trust, effective policy, and permission for paid use remain unknown. Exit 3 reports a known blocker. Exit 2 reports invalid plan or supplied configuration. Do not proceed past a known blocker or treat an unknown as authorization.

This standalone inspection is optional because helper `run` repeats doctor immediately before starting the runner. It prints its JSON to the foreground session; helper collection does not save this standalone report. Use the same reviewed policy path that will be passed to `run`:

```sh
python3 /absolute/path/to/execplan-implement-loop/scripts/run.py /tmp/execplan-loop-qualification-2026-10-28/project/ExecPlan.md --doctor
```

If the result is blocked, resolve the reported prerequisite only through already-authorized paths, then inspect doctor again. A missing skill file, wrong provider version, or invalid selected policy is a blocker. Do not bypass a user, sandbox, policy, filesystem, or path restriction. An alternate I/O method is allowed only for the same already-authorized writable path.

## Run in the foreground

Only after the owner explicitly authorizes a paid provider attempt, run the helper in a long-session-capable foreground tool. The helper repeats doctor, saves its report and stderr, and starts the bundled runner only when doctor has no known local blocker. Its total limit is 600 seconds and its iteration limit is 300 seconds. Keep waiting on the same session until it completes. Do not detach it, start a daemon, or launch a replacement while it may still be running.

```sh
python3 /absolute/path/to/execplan-implement-loop/scripts/qualify.py run --root /tmp/execplan-loop-qualification-2026-10-28 --authorize-paid-run
```

For an already-reviewed policy, append its literal path as `--policy /absolute/path/to/reviewed-policy.toml`. `--authorize-paid-run` is required on every run and resume, together with actual authorization from the owner. A doctor result with `readiness.status: "unknown"` and `can_attempt: true` permits only an attempt; it does not authorize or predict a successful provider call.

The helper numbers attempts and stores doctor JSON, runner summary, progress, and state under `evidence/attempts/`. It preserves earlier attempts and refuses to overwrite evidence or run concurrently. Review the JSON it prints and the paths it names. The helper never scrapes provider transcripts.

## Resume and collect evidence

If a run stops with a recorded run directory, preserve the project and resume that same run after reviewing the report. Use the exact run directory printed by the previous report:

```sh
python3 /absolute/path/to/execplan-implement-loop/scripts/qualify.py run --root /tmp/execplan-loop-qualification-2026-10-28 --resume /tmp/execplan-loop-qualification-2026-10-28/evidence/attempts/attempt-0001/runner-state --authorize-paid-run
```

Supply `--policy` again only when using the same reviewed policy, or explicitly select newly reviewed bytes after reviewing the change. Never start a fresh run over partial work. A `cleanup_unconfirmed` result means the helper or runner could not confirm that owned child processes stopped. Do not launch a replacement. Confirm the old process tree has stopped, inspect the report, project status, task delta, HEAD, index, plan, and lock ownership, then follow the runner's recovery requirements. The qualification helper does not expose `--acknowledge-unclean-stop`; if the runner reports `unclean_execution_requires_reconciliation`, preserve the evidence and stop the helper flow for owner-directed recovery. The acknowledgement is an assertion after reconciliation, not a cleanup action. Never acknowledge blindly, delete a lock as a shortcut, reset files, or discard partial work.

Collect local evidence after setup, a run, and any resume:

```sh
python3 /absolute/path/to/execplan-implement-loop/scripts/qualify.py collect --root /tmp/execplan-loop-qualification-2026-10-28
```

Collection refreshes baseline reachability, branch, HEAD, Git status, commit history, and saved doctor and runner reports. It writes a new numbered collection without replacing earlier evidence, and reports missing expected artifacts in `missing_evidence`. A successful collection means collection finished; it does not mean qualification succeeded. In particular, an empty collection before a paid run is not live qualification evidence.

## Review the result

Review the doctor report, runner summary, progress file, baseline commit, current Git status, and commit log named by the collection. A successful runner attempt has exit 0, status `completed`, all fixture tasks and acceptance checks completed, and runner-owned commits matching the report. Inspect the Gemini session through its normal session interface to confirm skill activation and the test-first sequence; the helper does not copy raw transcripts. Preserve blocked or incomplete artifacts and report their reason codes. Do not claim current-machine readiness beyond the checks and attempt evidence, and do not mark the new follow-up live-qualified from fake-provider tests.
