# R1 Standards repair review

Independent review of the T6/T7/T8 delta on `0ecd490d07c34519e86f10719ef778cebff73fae`, 2026-10-14: **no new required standards findings**. The original P1 tool-label disclosure remains valid historically and is closed by T6. Focused reporting checks confirm prefixed-token redaction across denial, warning and clean logging, with safe names and native profiles intact.

T7 follows the trusted-launch boundary: installers select an absolute interpreter, registrations use `-I -S -B` and absolute script paths, and runtime launch avoids PATH lookup. Independent actual Bash/macOS PowerShell installed-command tests passed (2 tests, 23.577s), covering hostile startup/PYTHONPATH, replaced PATH executables, quoting-sensitive paths, ordinary scanning, Guardian denial, completed audit, doctor matching and appended-operand rejection. Additional pair probes accepted exact previous-interpreter registrations and rejected appended operands, shell suffixes and mismatched pairs. POSIX quoting round-tripped; ambiguous Windows path characters were refused.

T8's Copilot delimiter-path test passed, including staged-only credentials, safe worktree replacements and colliding display names. Inspection confirms long-path and PowerShell checks preserve detection, enforcement and redaction. Freshness passed for 38 files; independent provider-neutral comparisons passed for scanner, diagnostics and policy helpers. Worktree stayed clean.

**Optional, possible Duplicated Code smell:** `scripts/trusted_hook_launch.py:13` and `hooks/families/diagnostics.py:309` independently render the same launch forms. Sharing pure formatting source embedded during generation could reduce drift while preserving standalone diagnostics. This is a judgment call, not a documented-standard violation or required defect repair.

Final T9 supplement on `4061420e`: no new required findings. Seven fixture-local sentinel calls follow the existing observability testing rule. Rotation, persistence schema recovery, cleanup, locking and intentional maintenance assertions remain intact. Rate limiting, retention/scavenging and fail-open coverage are unchanged. Evidence distinguishes the controlled race from V1's unknown original statement. This supplement launched no tests/probes; none remain running. Worktree stayed clean.

Final Standards result: the original required finding is closed; zero required findings remain, with one optional duplication suggestion. Release/performance acceptance, native Windows and authenticated provider delivery remain separate.
