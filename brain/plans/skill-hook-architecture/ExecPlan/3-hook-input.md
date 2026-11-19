# M3. Complete-event hook input

Status: done
Acceptance: met

## Tasks and prerequisites

**T3a, characterize the three readers.** The hook maintainer uses isolated copies of revision `069b3f22` and the byte-stream matrix below. Record the original public outputs, stderr, mock RTK input, and whether each pipe closes or remains open. Identify the reader from its entry point (`_read_json_input_text`, `read_hook_input` or Codex `read_json_input`). Stop after capturing expected outcomes on the available platforms. [Assignment](3a-input-baseline.md)

**T3b, migrate the readers.** Once the T3a matrix exists and corrected M2 outputs are integrated, render a single readiness/chunk/completion implementation from `hooks/families/common.py` into the family outputs and standalone Codex executable. Pass a consumer policy for completion, whitespace, limits and deadline behavior. Return original bytes or a classified read failure to the consumer. Preserve the bounded reader's incremental state across chunks. Use `hooks/manifest.py` and the generator for newly rendered output. Migrate one reader at a time against the captured streams, then exercise all three from the integrated checkout. Stop after the suites and native Windows/POSIX comparison. [Assignment](3b-input-reader.md)

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

- [x] (2026-11-19) [milestone-3] T3a captured the macOS public-reader reference at `81413348`; native Windows remains open.
- [x] (2026-11-19) [milestone-3] Integrated the strengthened public pipe fixture at `ef9392b3`. On macOS and Windows it compared the original hooks against the generated ones, including a pipe held open and exact bytes forwarded to RTK. [Windows run](https://github.com/japurcell/skills/actions/runs/44496566199/job/135465141445)
