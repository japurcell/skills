---
type: Research Findings
description: Official provider install prerequisites, passive version discovery, and Python sqlite3 lifecycle facts
---

# Adoption prerequisites: factual briefing

Research date: 2026-09-30. Official documentation checked on this date. Provider CLIs were not launched. Installed metadata observation is separated below from documented facts.

## Supported platforms and prerequisites

| Target | Officially documented platform/runtime facts |
| --- | --- |
| Codex desktop | OpenAI's desktop overview offers macOS, Windows, and Linux. Linux is explicitly preview and supports Ubuntu 24.04/26.04, Debian 13, Fedora 43/44, and current fully updated Arch, each x64 and ARM64. The cited pages do not state a minimum macOS or Windows release. The Windows app can run its Codex agent natively in PowerShell or in WSL2; WSL1 is unsupported beginning Codex 0.115. No desktop-wide Python or Node prerequisite is stated. [Desktop overview](https://learn.chatgpt.com/docs/app), [Linux requirements](https://learn.chatgpt.com/docs/linux/linux-app), [Windows app](https://learn.chatgpt.com/docs/windows/windows-app)
| Codex CLI | Official CLI docs offer standalone install for macOS/Linux and Windows, plus npm and Homebrew install choices. The cited install guide does not state minimum OS releases or a Python/Node runtime prerequisite for the standalone binary. [CLI install](https://learn.chatgpt.com/docs/codex/cli)
| GitHub Copilot CLI | npm installation is cross-platform and requires Node.js 22 or later. Official install methods also include WinGet on Windows and Homebrew on macOS/Linux; docs do not state a runtime prerequisite for these package-manager paths. [Quickstart](https://docs.github.com/en/copilot/get-started/cli-quickstart)
| Gemini CLI | Its current installation page labels these as recommended system specifications: macOS 15+, Windows 11 24H2+, Ubuntu 20.04+, Node.js 20.0.0+, Bash/Zsh/PowerShell, internet, and Gemini Code Assist supported location. It documents npm, Homebrew for macOS/Linux, MacPorts for macOS, and Anaconda. The OS list is phrased as recommendations, not an exhaustive support guarantee. [Installation and requirements](https://geminicli.com/docs/get-started/installation/)

## Exact version/build discovery without an agent session

Documented version queries that do not require sending a prompt or starting a model session:

- Codex CLI: `codex --version`. Codex desktop's bundled Codex binary: macOS compatibility path `/Applications/Codex.app/Contents/Resources/codex --version`. Official docs note that desktop and CLI may include different Codex versions. [Troubleshooting/version discovery](https://learn.chatgpt.com/docs/reference/troubleshooting)
- Copilot CLI: `copilot --version` / `copilot -v` displays version information. The separate `copilot version` command also checks for updates, so it is not merely passive version discovery. [Command reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
- Gemini CLI: `gemini --version` / `gemini -v`; passive package-manager inventory is also documented for npm, pnpm, yarn, bun, and Homebrew. `/about` requires an active session and is therefore excluded. [FAQ](https://geminicli.com/docs/faq/)
- Desktop app's own version: OpenAI's inspected official docs give the bundled Codex version command on macOS but did not establish a documented, no-agent-session procedure for retrieving the desktop app's own build number on every OS. **Unknown from inspected docs.**

## Python and stdlib SQLite facts

- Python's `sqlite3` module became invokable as a basic SQLite shell via `python -m sqlite3` in Python 3.12; its `-v/--version` option prints the underlying SQLite library version. This makes 3.12 the lowest Python version with the documented stdlib shell. The shell is optional product functionality, not a prerequisite of the current adoption product. [Python 3.12 sqlite3 docs](https://docs.python.org/3.12/library/sqlite3.html)
- SQLite library requirements vary by Python release: Python 3.11 and 3.12 docs state SQLite 3.7.15 or newer; Python 3.13 states SQLite 3.15.2 or newer. Python 3.14 describes SQLite as a required third-party library and marks `sqlite3` as an optional module; the docs do not give one numeric minimum there. These are module-build/runtime facts, separate from whether the stdlib shell exists. [Python 3.11 sqlite3 docs](https://docs.python.org/3.11/library/sqlite3.html), [Python 3.12 sqlite3 docs](https://docs.python.org/3.12/library/sqlite3.html), [Python 3.13 sqlite3 docs](https://docs.python.org/3.13/library/sqlite3.html), [Python 3.14 sqlite3 docs](https://docs.python.org/3.14/library/sqlite3.html)
- The Python status table separately reports the current phase and scheduled end-of-life date: 3.14/3.13 are in `bugfix` phase (EOL 2030-10/2029-10); 3.12/3.11 are in `security` phase (EOL 2028-10/2027-10); 3.10 is in `security` phase (EOL 2026-10). Python defines bugfix phase as accepting bug and security fixes and issuing binaries; security phase accepts only security fixes and no longer issues binaries. 3.9 and earlier are listed as EOL. [Python version status](https://devguide.python.org/versions/)

## Passive local observation (not a support claim)

On the inspected macOS ARM64 host, the Codex CLI package metadata at `/Users/adam/homebrew/Caskroom/codex/0.159.2/codex-package.json` reports version `0.159.2`, target `aarch64-apple-darwin`. The bundled copy at `/Users/adam/Applications/ChatGPT.app/Contents/Resources/codex-cli/codex-package.json` reports the same. ChatGPT.app host application `Info.plist` reports product version `26.928.21956`; this is host application metadata, not a certified Codex desktop build number. Compatibility between that installed host and the standalone Codex desktop package is unverified. This is a local filesystem observation, not a current universal release fact; version commands were not run. `copilot` and `gemini` were not found by `which -a` on this host, so their installed versions are unknown (absence from PATH does not prove they are not installed elsewhere).

## Existing briefings reused

The provider lifecycle and context-stage invocation briefings supply relevant behavior facts and unresolved contract caveats; they do not establish these OS/runtime minima. Their prior entries explicitly treat observations as version-specific and separate them from provider documentation: [provider lifecycle capabilities](../provider-lifecycle-capabilities/findings.md), [context-stage invocation](../context-stage-invocation/findings.md).

## Source/version caveats

The cited pages are live docs inspected 2026-09-30. Their content may change. Provider docs generally specify installation pathways rather than a full OS support matrix; Gemini's OS values are explicitly recommendations, and no minimum OS could be confirmed for Codex CLI or Copilot CLI beyond the availability of package-manager installers. No VS Code harness facts are included.
