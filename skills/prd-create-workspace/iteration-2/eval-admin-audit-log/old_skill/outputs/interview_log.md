# Interview Log

## Assumptions surfaced immediately

ASSUMPTIONS I'M MAKING:
1. This is a web application with authenticated team and organization admin settings.
2. Role management, billing settings, and SSO configuration are privileged admin actions.
3. The feature should reuse the target application's existing stack instead of introducing a new toolchain.
4. Compliance reviewers need actor, target, timestamp, result, and redacted before/after detail.
5. Because this is benchmark mode, I will simulate answers if you do not respond live.

## One-question-at-a-time sequence

### Question 1

**Question:** Should v1 cover all sensitive team-admin configuration changes for user roles, billing settings, and SSO configuration, including denied attempts, rather than only successful writes?

**Why it matters:** This is the parent scope decision. It determines event taxonomy, permissions, retention volume, filter design, and what compliance reviewers can rely on.

**Recommendation:** Yes. Capture successful changes and denied attempts for these three domains in v1, because compliance review is materially weaker if a privileged action attempt leaves no trace.

**Options:**
1. Successful changes only — lower effort, but misses risky attempted actions.
2. Successful and denied attempts for roles, billing, and SSO — best compliance value and my recommendation.
3. All admin actions platform-wide — broader than the prompt and likely too large for v1.

**Depends on this answer:** event schema, filter options, success criteria, and rollout size.

**Assumed accepted answer:** Option 2 accepted. V1 covers successful and denied actions for user roles, billing settings, and SSO configuration only.

### Question 2

**Question:** Should access be scoped so team admins can review their own team's events, while organization owners and a read-only compliance role can review/export broader audit history?

**Why it matters:** This defines the authorization model, least-privilege boundaries, export permissions, and support workflows.

**Recommendation:** Yes. Team admins should see only their team scope, while organization owners and a dedicated read-only compliance role can view/export the broader log. This preserves least privilege while supporting formal review.

**Options:**
1. Team admins only — simplest, but weak for cross-team compliance review.
2. Team admins plus org owners plus read-only compliance reviewers — recommended.
3. All authenticated admins can see everything — easier to ship, but over-broad.

**Depends on this answer:** permissions matrix, export controls, testing decisions, and boundaries.

**Assumed accepted answer:** Option 2 accepted. Team admins are team-scoped; org owners and compliance reviewers have broader read/export access.

### Question 3

**Question:** Should each event show redacted before/after detail for the changed fields, while suppressing secrets such as raw card data, API secrets, certificates, and tokens?

**Why it matters:** This determines whether the audit log is actually useful for compliance review without creating a new sensitive-data exposure surface.

**Recommendation:** Yes. Include field-level before/after detail where it helps reviewers understand the change, but redact or summarize secret values and sensitive payment credentials.

**Options:**
1. Actor + action only — safer, but often insufficient for compliance review.
2. Full before/after values including secrets — unacceptable security risk.
3. Redacted before/after detail with secret suppression — recommended.

**Depends on this answer:** event schema, UI detail view, export schema, and privacy testing.

**Assumed accepted answer:** Option 3 accepted. Before/after detail is included when safe and useful, with mandatory redaction for secrets and high-risk sensitive values.

### Question 4

**Question:** Should audit-log viewing and export actions themselves be audited, and should the log be append-only from normal admin surfaces?

**Why it matters:** This determines trustworthiness of the feature and whether reviewers can trace who accessed or extracted sensitive audit data.

**Recommendation:** Yes. Audit-log access and export should generate their own events, and normal admins should never be able to edit or delete audit records.

**Options:**
1. Log mutations only — simpler, but leaves sensitive access untracked.
2. Log mutations plus view/export access, with append-only records — recommended.
3. Allow privileged admins to edit/delete entries — incompatible with trustworthy compliance review.

**Depends on this answer:** storage constraints, export behavior, permissions, and success criteria.

**Assumed accepted answer:** Option 2 accepted. Audit-log access/export is itself auditable, and the log is append-only.

### Question 5

**Question:** Should v1 ship with a filterable audit-log page and CSV/JSON export, using asynchronous export for large date ranges?

**Why it matters:** This defines the review workflow. Compliance review usually needs more than a raw feed; it needs filters, pagination, and a durable export path.

**Recommendation:** Yes. Provide a filterable page for day-to-day review and CSV/JSON export for evidence gathering. Use asynchronous export for large result sets so the UI stays responsive.

**Options:**
1. On-screen log only — fastest, but weak for formal review.
2. Filterable UI plus direct export for all ranges — okay until data volume grows.
3. Filterable UI plus CSV/JSON export, with async export for large ranges — recommended.

**Depends on this answer:** UI states, export jobs, accessibility behavior, and observability.

**Assumed accepted answer:** Option 3 accepted. V1 includes filterable review plus CSV/JSON export, with async export for large ranges.

### Question 6

**Question:** Should v1 start as net-new capture only, without promising historical backfill for pre-launch admin changes?

**Why it matters:** Backfill feasibility depends on existing data sources, event quality, and trust in historical reconstruction. The current benchmark repo provides no evidence that reliable backfill is possible.

**Recommendation:** Yes. Start with net-new capture from release forward and communicate the cutoff clearly. This avoids false confidence in reconstructed historical records.

**Options:**
1. Require historical backfill — high effort and high risk without source evidence.
2. Net-new capture only from launch onward — recommended.
3. Limited best-effort backfill for select events — possible later, but not safe to promise now.

**Depends on this answer:** rollout plan, success criteria, and further notes.

**Assumed accepted answer:** Option 2 accepted. V1 is authoritative from launch forward; no historical backfill commitment is made.

### Question 7

**Question:** Should this PRD stay stack-agnostic and require the implementation to reuse the target application's existing admin UI, backend services, and validation/test commands once the real product repo is identified?

**Why it matters:** The benchmark repository is not the target application, so choosing a framework, language, or command set here would be invented prior art.

**Recommendation:** Yes. Keep the PRD product-specific but stack-agnostic, and explicitly require reuse of the target application's existing stack and commands.

**Options:**
1. Invent a stack now to make the PRD look more concrete — not trustworthy.
2. Keep the PRD stack-agnostic and defer exact tech/commands to the real repo — recommended.
3. Stop and refuse to draft the PRD — unnecessary because assumptions can be documented.

**Depends on this answer:** Tech Stack, Commands, Project Structure, and Further Notes sections.

**Assumed accepted answer:** Option 2 accepted. The PRD remains stack-agnostic and explicitly defers exact implementation stack and commands to the target application repository.

## Resulting accepted assumptions

1. V1 covers successful and denied role, billing, and SSO admin actions.
2. Team admins are team-scoped; org owners and compliance reviewers have broader read/export access.
3. Events include redacted before/after detail but never raw secrets.
4. Audit-log viewing/export is itself auditable, and audit records are append-only.
5. V1 includes filterable review plus CSV/JSON export with async handling for large ranges.
6. V1 is net-new capture only.
7. Exact stack and executable commands must be inherited from the target application repository.
