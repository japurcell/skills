# Feature Specification: Recurring Invoice Tax Workflow

**Created**: 2026-03-26  
**Status**: Draft  
**Input**: User description: "Add recurring invoices to our billing workflow. Finance admins should create monthly invoices from subscription records, review generated draft invoices, and send them in batch. If customer tax data is missing, invoice send must be blocked with clear guidance. We sell in US and EU and need configurable tax rules by region."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Generate Monthly Draft Invoices (Priority: P1)

Finance admins generate monthly draft invoices from active subscription records so recurring billing can be prepared at the start of each billing cycle.

**Why this priority**: Without draft generation, recurring invoicing cannot happen and downstream review or sending is blocked.

**Independent Test**: Can be fully tested by initiating a monthly run for a known set of active subscriptions and confirming draft invoices are created only for eligible subscriptions.

**Acceptance Scenarios**:

1. **Given** active subscriptions with billable monthly periods, **When** a finance admin runs monthly invoice generation for a target month, **Then** the system creates one draft invoice per eligible subscription for that month.
2. **Given** subscriptions that are canceled or already invoiced for the target month, **When** a finance admin runs monthly invoice generation, **Then** the system excludes those subscriptions and reports the exclusion reasons.
3. **Given** a completed generation run for a target month, **When** a finance admin reruns generation for the same month, **Then** duplicate draft invoices are not created.

---

### User Story 2 - Review Draft Invoice Set (Priority: P2)

Finance admins review generated draft invoices before sending to ensure invoice data and tax treatment are correct.

**Why this priority**: Review is the main quality control step that prevents incorrect billing before invoices are sent.

**Independent Test**: Can be fully tested by opening a generated batch, filtering drafts by status or tax readiness, and verifying draft-level details and issues are visible.

**Acceptance Scenarios**:

1. **Given** a generated draft batch, **When** a finance admin opens the batch review view, **Then** they can see each draft invoice with subscription, customer, amount, region, and tax status.
2. **Given** drafts with and without complete tax data, **When** a finance admin filters for blocked drafts, **Then** only drafts missing required tax data are shown with explicit remediation guidance.

---

### User Story 3 - Send Eligible Invoices in Batch (Priority: P3)

Finance admins send invoices in batch after review, while drafts missing required tax data remain blocked and unsent.

**Why this priority**: Batch send delivers operational efficiency and ensures only compliant invoices are issued.

**Independent Test**: Can be fully tested by sending a mixed batch and verifying eligible drafts are sent while blocked drafts remain in draft with clear reasons.

**Acceptance Scenarios**:

1. **Given** a reviewed batch containing eligible and tax-blocked drafts, **When** a finance admin starts batch send, **Then** only eligible drafts are sent and blocked drafts remain unsent.
2. **Given** a blocked draft with missing customer tax data, **When** a finance admin views send results, **Then** the system provides clear guidance on missing fields and where to update them.
3. **Given** all drafts in a batch are tax-blocked, **When** a finance admin starts batch send, **Then** no invoices are sent and the batch is marked as blocked with actionable guidance.

### Edge Cases

- A customer changes billing region (US to EU or EU to US) between draft generation and send; send must re-evaluate tax eligibility using current region rules.
- Subscription records missing billing contact or legal entity information needed for invoice issuance are flagged during generation and excluded with reason codes.
- A batch contains drafts in multiple regions with different tax requirements; each draft is validated against its own region rule set.
- Tax rules are updated after drafts are generated; the system applies the currently active rule set at send-time validation.
- A finance admin retries batch send after correcting tax data; only previously blocked drafts that now pass validation are sent.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST allow finance admins to generate monthly draft invoices from active subscription records for a selected billing month.
- **FR-002**: System MUST generate at most one draft invoice per eligible subscription per billing month.
- **FR-003**: System MUST exclude ineligible subscriptions (for example canceled, not billable for month, or already invoiced) and record exclusion reasons.
- **FR-004**: System MUST provide a generation summary that includes total subscriptions evaluated, drafts created, exclusions, and failure counts.
- **FR-005**: System MUST allow finance admins to review generated draft invoices before send.
- **FR-006**: System MUST display per-draft details needed for review, including customer, subscription reference, region, line amount totals, and tax readiness state.
- **FR-007**: System MUST evaluate tax-data completeness for each draft invoice using configurable tax rules for the customer region.
- **FR-008**: System MUST support region-specific tax rule configuration for at least US and EU regions.
- **FR-009**: System MUST block sending any draft invoice that fails tax-data completeness checks.
- **FR-010**: System MUST present clear, actionable guidance for blocked drafts, including which customer tax fields are missing and where corrections are made.
- **FR-011**: System MUST allow finance admins to send eligible draft invoices in batch.
- **FR-012**: System MUST process batch sends as partial-success capable, where eligible drafts are sent and blocked drafts remain draft.
- **FR-013**: System MUST provide a send result summary with counts for sent, blocked, and failed drafts and include reason codes for unsent drafts.
- **FR-014**: System MUST maintain an auditable status history for draft creation, review readiness, send attempts, send outcomes, and block reasons.

### Key Entities _(include if feature involves data)_

- **Subscription Record**: Represents a recurring customer plan enrollment used as source data for monthly invoicing; includes billing cadence, active period, customer link, and billable state.
- **Draft Invoice**: Represents a not-yet-issued invoice generated for a specific subscription and billing month; includes region, amount details, tax readiness state, and send eligibility.
- **Invoice Batch**: Represents a group of draft invoices selected for a send operation; includes run metadata, per-draft outcomes, and aggregate result counts.
- **Tax Rule Set**: Represents configurable regional tax requirements (for example US and EU) used to determine required customer tax data and send eligibility.
- **Customer Tax Profile**: Represents customer tax-related attributes needed for invoicing in a region; includes required identifiers and completeness status.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 95% of monthly recurring draft generation runs for up to 10,000 eligible subscriptions complete within 10 minutes.
- **SC-002**: 100% of invoices sent from recurring batches pass configured regional tax-data requirements at send time.
- **SC-003**: Finance admins can complete review and initiate send for a 1,000-invoice batch in under 15 minutes in at least 90% of observed runs.
- **SC-004**: At least 98% of blocked invoices include guidance that finance admins rate as clear and actionable in post-run feedback.
- **SC-005**: Duplicate invoice issuance for the same subscription and billing month is reduced to 0 in recurring batch sends.

## Assumptions

- Finance admins already have permission to access billing workflows and perform invoice generation and sending.
- Subscription records already contain enough billing metadata to determine monthly eligibility.
- Existing billing workflows already support invoice draft and sent statuses; this feature extends those workflows for recurring operations.
- US and EU regional tax rule definitions are maintained by authorized business users outside this feature and are available before monthly runs.
- Customer tax profiles are stored in an existing customer record domain that this workflow can reference during validation.
