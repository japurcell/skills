# Portable subagent model and effort controls

Checked 2026-09-30, America/Los_Angeles. This is documentation and source research, not a live four-provider compatibility test.

## Recommendation

Use a short launch instruction that covers both tool arguments and agent configuration:

> Launch with the routed model and any specified effort using native tool arguments or agent configuration. Ask before substituting unsupported settings.

Keep verification separate:

> Report requested, configured, and runtime-confirmed settings separately; mark unverified values unknown.

These are proposed instructions, not a standardized API. The approval clause preserves this repository's requested fallback policy. A provider may otherwise fall back automatically. The first instruction is 21 words; the second is 11 words, counting hyphenated words as one.

Put provider-specific mappings in a reference reached when needed. The key correction is to cover the effective agent configuration: checking only spawn arguments misses providers that configure effort in agent definitions or settings.

## Official provider controls

| Provider | Native model control | Native reasoning control | Important limit |
| --- | --- | --- | --- |
| Codex | Exposed `spawn_agent.model`, or agent TOML `model` | Exposed `spawn_agent.reasoning_effort`, or TOML `model_reasoning_effort` | A custom agent file can override spawn values; some runtime schemas hide overrides. |
| Claude Code | `Agent.model` family override, or configured agent `model` with an exact ID | Agent definition `effort` | The published Agent input schema has no effort argument. Environment and policy can override definitions. |
| GitHub Copilot CLI | Custom agent `model` or ordered `models` | Custom agent `reasoningEffort` | CLI, SDK, experimental RPC, VS Code, and GitHub.com are different surfaces. |
| Gemini CLI | Configured agent `model`, then select it by name | Agent-specific `thinkingConfig` in settings | Inspected `invoke_agent` accepts only `agent_name` and `prompt`; thinking levels/budgets are model-specific. |

### Codex

Official OpenAI documentation supports explicit prompt requests, `[agents]` defaults, and custom TOML agents. Precedence is custom agent file, explicit spawn settings, agent defaults, then inherited settings. Choosing another model without effort can select that model's default. Thus an argument check alone cannot establish the final configuration. [Official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents#choosing-models-and-reasoning), [custom agent precedence](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents).

First-party source exposes `model` and `reasoning_effort` conditionally, validates available models and supported efforts, then applies agent configuration. The inspected spawn result returns identity metadata, while resolved model/effort are recorded separately in telemetry. Tool-call acceptance is not independent execution evidence. [Tool schema](https://github.com/openai/codex/blob/cda82a2c6853b484e0ba56d38f13902adfb2a6a1/codex-rs/core/src/tools/handlers/multi_agents_spec.rs#L108), [configuration resolution](https://github.com/openai/codex/blob/cda82a2c6853b484e0ba56d38f13902adfb2a6a1/codex-rs/core/src/agent/child_config.rs#L45), [spawn handler](https://github.com/openai/codex/blob/cda82a2c6853b484e0ba56d38f13902adfb2a6a1/codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs#L80).

Local CLI was `0.159.2`; its inspected release-tag schema also has conditional model/effort fields. Latest release metadata reported `rust-v0.159.3`. Current-main source is pinned separately above; runtime instructions can impose additional restrictions. [Installed-version schema](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/core/src/tools/handlers/multi_agents_spec.rs), [latest checked release](https://github.com/openai/codex/releases/tag/rust-v0.159.3).

### Claude Code

Current custom-agent frontmatter supports a full model ID or family alias plus `effort`. Invocation model overrides, environment force settings, effort environment settings, and organizational caps affect the effective choice. Select an agent definition matching both requested values; an unsupported effort can be reduced by the runtime. [Custom subagents](https://code.claude.com/docs/en/sub-agents#frontmatter-reference), [model and effort settings](https://code.claude.com/docs/en/model-config#adjust-effort-level).

The official SDK documentation publishes the native `Agent` input/output schema: its model argument selects a family, with no effort input. Outputs such as `resolvedModel` and `modelsUsed` provide model evidence, not a guarantee about every request. The public Python SDK separately exposes agent-definition `model` and `effort`; these host configuration fields are not launch-tool fields. [Agent schema](https://code.claude.com/docs/en/agent-sdk/python#agent), [SDK agent configuration](https://code.claude.com/docs/en/agent-sdk/subagents#agentdefinition-configuration), [first-party Python types](https://github.com/anthropics/claude-agent-sdk-python/blob/main/src/claude_agent_sdk/types.py).

Checked releases: [Claude Code v2.1.286](https://github.com/anthropics/claude-code/releases/tag/v2.1.286), [Python SDK v0.2.163](https://github.com/anthropics/claude-agent-sdk-python/releases/tag/v0.2.163). Python types were inspected on unpinned main; closed native implementation was not available.

### GitHub Copilot CLI

The current CLI reference explicitly documents `model`, `models`, `reasoningEffort`, and `modelPolicy`. A required authored model policy can refuse dispatch instead of ordinary fallback. Documented selection checks per-call settings, subagent settings, authored definitions, then the parent. Effort support depends on the chosen model. [CLI agent fields](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#custom-agent-frontmatter-fields).

First-party SDK types confirm `CustomAgentConfig.model` and `reasoningEffort`. They qualify effort inheritance: a different model can use its own default. Generated experimental RPCs differ: `TasksStartAgentRequest` has model but no effort field, while `WorkflowAgentOptions` has both. Do not derive the model-facing `task` tool's argument names from YAML or SDK names. [Agent types](https://github.com/github/copilot-sdk/blob/b6bb031d2d4dc67345b054119f39142edff0bcaf/nodejs/src/types.ts#L1925), [start-agent RPC](https://github.com/github/copilot-sdk/blob/b6bb031d2d4dc67345b054119f39142edff0bcaf/nodejs/src/generated/rpc.ts#L26123), [workflow options](https://github.com/github/copilot-sdk/blob/b6bb031d2d4dc67345b054119f39142edff0bcaf/nodejs/src/generated/rpc.ts#L27553).

Checked CLI release: [v1.0.90](https://github.com/github/copilot-cli/releases/tag/v1.0.90). SDK source is pinned to current main, not asserted identical to that release. The complete native `task` input schema remains unverified.

### Gemini CLI

Inspected native source uses `invoke_agent(agent_name, prompt)`. Its strict Markdown agent schema includes model but no thinking field. Settings can deep-merge agent-specific generation configuration through `agents.overrides.<name>.modelConfig.generateContentConfig.thinkingConfig`; scoped model configuration is another supported route. [Launch schema](https://github.com/google-gemini/gemini-cli/blob/c6bccb7ecbf6d8368d995455dd725ed34466faad/packages/core/src/agents/agent-tool.ts#L43), [agent loader](https://github.com/google-gemini/gemini-cli/blob/c6bccb7ecbf6d8368d995455dd725ed34466faad/packages/core/src/agents/agentLoader.ts#L92), [override merge](https://github.com/google-gemini/gemini-cli/blob/c6bccb7ecbf6d8368d995455dd725ed34466faad/packages/core/src/agents/registry.ts#L647), [generation settings](https://geminicli.com/docs/cli/generation-settings/).

Use model-supported `thinkingLevel` or `thinkingBudget`. A numeric thinking budget is not interchangeable with an OpenAI effort label. The generation-settings example uses an older scope spelling; inspected execution uses the actual agent name, such as `codebase_investigator`. [Google thinking guide](https://ai.google.dev/gemini-api/docs/generate-content/thinking), [scope propagation](https://github.com/google-gemini/gemini-cli/blob/c6bccb7ecbf6d8368d995455dd725ed34466faad/packages/core/src/agents/local-executor.ts#L1002).

Checked release: [v0.62.0](https://github.com/google-gemini/gemini-cli/releases/tag/v0.62.0). Source is separately pinned to current main. Published subagent docs and current source differ on tool exposure, so use the schema exposed by the actual installation. [Subagent documentation](https://geminicli.com/docs/core/subagents/).

## Popular repository patterns

Stars are a dated popularity snapshot, not proof of correct runtime behavior. The first three repositories establish adoption; the fourth is a smaller implementation example. [Superpowers metadata](https://api.github.com/repos/obra/superpowers), [Matt Pocock metadata](https://api.github.com/repos/mattpocock/skills), [wshobson metadata](https://api.github.com/repos/wshobson/agents), [shinpr metadata](https://api.github.com/repos/shinpr/sub-agents-skills).

| Repository | Stars at inspection | Relevant pattern | Model/effort evidence |
| --- | ---: | --- | --- |
| `obra/superpowers` | 293,495 | Shared skill intent plus harness adapters | Explicit model selection and tier rubric; no universal effort mapping in inspected instructions. |
| `mattpocock/skills` | 273,040 | Generic natural-language dispatch | Removes host tool/type names for portability; inspected review skill leaves model/effort unspecified. |
| `wshobson/agents` | 40,120 | Generated native agent artifacts | Codex and Copilot adapters translate model choices; inspected emitters omit reasoning effort. |
| `shinpr/sub-agents-skills` | 91 | Python runner launches separate provider CLI processes | Backend-specific model/effort flags; unsupported effort errors rather than invented native arguments. |

**Superpowers:** its implementer template explicitly reserves a model choice, while its porting guide puts host integration in adapters. This supports compact common instructions plus conditional provider references, not a claim that identical model/effort fields work everywhere. If dispatch is absent, its porting guidance permits inline work or reporting the missing capability. Checked v6.4.2 at `8ca22db`. [Development skill](https://github.com/obra/superpowers/blob/8ca22db/skills/subagent-driven-development/SKILL.md), [implementer template](https://github.com/obra/superpowers/blob/8ca22db/skills/subagent-driven-development/implementer-prompt.md), [porting guide](https://github.com/obra/superpowers/blob/8ca22db/docs/porting-to-a-new-harness.md).

**Matt Pocock:** the review skill says, "Spawn both sub-agents in parallel." Its v1.2.3 release notes specifically explain removing Claude tool/type names for Codex and other harnesses. That establishes portable intent, while the inspected skill supplies no model/effort enforcement. [Review skill at `6acc160`](https://github.com/mattpocock/skills/blob/6acc160/skills/engineering/code-review/SKILL.md), [release notes](https://github.com/mattpocock/skills/releases).

**wshobson:** actual emitter source resolves model aliases and writes Codex TOML or Copilot Markdown. It illustrates a maintained adapter layer; generated agent support is distinct from skills-only installation. Its harness guide covers several hosts, including Antigravity, which must not be treated as Gemini CLI. The inspected Codex/Copilot emitters do not emit effort. [Codex emitter](https://github.com/wshobson/agents/blob/156b7a5e7a8b93642628a339ee4039c925b34c7f/tools/adapters/codex.py#L400), [Copilot emitter](https://github.com/wshobson/agents/blob/156b7a5e7a8b93642628a339ee4039c925b34c7f/tools/adapters/copilot.py#L98), [harness guide](https://github.com/wshobson/agents/blob/156b7a5e7a8b93642628a339ee4039c925b34c7f/docs/harnesses.md).

**shinpr:** its runner reads model/effort from agent definitions, then constructs backend CLI flags. Codex effort becomes a configuration override, Claude effort becomes `--effort`, and OpenCode uses `--variant`. The inspected backend table rejects Gemini effort and has no Copilot CLI backend. This is external process orchestration, not a portable native subagent launch contract. [Skill](https://github.com/shinpr/sub-agents-skills/blob/84e1d4b311dd1f87b71687b62cb1d97744393b80/skills/sub-agents/SKILL.md), [argument builder](https://github.com/shinpr/sub-agents-skills/blob/84e1d4b311dd1f87b71687b62cb1d97744393b80/skills/sub-agents/scripts/_builder.py#L146).

## Implications for these skills

1. Keep task-based model/effort selection in `subagent-model-router`.
2. Replace provider-shaped launch wording in `delegate-to-subagents` with the proposed native-arguments-or-configuration instruction.
3. Preserve the requested fallback approval policy in one place.
4. Report runtime confirmation only when evidence is exposed. Do not require unavailable telemetry or infer execution from accepted arguments.
5. Load a provider mapping only when the exposed tool/configuration needs it. Exact model IDs and supported reasoning values remain provider/model dependent.

No inspected popular repository establishes one native model-and-effort launch syntax across all four requested providers. The recommendation is a synthesis of their portability patterns and official controls. Skills-format support alone does not prove native model/effort support. Current source inspection also does not prove compatibility with older installed releases.
