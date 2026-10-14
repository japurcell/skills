# R0 independent security review

Reviewed 2026-10-14 by `/root/early_security_review`. No reproduced security finding in `bc52d7d6..23f7f38b`. This bounded early review covers T1/T2 only, not later scanner, recovery, reporting, release or installation work.

The review worktree HEAD was `048944b1ec4def6f12c8d7d953ccdfc71cc24e20`. A file-scoped `git diff --exit-code 23f7f38b` confirmed reviewed canonical sources, common helper and Guardian adapters match the integrated implementation. `git diff --check bc52d7d6..23f7f38b` passed. The reviewer's read-only boundary prohibited writes; the coordinator retained this report. No review branch or empty commit was required.

## Conclusions

- Transport charges bytes before retention; idle/total/depth bounds and trailing drain share explicit limits. Complete JSON may return with stdin open. Future bytes after an empty readiness snapshot remain outside the completion contract.
- Escape-aware boundary scanning distinguishes delimiters in strings and rejects mismatched containers/trailing data before JSON decoding.
- Windows readiness separates available bytes, empty pipes, broken-pipe EOF, regular files and unexpected errors. Unexpected errors propagate.
- Native schema matching uses exact types, excluding booleans from integer counters. Known optional fields receive bounded counter, enum, shell and nested-permission validation.
- Inert annotations preserve command inspection; working directories, permission prefixes and permission paths receive independent strict inspection. Unknown/malformed profiles retain strict fallback.
- Native proof occurs after whole-input string/key/node/depth accounting. Metadata cannot bypass those budgets.
- Supported metadata preserves safe semicolon-rich literal searches; paired protected-branch executable operations deny.
- No new third-party dependency or hardcoded credential was identified. Web authentication/SQL/XSS/CSRF/SSRF checks do not apply to this change.

Key reviewed locations at the pinned tree: `hooks/families/common.py` lines 31, 38, 68, 90, 120, 152 and 161; `hooks/families/tool_guard.py` lines 662, 1462, 1713, 1751 and 1823.

## Independent probe evidence

The reviewer executed generated adapter classification functions without `main()` or logging, and common-reader subprocesses through real stdin descriptors. `-B` prevented bytecode creation. Supplied command strings were inspected, never executed. No filesystem fixture writes or live homes were used.

Twenty-five classification probes passed across Codex/Copilot/Gemini: literal and inert-metadata searches allowed; protected-branch executable/context/permission controls denied; unknown semicolon-rich shapes denied with `command_segments`; oversized metadata denied with `structured_bytes`; surrogate metadata denied with `inspection_failure`. Codex boolean counters fell back to strict inspection, and the exact maximum integer counter allowed. The first exploratory control omitted a protected destination and incorrectly expected the protected-branch rule to match. Source inspection corrected the test input; no product behavior was weakened.

Twelve real-descriptor transport probes passed: empty retained input denied; complete and escaped-backslash input returned with stdin retained; a second object and trailing NUL denied; depth64 allowed/depth65 denied; exact2,097,152 raw bytes allowed/next byte denied; a surrogate pair allowed; invalid UTF-8 and nonextendable trickle denied. Trickle supplied one whitespace byte each0.1seconds after an opening brace under an outer watchdog.

Five simulated Windows readiness branches passed: available=True, empty=False, broken-pipe EOF=True, regular file=True, unexpected error=OSError. This substitutes Windows API calls and does not establish native Windows behavior.

## Limitations and disposition

The reviewer inspected public tests and I1 evidence but did not rerun complete suites. Custom probes bypassed native response construction and logging; I1 retains that public proof separately. Native Windows, authenticated provider delivery, installed assets, isolated latency/RSS and external advisory scanning were not exercised. No third-party dependency was added. The two-second input deadline is not a universal whole-hook deadline.

R0 found no reproduced defect requiring a repair node. Final biaxis/security review and all remaining integration/platform/resource gates remain required.
