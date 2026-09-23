# Disposable Probe Files

**Type:** grilling
**Status:** closed
**Blocked By:** none
**Research Dir:** none

## Question

Where should agents place disposable probe and test scripts, how should they clean them up, and is a `probe*.ps1` ignore rule useful or harmful? Decide provider guidance that keeps tracked areas clean without hiding meaningful files.

---

## Resolution

Put disposable probe and test scripts in `.agents/scratchpad/` when they need a repository-local location, or in the operating system's temporary directory when they do not. Keep scripts intended as permanent tests or tools in tracked source paths. This complements [PowerShell Authoring Guidance](powershell-authoring-guidance.md): agents create multiline or reusable scripts with their provider's native file tool, then run the saved file.

Before finishing, remove disposable files the agent created, using their exact paths. If a file is needed to reproduce a reported failure, retain it in the scratchpad or temporary directory and record its path and purpose in the handoff. Inspect before cleanup; never remove or overwrite a pre-existing user file. Compare the final Git status with the starting status so a probe does not leave new changes in tracked repository areas.

Do not add `probe*.ps1` to `.gitignore`. `.gitignore:4` already ignores `.agents/scratchpad/`; a broad probe-name rule would hide misplaced scripts in tracked directories. Keep those mistakes visible so the agent can correct them.

Implementation adds the rule only to `.gemini/GEMINI.md`, `.copilot/copilot-instructions.md`, and `.codex/AGENTS.md`. The three checked-in instruction files are the complete change for this milestone. Do not add a `.gitignore` rule or edit `.agents/instructions/repo.md`.

Completion condition: each of the three instruction files states the placement, cleanup, retained-repro, permanent-test, and Git-status guidance above. This milestone requires no installer checks, local agent runs, automated Windows checks, or Windows live-check checklist.

The user initially accepted broader guidance placement and verification, then narrowed this milestone to the three provider instruction files with no installer checks, local agent runs, or automated Windows checks. This later instruction controls the plan. This is planning only; no provider instructions or `.gitignore` rules changed while resolving the ticket.
