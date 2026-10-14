# R1 specification review

Reviewed `bc52d7d69aaa046ea97e323879402241a01fead7..59ddff1d939db08e427c4b835b2fe0f92a638bf0` independently on 2026-10-14. Verdict: request changes.

1. **P1: Installed hook launches remain non-isolated.** `scripts/install.sh:103`, `:107`, `:141` and corresponding PowerShell calls at `scripts/install.ps1:342`, `:347`, `:398` retain PATH-based Python or environment shebang registrations. `streaming-design.md:176` requires installer-selected absolute Python, `-I -S -B`, and absolute hook paths. After actual Bash installation into disposable HOME/CODEX_HOME, all six scanner/Guardian commands executed a harmless sentinel from PYTHONPATH `sitecustomize.py` before enforcement, including diagnostic denial. Repair actual registrations and test their commands directly; manually isolated test invocations do not prove installation safety.
2. **P2: Guardian's identifier fast path leaks embedded credentials.** `hooks/families/tool_guard.py:1412-1414` checks credential prefixes only at the start. With tool name `"tool_" + ("ghp_" + "FAKE"*9)` and command `git push --force origin main`, all three providers deny but copy the complete fake token into native denial and audit. This violates the plan's label sanitization and credential-free reporting requirements. Inspect the entire bounded identifier before returning.

No additional retained specification or scope findings arose from transport, snapshot acquisition, streaming matching, exact suppression, classification replay, recovery, reporting, or verification preparation.

Verification was read-only with disposable homes/repositories/logs, fake credentials, OBSERVABILITY_TESTING=1, and bytecode disabled. Worktree remained clean. Full benchmarks, aggregate release checks, native Windows, and authenticated provider dispatch were not verified by this review. T6/T7 repair and independent re-review remain required.
