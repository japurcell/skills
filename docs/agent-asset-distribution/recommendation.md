# Distribution Recommendation

Research date: 2026-09-29. The user-approved distribution contract is recorded in [Choose the Distribution Contract](tickets/choose-distribution-contract.md). This document retains the comparative research and rationale. The contract is approved for implementation planning; installer and updater behavior have not been implemented or live-tested.

## Recommended direction

Use one versioned Git repository as the source of distribution, with selectable components and client-specific installation adapters. Make repository installation the baseline for complete team setups, and publish native plugins or extensions as additional delivery options. Preserve the existing user-global installation workflow.

Use the Agent Skills format for canonical skill content. Where clients support it, package that content through the shared Agent Plugins format. Generate native configuration, custom-agent definitions, and hook registrations from the same maintained sources. This avoids tying the entire distribution to one client's package format while retaining native discovery, updates, and plugin UX.

For this repository, a selective repository installer is the most direct route to the complete requirement because skills, agents, hooks, instructions, and settings already exist as distinct source families. Native plugin distribution can complement that route, but the shared plugin core does not establish universal support for those additional asset types. This conclusion is an inference from the capability research and [current source inventory](local-inventory.md).

## What is portable today

Agent Skills standardizes skill content around `SKILL.md`. Agent Plugins standardizes a package core around root `plugin.json`, skills, and MCP configuration, with vendor extension namespaces. OpenAI, GitHub Copilot, and Cursor document support for the shared plugin format. OpenAI places its hook configuration under `extensions.com.openai`, with `.codex-plugin/plugin.json` retained as a compatibility fallback. Package compatibility therefore needs to be assessed per component, not inferred from the presence of a compatible manifest. [OpenAI packaging documentation](https://developers.openai.com/plugins/build/plugins), [Copilot plugins](https://docs.github.com/en/copilot/concepts/agents/about-plugins), [portable-method findings](research/portable-methods/findings.md).

There are four separate questions for every client: how the package is obtained, where its files are stored, which repository enables it, and which components the client actually loads. A workspace-scoped enablement can still depend on a user-installed package cache. A repository settings file can be shared without shipping the executable scripts it references. [Codex and Copilot findings](research/codex-copilot/findings.md), [Claude Code and Gemini findings](research/claude-gemini/findings.md).

## Client comparison

| Client | Repository setup | Native distribution | Consequence for this repository |
| --- | --- | --- | --- |
| Codex | Repository `.agents/skills`, `.codex/agents/*.toml`, hooks, and project configuration | Shared Agent Plugins core with OpenAI extensions | Standalone skills work in CLI, desktop, and IDE; the IDE extension explicitly does not support plugins. Use direct repository files for custom agents. |
| GitHub Copilot | Repository skills, `.github/agents/*.agent.md`, hooks, and project settings; surface support differs | Plugins with Copilot-specific components | Convert canonical agent filenames and configuration; distinguish CLI, VS Code, and hosted coding agent. |
| Claude Code | `.claude/skills`, `.claude/agents`, `CLAUDE.md` or version-dependent `AGENTS.md` support, and project settings | Claude plugins and marketplaces | Project plugin enablement is committed in `.claude/settings.json`; teammates still install the package separately. Local overrides use `.claude/settings.local.json`. |
| Gemini CLI | `.agents/skills` or `.gemini/skills`, `.gemini/agents`, and `.gemini/settings.json` | Gemini extensions | Extensions install under `~/.gemini/extensions`; workspace activation in project settings does not bootstrap that installation. Extension-packaged agents remain preview/unclear. |
| Cursor | Native project skills, agents, rules, and hooks | Shared Agent Plugins core and Cursor plugin components | Reuse portable content while generating Cursor-specific behavior. |
| OpenCode | Project skill and agent files, project configuration | JavaScript/TypeScript plugins and npm packages | Reuse compatible skill files; event integration uses a different plugin runtime. |

Detailed paths, product surface limits, and first-party sources are recorded in the [Codex/Copilot report](research/codex-copilot/findings.md), [Claude/Gemini report](research/claude-gemini/findings.md), and [portable methods report](research/portable-methods/findings.md). This matrix describes documented support; installation behavior has not been verified by running all six clients. Codex cloud support for plugins, project custom agents, and hooks remains unverified. Copilot cloud supports committed repository inputs but runs hooks in a separate ephemeral Linux sandbox.

## Distribution alternatives

| Method | Best use | Main limitation | Recommendation |
| --- | --- | --- | --- |
| Selective repository installer | Complete setups containing skills, agents, hooks, and instructions | Must own adapters, config merging, updates, and removal | Baseline for committed team setup, using existing source and generator patterns. |
| Native plugins and extensions | Convenient personal installation and project activation; native discovery and update UX | Vendor payloads and runtime behavior differ; package storage may be user-global | Publish as additional outputs from the same canonical sources. |
| Vercel `skills` CLI | Installing selected skill workflows across clients | It installs skills, not generic agents, hooks, or instructions | Offer as the easiest skills-only path, with clearly documented dependency requirements. |
| Vendored copies from a release | Reproducible, reviewable team setup that travels with the repository | Requires a deliberate update mechanism | Prefer copies for committed runtime files, with recorded upstream provenance. |
| Git submodule or subtree | Maintaining a versioned upstream source dependency | Does not register client assets or rewrite their discovery paths | An optional source acquisition method beneath the installer. |
| npm package or release archive | Fetching one versioned bundle without a full source checkout | Delivery alone does not provide client discovery or activation | Transport for the same selective installer or native artifacts. |
| Repository template | Fast initial setup for a new project | Existing projects and later updates need another mechanism | Optional starter experience after distribution behavior is defined. |
| Symlinks | Local development against a checkout | Clone behavior, external targets, permissions, and Windows support complicate team portability | An explicit local development option; prefer copies for team setup. |
| MCP server | Sharing executable tools and service capabilities | It does not replace client hook events, subagents, or instruction discovery | Use when a component needs shared tools, not merely to distribute existing files. |

The delivery rankings above are recommendations, not claims that the methods have identical functionality. Supporting format, CLI, and Git evidence appears in the [portable methods report](research/portable-methods/findings.md).

## Versioning and team setup

A committed setup should record selected components, enabled clients, and an immutable upstream revision or artifact digest. It should also retain the resolved runtime files or a documented restoration process appropriate to each client. Mutable branches, floating package tags, and automatic marketplace updates are separate convenience policies; they should not be described as a frozen team environment.

The Vercel CLI's project lock records source information and content hashes, but its experimental restoration behavior should not be assumed to provide universal immutable restoration for every supported client. It also does not establish installation dependencies between workflows that activate other skills. These limits matter here because [several existing workflows invoke other skills](local-inventory.md). [Portable methods findings](research/portable-methods/findings.md).

For local untracked setup, use native local configuration where supported and keep generated local artifacts excluded without changing the shared team configuration. The installer should report where each component is installed and activated. Apply the approved contract's collision, ownership, and removal policies; project/global precedence still differs across clients.

## Changes required before implementation

The current installers use fixed personal destinations and copy whole collections. Hook templates contain home paths, the Codex skill loader directly reads the global skill root, and Gemini global settings combine selected behavior with personal configuration. A repository option needs provider-aware output and dependency handling, rather than copying the entire personal installation into a project. [Current source inventory](local-inventory.md).

Keep canonical hooks as build-time sources and package their generated provider-local runtime files. Separate package code from writable logs and state. Extract repository policy from personal instructions and settings. Preserve unrelated client configuration and apply the approved pruning rules to managed items. These source constraints inform implementation planning; behavioral decisions are authoritative in the [Choose the Distribution Contract](tickets/choose-distribution-contract.md) decision ticket.

## Ready for implementation planning

The distribution interview is complete, including source targeting, restoration, managed ownership and pruning, project/global coexistence, and operating-system targets. Easy updates are part of the initial contract. Implementation planning is the next separate effort.

The confirmed choices, including the user's exclusion of a rollback feature, are authoritative in the ticket. Native package caches and updater policies still must not be assumed to behave identically across clients. A scoped check of current release conventions appears in [the source inventory](local-inventory.md); it does not establish an existing stable release channel.

Research and decision history live in the [Agent Asset Distribution map](map.md). Installer changes and publishing are outside this research session.

## Validation and documentation pass

Current documentation-pass and verification results are recorded in the [feature handoff](handoff.md). All four decision tickets are closed. Source, installer, runtime configuration, public API, and test behavior remain unchanged; client installation was not live-tested.
