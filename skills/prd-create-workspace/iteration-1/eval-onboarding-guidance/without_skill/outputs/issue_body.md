## Summary

Create a guided onboarding experience that appears when a new workspace is created and helps the user complete the first meaningful setup steps: inviting teammates, connecting integrations, and completing one useful workspace-specific setup action.

## Problem

New workspaces can feel empty and ambiguous immediately after creation. Users may not know which setup steps matter most, and teams can fail to reach the first collaborative or operational moment quickly. Without guidance, users may defer key actions such as inviting teammates or connecting tools, reducing activation and long-term retention.

## Goals

- Guide workspace creators through the highest-value setup steps immediately after workspace creation.
- Increase the percentage of new workspaces that invite at least one teammate.
- Increase the percentage of new workspaces that connect at least one integration.
- Help users complete a first useful setup action that demonstrates product value.
- Make onboarding resumable so users can leave and return without losing progress.

## Non-goals

- Rebuilding the entire workspace creation flow.
- Implementing a full lifecycle marketing or email onboarding program.
- Forcing every user to complete all setup steps before accessing the product.
- Designing every possible integration-specific configuration flow in this first release.

## Target users

- Workspace creators setting up a workspace for a team.
- Admins or owners responsible for initial workspace configuration.
- Small-team users who need a lightweight path from empty workspace to usable workspace.

## User story

As a workspace creator, I want clear guidance after creating a workspace so that I can invite teammates, connect the tools my team uses, and complete the first setup action that makes the workspace useful.

## Proposed experience

After a workspace is created, show a guided onboarding checklist or setup panel with three primary steps:

1. **Invite teammates**
   - Prompt the user to invite one or more teammates by email or shareable invite link.
   - Explain why collaboration improves the workspace experience.
   - Mark the step complete when an invite is sent or a teammate joins.

2. **Connect integrations**
   - Present a short list of recommended integrations relevant to the workspace type or common usage patterns.
   - Allow users to connect an integration or skip for now.
   - Mark the step complete when at least one integration is connected.

3. **Complete first useful setup action**
   - Guide the user to perform one concrete action that creates immediate value.
   - The exact action should be configurable by product area; examples might include creating the first project, importing data, configuring a workflow, creating a document, or adding a first task.
   - Mark the step complete when the action succeeds.

The onboarding should remain visible but non-blocking until completed or dismissed. Users should be able to skip individual steps, and skipped steps should be recoverable from a setup checklist or workspace settings area.

## Functional requirements

- When a new workspace is created, the creator sees the onboarding guidance on first arrival in the workspace.
- The guidance includes steps for inviting teammates, connecting integrations, and completing the first useful setup action.
- Each step has a clear call to action, completion state, and optional skip/dismiss behavior.
- Progress is persisted per workspace and user where appropriate.
- Completed steps remain completed across page reloads and sessions.
- The onboarding can be dismissed without blocking access to the workspace.
- Users can reopen or resume onboarding from a discoverable location.
- The integration step supports at least one available integration entry point in the initial release.
- The first useful setup action is instrumented as a configurable product action rather than hard-coded copy only.
- Empty, loading, error, permission-denied, and already-completed states are handled gracefully.

## UX requirements

- Use concise, action-oriented copy.
- Show visible progress, such as completed step count or checkmarks.
- Avoid modal-only blocking unless needed for a specific sub-flow.
- Make skipping or dismissing possible but less prominent than completing the next best action.
- Adapt content for users without permission to invite teammates or manage integrations.
- Provide accessible labels, focus states, and keyboard navigation for all controls.

## Analytics and success metrics

Track events for:

- Onboarding shown after workspace creation.
- Each step started.
- Each step completed.
- Each step skipped.
- Onboarding dismissed.
- Onboarding fully completed.
- Time from workspace creation to first teammate invite.
- Time from workspace creation to first integration connection.
- Time from workspace creation to first useful setup action.

Primary success metrics:

- Increase activation rate for new workspaces.
- Increase percentage of new workspaces with at least one teammate invited within 24 hours.
- Increase percentage of new workspaces with at least one integration connected within 24 hours.
- Increase percentage of new workspaces completing the first useful setup action within 24 hours.

## Acceptance criteria

- Given a user creates a workspace, when they land in the new workspace, then they see guided onboarding with the three setup steps.
- Given a user sends a teammate invite, when the invite succeeds, then the invite step is marked complete.
- Given a user connects an integration, when the connection succeeds, then the integration step is marked complete.
- Given a user completes the configured first useful setup action, when the action succeeds, then that step is marked complete.
- Given a user reloads the workspace, when onboarding progress already exists, then completed and skipped states are preserved.
- Given a user dismisses onboarding, when they continue using the workspace, then access is not blocked and the onboarding can be reopened.
- Given a user lacks permission for a step, when they view onboarding, then they see an appropriate disabled or alternate state.
- Given an onboarding event occurs, when analytics are inspected, then the event includes workspace id, user id, step id, action, and timestamp where permitted by privacy policy.

## Open questions

- What is the product-specific "first useful setup action" for the initial release?
- Should onboarding progress be tracked per user, per workspace, or both?
- Which integrations should be recommended first, and should recommendations depend on workspace type?
- Where should dismissed onboarding be reopened from?
- What permissions are required for inviting teammates and managing integrations?
- Should skipped steps count toward completion, or remain available as incomplete recommendations?

## Rollout plan

1. Ship behind a feature flag for newly created workspaces only.
2. Validate analytics instrumentation in internal or beta workspaces.
3. Run an A/B test or staged rollout comparing activation metrics against the existing experience.
4. Iterate on copy, ordering, and recommended integrations based on completion/drop-off data.
5. Expand to additional workspace types and more contextual setup actions.

## Risks and mitigations

- **Risk:** Onboarding feels intrusive.
  - **Mitigation:** Keep it non-blocking, dismissible, and resumable.
- **Risk:** Users lack permission for recommended actions.
  - **Mitigation:** Detect permissions and provide alternate guidance.
- **Risk:** Integration setup is too complex for onboarding.
  - **Mitigation:** Start with a small number of high-confidence integrations and link to full setup flows.
- **Risk:** The first useful action is not universally relevant.
  - **Mitigation:** Make the action configurable by workspace type or product surface.
