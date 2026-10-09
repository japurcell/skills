# Tool Guardian T3 result

Verified 2026-10-08 in the private guardian task worktree. Canonical source and six provider-local adapters/helpers were updated through `scripts/generate-hooks.py --write`.

## Result and scope

Exact Codex `apply_patch` `{command: string}` and exact Copilot `toolName: apply_patch` plus raw string `toolArgs` receive the 262,144-byte patch aggregate budget. Codex counts its seven-byte key; Copilot raw data has no key overhead. Successful grammar validation separates patch bodies from executable text and preserves protected delete/move-source inspection.

Other native data remains 65,536 bytes; strict/normalized work remains 32,768 bytes; shell segments remain 128. The patch grammar is unchanged. Copilot object forms, serialized JSON, alternate name/input fields, tool aliases, and other-provider scalar patches remain strict. Malformed Copilot raw patches retain their original scalar strict representation.

Both capped segment paths now carry typed `measured_is_lower_bound` state and report `at least 129 segments`, instead of implying a complete count.

Copilot shape evidence came from native execution arguments and actual post-tool payloads. An authenticated live pre-tool probe was unavailable. These tests prove source entrypoint behavior, not actual provider delivery, installed parity, or native Windows execution.

## Red-green evidence

- Exact Codex 262,144-byte aggregate first denied against 65,536; now ASCII/UTF-8 maxima allow and 262,145 bytes deny in block/warn modes.
- Raw Copilot 6,194-byte/134-line patch first denied on segments; raw 256 KiB first denied against strict 32 KiB. Both now allow; next aggregate byte denies.
- Raw Copilot delete/move sources for `.env` and `.git/config` first allowed in all four controls; now deny with the corresponding removal rule.
- Strict splitter and parsed shell controls for 129/1,000 segments first reported an exact 129; all 24 provider/mode/path controls now report the lower bound.

## Focused verification

All commands used `rtk proxy` with disposable subprocess homes and logs:

- `python3 scripts/test-tool-guard-native-data.py`: 22 tests passed.
- `python3 scripts/test-tool-guard-limits.py`: 18 tests passed.
- `python3 scripts/test-tool-guard-shell-data.py`: 17 tests passed.
- `python3 scripts/test-tool-guard-false-positives.py`: 144 public fixtures passed.
- `python3 scripts/generate-hooks.py --check`: 35 generated files current.
- `git diff --check`: passed.

Tests also cover synthetic versions of twelve historical patch dimensions, all four recent patch sizes, single/multi-file prose/YAML/shell examples, exact UTF-8 byte boundaries, late protected operations, malformed/trailing input, and normalized-operation maxima. Full-size high-line fixtures contain 130,004 lines. Denied multi-file prehook invocations leave environment, Git, and ordinary sentinel files unchanged; the guard does not execute patches, so this is not executor atomicity proof. Ordinary threat warnings retain their existing behavior; inspection-limit warnings remain denials.

The maintained resource runner now includes Codex and raw Copilot patch max/overflow, high-line maximum, malformed full-size controls, recent-size cases, and normalized operations. Its public fixture decisions passed 26 controls (Codex 11, Copilot 13 including unchanged create boundaries, Gemini 2). No timing/RSS samples were collected in this task. The coordinator owns frozen integrated benchmarks, shared provider/security suites, installation, actual provider validation, the plan, and the final knowledge pass.

This implementation is ready for coordinator integration after its private commit. Live provider pre-tool transport and native Windows delivery remain unverified; no alternate schemas were inferred to fill that gap.
