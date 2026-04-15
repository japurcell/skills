# Feature Specification: Support Inbox SLA

**Created**: 2026-03-26  
**Status**: Draft  
**Input**: User description: "We need a customer support inbox for our B2B SaaS. Agents should see all incoming emails, assign tickets to themselves, set status (open/pending/resolved), add internal notes, and reply to customers from the same view. We also need SLA tracking with alerts before breach, but only for enterprise accounts. Keep v1 web-only."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Triage Incoming Support Email (Priority: P1)

A support agent opens a unified inbox, reviews incoming customer emails as tickets, assigns a ticket to themselves, and updates ticket status so work is actively managed.

**Why this priority**: This is the core operational flow required to process customer requests and prevent unowned or stalled tickets.

**Independent Test**: Can be fully tested by receiving new emails into the inbox, assigning one ticket to an agent, and moving it through open and pending statuses while confirming visibility of ownership and status in the same view.

**Acceptance Scenarios**:

1. **Given** a new inbound customer email exists, **When** an agent opens the inbox, **Then** the email appears as a new support ticket with default status open.
2. **Given** an unassigned ticket, **When** an agent assigns the ticket to themselves, **Then** the ticket shows that agent as the current owner.
3. **Given** an assigned open ticket, **When** the agent changes status to pending, **Then** the ticket status updates immediately and remains visible in the ticket view.

---

### User Story 2 - Collaborate Internally And Respond Externally (Priority: P2)

A support agent reviews full conversation context, adds internal notes for teammates, and sends a customer reply from the same ticket view.

**Why this priority**: Efficient resolution requires internal collaboration and direct customer communication without switching tools.

**Independent Test**: Can be fully tested by opening an existing ticket, posting an internal note, sending a customer reply, and verifying both actions are recorded correctly with clear visibility boundaries.

**Acceptance Scenarios**:

1. **Given** an existing ticket, **When** an agent adds an internal note, **Then** the note is stored with author and timestamp and is visible to support agents only.
2. **Given** an existing ticket, **When** an agent sends a reply from the ticket view, **Then** the reply is added to the conversation thread and marked as customer-visible.
3. **Given** a ticket with notes and replies, **When** another authorized agent opens it, **Then** they can view complete internal and external history in chronological order.

---

### User Story 3 - Monitor Enterprise SLA Risk (Priority: P3)

A support lead or agent identifies enterprise-account tickets that are approaching SLA breach and receives warning alerts in time to act before breach.

**Why this priority**: SLA compliance for enterprise customers is a contractual and retention-critical requirement.

**Independent Test**: Can be fully tested by creating enterprise and non-enterprise tickets, simulating elapsed response/resolution time, and verifying alerts trigger only for enterprise tickets before breach thresholds.

**Acceptance Scenarios**:

1. **Given** an enterprise ticket with active SLA policy, **When** remaining SLA time crosses the alert threshold, **Then** the system flags the ticket as at-risk before breach.
2. **Given** a non-enterprise ticket, **When** response time approaches equivalent threshold windows, **Then** no SLA alert is generated.
3. **Given** an enterprise ticket that has breached SLA, **When** an agent views the ticket, **Then** the ticket is clearly marked as breached.

---

### Edge Cases

- What happens when multiple agents attempt to assign the same unassigned ticket at nearly the same time?
- How does system handle an inbound email that lacks a recognizable sender or has malformed metadata?
- What happens when an agent attempts to send a reply while ticket status is resolved?
- How does system handle enterprise account changes after ticket creation (for example, account downgraded before breach)?
- What happens when a large volume of inbound emails arrives in a short period and queue ownership is not yet set?

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST present all incoming customer support emails in a web-based shared inbox as individual tickets.
- **FR-002**: System MUST create new tickets from inbound emails with default status set to open.
- **FR-003**: System MUST allow an agent to assign an unassigned ticket to themselves.
- **FR-004**: System MUST allow agents to update ticket status to open, pending, or resolved.
- **FR-005**: System MUST display current ticket owner and current status within the ticket view and inbox listing.
- **FR-006**: System MUST allow agents to add internal notes to a ticket that are visible to internal support users only.
- **FR-007**: System MUST allow agents to send customer replies from the same ticket view where assignment, status, and notes are managed.
- **FR-008**: System MUST keep a chronological history of inbound messages, outbound replies, status changes, assignment changes, and internal notes for each ticket.
- **FR-009**: System MUST apply SLA tracking only to tickets associated with enterprise accounts.
- **FR-010**: System MUST generate a pre-breach SLA alert for enterprise tickets when remaining time reaches a configured warning threshold.
- **FR-011**: System MUST visibly mark enterprise tickets that have breached SLA.
- **FR-012**: System MUST NOT generate SLA alerts for non-enterprise tickets.
- **FR-013**: System MUST restrict v1 access to web users and exclude mobile-specific workflows from scope.

### Key Entities _(include if feature involves data)_

- **Ticket**: A support work item created from inbound email, including subject, customer identity, current status, current owner, timestamps, and account tier.
- **Message**: A conversation entry linked to a ticket, representing inbound customer email or outbound agent reply, with sender type, content, and timestamp.
- **Internal Note**: A non-customer-visible annotation on a ticket, including author, note content, and timestamp.
- **Assignment Event**: A record of ticket ownership change, including previous owner, new owner, actor, and timestamp.
- **Status Event**: A record of ticket status transition, including previous status, new status, actor, and timestamp.
- **SLA Policy**: Enterprise-specific timing rules and warning thresholds used to determine at-risk and breached ticket states.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 95% of new inbound support emails appear as tickets in the shared inbox within 1 minute of receipt during normal operating conditions.
- **SC-002**: 90% of sampled support agents can assign and set status on a ticket in under 30 seconds from opening the ticket view.
- **SC-003**: 95% of customer replies sent by agents are completed from the same ticket view without requiring navigation to a separate communication page.
- **SC-004**: 100% of SLA alerts in validation samples are generated only for enterprise tickets and 0% are generated for non-enterprise tickets.
- **SC-005**: For enterprise tickets that reach warning thresholds, 95% receive a visible pre-breach alert before SLA breach in test scenarios.
- **SC-006**: 90% of support users in UAT confirm they can understand ticket state and next action from a single ticket screen.

## Assumptions

- Existing account records already identify whether a customer is enterprise or non-enterprise.
- Support agents who use the inbox are authenticated internal users with permission to view tickets and internal notes.
- The product already has an outbound email capability that can send customer-visible replies from support workflows.
- v1 scope is web-only and excludes native mobile apps and mobile-specific interaction requirements.
- SLA timing definitions and warning thresholds for enterprise accounts are preconfigured by business operations.
