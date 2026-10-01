# Model and Baseline Evidence

Collected 2026-10-01 for [Set Audit Evidence and Model Coverage](tickets/set-audit-evidence-and-model-coverage.md). This file records facts and unresolved prerequisites. The human-confirmed policy lives in the ticket.

## Native CLI catalog

The parent ran `rtk proxy codex --version`, which reports `codex-cli 0.159.3`. A non-secret projection of `rtk proxy codex debug models` confirms the following native catalog entries. All have `visibility: list`; no model was invoked.

| Exact native ID | Advertised efforts | Catalog default |
| --- | --- | --- |
| `gpt-5.6-sol` | `low`, `medium`, `high`, `xhigh`, `max`, `ultra` | `low` |
| `gpt-6-sol` | `low`, `medium`, `high`, `xhigh`, `max`, `ultra` | `medium` |
| `gpt-6.1-sol` | `low`, `medium`, `high`, `xhigh`, `max`, `ultra` | `low` |
| `gpt-5.6-luna` | `low`, `medium`, `high`, `xhigh`, `max` | `medium` |
| `gpt-6-luna` | `low`, `medium`, `high`, `xhigh`, `max` | `medium` |
| `gpt-6-astra` | `low`, `medium`, `high`, `xhigh`, `max`, `ultra` | `low` |
| `gpt-5.6-terra` | `low`, `medium`, `high`, `xhigh`, `max`, `ultra` | `medium` |

The projection parses the catalog JSON, selects these exact `slug` values, and prints only `slug`, `visibility`, `default_reasoning_level`, and `supported_reasoning_levels`. It does not read credentials or print configuration. Reproduce that projection rather than collecting unrelated local state. Catalog advertisement does not prove successful execution, account entitlement, or preserved model selection during a run.

The desktop collaboration interface separately advertises these seven IDs with `medium` support. That interface's dispatch metadata and the native CLI catalog are different evidence surfaces. The [earlier provider research](research/provider-compatibility/findings.md#models-and-evidence-limits) establishes API and product documentation, not a successful native run. Do not transfer CLI effort values into API requests or infer filesystem skill support from an API feature row.

## Native execution contract

The parent ran `rtk proxy codex exec --help`. Version 0.159.3 advertises `--model`, `--config`, `--sandbox`, `--cd`, `--ephemeral`, `--ignore-user-config`, `--json`, `--output-schema`, and `--output-last-message`. `--sandbox` accepts `read-only`, `workspace-write`, and `danger-full-access`. These are help observations, not tested containment or successful execution.

The current [OpenAI configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) names `model_reasoning_effort` and makes supported values depend on the model and client. A later runner can request the agreed effort explicitly with `--config 'model_reasoning_effort="medium"'`, paired with the exact `--model` value. This documents the setting syntax; it does not validate a complete launch recipe or effective runtime selection.

`--ignore-user-config` ignores the user configuration but still uses `CODEX_HOME` for authentication. Help does not establish that this flag isolates skill discovery, user instructions, hooks, plugins, or installed copies. A fresh fixture directory and an instruction to ignore other copies do not by themselves prove isolation. Verify the discovered catalog, inherited instructions and hooks, dependency availability, and effective permissions before baseline execution. No complete isolated launch recipe has been validated.

The help output does not advertise `--full-auto`, although the dated [OpenAI skill-evaluation article](https://developers.openai.com/blog/eval-skills) uses it in examples. The article supports captured JSONL, artifact and process checks, and explicit, implicit, contextual, and negative prompts. Adapt example commands to the installed client; do not copy a flag absent from its help or bypass approvals to make an example work.

Both help and version commands exit 0 while warning that PATH aliases cannot be created in the sandbox. The warning is not a model failure. The catalog projection exits 0. No credentialed request, installer, native skill discovery run, or live baseline was executed.

## Existing evaluation inputs

The parent parsed these existing JSON files and checked the named fixture and grader paths. These are candidates for later eligibility review, not a selected or fixture-ready sample. No grader or scenario was executed.

| Candidate | Verified inputs | Eligibility limits |
| --- | --- | --- |
| Handoff | Three scenarios, fixture files, and a grader. The [first scenario](../../skills/handoff/evals/evals.json#L6) copies a small repository and produces a handoff and result JSON. | Existing scenarios use explicit invocation. Inspect synthetic redaction inputs, assertions, output paths, and current contracts before use. Native activation and negative-case coverage are unverified. |
| Spec to Tasks | Four scenarios and a grader. The [first scenario](../../skills/spec-to-tasks/evals/evals.json#L6) consumes an existing PRD fixture and produces task JSON. | Existing prompts and assertions are not proof of current semantic correctness or native triggering. Inspect the grader and dependency/output contracts before choosing cases. |
| OKF Authoring | Eight [repository-local scenarios](../../.agents/skills/okf-authoring/evals/evals.json#L15), including read-only, outside-root, and unavailable-linter cases. | Prompts require a coordinator to seed a complete fixture and independently apply and lint output. A raw prompt replay does not satisfy this contract. Coordinator readiness and native runtime compatibility remain unverified. |
| Explore | Three scenarios and a grader; the [first prompt](../../skills/explore/evals/evals.json#L6) requests proposed subagent invocation details. | No first-case input files or bundled fixture tree were identified. Proposed spawns do not prove actual delegation or exploration behavior. |
| Create Skill | Four scenarios, fixture files, and a grader. The [first scenario](../../skills/create-skill/evals/evals.json#L6) generates a bundle and describes validation and refresh commands. | The prompt declares no live human, while the skill has authoring and installation dependencies. Verify that the chosen scenario preserves the current contract within the safe baseline boundary; a mention of an installer is not evidence it ran. |

The sample of parsed JSON does not establish full suite coverage or grader correctness. Existing assertions may conflict with current intent; the adoption policy gives explicit instructions and human decisions precedence. No candidate is yet certified ready for the native baseline contract.

## Delegation and recovery

Grilling authorized read-only fact discovery. The explorer used explicitly selected and submitted `gpt-6-luna` at `max` effort, with a 360-second parent-enforced limit. Executed model and effort are unconfirmed. The parent interrupted it at the deadline after receiving partial model/catalog facts, then allowed one 90-second report-only recovery on the same explicitly configured agent. That recovery also ended without a completed report and was interrupted.

The route was Standard because source and client-contract reconciliation required judgment and prior source summaries had needed corrections. The provisional same-tier fallback was `gpt-5.6-luna` at `max`; it was not used. Neither attempt edited files, ran a baseline, or delegated further. Partial model facts were verified independently by the parent's catalog projection. The parent collected the help and JSON/path observations above; unreported explorer fixture claims are not relied on.

Both delegation attempts ended at their parent deadlines. No task depends on an active explorer. Preserve partial facts and unknowns rather than treating a timeout or an eval file's presence as successful validation.
