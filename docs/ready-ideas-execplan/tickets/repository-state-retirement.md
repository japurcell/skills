# Repository State Retirement

**Type:** grilling
**Status:** closed
**Blocked By:** none
**Research Dir:** none

## Question

The user has withdrawn the repository-state hook. What is the exact retirement boundary across canonical source, generated provider scripts, registrations, installers, tests, logs, installed user hooks, and current guidance? Which Git safety instructions and provider sandbox behavior remain, and how should the plan verify that the removed hook no longer runs without claiming stronger protection?

---

## Resolution

The user confirmed this retirement boundary on 2026-09-28:

- Remove the maintained repository-state hook family, its three generated provider scripts and manifest entries, Copilot/Gemini/Codex registrations, installer ownership entries, and dedicated tests. Update aggregate test references. Keep shared audit infrastructure and unrelated hooks. The guard has no dedicated audit log or state directory.
- Do not automatically remove installed user-level scripts or registrations. Document manual cleanup and state plainly that an old registration on another machine may continue to run until removed. A fresh installation must omit the retired guard; do not describe existing installations as cleaned.
- Keep the `AGENTS.md` ban on direct `.git` metadata edits and the review procedure before Git commands that could discard local work. Remove wording that depends on the retired hook blocking a command. Preserve the existing requirement for exact user approval when work would be lost. Provider sandbox protections may be described only where their effective configuration has been verified; neither instructions nor command-text checks guarantee protection from arbitrary later writes.
- Verify checked-in source and registration removal, generator and installer consistency, and absence of the guard from fresh installed registrations for Copilot, Gemini, and Codex. Run relevant existing validation after removing retired assertions. Do not add regression tests for this feature deletion. Preserve historical evidence as historical; revise active guidance and acceptance claims during implementation.

Current Mac inspection found no installed repository-state script at the three expected paths and no `repository-state` entry in the three checked user configuration files. This local observation does not prove other machines are clean.
