# Snapshot Maintenance

Load only when updating catalog/pricing snapshots or investigating historical exclusions. Routing uses the active catalog and current runtime capabilities.

## Refresh

1. Fetch the live sources linked in [model-catalog.md](model-catalog.md) and [pricing.md](pricing.md).
2. Reconcile status, restrictions, retirement dates, and intentional exclusions against the supported-models source. Pricing and comparison pages do not establish availability.
3. Reconcile price rows, input thresholds, cache charges, and promotion deadlines; verify the platform's applicable billing model.
4. Verify exact runtime model IDs and effort values separately.
5. Bypass stale caches before claiming a model or price is absent.
6. Update each changed snapshot's date and preserve provenance for restrictions and exclusions.

## Historical exclusions

These facts belong to the **2026-10-19** snapshot, not a fresh availability check.

- Claude Opus 4.7, Gemini 3.5 Flash, Gemini 3.6 Flash, and Kimi K2.7 Code retired on **2026-10-02**. GitHub recommends the latest respective Opus, Gemini Flash, and Kimi models; confirm exact dispatch configurations.
- Claude Sonnet 4 retired on **2026-05-01** and is excluded from routing candidates, though retained in the price table.
- Qwen2.5 lacks both a supported-models entry and a published Copilot rate in the cited snapshot.
- Gemini 4 Argon's GA status and task fit came from the [supported-models table](https://docs.github.com/en/copilot/reference/ai-models/supported-models#supported-ai-models-in-copilot) and [task comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison#recommended-models-by-task). Its model ID and candidate efforts remain local routing shorthand until confirmed by the runtime.
