# Interview Log

This benchmark could not pause for live stakeholder answers, so the interview was simulated exactly as the skill requires: **one question at a time**, each with why it matters, options, a recommendation, and an assumed accepted answer before moving to dependent questions.

## 1. Overall onboarding pattern

**Question:** Should the post-creation experience be a non-blocking, dismissible, resumable onboarding checklist instead of a mandatory wizard?

**Why it matters:** This is the parent decision for UX, persistence, accessibility, and analytics. Every later question depends on whether setup is flexible or strictly linear.

**Options:**
1. Non-blocking checklist — users can act in flexible order and return later.
2. Mandatory wizard — forces exposure but adds friction and delays product use.
3. Passive empty-state tips — lowest friction but much weaker guidance and measurability.

**Recommendation:** Choose a non-blocking checklist, because official task-list guidance is a better fit for multi-session, flexible-order tasks than a rigid wizard.

**Assumed accepted answer:** Use a non-blocking, dismissible, resumable checklist.

**Dependent decisions unlocked:** progress model, skip/dismiss behavior, persistence, measurement.

## 2. Primary actor and role model

**Question:** Should the initial experience target the workspace creator as the primary actor, while showing permission-aware states for members who cannot invite teammates or connect integrations?

**Why it matters:** Invite and integration actions usually cross permission boundaries, so the primary actor determines what actions are enabled and what fallback guidance is needed.

**Options:**
1. Workspace creator/owner first — simplest and most activation-focused.
2. All members equally — broader but requires many role branches.
3. Enterprise admins only — secure but too narrow for general onboarding.

**Recommendation:** Target the workspace creator first, with role-aware states for lower-permission users.

**Assumed accepted answer:** Primary actor is the workspace creator; permission-aware alternatives are required for other roles.

**Dependent decisions unlocked:** invite behavior, integration CTA behavior, analytics segmentation.

## 3. Core scope

**Question:** Should v1 keep exactly the three requested outcomes—invite teammates, connect one existing integration, and complete one first useful setup action—as the full scope of onboarding?

**Why it matters:** This is the scope boundary question. It prevents spillover into billing, SSO, profile setup, education campaigns, or a broader setup center.

**Options:**
1. Keep exactly the three requested outcomes.
2. Expand to broader workspace setup such as billing/security/profile tasks.
3. Reduce to only one or two tasks.

**Recommendation:** Keep exactly the three requested outcomes in v1.

**Assumed accepted answer:** Scope is limited to those three outcomes.

**Dependent decisions unlocked:** completion definition, user stories, out-of-scope section.

## 4. First useful setup action definition

**Question:** Should the “first useful setup action” be defined as a configurable, product-specific activation event rather than hard-coded in this PRD?

**Why it matters:** The target app is unknown, so a hard-coded action would be invented rather than evidenced.

**Options:**
1. Configurable product-defined activation action.
2. Hard-code a generic action such as “create first project.”
3. Treat invite or integration as the first useful action.

**Recommendation:** Make it configurable and require product/engineering to map it to the real activation event before implementation.

**Assumed accepted answer:** The first useful action is configurable and uses the product’s real primary workflow.

**Dependent decisions unlocked:** success criteria, completion logic, analytics taxonomy.

## 5. Completion semantics

**Question:** Should onboarding count as complete only when all three primary outcomes are completed, while skipped tasks remain recoverable rather than silently counted as success?

**Why it matters:** This determines activation measurement, reminder behavior, and whether “completion” actually means the workspace is ready.

**Options:**
1. Complete only when all three outcomes are done.
2. Count skipped tasks as complete.
3. Count onboarding as complete after any one task.

**Recommendation:** Count onboarding complete only after all three outcomes are done; keep skipped tasks recoverable.

**Assumed accepted answer:** Completion requires all three outcomes; skips are remembered but not counted as success.

**Dependent decisions unlocked:** status labels, metrics, resume behavior.

## 6. Integration scope

**Question:** Should the integration step surface only already-supported integrations in v1 instead of adding new providers for onboarding?

**Why it matters:** Adding providers materially changes product, security, support, and implementation scope.

**Options:**
1. Reuse existing supported integrations only.
2. Add one new provider specifically for onboarding.
3. Show placeholder integrations and defer connection later.

**Recommendation:** Reuse existing supported integrations only.

**Assumed accepted answer:** v1 only surfaces real, already-supported integrations.

**Dependent decisions unlocked:** OAuth requirements, out-of-scope boundaries, rollout risk.

## 7. Shared vs. personal state

**Question:** Should task completion be stored at the workspace level, while dismissal and reminder preferences stay user-specific?

**Why it matters:** Invite and integration completion are shared workspace facts, but hiding guidance is a personal UX choice.

**Options:**
1. Workspace-level completion + user-level dismissal.
2. Per-user state for everything.
3. Workspace-level state for everything.

**Recommendation:** Use workspace-level completion with user-level dismissal/reopen preferences.

**Assumed accepted answer:** Shared setup progress is workspace-scoped; dismiss/reopen is user-scoped.

**Dependent decisions unlocked:** persistence requirements, testing matrix, reopen behavior.

## 8. Permission handling

**Question:** Should users who lack invite or integration permissions see disabled or alternate guidance instead of having those tasks hidden?

**Why it matters:** Hidden tasks make progress confusing, while enabled unauthorized actions create failure loops and security risk.

**Options:**
1. Show the task with a disabled or alternate state and explanatory text.
2. Hide unauthorized tasks completely.
3. Let the user attempt the action and fail server-side.

**Recommendation:** Show permission-aware alternate states with clear next actions.

**Assumed accepted answer:** Unauthorized users see explanatory disabled/alternate states.

**Dependent decisions unlocked:** accessible messaging, support stories, authz tests.

## 9. Analytics privacy

**Question:** Should onboarding be instrumented with privacy-safe events such as shown, started, completed, skipped, dismissed, reopened, and fully completed, without raw emails, tokens, or secrets?

**Why it matters:** The product needs activation measurement, but invite and integration flows expose potentially sensitive values.

**Options:**
1. Privacy-safe event taxonomy with bounded parameters.
2. Rich payloads including raw invite or integration values.
3. No onboarding analytics in v1.

**Recommendation:** Use privacy-safe events only.

**Assumed accepted answer:** Analytics are required, but payloads must exclude PII and secrets.

**Dependent decisions unlocked:** success metrics, privacy constraints, event-testing requirements.

## 10. Rollout strategy

**Question:** Should the feature launch behind rollout control for newly created workspaces first rather than changing onboarding for every workspace immediately?

**Why it matters:** First-run experience changes are high-impact and should be measured carefully before broad exposure.

**Options:**
1. Feature-flagged rollout for new workspaces first.
2. Immediate rollout to all workspaces.
3. Existing-workspace-only rollout.

**Recommendation:** Use rollout control for new workspaces first.

**Assumed accepted answer:** Launch behind feature-flag or equivalent control for newly created workspaces.

**Dependent decisions unlocked:** rollout metrics, support monitoring, out-of-scope migration work.
