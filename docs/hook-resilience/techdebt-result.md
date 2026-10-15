# Hook resilience duplication cleanup

Scope: `main...HEAD`, initially main `47d82b8b` and HEAD `8f58c7f2`. All 28 accepted safe consolidation groups are implemented and independently validated in the working tree. Final review identified no further safe, meaningful duplication in scope. No commits, push, or live hook installation occurred.

The completed working plan was removed under repository retention rules. This result preserves its candidate decisions, acceptance evidence, and limitations.

## Complete findings

Generated provider copies and historical evidence are intentional. Canonical changes were regenerated; shared primitives are embedded at generation time so provider installations remain independent.

| ID | Kind | Fixed duplication |
| --- | --- | --- |
| S1 | near | Scanner attribution formatting with explicit security, audit, enforcement, route, and cause. |
| S2 | near | Early provider denial payloads shared with recovery; Codex Stop and PreToolUse remain distinct. |
| S3 | reimplementation | Finding accounting, preserving 100 retained, 1000 processed, order, and draining. |
| S4 | near | Index-record parsing with explicit stage and canonical-path requirements. |
| S5 | near | Index-source classification for reservation and acquisition. |
| S6 | near | Common normal scanner logging context; exception recovery retains its separate deadline and location. |
| S7 | near | Scanner fixture mixin/constants; removed dynamic imports and grafting from concrete test classes. |
| S8 | near | Fake Git installation; individual case programs and I/O policies remain visible. |
| S9 | near | Narrow scanner tool-call envelopes. |
| S10 | near | Shell scanner attribution expectations; only build identity comes from actual output. |
| S11 | near | Twenty-two shared Copilot/Gemini scenarios, retaining both provider executions and differing assertions. |
| S12 | exact | Guardian suffix log normalization reuses its existing helper. |
| D4 | near | Credential-label detection with separate diagnostics and report presentation. |
| D5 | near | Recovery registration traversal retaining mutable handler identity. |
| D6 | exact | Raw provider envelopes without alias or payload conversion. |
| D7 | near | Entrypoint paths with explicit root and filename. |
| D8 | exact | Fresh common-module loading without cached patched state. |
| D9 | exact | Diagnostics owner/mode checks retaining the Windows exemption. |
| P1 | reimplementation | Trusted launch serialization and security filenames shared by installers and embedded diagnostics. |
| P2 | near | POSIX trusted-argument recognition; ownership and Windows validation remain separate. |
| P3 | near | Guardian incomplete predicates and attribution, preserving explicit fields and bootstrap availability. |
| P4 | near | Guardian audit payloads; provider storage remains separate. |
| P5 | near | Warm-sample retention/finalization, preserving scheduling, adjacency, failure evidence, and statistics. |
| P6 | reimplementation | Disposable benchmark environment base with caller overlays. |
| P7 | near | Separate checked macOS RSS collection/parsing outside latency measurement. |
| P8 | reimplementation | Runtime fingerprint footprint with distinct Git-object and filesystem readers. |
| P9 | near | Exact-capacity/high-line patch fixtures and historical dimensions, retaining independent assertions. |
| P10 | exact | Release test loader reuse with fresh modules. |

Canonical owners: [reporting](../../hooks/families/reporting.py), [diagnostics](../../hooks/families/diagnostics.py), [scanner](../../hooks/families/scan_secrets.py), [streaming](../../hooks/families/scanner_stream.py), [Guardian](../../hooks/families/tool_guard.py), and [trusted launches](../../scripts/trusted_hook_launch.py).

New shared modules: [benchmark support](../../scripts/hook_benchmark_support.py), [provider test support](../../scripts/hook_test_support.py), [scanner Python fixtures](../../scripts/scanner_test_support.py), and [scanner shell scenarios](../../scripts/scanner-test-support.sh).

## Defects fixed

Diagnostic labels now redact OpenAI-shaped `sk-` credentials, API-key assignments, and compatible Unicode spellings. Public standalone/recovery cases failed before the fix for all three providers, then passed. Diagnostics retains Unicode, control filtering, and 160-byte UTF-8 clipping; security reports retain their NFKC/ASCII formatting and bounds.

Independent validation found a missing release-harness fingerprint dependency. `hook_test_support.py` now participates in the complete seven-file identity; the existing mechanics test asserts that footprint and an independent probe verified each hash.

Final review found that embedded launch-parser annotations lost their module's future import. Native Python 3.9.6 reproduced standalone startup failure. The standalone header now postpones annotations; all 10 diagnostics tests pass on Python 3.9.6. Independent review closed the finding. Scanner recovery already had the required future import.

## Validation

Commands ran from the repository root using `rtk proxy`, with `login:false`. Every row below passed, without deleting, disabling, or skipping maintained tests.

| Command after `rtk proxy` | Result |
| --- | --- |
| `python3 scripts/test-hook-diagnostics.py` | 10 passed. |
| `/usr/bin/python3 scripts/test-hook-diagnostics.py` | 10 passed on native Python 3.9.6 after the compatibility fix. |
| `python3 scripts/test-hook-diagnostic-recovery.py` | 13 passed, including disposable Bash/macOS PowerShell installs and registered-command execution. |
| `python3 scripts/test-hook-input-bounds.py` | 17 passed. |
| `python3 scripts/test-security-reporting.py` | 14 passed. |
| `python3 scripts/test-security-banners.py` | 14 passed. |
| `python3 -B scripts/test-scan-secrets-stream-component.py -v` | 12 passed. |
| `python3 -B scripts/test-scan-secrets-streaming.py -v` | 13 passed across all providers. |
| `python3 -B scripts/test-scan-secrets-merge.py -v` | 33 passed across all providers. |
| `python3 -B scripts/test-scan-secrets-capture.py PROVIDER` | Complete matrix passed separately for Copilot, Gemini, and Codex. |
| `python3 scripts/test-tool-guard-native-data.py` | 26 passed. |
| `python3 scripts/test-tool-guard-limits.py` | 18 passed. |
| `python3 scripts/test-tool-guard-false-positives.py` | 153 corpus cases passed. |
| `python3 scripts/test-install-codex-hooks.py` | Passed. |
| `bash scripts/test-hooks-secrets-scanner.sh` | Exact isolated repetition passed capture precheck and all 28 shell tests, including the 22 shared scenarios. |
| `bash scripts/test-gemini-hooks-secrets-scanner.sh` | Capture precheck and all 25 shell tests passed. |
| `bash scripts/test-codex-hooks-secrets-scanner.sh` | Public envelopes and capture checks passed. |
| `bash scripts/test-hooks-tool-guard.sh` | Passed. |
| `bash scripts/test-gemini-hooks-tool-guard.sh` | Passed. |
| `bash scripts/test-codex-hooks-tool-guard.sh` | 14 passed. |
| `python3 scripts/test-generate-hooks.py` | 26 passed; protected fixture writes used approved escalation. |
| `python3 scripts/test-verify-hook-release.py` | 15 passed in final quiet window; native RSS used approved escalation. |
| `python3 scripts/test-benchmark-high-rate-hooks.py` | Two passed, sequentially after release mechanics. |
| `python3 scripts/generate-hooks.py --check` | All 38 generated files current. |
| `git diff --check` | Passed. |

Shell checks used disposable writable `OBSERVABILITY_LOG_PATH` values. Each affected shell script was syntax-checked separately. Python discovery retains 33 merge, 13 streaming, and 14 reporting tests; the fixture mixin contains no tests. Copilot/Gemini retain original 28/25 call counts and order.

Additional proofs matched 164 old/new launch outcomes, resource fixture bytes, benchmark environments, and runtime footprints. A direct-render scanner comparison passed 24 public scenarios. Final compatibility regeneration changed only standalone future imports and build identities in six outputs.

These are functional and verification-mechanics checks. They do not replace earlier complete latency acceptance evidence, which remains tied to its original source.

## Retained failures and limits

The first Copilot shell run stopped in its capture precheck: a credential control returned incomplete `git_capture_failed/git_head` instead of findings. Focused block/warn controls, the complete Copilot capture matrix, and the exact isolated full shell suite subsequently passed. The original cause remains unexplained; later passes do not erase or explain it. Its expected-finding assertion was unchanged.

The [follow-up investigation](capture-reliability-result.md) reproduces and repairs transient Git launch exhaustion and adds safe OS diagnostics. It preserves the distinction between that proven failure class and the historical incident's missing errno.

Initial RSS collection was sandbox-denied. A later mechanics run overlapped high-rate testing and failed a gate; its temporary report was removed by the existing test, leaving its cause unproven. Final independent serial checks passed with retained logs. No complete performance acceptance is inferred.

Moved synthetic literals initially blocked normal source tools. Automatic review rejected Terminal; the user approved the narrow repair, but the computer-use runtime still prohibited that app. The user restored the three extraction files twice. No alternate app or disabled guard was used. Successful recovery dynamically constructed all fixture literals, preserved runtime bytes, and checked complete candidate files plus actual Git additions using installed/generated scanners in disposable Git before repository writes.

Native Windows execution and authenticated provider delivery remain unverified. macOS PowerShell is not Windows proof. No live installation occurred.

## Deliberately retained boundaries

These are not safe mechanical duplication fixes: independent matching oracles; Unicode versus byte-first diff framing; bounded streaming allowlist specialization; filesystem readers with different trust/fallback rules; classification before replay; retention and serialization defenses; different duplicate-key errors; distinct build identities and response bounds; strict Guardian versus scanner response readers; complete fixture lifecycles; installer preflight timing; provider ownership recognition; platform copy paths; independent expected launch strings and test schema tables. Unifying these would change behavior, weaken independent evidence, or require a separate architectural decision.

No further safe in-scope duplication target remained after final review.

## Knowledge maintenance

The single coordinated `update-agent-docs` pass checked current source against security/testing instructions and scanner consistency memory. Existing contracts remain accurate. Ordinary helper layout and session history do not qualify for canonical memory.

Added: None. Changed: None. Split or moved: None. Deduplicated: None. Index updates: None. Remaining canonical doc quality TODOs: None.

## Delegation audit

Selected and submitted values below are the exact initial spawn arguments. Executed model/effort were not reported by the runtime and remain unconfirmed. Thresholds were monitored with bounded waits and progress reports. No task was cancelled for exceeding its threshold. Follow-ups resumed their original task and agent. No nested delegation occurred.

| Agent/task | Selected and submitted model/effort | Warning threshold | Status | Output verified | Routing compliant |
| --- | --- | --- | --- | --- | --- |
| `debt_scope` | `gpt-6-luna` / `medium` | Not explicitly set | completed | yes | no: missing threshold |
| `debt_scanner` | `gpt-6.1-sol` / `high` | 15 minutes | completed | yes | yes |
| `debt_diagnostics` | `gpt-6.1-sol` / `high` | 15 minutes | completed | yes | yes |
| `debt_support` | `gpt-6.1-sol` / `high` | 15 minutes | completed | yes | yes |
| `dedupe_diagnostics` | `gpt-6.1-sol` / `high` | 25 minutes | completed | yes | yes |
| `dedupe_scanner` | `gpt-6.1-sol` / `high` | 25 minutes | completed | yes | yes |
| `dedupe_support_impl` | `gpt-6.1-sol` / `high` | 25 minutes | completed | yes | yes |
| `dedupe_scanner_tests` | `gpt-6.1-sol` / `high` | 25 minutes | completed | yes | yes |
| `dedupe_scanner_shell` | `gpt-6.1-sol` / `high` | 25 minutes | completed | yes | yes |
| `validate_support` | `gpt-6.1-sol` / `high` | 20 minutes | completed | yes | yes |
| `validate_diagnostics` | `gpt-6.1-sol` / `high` | 20 minutes | completed | yes | yes |
| `validate_scanner` | `gpt-6.1-sol` / `high` | 20 minutes | completed | yes | yes |
| `validate_shell` | `gpt-6.1-sol` / `high` | 20 minutes | completed | yes | no: route printed after dispatch |
| `review_techdebt` | `gpt-6.1-sol` / `high` | 20 minutes | completed | yes | yes |

One additional gated follow-up sent implementation context to the completed Fast scope agent without a new explicit configuration. It inspected and edited nothing, returned awaiting routing, and was not used for implementation. That attempted dispatch was noncompliant; the actual implementation used the properly routed Premium worker. Failed capacity-limited spawn attempts created no worker. The independently checked results remain valid despite these procedural deviations.
