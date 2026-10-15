# T9b: verified native Darwin capture evidence

Observed on 2026-10-15 in `/Users/adam/.codex/worktrees/design-b-t9b/skills`, private branch `codex/design-b-t9b`, starting at `2f8cc4320387e4fdfc6dda595b0aba74a26a0dce`. This task owns only `scripts/test-scan-secrets-capture.py`, the scanner log capture and native-evidence validation in `.github/workflows/hooks-posix.yml`, and this document. The primary owns integration, the current ExecPlan, README, registry and the coordinated knowledge-maintenance pass. No production runtime, generated assets, installer, Windows workflow or provider registration changed.

## Evidence contract

The existing `native_once` wrapper lowers only its disposable child process's soft `RLIMIT_NPROC` to zero around the original `subprocess.Popen`. It now records the actual caught native errno and numeric `before`, `lowered` and `after` limit pairs only after its `finally` restoration succeeds and `getrlimit` verifies the restored pair. The original exception still reaches the scanner's existing bounded retry path. An unexpected errno, successful launch, absent branch or failed restoration cannot produce accepted evidence.

The parent reads at most 257 bytes and rejects observations longer than 256. It verifies integer limit pairs, a positive original soft limit, zero lowered soft limit, the original soft limit after restoration, the retained post-lowering hard limit and `errno.EAGAIN`. It also requires the existing audit outcome to match the clean/findings fixture. It emits one static-prefix JSON event containing only provider, mode, clean/findings status, numeric native errno and precise restoration/clamp flags. It retains the original `(response, log)` return contract and every existing capture assertion. No paths, arguments, raw stderr, raw exception text or fake credential bytes enter these events.

For example, the observed Codex/block/findings event is:

```text
SCANNER_NATIVE_CAPTURE {"hard_limit_clamped": true, "mode": "block", "native_errno": 35, "post_lowering_hard_retained": true, "provider": "codex", "soft_limit_restored": true, "status": "findings"}
```

The public event deliberately does not claim full restoration of the original hard limit. A disposable child probe observed `before=(10666, 16000)`, `lowered=(0, 10666)`, native errno `35`, and `after=(10666, 10666)` using the existing restoration method. An initial attempt to restore the whole original pair raised `ValueError`; the strengthened observation check caught that failure through its missing observation. The correction preserves the original `(before_soft, current_hard)` restoration and explicitly verifies what it restores. Parent process limits stayed `(10666, 16000)` across all 12 final native cases.

Apple's published [XNU `dosetrlimit` implementation](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/kern/kern_resource.c) caps both requested `RLIMIT_NPROC` values at `maxprocperuid` for a non-root process. This supports the clamp explanation; the retrieved current published source is not an exact source/build match for this host kernel. The numeric child observation above is direct host evidence. The test changes no host-wide limit or parent limit and exits each disposable child after its scan.

## CI behavior

The same seven existing test commands retain their meanings and order. Each of the three scanner-shell commands now sends combined stdout/stderr through `tee` to its own log under `$RUNNER_TEMP/hook security/logs`. GitHub's explicit Bash shell and the locally exercised `bash -e -o pipefail` preserve the scanner command's failure even when `tee` succeeds. The shells already invoke their capture suites, so CI adds no second capture invocation.

A separate final step validates those logs. Each provider must contribute exactly the four combinations of `block`/`warn` and `clean`/`findings`, for 12 total. The validator requires Darwin, the exact allowlisted schema, platform `errno.EAGAIN`, true soft-restoration and retained-hard flags, and a Boolean clamp flag. It rejects missing cases, malformed JSON, duplicate fields/events, unexpected fields/providers, incorrect types, wrong errno and false restoration flags. It does not print rejected input. A generic PASS, skip or `native_once` label is insufficient.

Read-only permissions, checkout without persisted credentials, the macOS runner, prerequisite checks, Homebrew bootstrap, Python 3.13 precedence, runner-temporary homes/logs with spaces and the initial four test commands remain unchanged. No prerequisite skip or `continue-on-error` was introduced.

## Local verification

Platform: macOS 26.7.1 arm64. The exact CI scanner blocks and native evidence validator use Python 3.13.14. The original red native-functional run and initial diagnostic probes used Python 3.14.6. Darwin `errno.EAGAIN` is `35`; no Linux-specific `11` is hardcoded in maintained source. Git is 2.54.0 (Apple Git-157), Bash 3.2.57 and RTK 0.51.0. Dependencies were not installed globally and no real home was deployed.

Before changing the capture source, a disposable Python driver imported its public `run_case` helper and ran all three providers, both modes and both clean/findings cases with `launch_fault='native_once'`. All 12 existing functional outcomes passed. Their logs contained no native evidence, and the exact new workflow validator exited 1 with `Missing native capture evidence for codex: 0/4 cases.` This is the meaningful red of the evidence requirement, not a source snapshot assertion.

After the correction, all 12 real native cases passed through the generated provider JSON entrypoints with the bounded child observations. All 12 events reported `native_errno=35`, `soft_limit_restored=true`, `post_lowering_hard_retained=true` and `hard_limit_clamped=true`. Coverage was exactly:

| Provider | block/clean | block/findings | warn/clean | warn/findings |
| --- | --- | --- | --- | --- |
| Codex | observed | observed | observed | observed |
| Copilot | observed | observed | observed | observed |
| Gemini | observed | observed | observed | observed |

The exact validator passed against those real native logs. Ten disposable log controls each exited 1: missing one case, malformed JSON, errno `11`, false soft restoration, false retained-hard flag, non-Boolean clamp flag, duplicate event, duplicate field, extra field and wrong provider. A separate disposable source control bypassed the native branch while retaining the `native_once` label: the parent failed for the missing observation and emitted no event. The exact Codex scanner pipeline was also exercised against a process-boundary Bash fixture that exited `37`; the pipeline retained exit `37` and `tee` saved its static failure line.

Final frozen-source verification ran the exact three workflow scanner blocks serially, with the workflow's isolated environment under `/private/tmp/t9b-evidence/final/hook security` and Python 3.13.14 first on PATH. Each block ran with `bash -e -o pipefail`:

```sh
rtk proxy bash scripts/test-codex-hooks-secrets-scanner.sh 2>&1 | tee "$RUNNER_TEMP/hook security/logs/codex-scanner.log"
rtk proxy bash scripts/test-hooks-secrets-scanner.sh 2>&1 | tee "$RUNNER_TEMP/hook security/logs/copilot-scanner.log"
rtk proxy bash scripts/test-gemini-hooks-secrets-scanner.sh 2>&1 | tee "$RUNNER_TEMP/hook security/logs/gemini-scanner.log"
```

All three shell suites exited 0, and each transitive capture suite printed its existing `PASS: <provider> scanner capture failures and no-HEAD success`. Each actual scanner log contained exactly its four required native events with the final schema. The exact final validator, extracted without modification from the workflow into `/private/tmp/t9b-evidence/validate-native.sh`, exited 0 both in the serial controller and through this independent invocation:

```sh
RUNNER_TEMP=/private/tmp/t9b-evidence/final rtk proxy bash -e -o pipefail /private/tmp/t9b-evidence/validate-native.sh
```

It printed `Verified all 12 native Darwin capture cases with restored soft process limits.` A disposable copy of those final actual scanner logs with one Codex event removed exited 1 with `Missing native capture evidence for codex: 3/4 cases.` The final combined log is `/private/tmp/t9b-evidence/final-run.log`; per-provider logs are under `/private/tmp/t9b-evidence/final/hook security/logs`. All temporary drivers, logs and controls remain disposable local artifacts, not required repository dependencies.

An earlier exploratory serial run passed the three functional scanner suites but correctly failed the final validator with `Invalid native capture evidence for codex.` The first two providers in that run had loaded the earlier ambiguous restoration event schema before the precision correction, while Gemini loaded the final schema. Those superseded logs remain under `/private/tmp/t9b-evidence/green`. The complete frozen-source repeat above replaces that mixed-schema run as acceptance evidence.

Vendored PyYAML 6.0.3 from `scripts/vendor` parsed the workflow with `BaseLoader`, preserving the `on` key. Structural checks preserved triggers, read-only permission, macOS runner, action ordering, Python 3.13, the seven serial test meanings and absence of a duplicate capture invocation or `continue-on-error`. `bash -n` passed every run block, now 11 including the added validator. Python AST parsing passed. `git diff --check` passed.

The [T9a recovery/drift controls](t9a-evidence.md) were not repeated merely to add log capture. Their initial four workflow commands and generator source are unchanged. Relative to integrated T9a `951618769b81b4364b0b3e7ea59c060a393b4c25`, the only recovery-suite change before T9b is T3a's added helper-closure test; the existing assertions used by T9a's deliberate recovery fault remain intact. T9b leaves all of them unchanged and separately proves failure propagation for its new pipeline. The [I1 evidence](i1-evidence.md) remains preparation evidence, not a new hosted run.

## Source identities and limits

SHA-256 identities for the final executable test tree:

| Source | SHA-256 |
| --- | --- |
| `scripts/test-scan-secrets-capture.py` | `fdf9314ea62508d405871a2870dda8c7da46b2ecca435378e11aaf2a7026d7d3` |
| `.github/workflows/hooks-posix.yml` | `e7948bb0bd1f92516725683eb6e84a369b2a565be33e06b00783fdbf1af221bb` |
| `hooks/runtime/scan_git.py` | `e85d2da00c3d61e006bc77ae2203796fce94c336352ff22e7467bda998ab082d` |
| `.codex/hooks/scan-secrets.py` | `ae047b4b96ea3b775c061b35a9f648c0e362dddb7b68d932ef754a3cbca42f1c` |
| `.copilot/hooks/scripts/scan-secrets.py` | `73a67c465d9ffda11ab52f1b3c9976f036c7eac7bac29c2c997dbb6d69901a5b` |
| `.gemini/hooks/scripts/scan-secrets.py` | `769c5acbd7c1efcd5fe62261ffd4513bfc4dd67fa5a6aec1c4e50a1804dd1a13` |

The original capture source used by the red run had SHA-256 `0061d58147aa93fa74b87587caa1cda34b80bed22e14dea4a611223367a766c9`; the starting workflow had `c1c8c8fff4172b7421db49e29d7a653f10af8d234f19809a5350b657863d43bc`.

These are local native Darwin process and source-test observations. No hosted Actions run, hosted prerequisite installation, branch protection, native Windows run, authenticated provider delivery, push, PR or real-home deployment is claimed. Later CLI/gate/lifecycle/installation CI coverage belongs to T9c after I4. No timing benchmark or performance acceptance was attempted.
