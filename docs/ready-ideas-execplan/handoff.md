# Ready ideas ExecPlan handoff

## Goal and status

Implement [ExecPlan](ExecPlan.md) on `codex/ready-ideas-execplan`. It now has 12 milestones: eight Ready problems, shared hook transport, integrated automation, and later live Copilot/VS Code and Gemini checks. Keep its `Progress`, milestone acceptance, discoveries, decisions, and outcomes synchronized. All Wayfinder tickets in [the map](map.md) are closed.

- **Accepted and integrated:** milestone 1 read-only orientation (`AGENTS.md`, `.agents/memory/INDEX.md`); milestone 3 disposable-probe guidance in only the three provider instruction files.
- **Integrated, acceptance open:** milestone 2 file-first PowerShell guidance and temporary-home installer checks; native Windows automation remains. Milestone 4 Codex scanner transport, installer merger, Windows workflow, and delivery probe; deployed Codex `PreToolUse`/`Stop` and timeout behavior remain unproved.
- **Active isolated branches:** milestone 5 scanner shutdown in `codex/ready-ideas-m5` at `/Users/adam/.codex/worktrees/ready-ideas-m5/skills`; milestone 9 explicit RTK rewrite in `codex/ready-ideas-m9` at `/Users/adam/.codex/worktrees/ready-ideas-m9/skills`. Both started from base tip `92b5adf0`; preserve their edits and integrate one at a time.
- **Remaining:** milestones 6–8 and 10, plus later-session live milestones 11 (Copilot CLI and local VS Code) and 12 (Gemini CLI). Do not mark the full plan complete while these remain open.

## Next step

Wait for milestone-5 and milestone-9 implementers. Review their evidence and clean worktrees. Rebase and fast-forward one branch at a time onto the current base; use a merger agent before any conflict-prone rebase, then rerun affected tests only if conflicts occur. Update `ExecPlan.md` immediately after each accepted integration. Milestone 6 follows scanner shutdown because both edit `hooks/families/scan_secrets.py`.

## Decisions and constraints

- User explicitly approved milestone-4 edits to `.codex/global-hooks.json`, canonical `hooks/`, and persistent user-level Codex registrations after automatic approval review wrongly applied milestone 3's three-file limit.
- User chose **no local installation** of absent Copilot or Gemini CLIs. Their deployed checks belong to separate milestones 11 and 12 in another session. Source fixtures never count as deployed proof. Native Windows automated tests and a live-check checklist remain required; live Windows execution is supplemental.
- Milestone 3 alone changes `.gemini/GEMINI.md`, `.copilot/copilot-instructions.md`, and `.codex/AGENTS.md`; it has no installer, agent-run, or Windows acceptance check. Do not broaden it while finishing other milestones.
- RTK uses published, pinned `dev-0.50.0-rc.451` side by side with stable RTK and child-scoped `RTK_SUPPRESS_HOOK_WARNING=1` for explicit agent commands. Preserve RTK stderr and other errors. Milestone-9 implementer verified release metadata and asset checksum list; see its branch for exact pins.
- Do not add dependencies without approval. Never bypass provider hook trust. Install into a real user home only after source and temporary-home tests and review of destination changes. Do not discard unrelated user work.

## Evidence and open risks

- Milestone 1: `rtk test python3 scripts/lint-okf.py` and `rtk git diff --check` passed. Its first patch was auto-review rejected; narrower wording preserved every edit-time read and passed.
- Milestone 2: `rtk test bash scripts/test-install.sh` and `rtk test pwsh -NoProfile -File scripts/test-install.ps1` passed on macOS. A Codex multiline `.ps1` file-tool exercise with quotes and a here-string passed. Copilot/Gemini agent runs moved to milestones 11/12.
- Milestone 3: three-file diff review and whitespace check passed. No probes or extra checks were created.
- Milestone 4: integrated tip `a74d5a02` had passing scanner, startup, merger, installer, generator, runner-registry, and nine probe tests on macOS. `codex-cli 0.155.1` exited `0` in two guarded read-only probes but produced zero `PreToolUse` markers; cleanup restored the original `~/.codex/hooks.json` bytes. [Codex hook docs](https://developers.openai.com/codex/hooks) say non-managed hooks require exact-definition trust through `/hooks`; no trust bypass was used. Inspect trust and event delivery before claiming installed behavior.
- Custom `CODEX_HOME` remains a Codex hook-install limitation: installers put hooks/config under `HOME/.codex` and registered commands point there, while the probe can target custom `CODEX_HOME`. Coordinate installer and template paths before claiming custom-home support.
- `.github/workflows/ready-ideas-windows.yml` exists but has not run on native Windows. `rtk gh auth status` failed because the local GitHub token is invalid; do not claim CI proof until a runner result exists. macOS `pwsh` is not native Windows evidence.
- Copilot and Gemini CLIs are absent on this Mac. No provider versions or live outcomes were fabricated. Copilot cloud is outside user-level hook scope; arbitrary child-process writes cannot be fully intercepted by pre-tool hooks.

## Relevant files

- [ExecPlan](ExecPlan.md): task graph, source paths, commands, acceptance, and recovery; authoritative implementation state.
- `hooks/families/scan_secrets.py`: milestone-5 canonical scanner change; generated outputs belong to the generator.
- `hooks/families/rtk.py`: milestone-9 canonical RTK rewrite; automatic forwarders remain unchanged.
- `scripts/install-codex-hooks.py:90-135`: exact two-command owned-handler merge; preserve unrelated user groups and fields.
- `scripts/probe-provider-hook-delivery.py`: owner-only prepare/verify/cleanup for installed events; never treat its fixtures as deployed proof.
- `.github/workflows/ready-ideas-windows.yml`: native Windows automation route, still awaiting runner execution.

## Resume rules

Read `.agents/memory/INDEX.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, and affected area instructions before edits. Apply `exec-plans` and `tdd` for implementation, and the ExecPlan implementer's commit-message rules. Integrate private worker branches by clean-worktree rebase and `git merge --ff-only`; keep the base branch clean. Run `update-agent-docs` once at the end of the code work session and synchronize this handoff before stopping.
