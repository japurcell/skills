# Standards review - live repair cycle 3

Base: `305ee3a3bc67c7d2ece26dba509cca3899854258`. Reviewed pin: `8f8e14da1c629b7987ba795466613525114b6b30`. Clean frozen checkout; 24 changed files, 1,921 insertions, 90 deletions. Independently inspected the full product/test/doc diff, commit list, active plan, own cycle-2 report, and repair delta from `1d57f60b`. Did not consult either Spec report.

## Documented-standard breaches

1. **[P2] Preserve whole PEM blocks before removing their labels.** `skills/default/execplan-implement-loop/scripts/reporting.py:72` runs label redaction before the PEM expression at line 75. For `PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nFAKE_PRIVATE_MATERIAL_REVIEW_ONLY\n-----END PRIVATE KEY-----`, the unquoted-value scan at lines 47-49 removes only `PRIVATE_KEY=-----BEGIN`. The PEM expression can no longer recognize its opening marker, so the private-key body and footer reach `provider-stderr-*.log`, while metadata says `known_patterns_applied`. The same block without the label is completely removed. Standard: `/Users/adam/.agents/skills/addy-security-and-hardening/SKILL.md:68`, “Never log sensitive data (passwords, tokens, full credit card numbers)”. Recognize/remove the complete multiline credential before its marker can be consumed, or omit ambiguous content. Keep an end-to-end fake-provider case for the combined labeled-PEM form. This is a supported-pattern interaction, beyond the documented arbitrary-secret limitation.

## Heuristic judgments

No actionable Fowler smell established across all 12 required heuristics. Repository conventions override these judgments; no forced JSON abstraction or file-size finding.

## Verification and limits

Two serial process-enabled public copied-runner/fake-provider probes completed in 1.663 seconds: bare PEM retained 11 redacted bytes; labeled PEM retained 88 bytes including the fake body. Both exited 3 with `provider_blocked`. Six focused maintained public CLI credential checks passed in 5.075 seconds, preserving the prior escaped/common/prefixed-label, raw/JSON environment-value, malformed-quote, collision, and incomplete-capture repairs. Prior active-discoveries wording is closed at `ExecPlan.md:100-103`, with historical observations and current T24/T26/T33/T40 resolutions explicit. No real provider, authentication, global configuration, source, or plan changes. Full 99/99 runner and 33/33 helper results remain coordinator evidence; unchanged T31 single-sample grades establish no performance, confinement, or live-provider claim.

Standards: **1 finding; worst P2**.
