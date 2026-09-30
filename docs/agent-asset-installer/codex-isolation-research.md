# Codex CLI isolation feasibility

Research date: 2026-09-29 America/Los_Angeles (2026-09-30 UTC). Target: installed macOS arm64 Codex CLI 0.159.0. This supplements [codex-cli-prerequisites.md](codex-cli-prerequisites.md), which records the earlier help inspection.

## Finding and evidence boundary

A credential-free custom-provider experiment has a documented configuration route. A loopback Responses fixture could plausibly drive the real CLI far enough to inspect native skill/agent discovery and hook delivery. This is an inference from the provider and protocol documentation, not an executed experiment. Complete client isolation, unauthenticated TUI onboarding, fixture compatibility, normal trust persistence, and native delivery remain unproved.

This research read installed binary metadata/static strings and official documentation. It did not launch Codex, start a server, install a client, inspect or copy credentials, modify personal state, fabricate trust, or exercise a model session. Online documentation is current rather than pinned to 0.159.0; runtime acceptance must verify the exact installed version.

## Installed evidence

The existing launcher resolves to `/Users/adam/homebrew/Caskroom/codex/0.159.0/bin/codex`. Its installation contains native `codex` and `codex-code-mode-host` executables; no local Rust source was available in that directory. Static printable strings establish that the binary contains the following settings and diagnostics, but do not establish their complete runtime behavior:

| Observation | Implication and limit |
| --- | --- |
| `CODEX_HOME`, `CODEX_SQLITE_HOME`, `sqlite_home`, `cli_auth_credentials_store`, `requires_openai_auth`, `model_providers` | Relevant isolation/provider code exists. This does not prove all writes or credential reads follow those settings. |
| Diagnostic rejecting `wire_api = "chat"` and requesting `responses` | The later fixture should target Responses, not the legacy Chat Completions protocol. |
| PATH-alias creation warning; stale `arg0` temporary-directory cleanup warning; refusal to create helper binaries under a temporary directory | Launcher setup itself can touch filesystem state before a session. A temporary Codex home may encounter an intentional helper-path restriction. Its exact path predicate and impact were not established. |
| Project-trust persistence and hook-trust strings | Native trust mechanisms exist. Static strings cannot prove which records are written or whether a fresh unauthenticated client can reach their UI. |

The earlier help inspection already encountered a refused PATH-alias write. Repeating help against the real home would add no useful isolation proof. No documented alias-disable control was established here; absence from the inspected strings is not proof that none exists.

## Supported controls and their limits

`CODEX_HOME` relocates Codex configuration and local state, including authentication files, logs, sessions, and skills. Its directory must already exist. `CODEX_SQLITE_HOME` defaults to that home; configured `sqlite_home` takes precedence. Use absolute private paths. These documented controls do not promise containment of every OS/cache write. [Environment variables](https://learn.chatgpt.com/docs/config-file/environment-variables).

Profiles load an additional `<profile>.config.toml` inside the same home, after the base config. A profile is therefore configuration layering, not a separate state container. Project provider/auth settings are ignored, so the custom provider belongs in the disposable user configuration. Trusted project layers still matter for repository assets. [Advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced).

Authentication can use a file, the OS credential store, automatic selection, or process-memory-only `cli_auth_credentials_store = "ephemeral"`. Existing credentials can be shared by CLI and IDE, and session token refresh can write cached state. A future experiment should inherit no credentials and use ephemeral storage. This setting is not a guarantee against other caches or logs. Managed authentication requirements may override local choices. [Authentication](https://learn.chatgpt.com/docs/auth).

`exec --ephemeral` omits session rollout files. `--ignore-user-config` omits the base user configuration but does not create a separate home or remove authentication dependencies; it would also omit a provider configured there. Neither flag establishes client containment. [Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode), [Developer commands](https://learn.chatgpt.com/docs/developer-commands).

## Credential-free provider feasibility

Custom providers have a configurable `base_url`; `requires_openai_auth` defaults to false and the supported `wire_api` is `responses`. Configuration exposes WebSocket support, retry limits, log/state paths, and history persistence. MCP credential storage supports `auto`, `file`, and `keyring`, not `ephemeral`. [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

The advanced guide includes a local HTTP provider without an `env_key`. For a later fixture, choose a new provider ID, a loopback-only base URL, explicit `requires_openai_auth = false`, Responses, and bounded retries. Omit credential helpers, bearer tokens, authentication environment keys, and custom authorization headers. Do not override reserved built-in provider IDs. [Advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced).

The app-server account documentation explicitly associates `requiresOpenaiAuth: false` with a provider that can operate without OpenAI credentials. This corroborates the configuration route, but does not prove CLI 0.159.0 bypasses its sign-in onboarding for that provider. [App-server authentication](https://learn.chatgpt.com/docs/app-server).

A future loopback fixture would need valid Responses streaming events, output items, and function-call arguments, not just a text body. The API documents semantic SSE events including response creation, text deltas, completion, and errors. Its documentation does not establish a complete Codex-compatible stub. Derive exact tool schemas from the real client's request and verify acceptance in a bounded experiment. [Streaming Responses](https://developers.openai.com/api/docs/guides/streaming-responses).

## Normal trust and native evidence

Project hooks load only from trusted project layers. Non-managed hook definitions additionally require native review of their current definition through `/hooks`; changed definitions require renewed review. Hook sources are additive, and managed policy can exclude non-managed hooks. Large hook context may spill into the OS temporary directory. A private `TMPDIR` and short outputs belong in the later isolation design. Never bypass hook trust or handwrite trusted-project/definition records. [Hooks](https://learn.chatgpt.com/docs/hooks).

Codex discovers repository skills under `.agents/skills` from the current directory up to the repository root. It initially loads metadata and paths, then reads the full skill when selected; `$skill-name` provides explicit invocation. Thus a catalog listing alone proves less than activation. [Build skills](https://learn.chatgpt.com/docs/build-skills).

Custom agents are standalone TOML under project `.codex/agents` or personal `.codex/agents`; required fields are `name`, `description`, and `developer_instructions`. Native use requires spawning the selected custom agent. A later fixture must observe that child's request and distinctive instructions, rather than infer discovery from a file's presence. [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).

## Prerequisites for a later authorized experiment

These are proposed acceptance gates, not completed steps:

1. Establish an external process boundary and write audit before launching the client. Deny access to personal credential material and real-home writes; allow only the disposable project/state paths and installed executables. The model's tool sandbox is insufficient evidence of containment of the CLI itself. Allow network only to the allocated loopback endpoint and stop if startup requires another endpoint.
2. Pre-create private child-process home, Codex home, SQLite, log, cache, and temporary directories. Set child `HOME`, `CODEX_HOME`, `CODEX_SQLITE_HOME`, `TMPDIR`, and relevant XDG paths without changing the parent environment. Use a minimal environment allowlist and absolute executables, with no inherited provider/auth tokens or personal shell initialization. Do not copy personal config, skills, plugins, or credentials. Account for admin/system layers rather than assume a custom home disables them.
3. Verify help-only startup under that boundary first, including PATH-alias setup and cleanup. Record paths and write outcomes. Stop on an unsafe write or helper-path refusal that prevents normal operation; resolve through a supported location or disposable OS environment, not by patching or disabling safety checks.
4. Configure only the disposable user home with the custom provider and ephemeral CLI credential storage. Keep MCP/plugins unconfigured; if MCP storage must be specified, use `file` within the private home. Confirm effective managed policy permits the experiment before proceeding. Do not weaken imposed policy.
5. Start the separately authorized, bounded loopback fixture and enter the normal native UI. Complete project approval and `/hooks` review there. Record approval UI and filenames/hash changes without reading any credential contents. If sign-in is still required, stop and record that unmet gate. Restart through the normal client path so startup hooks can run with the reviewed definition.
6. Observe distinctive installed skill metadata, explicit skill activation, and the spawned custom agent's instructions in actual client requests. Drive a harmless tool call using the client's offered schema, then capture native hook input/output and the next request's hook context. Correlate session IDs, events, and a private marker. Directly executing hook scripts or feeding handcrafted hook JSON is subprocess evidence only.
7. Repeat from a nested working directory and a relocated repository path containing spaces. Verify private state/write accounting, unchanged personal state, no credential-store access, no unintended outbound traffic, bounded requests, clean shutdown, and no source mutation. Report each event separately; do not infer `SessionEnd` from process exit alone.

## Unmet gates

No runtime evidence yet demonstrates disposable-home PATH-alias compatibility, all client/cache write locations, policy-layer behavior, unauthenticated native onboarding, Responses-fixture compatibility, normal trust persistence, native skill/custom-agent activation, or hook event delivery. A custom provider avoiding OpenAI authentication does not by itself prove absence of other OpenAI network activity. This research supports designing the bounded experiment; it does not satisfy M6 native acceptance or provide evidence for Windows, Linux, Copilot, or Gemini.
