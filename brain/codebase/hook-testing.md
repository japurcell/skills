# Hook testing

- After canonical edits, regenerate successfully before dependent checks. Run `scripts/generate-hooks.py --check` and `scripts/test-generate-hooks.py`, then recheck freshness after affected suites.
- Serialize generator and installer fixtures. Pause all repository writes during generator tests: some assertions snapshot the whole checkout.
- Test public protocol envelopes, UTF-8, retained stdin, buffered trailing data, bounded errors, and quiet high-rate success.
- Assert actual registered Bash/PowerShell paths and required relative ordering, not incidental array positions.
- Installer tests must resolve every registered command and invoked local launcher to installed files in disposable homes for both installers.
- Keep live event/context delivery separate from fixture proof. Native Windows tests must actually execute on Windows.

## Select affected public suites

- For required-skill boundaries or startup changes, read and run the affected [Copilot](../../scripts/test-hooks-startup.sh), [Gemini](../../scripts/test-gemini-hooks-startup.sh), and [Codex](../../scripts/test-codex-hooks-startup.sh) startup suites. Keep multi-skill fixtures self-contained and independent of optional installed skills. Evaluate deliberate missing-skill diagnostics by assertions and exit status; a fixture hard stop does not establish native provider enforcement.
- Preserve deterministic line-oriented required-skill delimiter parsing and diff-only secret suppression through the startup suites and [scanner merge suite](../../scripts/test-scan-secrets-merge.py); keep exact grammars in source/tests.
- For shared helper or UTF-8 fallback changes, read [helper tests](../../scripts/test_helpers.py), including isolated module setup and the simulated CP1252 fixture using `TextIOWrapper(BytesIO(...))`.
- Exercise affected supported interpreter versions for parser/import changes. For RTK forwarding run both [Copilot](../../scripts/test-hooks-rtk.sh) and [Gemini](../../scripts/test-gemini-hooks-rtk.sh) suites; configuration changes also require [stable-RTK tests](../../scripts/test-rtk-stable.py).

Evidence: [generator suite](../../scripts/test-generate-hooks.py), [stdin suite](../../scripts/test-hook-input-bounds.py), checked 2026-10-20. Recheck runtime and registration changes. See [live-hook-testing](live-hook-testing.md).
