# Set Safe Command Validation Scope for AGENTS Authoring

**Type:** grilling
**Status:** open
**Blocked By:** review-skill-authoring-and-repository-guidance.md
**Research Dir:** not applicable

## Question

What execution and approval boundary should Create AGENTS.md apply when verifying the setup, database, deployment, and test commands it documents?

[SAG-013](../findings.md#sag-013-public-claims-and-command-validation-ambiguity) owns the evidence. The skill asks that all commands work and includes mutation-capable public examples, while its documented output covers setup, database, and deployment instructions. Example/customization labels already limit transfer; actual unsafe execution has not been observed. The unresolved issue is authority, not whether unsupported commands should be copied.

Decide which verification is inspection, which isolated executions are permitted, and which operations require separate approval or remain human-run. Preserve accurate repository-specific instructions and honest tested/inspected/unverified labels. Public-fact and example wording cleanup may proceed independently only when it does not select the unresolved execution policy. No setup, deployment, installer, or live command execution is authorized by this audit ticket.

---

<!-- Resolution will be appended here. -->
