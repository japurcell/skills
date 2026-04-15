# Feature Specification: Support Inbox SLA

**Created**: 2026-03-26  
**Status**: Draft  
**Input**: User description: "We need a customer support inbox for our B2B SaaS. Agents should see all incoming emails, assign tickets to themselves, set status (open/pending/resolved), add internal notes, and reply to customers from the same view. We also need SLA tracking with alerts before breach, but only for enterprise accounts. Keep v1 web-only."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Process Incoming Support Requests (Priority: P1)

A support agent reviews all new incoming customer emails in a unified inbox, opens a ticket, and sends a reply to the customer without leaving the same ticket view.

**Why this priority**: This is the core value of the feature. If agents cannot triage and respond from one place, the inbox does not solve the primary workflow problem.

**Independent Test**: Can be fully tested by receiving a new customer email, opening the created ticket, sending a reply from the ticket view, and verifying the customer receives the response.

**Acceptance Scenarios**:

1. **Given** a new customer email arrives, **When** an agent opens the inbox, **Then** the ticket appears with sender, subject, and received time.
2. **Given** an open ticket, **When** an agent writes and sends a reply from that ticket view, **Then** the outgoing message is sent to the customer and recorded in the same conversation timeline.

---

### User Story 2 - Own and Track Ticket Progress (Priority: P2)

A support agent assigns a ticket to themselves, updates ticket status as work progresses, and adds internal notes visible only to internal staff.

**Why this priority**: Ownership and status management reduce duplicate work and improve handoff clarity, which is essential for team operations after core replying is in place.

**Independent Test**: Can be fully tested by assigning an unassigned ticket to an agent, updating status through open/pending/resolved, and confirming internal notes are visible to agents but not customers.

**Acceptance Scenarios**:

1. **Given** an unassigned ticket, **When** an agent assigns it to themselves, **Then** the ticket owner updates to that agent.
2. **Given** a ticket in progress, **When** an agent sets status to pending or resolved, **Then** the updated status is shown in inbox and ticket detail views.
3. **Given** a ticket conversation, **When** an agent adds an internal note, **Then** the note is saved in the ticket timeline and excluded from customer-facing messages.

---

### User Story 3 - Monitor Enterprise SLA Risk (Priority: P3)

A support manager and assigned agent can see SLA countdown and receive alerts before breach for enterprise account tickets.

**Why this priority**: SLA monitoring is contract-critical for enterprise customers but can be delivered after base inbox workflows are working.

**Independent Test**: Can be fully tested by creating two tickets (enterprise and non-enterprise), confirming SLA countdown and pre-breach alerts appear only on the enterprise ticket.

**Acceptance Scenarios**:

1. **Given** a ticket for an enterprise account, **When** the remaining SLA time reaches the alert threshold, **Then** an alert is shown to the assigned agent and support managers before breach.
2. **Given** a ticket for a non-enterprise account, **When** time passes, **Then** no SLA countdown or breach alert is displayed.

---

### Edge Cases

- What happens when two agents try to assign the same unassigned ticket at nearly the same time? The system should keep exactly one final assignee and show the latest assignment state to all viewers.
- How does system handle a reply send failure? The reply should remain unsent in the ticket with clear failure feedback and allow retry.
- What happens when an enterprise account is downgraded while tickets are open? Existing tickets retain their SLA behavior as of ticket creation unless account policy explicitly changes them.
- How does system handle very long email threads? Agents should still be able to view full history and clearly distinguish customer messages, agent replies, and internal notes.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST ingest incoming customer support emails and create or append to a corresponding ticket conversation visible in the support inbox.
- **FR-002**: System MUST provide agents a unified inbox view listing all incoming tickets with at least ticket subject, customer identity, current status, assignee, and most recent activity time.
- **FR-003**: Agents MUST be able to open a ticket and view the full conversation history, including incoming customer emails, agent replies, and internal notes.
- **FR-004**: Agents MUST be able to assign any unassigned or reassigned ticket to themselves.
- **FR-005**: Agents MUST be able to set ticket status to open, pending, or resolved.
- **FR-006**: Agents MUST be able to add internal notes to a ticket, and those notes MUST not be visible in customer communications.
- **FR-007**: Agents MUST be able to compose and send customer replies from within the same ticket view where they read the conversation.
- **FR-008**: System MUST record outbound replies in the related ticket conversation with send time and sender identity.
- **FR-009**: System MUST apply SLA tracking only to tickets associated with enterprise accounts.
- **FR-010**: For enterprise-account tickets, system MUST display remaining SLA time and signal when the ticket is at risk of breach before the breach occurs.
- **FR-011**: For non-enterprise tickets, system MUST not display SLA countdowns or pre-breach alerts.
- **FR-012**: System MUST make SLA risk alerts visible to the assigned agent and designated support managers.
- **FR-013**: System MUST ensure this feature is accessible through web interfaces for v1 and not require mobile app functionality.
- **FR-014**: System MUST maintain an auditable timeline per ticket of assignment changes, status changes, notes, inbound messages, and outbound replies.

### Key Entities _(include if feature involves data)_

- **Ticket**: A support work item tied to a customer conversation, including status, assignee, timestamps, and associated account tier.
- **Message**: A customer-visible communication item in a ticket, including inbound emails and outbound agent replies.
- **Internal Note**: A non-customer-visible note attached to a ticket for collaboration and handoff.
- **Account**: Customer account record with tier classification, including whether enterprise SLA policies apply.
- **SLA Policy**: Time target and alert threshold definition that determines pre-breach risk for eligible tickets.
- **SLA Alert**: A notification event triggered when an enterprise ticket approaches breach threshold.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 95% of new inbound support emails appear in the inbox as tickets within 1 minute of receipt during normal operating conditions.
- **SC-002**: In usability testing, at least 90% of agents can assign, update status, add an internal note, and send a reply on a ticket without guidance on first attempt.
- **SC-003**: 100% of enterprise-tier tickets display SLA countdown and generate a visible pre-breach alert before breach when thresholds are met.
- **SC-004**: 0% of non-enterprise tickets display enterprise SLA countdowns or pre-breach alerts.
- **SC-005**: At least 85% of support agents report that handling a ticket from intake to first reply is faster in the new inbox than in the previous workflow after two weeks of use.

## Assumptions

- v1 supports agent workflows only in web browsers; native mobile app workflows are out of scope.
- Customer identity and account tier (including enterprise designation) are already available from existing account records.
- Authentication and agent authorization already exist and can be reused for support staff access.
- Support managers are a pre-defined role that can receive SLA risk visibility alongside assigned agents.
- The business defines enterprise SLA targets and pre-breach thresholds outside this document.
