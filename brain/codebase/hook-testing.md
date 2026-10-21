# Hook testing

- After canonical edits, regenerate successfully before dependent checks. Run `scripts/generate-hooks.py --check` and `scripts/test-generate-hooks.py`, then recheck freshness after affected suites.
- Serialize generator and installer fixtures. Pause all repository writes during generator tests: some assertions snapshot the whole checkout.
- Test public protocol envelopes, UTF-8, retained stdin, buffered trailing data, bounded errors, and quiet high-rate success.
- Assert actual registered Bash/PowerShell paths and required relative ordering, not incidental array positions.
- Installer tests must resolve registered commands to installed scripts in disposable destinations.
- Keep live event/context delivery separate from fixture proof. Native Windows tests must actually execute on Windows.

Evidence: [generator suite](../../scripts/test-generate-hooks.py), [stdin suite](../../scripts/test-hook-input-bounds.py), checked 2026-10-20. Recheck runtime and registration changes. See [live-hook-testing](live-hook-testing.md).
