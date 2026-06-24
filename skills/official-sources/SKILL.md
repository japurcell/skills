---
name: official-sources
description: Use for framework-, library-, SDK-, or versioned API work when correctness and current documented patterns matter. Use whenever code depends on a named framework/library/version, or whenever any web page is fetched/webfetched/WebFetch’d to verify implementation details. Verify against official docs for the detected version, implement the documented pattern, and cite sources for non-trivial decisions.
---

# Official Sources

Use this skill for framework-, library-, SDK-, or versioned API code when correctness, current patterns, and verifiable sources matter.

## Use when

- Writing, changing, reviewing, debugging, or upgrading framework-, library-, or SDK-specific code
- Creating boilerplate, starter code, or reusable patterns for a named stack
- The user asks for documented, verified, official, or current best practice
- Recommended patterns may matter, such as routing, forms, auth, state, data fetching, config, platform APIs, or migrations
- The task names a framework, library, SDK, or versioned API
- You fetch, webfetch, or WebFetch any web page to verify implementation details

## Do not use when

- The task is truly framework-agnostic and version-independent
- The user explicitly prefers speed over verification and accepts unverified guidance

## Process

Follow: DETECT → FETCH → IMPLEMENT → CITE

### 1) DETECT

Identify the stack and exact versions from project files when available, for example:

- `package.json`
- `requirements.txt`, `pyproject.toml`
- `composer.json`
- `go.mod`
- `Cargo.toml`
- `Gemfile`
- `*.csproj`
- `Directory.Packages.props`

State the detected stack and versions explicitly. If a relevant version is missing or unclear, ask the user. Do not guess.

Reuse rule:

- If stack, version, and requested API surface are unchanged from prior verified work in the same task/session, reuse those official-source findings and citations.
- If framework, version, or requested API surface changed, rerun DETECT and FETCH before making claims.

### 2) FETCH

Fetch the specific official documentation page for the feature being implemented, not the docs homepage.

Rules:

- MUST use official docs as the primary source
- MUST NOT rely on memory alone
- Prefer fetching pages through a markdown converter when possible
- MUST NOT use third-party tutorials, Stack Overflow, or AI summaries as primary authority
- For new verification work, fetch official docs again (do not skip source verification).
- Stop URL guessing after two failed official deep-link URL variants for the same target page.
- After two failed variants, switch to an official docs index/search page; if still unresolved, mark the guidance `UNVERIFIED`.

Fetch priority:

1. `WebFetch("https://markdown.new/<target-url>")`
2. `WebFetch("https://r.jina.ai/http://<target-url>")` or `WebFetch("https://r.jina.ai/http://<full-url>")` if needed
3. Raw `WebFetch("<target-url>")` only for JSON/API endpoints or authenticated pages
4. Use `gh` CLI when GitHub is the official source

Source priority:

1. Official docs
2. Official migration guides, changelogs, or official blog posts
3. Standards references, such as MDN or specifications
4. Compatibility references, such as caniuse or node.green

If official sources conflict, surface the conflict, cite both, and identify which guidance matches the detected version.

### 3) IMPLEMENT

Implement the documented pattern for the detected version.

Rules:

- Use documented API names and signatures
- Prefer the current recommended pattern for that version
- Avoid deprecated APIs
- If docs do not cover the pattern, mark it `UNVERIFIED`

If docs conflict with the existing codebase, do not silently choose. Surface the conflict and ask whether to follow:

- the documented current pattern, or
- the existing codebase pattern

### 4) CITE

Cite sources for non-trivial framework-specific decisions, especially:

- API or hook choice
- Architectural or pattern choice
- Deprecation or migration decisions
- Compatibility-sensitive features

Use full URLs and deep links when possible. Include a short quote only when the reason is non-obvious.

If something cannot be verified, say:
`UNVERIFIED: I could not find official documentation for this pattern.`

## Output pattern

When useful, summarize:
STACK DETECTED: - ...
OFFICIAL SOURCES: - ...
IMPLEMENTATION NOTES: - ...
UNVERIFIED: - none

## Red flags

- Framework-specific code written without checking docs
- Unknown version treated as known
- Deprecated or undocumented APIs used
- Third-party sources treated as primary
- Non-trivial decisions given without citations

## Final check

- [ ] Versions detected or explicitly requested
- [ ] Relevant official docs fetched
- [ ] Documented pattern used for that version
- [ ] Non-trivial decisions cited
- [ ] Conflicts or unverifiable parts surfaced clearly
