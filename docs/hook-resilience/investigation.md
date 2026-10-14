# Hook resilience: diagnosis and recommended changes

Investigated on 2026-10-14 against `bc52d7d69aaa046ea97e323879402241a01fead7`, using macOS and Git 2.54.0. This report describes reproduced current behavior and proposed improvements. Production hooks and installed settings were not changed. The original Linux worktree was unavailable.

## Diagnosis of the new report

The reported failure is reproducible exactly, but the report misidentifies the limit. **2,030,848 bytes is one worktree candidate's size, not the combined size of nine files.** `_read_bounded_descriptor()` checks `fstat().st_size` against `MAX_FILE_BYTES=1048576` before reading an already oversized file. The aggregate allowance is separately `MAX_TOTAL_BYTES=8388608`. See [scanner source](../../hooks/families/scan_secrets.py), constants at lines 85-89 and descriptor reading at line 674.

Public Copilot subprocess observations, with `SCAN_MODE=block`, `SCAN_SCOPE=diff`, isolated repositories/homes/logs, and no skip or allowlist overrides:

| Fixture and requested operation | Observed result |
| --- | --- |
| Clean repository; `rtk git status --short` | Allow |
| One safe untracked file of 2,030,848 bytes; same request | Deny, exact `file_bytes_limit/candidate_read`, measured 2030848, limit 1048576 |
| Nine safe files totaling 2,030,848 bytes, each below 1 MiB; same request | Allow |
| Committed benign 2,030,848-byte file plus a 13-byte benign edit | Deny, measured 2030861, before added-diff scanning |
| Small unmistakably fake credential in pending content | Findings denial, without its value |

The oversized-file and fake-secret controls also passed through Gemini and Codex public scanners: all three deny the oversized candidate as incomplete and deny the fake credential as a finding. These controls verify response decisions, not just exit status; a deliberate security denial returns exit zero and native JSON. An initial exploratory assertion incorrectly expected a semicolon after the findings phrase; the actual response uses a period. The corrected probe checked the findings phrase and absence of an incomplete result, then all six provider/scenario controls passed. No production code changed to obtain that result.

The lockout follows directly from `main()` at lines 1519-1555: select pending Git snapshots, read full candidates, then choose the appropriate detection mode. The requested tool and its arguments do not select those candidates. Every request inherits the same unrelated repository failure, including the request to diagnose it.

The earlier repair deliberately retained the 1 MiB per-file bound. It improved the error message but did not solve this usability failure. Receiving the same limit after updating is therefore expected from this source and does not prove a stale installation. The new diagnostic establishes that a diagnostic-capable implementation ran; it cannot identify the remote build or offending path. The nine Angular templates are possible candidates, not identified culprits.

## What the scanner actually protects

The current scanner detects selected credential patterns in pending repository changes. It does not inspect arbitrary requested content or prospective tool write bodies. Fresh public Copilot fixtures requesting reads of fake credentials in a clean tracked file, an ignored file, and an outside-repository file each returned a clean result. This is a contract limitation, not evidence that the known credential recognizer failed.

Current semantics must be preserved deliberately during a streaming rewrite:

| Candidate | Current inspection |
| --- | --- |
| Ordinary tracked text with HEAD in default `diff` scope | Added diff lines, after first reading the entire candidate |
| `staged` scope | Full staged snapshot |
| Untracked, unborn repository, and unresolved index/worktree snapshots | Full snapshot |
| Binary-classified candidate | Full ASCII projection, including tokens after a NUL |
| Credential path | Separate critical path finding |
| `.env` path | Recorded as an environment file; not automatically a credential finding |
| Deleted-only path | Excluded from candidate collection |

Exact suppression depends on `path:line:pattern:full_match`, defined in [allowlist source](../../hooks/families/allowlist.py). Source-specific staged and merge snapshots matter: a safe working tree must not hide a secret in the index or another conflict stage. Candidate enumeration, reads, and later Git diffs are not an atomic repository snapshot; the log lock does not make them atomic.

## Additional confirmed fragility

### Valid Guardian metadata changes the security decision

The same safe literal search has different decisions under current Codex envelopes:

```python
command = "rg '" + "example;" * 130 + "' docs"
```

| `exec_command` arguments | Observed decision |
| --- | --- |
| `{"cmd": command}` | Allow |
| Same plus `max_output_tokens: 1000` | Deny, `command_segments` |
| Same plus `workdir: "."` | Deny, `command_segments` |
| Same plus an unknown option | Deny, `command_segments` |

The live tool contract in this investigation exposes both optional fields. `_native_tool_shape()` in [Guardian source](../../hooks/families/tool_guard.py), line 1714, accepts only the sole command key for this shell profile. Adding output metadata loses shell-aware data classification; strict fallback counts literal semicolons. `max_output_tokens` is the decisive false positive because it does not turn the search pattern into executable code. `workdir` affects execution context and needs its own interpretation.

The 22 native-data tests and 144 false-positive fixtures pass despite this reproduction. Their simplified corpus envelopes do not cover the complete current option set. Supported Copilot raw patches and Codex `command` object patches still pass; the new report does not establish a new regression in those repaired paths. Its old unqualified “129” message also lacks a current execution identity.

### Shared input reading can outlive the provider deadline

[Shared input source](../../hooks/families/common.py), lines 121-145, uses blocking `os.read()` before the first byte and after incomplete JSON. Its 0.5-second readiness wait is inserted only for the GitHub adapter at lines 445-452. Copilot, Codex, and Gemini lack that input-completion deadline.

Public probes with a complete object and retained stdin returned. Empty/incomplete retained input did not return within a short watchdog. A longer Copilot Guardian probe with only an opening brace remained alive after **10,507 ms**, with no stdout or stderr, before the disposable watchdog terminated it. Its configured provider timeout is ten seconds in [Copilot registration](../../.copilot/hooks/hooks.json).

This is a source-level completion defect. GitHub documents that command-hook timeouts fall through to normal permission handling, unlike explicit denials and ordinary hook errors. That makes an internal deadline essential; an actual authenticated-host bypass was not demonstrated. [Official Copilot reference](https://docs.github.com/en/copilot/reference/hooks-reference#pretooluse--pretooluse).

Decoded Guardian traversal limits also arrive after JSON accumulation/parsing. They do not bound raw-envelope memory, repeated decoding work, or an unbounded trailing-data drain.

### Operational dependencies share the same failure surface

The scanner materializes Git captures, an index-content dictionary, full worktree bytes, decoded text, and numbered line arrays. A byte cap does not describe peak memory. Many short lines and binary conversion amplify allocations. `MAX_SCAN_SECONDS` covers Git, matching, log locks, rotation, and `fsync`; required audit failure can turn an otherwise clean scan into incomplete denial. Preserve that policy explicitly instead of accidentally allowing on a logging failure.

Finding count is bounded, but the 64 KiB serialized log-record check occurs afterward. Long paths or identifiers can exceed it. Bound retained report bytes as well as finding counts, and preserve a positive finding when detail must be omitted. Distinguish the security result, audit status, and final enforcement decision.

## Recommended design

Keep the canonical renderers and independent generated provider adapters. Those boundaries already avoid maintaining three different implementations. Strengthen the boundaries inside them.

### 1. Bound transport before policy

Give every provider a bounded raw-input reader: first-byte/incomplete-input idle deadline, nonextendable total deadline, byte ceiling, nesting/node safeguards, and bounded trailing-data drain. Return native denial before the provider timeout. Malformed input and timeout are explicit incomplete outcomes, never clean scans. Preserve complete-JSON-with-open-stdin behavior and Windows readiness support.

Choose actual ceilings using the supported envelopes and full-process measurements. A raw byte cap equal to 256 KiB would reject legitimate escaped 256 KiB patches; allow for JSON escape expansion and bounded envelope metadata. Reserve time for denial/logging. Cooperative checks cannot interrupt a blocking filesystem read or `fsync`; if strict whole-process deadlines are required, test a small supervisor that terminates the worker and emits one final denial before the host deadline. Do not claim that a monotonic clock check alone supplies that guarantee.

### 2. Normalize exact provider profiles into typed operations

Maintain explicit provider/event/tool schema profiles, with independently validated fields. `cmd` is executable input. Output limits are bounded inert numbers. Shell, login, environment, permission options, and working directory can affect execution and require separate proof. Unknown or malformed fields keep strict handling, with a safe reason identifying the unsupported profile rather than silently treating all serialized fields as shell syntax.

Both hooks may consume shared classification facts, but each keeps its own policy: a proven inert patch body for Guardian may still contain a credential for a content scanner. Share canonical source through generated provider-local helpers, not cross-provider runtime imports.

Copilot's lowercase native events and PascalCase compatibility events have different field/tool-name mappings. The latter maps several operations to `Edit`, which alone cannot prove a patch schema. Current repository registration is lowercase. Treat compatibility profiles as separately tested contracts, not guessed aliases. [Official input reference](https://docs.github.com/en/copilot/reference/hooks-reference#pretooluse--pretooluse).

### 3. Provide a narrow recovery capability

Add a trusted health/candidate-metadata command with exact arguments, bounded structured output, and no arbitrary command, script, environment, or path operands. Make it usable when ordinary candidate scanning or audit storage fails. Recognize it before those optional diagnostic dependencies, while retaining independent request validation and Guardian checks. Give it an out-of-band human-terminal invocation for failures in the input reader or policy helper itself.

Return build/helper fingerprints, provider/profile identifiers, policy-limit values, phase, candidate/snapshot counts, sizes, and bounded sanitized repository-relative labels. Filenames can contain credentials and control characters; use escaping, redaction, stable local candidate identifiers, and omission counts. Do not print raw exception messages, payloads, or environment values. Keep unknown causes fixed and sanitized. Incomplete scans stay incomplete.

Do not broadly exempt the report's list of Git commands. A disposable fixture proved that `git status --porcelain` executes a configured `core.fsmonitor` hook. Git documents that behavior. Also, `git log --oneline` returns commit subjects, which are arbitrary content. [Git configuration](https://git-scm.com/docs/git-config#Documentation/git-config.txt-corefsmonitor), [Git log formats](https://git-scm.com/docs/git-log#_pretty_formats).

A trusted collector must control Git executable selection, configuration/environment, fsmonitor, external diff/textconv, pagers, submodule behavior, and arguments. Metadata-only output does not establish zero internal body reads. A strict zero-body mode should use conservative index metadata plus `lstat`, label uncertain status, and avoid pretending it has computed a content diff. Ordinary status should pass once the 2 MiB candidate can be scanned; infrastructure failure should direct the agent to the dedicated recovery capability.

### 4. Stream bounded snapshots while preserving detection

Replace the 1 MiB materialization policy explicitly with per-snapshot reads charged against the remaining **existing 8 MiB aggregate budget**, retaining 256 snapshots and the scan deadline as initial design constraints. Support the reported 2 MiB file without raising every safety limit. Measure resource behavior before adopting this policy.

Preserve descriptor-relative/no-follow opening and regular-file checks. Pin index object IDs. Continue capturing Git output to protected temporary regular files and verifying completion/descendants before consuming it. Consume verified captures incrementally and release each snapshot instead of retaining every byte string in a dictionary.

Late NUL or invalid UTF-8 can change existing classification. Use a bounded private snapshot spool and replay that same snapshot after classification. Do not reopen a mutable path and call it the same content. Preserve the existing repository-consistency limitation for separate Git diffs.

Use stateful incremental matching and line tracking. Current fine-grained GitHub, Stripe, and Slack patterns have unbounded token suffixes. Fixed chunk overlap, truncated lines, or buffering one arbitrary line cannot preserve greedy matching and exact allowlist semantics. A long token may extend an otherwise allowlisted prefix. Finalize only at delimiter/EOF, keep bounded redaction state, and use the 8,192-character allowlist-input bound to avoid retaining unbounded full matches that cannot possibly be allowlisted. Preserve per-pattern nonoverlap and line-number behavior.

### 5. Make incidents attributable and releases realistic

Emit fixed build, helper, schema-profile, classification-route, failure-phase, and structured limit identifiers. Keep raw contents and unrecognized field names out of telemetry. Provide a doctor command that checks installed files and merged registrations, including duplicate/unowned handlers, without removing them automatically. Report a healthy diagnostic capability separately from an incomplete security scan.

Copilot CLI configuration changes load at CLI startup; a CLI restart is the documented activation step. A script-only replacement at an unchanged external Python entrypoint is expected to load on its next process launch, but that is an inference from this repository's command registration. Prove the actual loaded build with fingerprints. The report does not establish its exact CLI/extension version or active hook source, and VS Code reload behavior was not verified. [Official CLI activation instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-hooks).

Add release gates for complete current tool envelopes, not only reduced synthetic forms. Pair every new allowance with executable/unknown-shape negatives and realistic recovery workflows. Record semantic false-positive classes and per-phase resource measurements. Do not introduce an always-running service or clean-result cache before measuring need; caching by path/mtime/size can reuse stale security decisions.

## Proposed implementation sequence

The following tasks are proposed work, not completed changes. [ExecPlan](ExecPlan.md) records investigation status.

| Task | Prerequisites | Scope and observable exit criterion |
| --- | --- | --- |
| H1: Bound shared input transport | Current reproductions | Canonical common reader and existing protocol suites. All providers deny empty, truncated, oversized, slow-trickle, and trailing-invalid input before their configured deadlines; valid complete open-stdin requests pass. Finalize limits using escaped maximum-size envelope tests and process measurements. |
| H2: Repair Guardian option profiles | H1 | Canonical Guardian classifier and native/corpus suites. Adding validated inert output metadata preserves the literal-search decision; unknown fields and execution-changing controls retain their own checks. |
| H3: Add trusted recovery and build identity | H1; explicit recovery profile | Canonical hook adapters, diagnostic CLI, helpers, installer lists and tests. Bounded health/candidate metadata remains available during scan/audit failure, without launching repository-controlled code or admitting arbitrary shell requests. |
| H4: Stream candidate acquisition | Characterized scanner contract | Canonical scanner, Git capture/index readers, capture and merge tests. Transport changes preserve existing decisions and safe completion while reducing retained memory. |
| H5: Stream detection and adopt large-file policy | H4 | Stateful matching, classification replay, diff parsing, and per-snapshot budgeting. One benign 2 MiB snapshot and equivalent smaller snapshots pass; boundary/allowlist/merge/binary controls retain findings. |
| H6: Bound reports and complete release proof | H2, H3, H5 | Bounded diagnostic/audit records, generated freshness, provider suites, resource and installed-delivery checks. Findings survive reporting truncation, security failures remain explicit, and actual installed fingerprints identify the running release. |

H1 and H4 can begin independently on separate ownership boundaries. H2 and H3 need serialized edits to shared schema/adapters. H6 integrates all changes before any deployment claim. Avoid adding shared-file abstractions until the first public behavior slice establishes the needed interface.

## Acceptance matrix

| Area | Required positive and negative checks |
| --- | --- |
| Recovery workflow | Large pending file; obtain sanitized size/status; repair it; retry. Broken Git/audit/candidate access still permits only the trusted diagnostic capability. |
| Scanner sizes | Exact bounds and first overflow; one versus many files; tiny diff in large tracked file; multi-megabyte single line; newline-dense file. |
| Detection | Token split at every chunk boundary; EOF; long suffix after an allowlisted prefix; exact allowlist identity; late binary marker; split UTF-8/CRLF; unchanged tracked versus added-line semantics. |
| Snapshot integrity | Hidden staged secret, every merge stage, safe worktree versus unsafe index, symlink/reparse/FIFO rejection, growth/replacement, pinned object IDs, descendant-held/truncated Git captures. |
| Guardian | Full actual provider fields; inert metadata invariance; malformed/unknown/execution-affecting fields; data moved into command/substitution/pipeline sinks; late protected patch operations. |
| Transport | Complete object with open stdin; missing first byte; incomplete prefix; slow trickle; escaped Unicode; raw byte/nesting limits; trailing data; native denial before host timeout. |
| Diagnostics | Hostile filenames/session fields, token-shaped paths, missing helper, logging failure, contention, bounded report size, omitted counts, build/registration mismatch. |
| Release | Public subprocess tests, existing-home install preservation, actual provider invocation and visible decision, Linux/macOS/Windows evidence, full-process timing and RSS. |

Keep the existing scanner/merge/capture/security-banner suites and Guardian native/shell/limit/corpus suites. Extend their public entrypoints; do not replace failing expectations with skips. Use the maintained 500 ms Guardian finite-input resource gate and matched warm/cold acceptance procedure. Scanner streaming needs its own measured size/line-density/concurrency matrix under the unchanged logical work/time budget; no scanner RSS claim was measured in this investigation.

## Alternatives and limits

- Increasing limits alone retains the allocation cliff and all-tool failure coupling.
- Broad read-only or metadata exemptions can execute configuration or disclose content. Unknown operations must not become trusted diagnostics.
- Fixed-overlap chunking and diff-only shortcuts can lose existing detections or exact suppressions.
- Moving every repository scan to a later event changes enforcement. Define that as a separate policy decision; it is not a drop-in resilience fix.
- A new scanner dependency or full shell-parser replacement does not by itself fix transport, deployment, recovery, or incomplete-scan policy. Consider one only against this same cross-platform contract and measured resource gates.
- Pre-tool denial proves that the hook did not launch the requested tool. Atomic multi-file writes belong to the provider executor and need actual executor evidence.

The investigation is complete. Recommended production work remains proposed. The original Linux filename, installed build, authenticated provider delivery, Windows behavior, and an actual host timeout bypass remain unverified. See [delegation audit](delegation-audit.yml) for analysis provenance.
