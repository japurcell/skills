---
coverage: Current primary-source assessment of Copilot CLI surfaces for per-prompt OKF context selection
---

# Copilot CLI integration surfaces

## Scope and currency

**Assessment date:** 2026-09-08 UTC.

No `copilot` executable is available in this environment, so the installed target version and behavioral contract could not be tested. The findings below describe the current public GitHub documentation and the official `github/copilot-sdk` repository. Any implementation gate must also test the actual target CLI build.

## Conclusion

A repository-scoped Copilot CLI extension is the best available integration boundary for making the normal interactive Copilot CLI the primary OKF consumer. A project extension under `.github/extensions/` can use the CLI-bundled `@github/copilot-sdk/extension` package, join the active session, and register `onUserPromptSubmitted`. That hook receives the submitted prompt and working directory and can return `additionalContext` for the model. This avoids the config-file `userPromptSubmitted` output-discard behavior and the batched-message ambiguity of `userPromptTransformed`. It also requires no package installation because the CLI supplies the extension SDK. Extensions are currently experimental and require the CLI's experimental mode. [Official extension tutorial](https://docs.github.com/en/enterprise-cloud@latest/copilot/tutorials/create-an-extension) · [official extension authoring reference](https://github.com/github/copilot-sdk/blob/main/nodejs/docs/agent-author.md)

The remaining limitation is prompt admission. GitHub explicitly documents `onUserPromptSubmitted` context as advisory and says the hook cannot reject a prompt or enforce policy. Hard limits must be enforced before an SDK host calls `session.send()`, which a project extension does not control for prompts entered in the standard CLI interface. A project extension can deny tool calls through `onPreToolUse`, but the model has already received the prompt by then. [Official SDK prompt-hook reference](https://github.com/github/copilot-sdk/blob/main/docs/hooks/user-prompt-submitted.md) · [official CLI hook reference](https://docs.github.com/en/copilot/reference/hooks-reference)

This is not a regression from the current repository behavior. The existing `.github/hooks/scripts/inject-auto-ingest-context.py` prepends an instruction that pending ingest blocks normal work, uses post-turn stop hooks for enforcement, and explicitly fails open when prompt rewriting raises an unexpected exception. The earlier map accidentally promoted pre-model denial from a possible provider capability into a cross-provider compatibility requirement.

## Surface comparison

| Surface | Standard interactive CLI | Deterministic prompt context | Pre-model denial | Stability and cost | Assessment |
| --- | --- | --- | --- | --- | --- |
| Project extension `onUserPromptSubmitted` | Yes, with experimental extensions enabled | Yes: one submitted prompt, `workingDirectory`, and `additionalContext` | No | Experimental; SDK bundled with CLI; no package dependency | Recommended Copilot-first context path |
| Config `userPromptTransformed` hook | Yes | Can replace model-facing content, but fires for primary and preceding batched messages without a discriminator | No | Documented config surface | Keep only for existing compatibility/ingest behavior, not primary selection |
| Plugin `hooks.json` | Yes after installation | Same config-hook contract as above | No | Plugin contents are cached on install | Packaging option, not a stronger runtime boundary |
| Custom agent, skill, or MCP tool | Yes | Model-directed rather than guaranteed per prompt | No | Supported customization surfaces | Useful adjuncts, insufficient as the selector trigger |
| Standalone Copilot SDK host | Uses Copilot CLI as its backend but replaces the standard TUI | Yes; the host validates and selects before `session.send()` | Yes, because the host can refuse to call `session.send()` | Separate application and dependency/installation decision; some TUI-only features are unavailable | Optional strict-assurance product, not the default CLI integration |

The SDK-to-CLI protocol supports programmatic sessions, but GitHub documents several interactive CLI features as unavailable through the SDK, including slash-command UI, agent/model pickers, context management, deep research, and other terminal workflows. A strict SDK host would therefore change the user's main-agent experience rather than transparently wrap it. [SDK and CLI compatibility](https://docs.github.com/en/copilot/how-tos/copilot-sdk/troubleshooting/compatibility)

## Recommended contract change

Split the existing provider contract into two independently stated guarantees:

1. **Context-integrity guarantee:** the Copilot extension validates the active workspace and source-ingest state, invokes the shared selector, and returns exactly one complete OKF context block or one complete legacy context block. Projection errors, `no_match`, mandatory-budget exhaustion, and selector failures discard all OKF output and use the legacy loader. No mixed or partial context is allowed.
2. **Prompt-admission guarantee:** the standard Copilot CLI cannot currently enforce a pre-model hard stop. For unsafe states where even legacy context is not valid, the extension returns a minimal privacy-safe stop instruction and puts the session into a deny-all-tools state through `onPreToolUse`. This prevents repository mutation but does not prevent the model from reading the prompt or emitting text. The evaluation report must label this as `advisory_stop`, not `hard_stop`.

This change makes Copilot useful without claiming an enforcement property the host does not provide. Cases involving task confidentiality or a requirement to prevent any model inference remain ineligible for the standard CLI path; they require the optional SDK host or a future native prompt-admission hook.

## Required capability tests

Before Copilot becomes the default OKF consumer, test the actual target build and fail enrollment if any of these are false:

- the repository extension loads from `.github/extensions/<name>/extension.mjs` in the active Git worktree;
- `onUserPromptSubmitted` fires exactly once for each user submission, including queued and steered messages;
- `input.prompt`, `input.workingDirectory`, and the injected test clock have the documented values;
- `additionalContext` reaches the model once without altering the visible prompt;
- selector or extension failures yield the declared legacy or advisory-stop behavior without partial OKF context;
- `onPreToolUse` denies every mutating and read tool while advisory-stop state is active;
- extension stdout remains reserved for JSON-RPC and diagnostics contain no prompt or concept bodies;
- `/clear`, resume, worktrees, nested directories, and extension reloads preserve or reestablish the correct workspace-scoped state.

Because extensions are experimental, their behavioral capability suite must run against every candidate Copilot CLI upgrade before promotion. A version string alone is insufficient.
