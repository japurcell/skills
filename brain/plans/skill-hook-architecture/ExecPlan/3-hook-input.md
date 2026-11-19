# M3. Complete-event hook input

Status: open
Acceptance: not met

## Assignment

T3 belongs to the milestone implementer. Work from the repository root on a branch based on the committed plan. Integrate after M2 so regenerated brain artifacts include direct indexing. Reproduce any defect through the caller before editing. Stop when the behavior below is delivered, checks are recorded and any native evidence gap is named.

## Source and interfaces

- `hooks/families/common.py`
- `hooks/families/rtk.py`
- `.codex/hooks/load-required-skills.py`

## Shared behavior

Share readiness, chunk collection and completion detection at build time. Keep consumer policy for leading and trailing whitespace, object admission, invalid input, idle and total deadlines, depth, byte limits and diagnostics. RTK and standalone Codex currently accept U+00A0 adjacent to the JSON object. The common reader rejects it. RTK must forward the original bytes, including accepted whitespace. Installers still deploy self-contained provider-local code.

## Acceptance

Drive each unchanged executable and its proposed replacement with the same byte streams. Compare decisions, diagnostics and, for RTK, bytes received by the mock executable. Include ASCII and nonbreaking spaces on both sides, split multibyte characters, buffered trailing data, complete JSON with the pipe held open, a delayed final chunk, actual policy limits and fragmented large input. Run the supported Windows and POSIX pipe paths. Keep the existing bounded reader’s streaming work characteristics.

## Verification

Run from the checkout root. Each command must exit zero. Inspect the files or output specified above.

- `rtk proxy bash scripts/tests/hooks/test-hooks-rtk.sh`
- `rtk proxy bash scripts/tests/hooks/test-gemini-hooks-rtk.sh`
- `rtk proxy bash scripts/tests/hooks/test-codex-hooks-startup.sh`
- `rtk proxy python3 scripts/tests/tooling/test_helpers.py`
- `rtk proxy python3 scripts/tests/hooks/test-brain-hooks.py`
- `rtk proxy python3 scripts/generate-hooks.py --check`

## Progress

- [ ] [milestone-3] Implement T3 and exercise the public entry points.
- [ ] [milestone-3] Verify integrated behavior and record platform evidence.
