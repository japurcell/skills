---
type: Agent Instruction
description: Codex required skills, personal hook merging, trust, and deployment boundaries.
---

# Codex Hooks

Read [shared hook rules](hooks.md) for implementation changes. Consult the [official hook documentation](https://learn.chatgpt.com/docs/hooks) for current provider behavior.

- **Codex required skills:** Keep `.codex/global-hooks.json` inactive in the repository and merge its maintained `SessionStart`, `PreToolUse`, and `Stop` groups into user-global `~/.codex/hooks.json`. The hook must emit one JSON document, use `hookSpecificOutput.additionalContext`, announce the loaded-file count through `systemMessage`, fail closed with `continue: false`, and never import another runtime's hook code.
- **Codex size and audit boundaries:** Bound raw required-skill files independently from the final stripped-and-wrapped context so large removable YAML frontmatter does not consume the injection budget. Audit paths must reject symbolic links, Windows junctions, and other reparse points before opening or changing permissions.
- **Codex trust:** Non-managed Codex hooks must be reviewed after installation or definition changes through `/hooks`; never advise bypassing hook trust.
- **Codex install safety:** The shared merger must preserve unrelated hook data, replace only exact maintained POSIX or Windows commands, reject symlinked config destinations, back up only real semantic changes, and atomically write owner-only JSON. Bash and PowerShell installers must refuse a linked installed-hook destination instead of following it.
- **Codex registered-hook deployment:** When `.codex/global-hooks.json` gains a maintained handler, add its script and any local launcher it invokes to both installers' exact Codex copy lists and the merger's owned-file list. Temporary-home installer tests must resolve the registered command to an installed file and verify its launcher is installed too.

Project-local OKF `Stop` validation follows [OKF adapter rules](hooks-okf.md), independently of user-global hooks. Validate changes through [hook testing](testing/hooks.md).
