# T5a standalone diagnostics evidence

Date: 2026-10-14. Task base: `5dd8af43`. Private task branch:
`codex/hook-resilience-t5a`. This evidence covers the standalone collector and CLI;
T5b owns scanner embedding, reserved-request recognition, and native denial.

## Delivered interface

`hooks/families/diagnostics.py` owns `collector_source(provider)`, which returns
self-contained stdlib runtime plus fixed generated installation metadata.
`diagnostics_collect(__file__, doctor=False)` collects process-cwd metadata and
fixed installation observations. `doctor=True` omits repository enumeration.
`script_path` is the loaded trusted hook's own `__file__`; it must never come from
a payload, command operand, or config include. `diagnostics_encode(report)` emits
one complete UTF-8 JSON response capped at 16 KiB, including its newline. T5b can
embed this source before optional scanner/audit/policy imports without importing
another installed helper. All collector globals/imports use the diagnostics prefix.

Generated executable targets are `.codex/hooks/hooks-diagnostics.py`,
`.copilot/hooks/scripts/hooks-diagnostics.py`, and
`.gemini/hooks/scripts/hooks-diagnostics.py`. CLI arguments are exactly no
arguments, `--doctor`, or `--help`; everything else exits 2 with fixed usage and
no reflected operand. Both installers deliver the CLI; the Codex exact copy lists
were extended. Existing hook launch commands and registrations are unchanged.
README documents a human-owned absolute trusted Python launch with `-I -S -B`.

The collector never runs Git/subprocesses or opens candidate contents. Metadata
enumeration uses retained descriptor-relative no-follow directory handles on
supported hosts, skips `.git` contents, symlinks/reparse points and unsafe types,
and only stats `.git/index`. Linked `.git` files remain `linked_or_unknown`.
Pending/tracked/ignored state and index snapshots remain unknown.

Inventory limits are 1,024 directories, 4,096 entries, depth 32, 256 retained
records (240 largest regular files plus up to 16 unsafe records), 160 UTF-8 bytes
per sanitized label, and one shared second for collection. Ranking covers
observed entries only. The serializer removes labels, then lowest-priority
records, preserving largest sizes, counts and incompleteness. Omitted inventory
and serialization detail are explicit. Token-shaped and URL/auth/password-like
labels are redacted before clipping; controls and invalid Unicode are removed or
redacted. No raw exceptions, payloads, commands, settings values or contents are
returned. Owned-asset checks cap their inventory at 64 assets and total hashed
input at 1 MiB. Each fixed primary settings file is capped at 256 KiB. Includes
and custom command/config operands are never followed or executed.

Bootstrap, asset, registration, repository, audit and content-security health are
independent. Security is always unknown/`not_scanned`; audit is always
unknown/`not_attempted`. Unowned, repeated, malformed, missing or unsafe
registrations report uncertainty. Exact owned handler identity includes event,
matcher and handler data; duplicate command registrations are counted even if
their environment differs. Settings checks do not mutate configuration.

## Build and policy identity

The embedded build is deterministic over canonical `hooks/**/*.py` bytes, provider
template bytes, provider name and collector limits. It describes generated loaded
metadata, separately from bounded current on-disk asset hashes. Source versus
installed execution remains explicitly unverified. Entrypoint disk hashes are
`unverified` observations; hashing alone never declares scanner/Guardian healthy.
Common/audit/Guardian-policy helper hashes can identify canonical drift. Avoiding
entrypoint self-hashes also avoids scanner -> diagnostics -> scanner rendering
cycles during later embedding.

`policy_limits` is extracted at generation time with a restricted AST numeric
reader over trusted canonical source, never runtime scanner imports. It includes
scanner `MAX_FILES`, `MAX_FILE_BYTES`, `MAX_TOTAL_BYTES`, `MAX_SCAN_SECONDS` and
Guardian `MAX_SCAN_TEXT`, `MAX_NATIVE_DATA_BYTES`, `MAX_NATIVE_PATCH_BYTES`,
`MAX_COMMAND_SEGMENTS`, `MAX_COMMAND_TOKENS`, `MAX_STRUCTURED_DEPTH`,
`MAX_STRUCTURED_NODES`, `MAX_STRUCTURED_STRINGS`. Scope is explicit; this is not a
complete Guardian policy dump. Removed constants report `not_defined`; numeric
aliases and addition/subtraction/multiplication remain source-derived. Unsupported
canonical expressions fail generation rather than silently inventing values.

## Observed verification

- Initial public isolated CLI test failed for all three missing CLI paths; it
  passed after generation. A later expired-clock test reproduced an empty cwd
  being falsely complete after the deadline; the collector now reports incomplete
  before directory access. A modified duplicate-command handler initially counted
  only as unowned; it now also increments duplicates.
- `rtk proxy python3 -W error scripts/test-hook-diagnostics.py`: 8 tests passed
  (2.147 seconds). Cases cover exact parser modes and rejected operands, hostile
  cwd/PYTHONPATH/site imports, candidate contents absent from output, large-file
  retention beyond the initial 256 files, unsafe types/FIFO, redaction before
  clipping, entry/depth/directory/response bounds, fixed asset/hash limits,
  malformed/duplicate/oversized/include settings, missing/corrupt/linked helpers,
  no settings mutation, clock exhaustion, and build/policy source changes.
- A copied canonical fixture changes `MAX_TOTAL_BYTES` from 8,388,608 to 7,340,032,
  regenerates, and observes 7,340,032 plus a changed build. Removing the per-file
  constant reports `not_defined`, preventing a stale 1 MiB diagnostic claim.
- `rtk proxy python3 scripts/test-generate-hooks.py`: 26 tests passed
  (15.361 seconds). Explicit ownership/count assertions now include 38 outputs.
- `rtk proxy bash -n scripts/install.sh scripts/test-install.sh`: passed.
- `rtk proxy bash scripts/test-install.sh`: passed after final policy metadata.
  Fresh installation checks verify exact bytes/mode for all three CLIs, launch
  each installed path using absolute `sys.executable -I -S -B --doctor`, and
  preserve settings bytes. Existing user/retired handler preservation, idempotence,
  malformed config refusal, hard-link/link defenses and stale-output negatives
  remain active.
- `rtk proxy pwsh -NoProfile -File scripts/test-install.ps1`: passed on macOS
  before the final additive policy fields; junction creation was explicitly skipped.
  The fixture now verifies exact installed CLI bytes. Focused fresh-install proof
  passed for final generated bytes via the existing fresh-install function
  (`Focused diagnostics installer proof passed.`).
- Installer fixture templates intentionally differ from production; fixture setup
  now regenerates their copied canonical outputs after those changes. Stale-output
  negative cases still corrupt output afterward and retain their original checks.

## Integration and limitations

The coordinator owns the active ExecPlan, test-all registry and one final knowledge
maintenance pass. This task did not change `scan_secrets.py`, `tool_guard.py`, or
`common.py`. Integration must regenerate all outputs from merged canonical source,
including the integrated T1 common changes and later T4 scanner changes, then rerun
diagnostics, generation and disposable installer proofs. The task branch predates
those scanner/transport changes; its embedded identities are not final integrated
release identities.

No live-home installation, push, authenticated provider dispatch, native Windows
proof, scanner-recovery route, clean scan, executable exemption, or same-user
tamper resistance is claimed. Unsupported descriptor/no-follow platforms report
limited checks; five POSIX-only test cases are marked as requiring that capability.
Filesystem deadline checks are cooperative around bounded operations, not a claim
that the operating system can interrupt every stalled filesystem syscall. A damaged
CLI/interpreter requires human repair or reinstall from trusted source.
