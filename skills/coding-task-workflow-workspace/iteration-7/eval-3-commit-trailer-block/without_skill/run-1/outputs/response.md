# Commit message shape (general-knowledge answer)

> ⚠️ No skill is loaded in this session, so I cannot quote the exact format that the
> `coding-task-workflow` skill enforces. The structure below is what is conventionally
> expected for a workflow that tracks phased work items against a parent issue, and it
> matches the trailer rules called out in this repo's general guidance
> (`Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`). Treat the
> work‑item / phase trailer names as a reasonable convention — confirm them against the
> skill itself before relying on them in automation.

## General shape

Commits follow the **Conventional Commits** subject style, with a body that explains
*what* and *why*, and a trailer block at the very end that links the commit to the
parent issue, the work item, the phase, and any co-authors.

```
<type>(<optional scope>): <short, imperative summary ≤ 72 chars>

<Body paragraph(s) wrapped at ~72 chars. Explain what changed and why,
not how. Reference the phase goal and any decisions or trade-offs made
while implementing work item 2026-04-23-add-retry-mechanism.>

<Optional second paragraph: testing notes, follow-ups, risk callouts.>

Refs: #42
Work-Item: 2026-04-23-add-retry-mechanism
Phase: 11
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

### Concrete example for this work item

```
feat(retry): add exponential-backoff retry mechanism

Introduce a configurable retry wrapper for outbound calls so transient
failures are recovered automatically instead of bubbling up to callers.
Defaults to 3 attempts with jittered exponential backoff; callers can
override max attempts, base delay, and which error classes are retryable.

Tests cover success-on-first-try, success-after-retry, exhaustion, and
non-retryable error passthrough. No behavior change for callers that do
not opt in.

Refs: #42
Work-Item: 2026-04-23-add-retry-mechanism
Phase: 11
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## Required pieces

1. **Subject line**
   - Conventional Commits prefix: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, etc.
   - Optional scope in parentheses (e.g., `feat(retry):`).
   - Imperative mood, lowercase after the colon, no trailing period, ≤ 72 chars.

2. **Body** (blank line after subject)
   - Wrap at ~72 chars.
   - Explain *what* changed and *why*; mention the phase goal.
   - Note tests added/updated and any follow-ups or risks.

3. **Trailer block** (single blank line before it; one trailer per line; no blank
   lines *inside* the block — git only recognizes a contiguous trailer block at the
   very end of the message)

   Required trailers for this task:

   | Trailer            | Value for this task                                                          |
   | ------------------ | ---------------------------------------------------------------------------- |
   | `Refs:`            | `#42` (parent issue; use `Closes: #42` only if this commit fully closes it)  |
   | `Work-Item:`       | `2026-04-23-add-retry-mechanism`                                             |
   | `Phase:`           | `11`                                                                         |
   | `Co-authored-by:`  | `Copilot <223556219+Copilot@users.noreply.github.com>`                       |

## Trailer formatting rules

- Use `Token: value` form — capitalized token, single colon, single space, then value.
- Tokens are hyphenated, not spaced (`Work-Item`, not `Work Item`).
- Exactly **one trailer per line**; do not combine multiple trailers on one line.
- The trailer block must be the **last** block in the message and must be preceded by a
  single blank line. No blank lines or prose may appear *between* trailers.
- Use `Refs: #42` to link without closing the parent issue; use `Closes: #42` /
  `Fixes: #42` only when this commit actually resolves it. Phased work usually uses
  `Refs:` until the final phase.
- The `Co-authored-by:` trailer must use the exact GitHub no-reply address shown above
  so GitHub attributes the co-author correctly.
- Validate locally with `git interpret-trailers --parse` to confirm git recognizes the
  block.

## What I'm not certain about without the skill

- The exact trailer **token names** (`Work-Item`, `Phase`, `Refs`) — the workflow may
  use slightly different keys (e.g., `Issue:`, `Task:`, `Phase-Id:`).
- Whether the workflow requires **additional** trailers (e.g., `Reviewed-by`,
  `Signed-off-by`, a checklist link, or a phase-completion marker).
- Whether the subject line must embed the issue or work-item id.

Load the `coding-task-workflow` skill to confirm the exact tokens and any extra
required trailers before committing.
