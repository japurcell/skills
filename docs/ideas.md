# Ideas

Use this file as a lightweight inbox for ideas that are not ready for research or planning.
Add each idea as one short bullet. When work starts, move the idea into the appropriate
research, planning, or implementation artifact.

## Inbox

- [Personal Context vs Shared Context](https://dev.to/alexmercedcoder/personal-context-vs-shared-context-a-deep-dive-into-how-humans-and-organizations-should-feed-14md)
  - Read 'How do we keep shared context from going stale?'
- Add repo-level hooks for codex to achieve parity with Copilot and Gemini repo-level hooks (see `.github/hooks/hooks.json`).
- clean-agent-docs: shows potentially lossy compression
- complete novice to implement the feature end-to-end without prior knowledge of this repo

## Ready

1. I regularly see this in Copilot and Gemini sessions when running on Windows. It may happen on other platforms, but I haven't observed it yet: \[rtk\] /!\ No hook installed — run `rtk init -g` for automatic token savings. We have a wrapper around the hook to keep warnings to a minimum so we might need to change that: hooks/families/rtk.py.
2. $grilling Check stale docs hook. In several repos, .md docs are left with broken links or incorrect formats. We need to create a user-level hook (for copilot, gemini, and codex)that lints markdown files and checks for broken links.
3. $grilling On gemini, I see 'Tool Guardian blocked complete_task. database_destruction/critical. Adjust TOOL_GUARD_ALLOWLIST only if this action is intentional. [tool-guard]'. I also want to see the command blocked in the message. I also want to see this banner on copilot and codex. Ensure that 'scan_secrets' also has this notification banner.
4. $grilling I think this should be a user-level hook: Repository State Corruption via Unconstrained Python/PowerShell Scripts (System Integrity)
    - In 7bdf9b45, agent wrote scripts/update_repo_health_paths.py with os.walk() across the repo root without excluding .git/. It treated .git binary objects as text, corrupted repository metadata, broke git status, and wiped uncommitted staging.
    - In 1922bb9d, agent ran blind rtk git checkout -- <plan> on user-dirty files without running git diff first, destroying user edits and falsely confabulating that it was cleaning up its own probe edits.
    - Root Cause: Lack of automated path guardrails in the harness protecting .git/ and uncommitted user edits.
    - Recommendation:
      - Implement harness pre-execution guardrail rejecting any filesystem write or traversal into .git/.
    - Add strict rule in AGENTS.md: Never run destructive git checkout -- or git restore without running and displaying git diff first.
5. Observed on gemini and may or may not apply to copilot or codex: Hook Deadlock on Shutdown (scan-secrets.py) (Environment / Stability)
   - Evidence: Hook hung for 3.5 minutes on session exit before dying to KeyboardInterrupt inside scan-secrets.py:200 (reader.join(...) on git rev-parse).
   - Root Cause: Threaded stream reader in scan-secrets.py deadlocks on Windows pipes reading Git stdout.
   - Recommendation: Replace threaded pipe reader in scan-secrets.py with standard subprocess.run(..., capture_output=True, timeout=5).
6. Missing Exception Rule in AGENTS.md for Review / Read-Only Tasks (AGENTS.md Maintenance)
   - Evidence: AGENTS.md orientation mandates reading INDEX.md, ARCHITECTURE.md, and CONVENTIONS.md on every non-trivial task, burning 50k+ tokens during read-only code reviews and reports where only a diff or single doc was needed.
   - Root Cause: Rigid universal orientation checklist lacking task-type scoping.
   - Recommendation: Add clause to AGENTS.md: "Read-only audits, executive reports, and diff reviews are exempt from mandatory memory/conventions pre-reading."
7. Observed on gemini and may or may not apply to copilot or codex. Recommendation: Add note in GEMINI.md: When generating multi-line .ps1 or automation scripts, always use write_file first, then run via shell.
8. Ephemeral Probe and Test Scripts Polluting Tracked Repository Tree (Coding Standards)
    - Evidence: Agents authored temporary scripts (probe.ps1, screen.ps1, update_repo_health_paths.py) directly in repo root or scripts/, causing dirty git status and requiring extra cleanup turns.
    - Root Cause: No designated scratch location for temporary probe scripts.
    - Recommendation: Require all disposable agent test scripts to live in .agents/scratchpad/ or $env:TEMP, and add probe*.ps1 to .gitignore in AGENTS.md.
