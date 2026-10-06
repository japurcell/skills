# Resolve Harness Analysis Report Capture

**Type:** grilling
**Status:** open
**Blocked By:** review-quality-and-harness-skills.md
**Research Dir:** not applicable

## Question

Should Harness Analysis return a chat report captured by the evaluation harness, or allow an explicitly approved report-file exception with an accurately scoped read-only attestation?

[QH-008](../findings.md#qh-008-harness-eval-artifact-writes-conflict-with-the-absolute-read-only-statement) owns the absolute no-file-write rule and exact no-files-modified attestation versus eval prompts requesting `outputs/report.md`. User authorization can permit a scoped artifact, but the resulting attestation must remain truthful. Do not assume an exception or broaden audited-system write authority.

Preserve read-only audited systems, no hook execution, sensitive-data stops, evidence/uncertainty sections, bounded inspection and refusal of implementation. Retain useful report capture and independent artifact checks. Set exact capture, approval and attestation expectations before executable eval work; both final documents retain [QH-008](../findings.md#qh-008-harness-eval-artifact-writes-conflict-with-the-absolute-read-only-statement) and this route.

The human accepted retention of this separate route on 2026-10-06 in [Review Quality and Harness Skills](review-quality-and-harness-skills.md#resolution). That ticket is closed and this route is now unblocked. The underlying choice stays pending; retention gives no implementation authority, evidence waiver or residual-risk acceptance.

---

<!-- Resolution will be appended here. -->
