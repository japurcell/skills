---
name: official-sources
description: Base framework-specific code on official documentation. Use when correctness, current best practices, and source-cited implementations matter.
---

# Official Sources

## Overview

For framework- or library-specific code, verify against official documentation before implementing. Do not rely on memory alone: APIs change, patterns are deprecated, and training data becomes stale. The goal is code the user can trust and verify.

## When to Use

Use this skill when:

- Writing framework- or library-specific code
- Creating boilerplate, starter code, or reusable patterns
- The user asks for documented, verified, or current implementation
- Implementing features where recommended patterns matter, such as forms, routing, data fetching, state, or auth
- Reviewing or updating framework-specific code
- You are about to write framework-specific code from memory

Do not use this skill when:

- The task is framework-agnostic and version-independent, such as renaming variables, fixing typos, moving files, or basic logic
- The user explicitly prefers speed over verification

## Process

Follow this sequence:

DETECT → FETCH → IMPLEMENT → CITE

### 1) Detect stack and versions

Read dependency files to identify the exact stack and versions.

Examples:

- `package.json` → Node, React, Vue, Angular, Svelte
- `composer.json` → PHP, Laravel, Symfony
- `requirements.txt`, `pyproject.toml` → Python, Django, Flask
- `go.mod` → Go
- `Cargo.toml` → Rust
- `Gemfile` → Ruby, Rails

State the result explicitly, for example:

```text
STACK DETECTED:
- React 19.1.0
- Vite 6.2.0
- Tailwind CSS 4.0.3
→ Fetching official docs for the relevant patterns.
```

If versions are missing or unclear, ask the user. Do not guess.

### 2) Fetch the relevant official documentation

Fetch the specific page for the feature being implemented, not the docs homepage.

Prefer sources in this order:

1. Official documentation
2. Official migration guides, changelogs, or official blog posts
3. Standards references, such as MDN or specifications
4. Compatibility references, such as caniuse or node.green

Do not use these as primary sources:

- Stack Overflow
- Third-party blog posts or tutorials
- AI-generated summaries
- Training-data memory

Be precise:

- Bad: React homepage
- Good: `https://react.dev/reference/react/useActionState`
- Bad: Search for “django auth best practices”
- Good: `https://docs.djangoproject.com/en/6.0/topics/auth/`

Extract the relevant pattern, including deprecations or migration guidance.

If official sources conflict, surface the conflict and verify which guidance applies to the detected version.

### 3) Implement using the documented pattern

Write code that matches the detected version’s documentation.

Rules:

- Use documented API names and signatures
- Prefer the current recommended pattern
- Avoid deprecated APIs
- If the docs do not cover a pattern, mark it as unverified

If the docs conflict with the existing codebase, do not silently choose. Surface the tradeoff:

```text
CONFLICT DETECTED:
The codebase uses useState for form loading state,
but React 19 docs recommend useActionState.
Source: https://react.dev/reference/react/useActionState

Options:
A) Use the current documented pattern
B) Match the existing codebase pattern
→ Which do you prefer?
```

### 4) Cite sources

Cite the source for each non-trivial framework-specific decision so the user can verify it.

Use:

- Full URLs
- Deep links when possible
- Short quotes for non-obvious decisions
- Compatibility references when recommending platform features

Example in code comments:

```ts
// React 19 form handling with useActionState
// Source: https://react.dev/reference/react/useActionState#usage
const [state, formAction, isPending] = useActionState(
  submitOrder,
  initialState,
);
```

Example in conversation:

```text
I used useActionState for form submission state because React 19 documents it for this pattern.
Source: https://react.dev/reference/react/useActionState
```

If you cannot verify something, say so clearly:

```text
UNVERIFIED: I could not find official documentation for this pattern.
This may be outdated and should be verified before production use.
```

## Red Flags

- Writing framework-specific code without checking the docs
- Not knowing the version
- Using undocumented or deprecated APIs
- Citing third-party sources as primary authority
- Delivering framework-specific code without citations
- Fetching broad docs when one specific page is sufficient
- Saying “I think” or “I believe” instead of citing a source

## Checklist

Before finalizing:

- [ ] Detected framework/library versions from dependency files or the user
- [ ] Fetched the relevant official documentation
- [ ] Used official sources as primary authority
- [ ] Followed current documented patterns for the detected version
- [ ] Cited non-trivial framework-specific decisions
- [ ] Checked for deprecations or migration guidance
- [ ] Surfaced conflicts between docs and the existing codebase
- [ ] Marked anything unverifiable as unverified
