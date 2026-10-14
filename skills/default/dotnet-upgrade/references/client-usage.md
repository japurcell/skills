# Client usage and optional focused installation

Documentation retrieved October 1, 2026. Installed client versions and live behavior were not tested. Recheck the official sources below for the client's actual release before relying on discovery, invocation or enforcement. This document describes intended use, not universal controls.

## Shared discovery and required metadata

All three cited client documents describe user skills under `~/.agents/skills/`. They also describe project/workspace `.agents/skills/`, with different search and precedence rules. The authoring source `skills/dotnet-upgrade/` is not automatically an installed user skill. Avoid duplicate names and inspect the discovered location rather than assuming the preferred copy won.

Preserve the entry point's exact requested frontmatter:

```yaml
---
name: dotnet-upgrade
description: "Use only when the user explicitly invokes dotnet-upgrade to research, plan, execute, or verify a .NET version upgrade."
disable-model-invocation: true
---
```

Preserve `agents/openai.yaml` exactly:

```yaml
policy:
  allow_implicit_invocation: false
```

Codex documents the sidecar policy. Equivalent recognition of `disable-model-invocation` in Copilot CLI and Gemini CLI remains **unverified by this work**; their cited skills pages do not establish identical enforcement of these controls. The prose description and workflow boundaries are agent instructions, not framework-level security controls. Do not remove metadata to satisfy another client or validator.

The existing repository frontmatter validator rejects the requested property. This intentional exception is retained; validator execution, archive packaging and validator changes are excluded from this authoring effort. JSON/whitespace checks and document review do not establish runtime enforcement.

## GitHub Copilot CLI

[GitHub's skills documentation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills) lists personal `~/.copilot/skills` and `~/.agents/skills`, plus project `.github/skills`, `.claude/skills` and `.agents/skills`. It documents `/skills list`, `/skills reload` and `/skills info` for discovery in an interactive session.

After a separately authorized installation, start a fresh session or reload skills, inspect the discovered location with `/skills info dotnet-upgrade`, and explicitly mention the skill in the prompt:

> Use /dotnet-upgrade to research and plan this repository's .NET 8-to-10 upgrade. Do not execute migration edits.

The page also describes automatic selection based on description. Do not claim this work proved Copilot ignores the skill absent explicit invocation, or that its interpretation of the requested frontmatter matches Codex's sidecar. If enforcement is essential and the local release is not verified, do not rely on automatic discovery as a guardrail; keep this bundle outside discovery locations and explicitly request reading its entry point for permitted advice.

## Codex CLI

[OpenAI's skills documentation](https://learn.chatgpt.com/docs/build-skills) describes personal `$HOME/.agents/skills` and repository `.agents/skills` from the current directory up to the repository root. It notes duplicate names are not merged and can appear together. Codex detects changes automatically; restart if a change does not appear.

Invoke explicitly through the skill selector `/skills` or a `$` skill mention:

> $dotnet-upgrade Research and plan this repository's .NET 8-to-10 upgrade; do not execute migration edits.

The document states `policy.allow_implicit_invocation: false` in `agents/openai.yaml` disables implicit invocation while explicit `$skill` invocation remains available. That is documented behavior, not a live test here. Neither this policy nor skill invocation approves migration; the workflow still requires fresh necessary evidence and approval of the concrete plan.

## Gemini CLI

[Gemini's skills documentation](https://geminicli.com/docs/cli/skills/) describes user `~/.gemini/skills/` and `~/.agents/skills/`, plus workspace `.gemini/skills/` and `.agents/skills/`. Its documented precedence puts workspace above user skills, and the `.agents/skills/` alias above the provider directory within the same tier.

It documents `/skills list` and `/skills reload` for discovery. Activation is different: the model calls `activate_skill` when it identifies a matching task, and the documented interactive flow presents a consent prompt before loading the skill body and granting access to bundled resources.

Make an explicit natural-language request:

> Explicitly activate the dotnet-upgrade skill to research and plan this repository's .NET 8-to-10 upgrade. Do not execute migration edits.

Confirm the requested skill and directory in the consent prompt if that flow is available in the installed release. This is a request to the model, not a guaranteed activation command. There is no `/dotnet-upgrade` Gemini command established by the cited documentation; do not invent one. Activation consent is not concrete-plan approval. Noninteractive policy and consent behavior were not tested, and the requested frontmatter/sidecar's enforcement in Gemini remains unverified. Keep the bundle outside discovery locations if unverified automatic activation is unacceptable.

## Optional focused copy, only after separate authorization

These are future installation instructions, not actions performed by this authoring effort. Install only a complete, reviewed bundle with its internal references present. Do not run `scripts/install.sh`, `install.ps1`, a validator/packager or a general skill installer: account-wide flows can change other skills, agents, hooks, instructions and client settings.

1. Choose the reviewed authoritative source directory `skills/dotnet-upgrade/` in the user's skills source repository. Resolve its actual location; no particular home directory or original application checkout is required. Inspect `SKILL.md`, `agents/openai.yaml`, all referenced documents and five templates. Do not install an incomplete milestone branch. Record source revision and copied-file list outside the installation directory.
2. Inspect the prospective destination `~/.agents/skills/dotnet-upgrade` and provider/workspace copies with the same name. If the destination exists, including as a symlink, stop without merging, overwriting or deleting it. An update requires a separate reviewed backup/diff and explicit update scope; this new-install procedure does not authorize it.
3. After permission to create this new destination, create only that skill directory under the selected discovery root. Copy `SKILL.md`, `agents/`, `references/` and `assets/` from the reviewed bundle, preserving their relative layout and both controls. Do not copy root `evals/` or benchmark workspaces; runtime instructions do not depend on them. Record the exact newly created files and their contents/digests for bounded recovery. If copying fails partway, report it and treat the partial install as incomplete.
4. Compare the copy with source and inspect internal references before use. Refresh discovery using the client-specific documented mechanism above or a new session. Inspect the discovered location and report unverified controls honestly. This inspection is not a live model evaluation and need not change any settings.

Rollback is limited to the recorded files created by this new installation. Verify the exact destination is the owned new directory, not a pre-existing path or symlink; remove only recorded files that still match the installed contents, then remove owned empty directories. If files changed after copying, stop and preserve them for review rather than deleting later work. Never remove an entire discovery root, another skill, source repository or client configuration. An existing-directory update needs its own approved restore procedure; do not improvise one here.

## Scope remains separate from client activation

Explicit activation permits only the requested discovery, research, planning, approved execution or verification phase. Read-only requests do not authorize target writes. Offline drafts cannot replace refreshed necessary evidence. Unsupported routes remain research-only, material changes require renewed approval, and deployment deferral is not verification. Candidate lessons stay in the target project until authoritative-source updates are explicitly approved.

This bundle does not select a model or override runtime defaults. No installation, client settings/hooks/instructions changes, cross-project migration or live evaluation is claimed here.
