# Gemini CLI 0.65.0 usage observations

Pinned-source note for the live qualification evidence. Sources below are tag-pinned to `v0.65.0`.

## What `stream-json` exposes

- `init`: `session_id` and `model`; implementation uses `config.getModel()`. This is the configured selection, not guaranteed to be the model actually serving requests (`auto` is a valid configured value). Do not label it a resolved model.
- Terminal `result.stats`: `total_tokens`, `input_tokens`, `output_tokens`, `cached`, `input`, `duration_ms`, `tool_calls`, and `models`.
- `stats.models` is keyed by telemetry model name. Each value has only `total_tokens`, `input_tokens`, `output_tokens`, `cached`, and `input`. It has no per-model request count, error count, or latency.
- `input_tokens` is summed from `tokens.prompt` (API `input_token_count`); `cached` is summed from `tokens.cached` (API `cached_content_token_count`); `input` is `max(prompt - cached, 0)`. The source comment describes `cached` and `input` as a breakdown of `input_tokens`. Preserve all three fields; do not treat total tokens as billed cost.
- `tool_calls` counts CLI tool calls, not API requests.
- Stream stats are built by summing telemetry model token counters. Empty telemetry yields explicit zeros and `models: {}`. The event's `stats` itself is optional in the protocol; missing stats cannot mean measured zero.

## What richer JSON stats contain

- With `--output-format json`, `stats` is the full `SessionMetrics`, not `StreamStats`. `stats.models[model]` includes `api.totalRequests`, `api.totalErrors`, `api.totalLatencyMs`, optional `api.errorsByType`, and token counters `input`, `prompt`, `candidates`, `total`, `cached`, `thoughts`, and `tool`; role-level metrics can also be present.
- Telemetry keys model metrics by the model attached to each API response/error event, so they provide observed model identities. `api.totalRequests` counts recorded API response and error events; it is not exposed in stream result records.
- The CLI headless docs describe stream result stats as aggregated statistics and per-model token usage. The pinned type and formatter confirm that this does not include the JSON mode's per-model request counts.

## Parsing recommendation

- Keep stream usage limited to the fields actually emitted. Preserve `stats.models` and its token fields if detailed usage is useful; do not derive request counts from `tool_calls`, and do not infer model identity from init `model` when it is `auto` or another alias.
- Treat absent stats or absent individual fields as unknown (`null` in the runner report), never as zero. Accept only finite, non-negative numeric values. Explicit emitted zero is a measured/reportable zero. Do not calculate cost or claim billed usage from token totals.
- If exact API request counts or observed model identities are required, they are available in JSON mode's `stats.models[*].api.*`, but not in the current `stream-json` contract. Changing output mode would affect the live streaming protocol and requires an explicit design decision.

## Pinned authoritative sources

- [Headless mode reference](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/docs/cli/headless.md) - result event description.
- [Stream JSON types](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/packages/core/src/output/types.ts) - exact `StreamStats` and model-stat fields.
- [Stream JSON formatter](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/packages/core/src/output/stream-json-formatter.ts) - aggregation and cache/input semantics.
- [JSON formatter](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/packages/core/src/output/json-formatter.ts) - passes full telemetry stats through.
- [UI telemetry](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/packages/core/src/telemetry/uiTelemetry.ts) - request counting, actual model keys, cache token mapping.
- [Non-interactive CLI](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/packages/cli/src/nonInteractiveCli.ts) - init uses configured `getModel()` and result emits formatter stats.

Historical pre-extension cross-check at `e231bcc35b44d42c12f86b8893f514468dfc5f31`: `skills/default/execplan-implement-loop/scripts/processes.py` retained only the five numeric fields `total_tokens`, `input_tokens`, `output_tokens`, `duration_ms`, `tool_calls`; invalid or missing values became `None`. T9 additionally retains optional cached/uncached input tokens and per-model token observations; request counts remain unknown, and a resolved model is retained only when explicitly reported. `brain/plans/2026-10-22-execplan-implement-loop/evidence/resume-report.json` records populated values for those fields, but does not prove that missing fields are zero or billed cost.
