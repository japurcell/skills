# Resolve Techdebt Validation and Rollback

**Type:** grilling
**Status:** open
**Blocked By:** review-quality-and-harness-skills.md
**Research Dir:** not applicable

## Question

What does Techdebt keep, repair, revert or stop for after successful validation, initial failure, repair success and unresolved failure?

[QH-004](../findings.md#qh-004-techdebt-rollback-condition-has-competing-readings) owns the competing readings of `techdebt/SKILL.md:77`: "otherwise" can attach to validation failure or inability to repair/revalidate. Do not choose successful-validation behavior or a rollback command from that ambiguity. Establish intended branches and exactly when a user decision is required.

Preserve small behavior-preserving changes, meaningful validation, user edits, existing approval gates and bounded candidate scope. A rollback must not erase unrelated work. Later disposable fixtures and tool traces must distinguish all four branches. Both final documents retain [QH-004](../findings.md#qh-004-techdebt-rollback-condition-has-competing-readings) and this route; affected execution instructions remain pending.

The human accepted retention of this separate route on 2026-10-06 in [Review Quality and Harness Skills](review-quality-and-harness-skills.md#resolution). That ticket is closed and this route is now unblocked. The underlying choice stays pending; retention gives no implementation authority, evidence waiver or residual-risk acceptance.

---

<!-- Resolution will be appended here. -->
