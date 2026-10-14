# R1 Spec repair review

Independent review on `0ecd490d07c34519e86f10719ef778cebff73fae`, 2026-10-14: **both original findings closed; no new actionable specification findings**.

- **P1 closed.** The streaming design requires the installer-selected absolute trusted Python executable with `-I -S -B` and absolute hook path. Installers and mergers now materialize these commands. Independent Bash installation replay exercised actual registrations under hostile PYTHONPATH and post-install PATH replacement: all 12 attacks across six commands passed, no sentinel ran, and scanner diagnostics denied execution. The targeted macOS PowerShell installed-command test passed, covering awkward paths, ordinary enforcement/audit, idempotence and doctor rejection of extra operands.
- **P2 closed.** The implementation plan requires sanitizing labels and identifiers. Guardian checks the entire normalized identifier through shared redaction before clipping. Replaying the original prefixed classic fake-PAT case across all three generated Guardians confirmed denial with no complete token in native output, audit or stderr.
- **T8 preserves verification strength.** Bounded presentation assertions retain safe colliding filenames, delimiter fragments and replaced working files, independently proving staged acquisition. The targeted Copilot delimiter/leading-colon public test passed.

No unrequested scope expansion or weakened security requirement was identified. This closes reviewed findings, not release acceptance. T9 and final V1 verification remain. Native Windows and authenticated provider dispatch remain unverified. No full aggregate or benchmark ran during this review; the worktree stayed clean.
