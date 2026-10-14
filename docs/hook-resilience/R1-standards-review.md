# R1 Standards review

Reviewed `bc52d7d69aaa046ea97e323879402241a01fead7...59ddff1d939db08e427c4b835b2fe0f92a638bf0` on 2026-10-14.
Verdict: request changes.

- **P1 Required: credential disclosure in tool labels.** `hooks/families/tool_guard.py:1412-1414`
  returns ASCII identifiers before credential redaction when the credential prefix
  occurs after another identifier component. This violates the security-banner and
  safe-log requirements in `.agents/instructions/hooks-security.md`. The changed
  `not sanitized.lower().startswith(...)` condition protects only the beginning.
  Public generated-entrypoint probes used `token = "github_pat_" + "FAKE" * 8`,
  `tool = "custom_" + token`, and `{"command":"git push --force origin main"}`
  through all three native provider envelopes, with disposable homes/logs,
  `OBSERVABILITY_TESTING=1`, isolated Python and disabled bytecode. All three denied
  but included the complete fake token in both native denial and guard log.
  Strict-fallback classification did not prevent disclosure. Embedded-token leakage
  predates this baseline but remains in the changed sanitizer and violates T6.
  Detect credentials anywhere in the bounded normalized label before the shortcut;
  add public prefixed, clipping-boundary and clean-call logging cases.
- **Optional, possible Duplicated Code:** `reporting.py:34` and
  `tool_guard.py:1408` maintain separate credential detectors. Share one conservative
  label-safety primitive while keeping presentation formatting separate. This is a
  judgment call, not an additional required violation.

Generated freshness passed all 38 outputs. Independent provider-neutral comparisons
passed for common transport, scanner, diagnostics, Guardian and policy helper.
No further documented-standard violations were identified. The worktree remained
unchanged. Full release/performance, native Windows and authenticated provider
delivery acceptance remain pending. This is the original report; repair verification
will be retained separately.
