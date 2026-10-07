# Resolve ExecPlan Integration Validation

**Type:** grilling
**Status:** open
**Blocked By:** review-execution-and-handoff.md
**Research Dir:** not applicable

## Question

Define how an implementer branch validated on an older base becomes the tested integrated tip after a conflict-free rebase. Resolve the caller's no-rerun rule against the tested-tip requirement, including no-op rebases, combined behavior changes and subsequent plan-only SHA updates. Preserve isolated private worktrees, serial clean rebase/fast-forward integration, failed-test repair stops, living-plan state and protected cleanup. Do not remove no-rerun or invent new validation authority before this decision.

[EH-007](../findings.md#eh-007-execplan-integration-has-unresolved-tested-tip-validation) owns exact source evidence, predicted consequences and validation requirements. The source absence or ordering is static evidence; native behavior remains untested. Resolve this protected contract before selecting dependent wording or executable work. Retention of a route is not approval of its underlying behavior, implementation, installation, publication, evidence waiver or residual risk.

---

<!-- Resolution will be appended here. -->
