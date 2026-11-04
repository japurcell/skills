# Snapshot Maintenance

Load only when updating catalog/pricing snapshots or investigating historical exclusions. Routing uses the active catalog and current runtime capabilities.

## Refresh

1. Fetch the live sources listed in [`catalog.json`](catalog.json) under `sources`; each entry records its snapshot date.
2. Reconcile status, task guidance, restrictions, administrator enablement, retirement dates, exact model identifiers, and intentional exclusions against the supported-models and model-comparison sources. Pricing and comparison pages do not establish availability. Recheck retirement history on or after listed cutoffs; never restore a retired model from price rows alone.
3. Reconcile GitHub Copilot price rows, input thresholds, cache charges, and promotion deadlines; preserve currency and token units in the source metadata. Legacy annual plans may apply request multipliers rather than the token charges used by the CLI.
4. Verify exact runtime model IDs and effort values separately.
5. Bypass stale caches before claiming a model or price is absent.
6. Update each changed snapshot's date and preserve provenance for restrictions and exclusions.

## Historical exclusions

These facts were reconciled for the **2026-10-28** snapshot, not a fresh availability check at dispatch time. Source: [supported-models retirement history](https://docs.github.com/en/copilot/reference/ai-models/supported-models#model-retirement-history).

- GPT-5 mini, GPT-5.4, GPT-5.4 mini, GPT-5.5, and Gemini 3.7 Flash retired on **2026-10-19**. Their rows are absent from the current supported-models and pricing tables; exclude them from routing and the active price snapshot.
- Claude Opus 4.7, Gemini 3.5 Flash, Gemini 3.6 Flash, and Kimi K2.7 Code retired on **2026-10-02**. GitHub recommends the latest respective Opus, Gemini Flash, and Kimi models; confirm exact dispatch configurations.
- Claude Sonnet 4 retired on **2026-05-01** and is excluded from routing candidates, though retained in the price table.
- Qwen2.5 lacks both a supported-models entry and a published Copilot rate in the cited snapshot.
- Gemini 4 Argon's GA status and task fit came from the [supported-models table](https://docs.github.com/en/copilot/reference/ai-models/supported-models#supported-ai-models-in-copilot) and [task comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison#recommended-models-by-task). Its model ID and candidate efforts remain local routing shorthand until confirmed by the runtime.
- GPT-6.1 Terra is GA, with everyday agentic coding and terminal work documented in the task comparison. Its Standard/medium candidate is provisional; confirm the exact pair in the target runtime. Gemini 3.8 Flash's lightweight coding guidance supports its provisional Fast/medium candidate.

## Catalog ownership

`catalog.json` owns candidates, tiers, restrictions, pricing, and task defaults. Update it and its source metadata together when these facts change.
