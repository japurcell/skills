---
name: prd-create
description: Create a Product Requirements Document (PRD) from a feature or problem description and submit it as a GitHub issue. Use this whenever the user asks to create, draft, write, refine, or file a PRD/product requirements document; wants requirements gathered before implementation; or describes a feature/problem and asks for a product brief, requirements issue, or PRD-style GitHub issue, even if they do not explicitly say "PRD".
---

# PRD Create

Create a product requirements document that is grounded in the current codebase, current official references, and explicit user decisions. The output is a GitHub issue containing the PRD. Do not implement code while using this skill.

## Inputs

The user should provide a feature or problem description. Treat the text after the triggering request as the source description. If the description is empty or only says "create a PRD", ask for the feature or problem before doing any exploration.

Optional context may include:

- target repository or issue tracker
- product area, users, constraints, deadlines, or non-goals
- links to existing discussions, issues, designs, or docs

## Operating principles

- Prefer shared understanding over speed. A PRD that leaves material ambiguity unresolved creates downstream rework.
- Explore and research before making implementation or design decisions. Recommendations should be informed by actual code patterns and current authoritative references, not guesses.
- Ask the user one question at a time during the interview. Resolve parent decisions before asking dependent child decisions.
- For every implementation decision in the PRD, cite either an existing codebase pattern or a targeted research reference with a link and the reason it applies.
- Keep the PRD stable over time: do not include specific file paths or code snippets in the GitHub issue body.
- Do not begin implementation, create branches, edit application code, or open a PR.

## Workflow

### 1. Frame the request

Restate the feature or problem in one compact paragraph and identify:

- primary users and actors
- desired outcome
- likely product surface
- known constraints
- obvious non-goals
- unknowns that exploration might answer

If the request is too vague to direct exploration, ask one clarifying question first. Otherwise, proceed to codebase exploration.

### 2. Explore the codebase with parallel code-explorer subagents

Launch several `code-explorer` subagents in parallel. Use at least three when the repository is non-trivial or the requested feature touches multiple surfaces. Give each agent a distinct lens so their findings are complementary.

Recommended lenses:

1. Similar features and user flows.
2. Architecture boundaries, data flow, and extension points.
3. API contracts, persistence, schema, and integration patterns.
4. Tests, fixtures, accessibility, security, or operational constraints.

Each `code-explorer` prompt should include:

```text
We are creating a PRD, not implementing code.

Feature/problem description:
<paste the user's description>

Explore the repository for patterns relevant to this request. Focus on <lens>.

Return:
1. Key findings that materially affect requirements or implementation decisions.
2. Existing patterns/conventions to preserve, described without proposing code.
3. 5-10 key files with a one-sentence reason for each file.
4. Relevant tests or test patterns, if any.
5. Open questions or gaps that exploration could not answer.

Do not modify files.
```

After all explorers finish:

1. Merge their findings and de-duplicate repeated files or patterns.
2. Read the most important cited files yourself when a decision depends on a specific pattern.
3. Keep the file list as internal working context. Do not put specific file paths in the PRD issue body.
4. Convert concrete file findings into durable pattern citations, such as "the existing import workflow centralizes validation before persistence" rather than naming a file.

### 3. Identify gaps and build the decision tree

Create an internal decision tree from:

- user-provided requirements
- code-explorer findings
- unresolved questions from explorers
- product, UX, security, performance, accessibility, data, operational, rollout, and testing concerns

Classify each node:

- **Blocking**: the PRD would be misleading without the answer.
- **Decision-shaping**: the answer changes scope, UX, architecture, testing, rollout, or risk.
- **Documentable assumption**: a reasonable default exists and the decision does not materially change the PRD.
- **Out of scope**: explicitly excluded from this PRD.

Do not interview the user about questions that codebase exploration or official documentation can answer. Do interview the user about product intent, scope boundaries, trade-offs, and business priorities.

### 4. Perform targeted web research before decisions

Before recommending answers, selecting designs, or writing implementation decisions, launch several parallel research subagents. Use `general-purpose` subagents when available; otherwise perform the research inline with the available web tools.

Give each research subagent a narrow target, such as:

- official framework or library documentation for the relevant stack
- official API or platform docs
- official changelog or migration notes
- web standards, accessibility standards, security guidance, or privacy guidance
- official product or vendor blog posts that explain recommended patterns

Each research prompt should include:

```text
We are preparing a PRD, not implementing code.

Feature/problem description:
<paste the user's description>

Codebase context summary:
<paste only relevant patterns, not file paths>

Research target:
<specific framework, platform, standard, or best-practice question>

Find current authoritative guidance from official documentation, official blogs, changelogs, web standards, or vendor references. Prefer primary sources.

Return:
1. 3-7 findings that should affect PRD requirements, design constraints, or testing.
2. Links to the sources.
3. The date/version context when available.
4. Which implementation or testing decisions each source supports.
5. Risks, deprecations, accessibility/security concerns, or migration notes.
```

Use research to inform recommendations during the interview and citations in the PRD. If a source is not official but is still useful, label it as supplemental and do not use it as the sole citation for a major implementation decision.

### 5. Interview the user one question at a time

Interview relentlessly until there is shared understanding. Walk down the design tree by dependencies: ask about parent decisions first, then ask follow-up questions only after the parent answer is known.

For each question:

1. Ask exactly one question.
2. Explain why the answer matters.
3. Provide 2-4 concrete options when useful.
4. Provide your recommended answer and the reason for it.
5. Note which later decisions depend on the answer.
6. Wait for the user's response before asking the next question.

Use the available structured user-input tool when possible. A good question shape is:

```markdown
**Question:** Should <decision> be <recommended option>?

**Why it matters:** <scope, UX, architecture, compliance, or testing impact>

**Recommendation:** <recommended answer>, because <codebase pattern or research-backed reason>

**Options:**

1. <Option A> - <implications>
2. <Option B> - <implications>
3. <Option C> - <implications>
```

Continue until every blocking and decision-shaping question is answered. If the user explicitly accepts your recommendation for a branch, record that decision and continue to the next dependent question. If the user asks you to use your judgment, choose the recommendation, explain the assumption, and continue.

### 6. Write the PRD

Use this exact section order and headings:

```markdown
## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

1. As an <actor>, I want a <feature>, so that <benefit>

## Implementation Decisions

- <Decision>. Citation: <existing codebase pattern or research link>. Reason: <why this source supports the decision>.

## Testing Decisions

- <Decision>. Prior art: <existing test pattern or research link>. Reason: <why this is the right testing approach>.

## Out of Scope

<Excluded work and boundaries.>

## Further Notes

<Risks, rollout notes, dependencies, assumptions, or follow-up work.>
```

Section guidance:

- **Problem Statement**: Write from the user's perspective. Avoid implementation language.
- **Solution**: Describe the product outcome from the user's perspective.
- **User Stories**: Produce a long, numbered list. Cover primary flows, secondary flows, edge cases, permissions, error states, onboarding, migration, notifications, accessibility, privacy/security, admin/support needs, observability, and rollout where relevant.
- **Implementation Decisions**: Include modules, interfaces, architecture, schema, API contracts, integrations, data lifecycle, error handling, permissions, rollout, and operational decisions. Do not include specific file paths or code snippets. Every item must cite an existing codebase pattern or a targeted research source link, with the reason it was chosen.
- **Testing Decisions**: Start by stating that good tests verify external behavior and user-visible outcomes rather than implementation details. Include which modules or product surfaces should be tested and cite similar test patterns from the codebase when available. Do not include specific file paths.
- **Out of Scope**: Be explicit about excluded features, deferred integrations, unsupported user types, non-goals, and implementation work not covered by this PRD.
- **Further Notes**: Capture open risks, dependencies, rollout notes, assumptions accepted by the user, and research caveats.

### Citation rules

Use durable citations in the PRD:

- Good codebase citation: `Citation: Existing codebase pattern - account settings flows separate user-facing validation from persistence. Reason: this keeps requirements aligned with the product's current boundary between UI validation and data mutation.`
- Good research citation: `Citation: W3C WCAG guidance for form errors, <link>. Reason: the feature introduces user-correctable error states that should be perceivable and actionable.`
- Avoid: file paths, line numbers, copied code, or brittle implementation details that are likely to change.

### 7. Quality gate before filing

Review the PRD before creating the issue:

- The PRD follows the exact template and section order.
- The problem and solution are from the user's perspective.
- User stories are extensive and numbered.
- No specific file paths or code snippets appear in the issue body.
- Every implementation decision has a codebase-pattern citation or research citation with a reason.
- Testing decisions describe external behavior and cite prior art where available.
- Out-of-scope items are explicit.
- Blocking and decision-shaping questions are resolved or documented as user-approved assumptions.

If the quality gate fails, revise the PRD before filing. Do not file a knowingly incomplete PRD unless the user explicitly asks for a draft issue; in that case, label unresolved areas clearly in Further Notes.

### 8. Submit the PRD as a GitHub issue

Infer the repository from the current git remote unless the user provided a target repo. Create a GitHub issue with:

- Title: `PRD: <short feature name>`
- Body: the completed PRD

Use `gh issue create` with a temporary body file so markdown is preserved. If GitHub CLI authentication, permissions, or repository detection fails, do not discard the PRD. Report the failure and provide the exact command error plus the issue title and body so the user can file it manually.

After creating the issue, return:

- the issue URL
- the issue title
- any assumptions or follow-up notes from Further Notes that the user should remember

## Failure handling

- If subagents are unavailable, perform the exploration and research inline, but preserve the same evidence requirements and explain that the workflow ran without parallel subagents.
- If web access is unavailable, continue only with codebase evidence and user-approved assumptions; mark research-backed decisions as blocked rather than inventing citations.
- If the codebase is unavailable or the current directory is not a repository, skip codebase citations and rely on targeted research plus user interview, clearly noting that no repository patterns were available.
- If the user stops the interview early, create only a draft PRD if they explicitly ask for it; otherwise report the unresolved blocking questions.
