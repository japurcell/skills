---
type: Known Issue
description: Read when skill validation rejects invocation controls or benchmark reports imply measurements that were not collected.
---

# Skill Tooling Limitations

## Invocation controls and validation

The repository's [quick validator](../../../skills/skill-creator/scripts/quick_validate.py) does not allow `disable-model-invocation` in its frontmatter allowlist. A rejection therefore does not authorize removing a user-required invocation control. The scoped [dotnet-upgrade acceptance record](../../../skills/dotnet-upgrade/references/document-review.md) retains this incompatibility and distinguishes document review from client enforcement. Follow [skill validation instructions](../../instructions/testing/skills.md) for the approved acceptance scope and vendored YAML runtime.

Evidence checked: 2026-10-07 against the validator allowlist and retained acceptance scope. Recheck when the validator or invocation controls change; this does not certify enforcement in any deployed client.

## Benchmark measurements can be proxies

The [benchmark aggregator](../../../skills/skill-creator/scripts/aggregate_benchmark.py) substitutes zero for missing duration and can use output characters as its token metric. Its metadata defaults and configuration ordering can also mislead comparisons. Preserve raw artifacts, identify selected runs and delta direction, and label missing or proxy metrics. A single selected run per scenario does not establish repeated-run variance.

Evidence checked: 2026-10-07 against metric extraction and aggregate metadata construction. Recheck when those paths or the artifact schema change; an aggregate field alone does not prove measured time or token usage.
