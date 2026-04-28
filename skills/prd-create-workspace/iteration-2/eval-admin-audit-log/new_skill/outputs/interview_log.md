# Interview Log

## Assumptions I would surface immediately

1. This is a web-based SaaS team admin console, not a native mobile product.
2. The current repository is not the target application, so no app-specific admin, billing, or SSO prior art is available here.
3. The request is for an MVP audit log focused on compliance review, not a full SIEM, alerting platform, or anomaly-detection system.
4. Reviewers need both on-screen review and portable evidence for audits.

→ In this offline benchmark, I proceed with these assumptions unless corrected.

---

## Question 1

**Question:** Who should be allowed to view the audit log in v1?

**Why it matters:** This decides the permission model, whether a read-only reviewer role is needed, and how strict export access must be.

**Recommendation:** Allow organization owners plus a dedicated read-only audit/compliance reviewer role, because official admin-log products favor least-privilege viewing instead of requiring full admin rights.

**Options:**
1. Org owners only — simplest, but too restrictive for compliance teams.
2. All admins — broader access, but higher data-exposure risk.
3. Org owners plus a read-only audit/compliance reviewer role — best balance of access and least privilege.

**Assumed accepted answer:** Option 3.

**Next decisions that depend on this:** export permissions, redaction rules, and whether billing-only admins can see the full log.

---

## Question 2

**Question:** Should v1 capture only successful changes, or both successful and denied attempts for role, billing, and SSO changes?

**Why it matters:** Compliance and security reviews often need to know not only what changed, but also who attempted a privileged change and was denied.

**Recommendation:** Capture both successful and denied attempts for the in-scope admin-change families, because denied attempts add meaningful review value without expanding into all activity types.

**Options:**
1. Successful changes only — simplest, but weaker for compliance/security review.
2. Successful and denied attempts for in-scope admin changes — recommended MVP.
3. All attempted reads and changes everywhere — too broad for v1.

**Assumed accepted answer:** Option 2.

**Next decisions that depend on this:** event taxonomy, visible outcome fields, and testing scope.

---

## Question 3

**Question:** How much change detail should each audit entry show for sensitive settings?

**Why it matters:** Reviewers need enough detail to understand impact, but billing and SSO settings may contain secrets or sensitive values that must not be exposed.

**Recommendation:** Show field-level before/after summaries with redaction for sensitive values, because that preserves reviewability without leaking secrets.

**Options:**
1. Event name only — too little detail for compliance review.
2. Full raw payload diff — too risky for secrets and sensitive data.
3. Field-level before/after summaries with masking/redaction where needed — recommended.

**Assumed accepted answer:** Option 3.

**Next decisions that depend on this:** detail drawer design, export format, and negative test cases for redaction.

---

## Question 4

**Question:** Should compliance review be supported only in-product, or should v1 also support export of filtered results?

**Why it matters:** Many audits require evidence to be shared with reviewers outside the application, and export strongly affects scope, permissions, and data-shaping rules.

**Recommendation:** Include filtered export in v1, because the request explicitly mentions compliance review and vendor audit-log products treat export as a core workflow.

**Options:**
1. In-product review only — smaller scope, but weak for external audit workflows.
2. Filtered CSV/JSON export for authorized viewers — recommended.
3. Full API, streaming, and scheduled reports — useful later, but too broad for v1.

**Assumed accepted answer:** Option 2.

**Next decisions that depend on this:** export permissions, retained fields, and parity tests between UI and export.

---

## Question 5

**Question:** What retention promise should the product make for audit-log data in v1?

**Why it matters:** Retention is a product commitment that changes storage, export, and compliance expectations; vendor defaults vary too much to leave this implicit.

**Recommendation:** Commit to at least 1 year of searchable in-product retention, with exportable records for longer-term archival if required by customer policy.

**Options:**
1. 90 days — likely too short for compliance review.
2. 1 year searchable in product, with export/archive support beyond that — recommended.
3. Multi-year in-product retention for all customers — expensive and may exceed MVP scope.

**Assumed accepted answer:** Option 2.

**Next decisions that depend on this:** storage requirements, success criteria, and out-of-scope boundaries for archival systems.

---

## Question 6

**Question:** Should real-time alerts for sensitive admin changes be included in this PRD, or deferred?

**Why it matters:** Alerting changes scope significantly by introducing notification channels, throttling, delivery guarantees, and on-call expectations.

**Recommendation:** Defer real-time alerting and focus v1 on trustworthy recording, review, filtering, and export, because the core gap described is reviewability for compliance.

**Options:**
1. Include real-time alerts now — broader security feature, larger MVP.
2. Defer alerts and ship a strong audit trail first — recommended.
3. Exclude alerts permanently — too rigid.

**Assumed accepted answer:** Option 2.

**Next decisions that depend on this:** Out of Scope wording and follow-up roadmap notes.

---

## Accepted assumptions carried into the PRD

- Authorized viewers are org owners and read-only audit/compliance reviewers.
- The audit log records both successful and denied role, billing, and SSO changes.
- Sensitive fields use field-level before/after summaries with masking/redaction.
- Authorized viewers can export the currently filtered result set.
- Searchable in-product retention is at least 1 year.
- Real-time alerting is deferred from this PRD.
