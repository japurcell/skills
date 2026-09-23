# PowerShell Authoring Guidance

**Type:** grilling
**Status:** closed
**Blocked By:** none
**Research Dir:** none

## Question

When should Gemini write a multiline PowerShell or automation script to a file before running it, and where should that instruction live so installed Gemini sessions see it? Define exceptions for short commands and a concrete success check.

---

## Resolution

Use a file-first rule for multiline `.ps1` and reusable automation scripts in local Gemini, Copilot, and Codex sessions. Write the complete script with the provider's native file-write or edit tool, then execute the saved file through the shell. Name Gemini's `write_file` in Gemini guidance; use each other provider's actual native file tool rather than assuming a shared tool name. Short, non-script, one-line shell commands remain allowed. Do not construct script files through `echo`, heredocs, or equivalent shell text injection. The next [Disposable Probe Files](disposable-probe-files.md) ticket decides where temporary scripts live.

Update the checked-in instruction sources `.gemini/GEMINI.md`, `.copilot/copilot-instructions.md`, and `.codex/AGENTS.md`, then install them so user-level sessions read the new guidance. The existing Gemini and Copilot Gotchas sections already favor native file-write tools for code files; Codex has no matching section. Keep provider wording consistent while naming tools accurately. The Gemini installers copy `.gemini/GEMINI.md` to `~/.gemini/GEMINI.md` (`scripts/install.sh:66-76`, `scripts/install.ps1:286-290,438`); `scripts/test-install.ps1:747` already checks that copy.

Acceptance for this milestone:

1. Installed instructions for all three providers include the rule and the one-line exception. Installer-copy checks cover the edited sources on supported platforms.
2. Representative local agent runs in each provider create a multiline PowerShell script with quoting and a here-string using a native file tool, then execute that saved file. Confirm the file content and observed output; confirm a short one-line command remains permitted. Record any provider/tool limitation explicitly.
3. Automated Windows checks cover instruction installation and saved-file execution. Provide a precise Windows live-check checklist; a live Windows run is not the completion gate for this ExecPlan.

The user accepted the three scope, trigger, and proof recommendations and confirmed this summary. This is planning only; no provider instructions or scripts were changed while resolving the ticket.
