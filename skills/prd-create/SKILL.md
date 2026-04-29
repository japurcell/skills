---
name: prd-create
description: Create a Product Requirements Document (PRD) from a feature or problem description and submit it as a GitHub issue. Use this whenever the user asks to create, draft, write, refine, or file a PRD/product requirements document; wants requirements gathered before implementation; or describes a feature/problem and asks for a product brief, requirements issue, or PRD-style GitHub issue, even if they do not explicitly say "PRD".
disable-model-invocation: true
---

# PRD Create

Create a PRD grounded in codebase evidence, current official guidance, and explicit user decisions. The deliverable is a GitHub issue containing the PRD. Do not implement code while using this skill.

## Inputs

The user should provide a feature or problem description. Treat the text after the triggering request as the source description. If the request is only "create a PRD", ask for the feature or problem before exploring.

Optional context:

- target repository or issue tracker
- product area, users, constraints, deadlines, or non-goals
- links to existing discussions, issues, designs, or docs

## Core rules

- Explore before deciding.
- Research before recommending.
- Ask the user only about product intent, scope, priorities, or trade-offs that tools cannot answer.
- Ask one question at a time, in dependency order.
- Surface assumptions before drafting.
- Keep the PRD durable: no file paths, code snippets, copied commands, or brittle directory maps in the issue body.
- Every implementation decision needs a durable codebase-pattern citation or official-source link plus a short reason.
- Do not implement code, create branches, edit application code, or open a PR.

## Execution checklist

1. Explore first and share an `Exploration summary` that explicitly includes `Key files`.
2. Surface assumptions before the first interview question.
3. Research unresolved framework, platform, accessibility, security, privacy, or migration decisions from authoritative sources.
4. Ask one question at a time in dependency order until blocking and decision-shaping items are resolved.
5. Write the PRD in the exact required section order with durable citations.
6. Return the GitHub issue result, or the title/body/command fallback if the issue is not actually created.

## Workflow

### 1. Frame the request

Restate the feature or problem in one short paragraph and identify the users, desired outcome, likely product surface, constraints, non-goals, and unknowns. If the request is too vague to direct exploration, ask one clarifying question first.

### 2. Explore the codebase

Use 2-4 parallel `code-explorer` subagents when available; otherwise explore inline. Give each a distinct lens such as:

1. Similar features and user flows.
2. Architecture boundaries and extension points.
3. APIs, persistence, schema, and integrations.
4. Tests, accessibility, security, or operational constraints.

Use this prompt shape for each explorer:

```text
We are creating a PRD, not implementing code.
Feature/problem: <user request>
Lens: <assigned lens>
Return exactly:
1. Findings that affect requirements or implementation decisions.
2. Existing patterns to preserve.
3. 5-10 key files with one-line reasons.
4. Relevant tests or test patterns.
5. Open questions or gaps.
```

Each exploration pass should return:

1. Findings that affect requirements or implementation decisions.
2. Existing patterns to preserve.
3. 5-10 key files with one-line reasons.
4. Relevant tests or test patterns.
5. Open questions or gaps.

Then:

1. Merge and deduplicate the findings.
2. Before asking the first interview question, share this exact `Exploration summary` with the user:

```markdown
# Exploration summary

## Key findings

## Patterns to preserve

## Key files

- <file> - <one-line reason>

## Relevant tests

## Open questions
```

3. In `Key files`, list the merged 5-10 files with one-line reasons; do not keep them implicit.
4. Keep that file list out of the PRD issue body. The no-file-path rule applies to the PRD, not to the `Exploration summary`.
5. Read the most important cited files yourself before relying on a pattern.
6. Turn file findings into durable citations such as "validation happens before persistence" instead of naming files.

### 3. Identify gaps and build the decision tree

Create an internal decision tree from user requirements, exploration findings, unresolved gaps, and product / UX / security / performance / accessibility / data / rollout / testing concerns. Classify each node:

- **Blocking**: the PRD would be misleading without the answer.
- **Decision-shaping**: the answer changes scope, UX, architecture, testing, rollout, or risk.
- **Documentable assumption**: a reasonable default exists and the decision does not materially change the PRD.
- **Out of scope**: explicitly excluded from this PRD.

Resolve anything that exploration or official docs can answer. Take only product intent, scope boundaries, trade-offs, and business priorities to the user.

Surface assumptions now in a short list:

```text
ASSUMPTIONS I'M MAKING:
1. This is a web application, not a native mobile app.
2. Authentication uses the product's existing auth model rather than introducing a new one.
3. We're drafting a PRD, not implementation tasks.
→ Correct me now or I'll proceed with these.
```

### 4. Perform targeted web research before decisions

Before recommending answers or writing implementation decisions, research unresolved framework, platform, accessibility, security, privacy, or migration questions. Use 2-3 targeted research subagents when available; otherwise use web tools inline.

Prefer official docs, official blogs or changelogs, standards, or vendor guidance. For each research thread, capture:

1. Findings that change requirements or testing.
2. Source links.
3. Version or date context when available.
4. Which decision each source supports.
5. Risks, deprecations, or constraints.

Each research prompt should include: the feature/problem description, the relevant codebase-pattern summary, the exact research target, and a request to return the five items above from authoritative sources.

If a non-official source is useful, label it supplemental and do not use it as the only support for a major decision.

### 5. Interview the user one question at a time

Walk the decision tree in order and ask the fewest questions that still make the PRD trustworthy. Continue until every blocking and decision-shaping item is resolved.

For each question:

1. Ask exactly one question.
2. Explain why the answer matters.
3. Provide 2-4 concrete options when useful.
4. Provide your recommended answer and why.
5. Note which later decisions depend on the answer.
6. Wait for the user's response before asking the next question.

Use the available structured user-input tool when possible. A good question shape is:

`Question: ...`
`Why it matters: ...`
`Options: 1. ... 2. ...`
`Recommendation: ...`
`Later decisions that depend on this: ...`

If the user says "use your judgment", adopt your recommendation and record it as an assumption. Do not silently fill in ambiguous requirements.

### 6. Write the PRD

The issue body should stay durable and decision-oriented. Do not include file paths, code snippets, copied commands, or brittle directory maps. If stack details, commands, or project structure materially affect scope, summarize them as stable requirements inside the sections below instead of adding extra sections.

Use this exact section order and headings:

```markdown
# PRD: [Project/Feature Name]

## Objective

[What we're building, who it serves, why it matters, and what success looks like.]

## User Stories

1. As an <actor>, I want a <feature>, so that <benefit>

## Implementation Decisions

- <Decision>. Citation: <existing codebase pattern or research link>. Reason: <why this source supports the decision>.

## Testing Decisions

- <Decision>. Prior art: <existing test pattern or research link>. Reason: <why this is the right testing approach>.

## Success Criteria

[How we'll know this is done — specific, testable conditions]

## Out of Scope

<Excluded work and boundaries.>

## Further Notes

<Risks, rollout notes, dependencies, assumptions, or follow-up work.>
```

Section requirements:

- **Objective**: the who, the why, and what success means.
- **User Stories**: a long numbered list covering primary flows, edge cases, permissions, error states, accessibility, privacy/security, admin/support, and rollout where relevant.
- **Implementation Decisions**: modules, interfaces, architecture, schema, APIs, integrations, data lifecycle, error handling, permissions, rollout, and operations. Every item must include `Citation:` and `Reason:`.
- **Testing Decisions**: start from observable behavior and user-visible outcomes, then cite prior art or research.
- **Success Criteria**: concrete, user-visible launch conditions.
- **Out of Scope**: explicit boundaries and deferred work.
- **Further Notes**: risks, dependencies, rollout notes, user-approved assumptions, and research caveats.

Citation rules:

- Good codebase citation: `Citation: Existing codebase pattern - validation happens before persistence. Reason: this preserves the current product boundary.`
- Good research citation: `Citation: WCAG form-error guidance, <link>. Reason: the feature introduces user-correctable errors.`
- Avoid file paths, line numbers, copied code, and brittle implementation detail.

### 7. Quality gate before filing

Review the PRD before creating the issue:

- A visible exploration summary exists and includes the `Key files` list outside the PRD body.
- The PRD follows the exact template and section order.
- The objective contains the why, the who, and what success looks like.
- User stories are extensive and numbered.
- No specific file paths or code snippets appear in the issue body.
- Every implementation decision has a codebase-pattern citation or research citation with a reason.
- Testing decisions describe external behavior and cite prior art where available.
- Success criteria are specific, user-visible, and testable.
- Out-of-scope items are explicit.
- Blocking and decision-shaping questions are resolved or documented as user-approved assumptions.

If the quality gate fails, revise the PRD before filing. Do not file a knowingly incomplete PRD unless the user explicitly asks for a draft issue; in that case, label unresolved areas clearly in Further Notes.

### 8. Submit the PRD as a GitHub issue

Infer the repository from the current git remote unless the user provided a target repo. Create a GitHub issue with:

- Title: `PRD: <short feature name>`
- Body: the completed PRD

Use `gh issue create` with a temporary body file so markdown is preserved. If the issue is not actually created for any reason, including offline mode, benchmark mode, auth failure, permissions, or repository detection problems, do not discard the PRD. Report the exact command error when available and provide the issue title, issue body, and the intended `gh issue create` command so the user can file it manually.

After creating the issue, return:

- the issue URL
- the issue title
- the exact `gh issue create` command used
- any assumptions or follow-up notes from Further Notes that the user should remember

## Failure handling

- If subagents are unavailable, perform the exploration and research inline, but preserve the same evidence requirements.
- If web access is unavailable, continue only with codebase evidence and user-approved assumptions; mark research-backed decisions as blocked rather than inventing citations.
- If the codebase is unavailable or the current directory is not a repository, skip codebase citations and rely on targeted research plus user interview, clearly noting that no repository patterns were available.
- If the user stops the interview early, create only a draft PRD if they explicitly ask for it; otherwise report the unresolved blocking questions.
