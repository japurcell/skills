---
name: official-sources
description: For framework- or library-specific code, verify against official docs, use the documented pattern for the detected version, and cite sources for non-trivial decisions.
---
# Official Sources

Use this skill for framework- or library-specific code when correctness, current patterns, and verifiable sources matter.

## Trigger

Use when:
- Writing, changing, reviewing, or upgrading framework-, library-, or SDK-specific code
- Creating boilerplate, starter code, or reusable patterns
- The user asks for documented, verified, or current best practice
- Recommended patterns may matter, such as routing, forms, auth, state, data fetching, config, or platform APIs
- The task names a framework, library, SDK, or versioned API

Do not use when:
- The task is framework-agnostic or version-independent
- The user explicitly prefers speed over verification

## Process

Follow: DETECT → FETCH → IMPLEMENT → CITE

### 1) DETECT

Identify the stack and exact versions from project files when available, such as:
- `package.json`
- `requirements.txt`, `pyproject.toml`
- `composer.json`
- `go.mod`
- `Cargo.toml`
- `Gemfile`
- `*.csproj`
- `Directory.Packages.props`

State the result explicitly.

If a relevant framework or library version is missing or unclear, ask the user. Do not guess.

### 2) FETCH

Fetch the specific official documentation page for the feature being implemented, not the docs homepage.

Rules:
- MUST use official docs as the primary source
- MUST NOT rely on memory alone
- MUST fetch web pages through a markdown converter when possible
- MUST NOT use third-party tutorials, Stack Overflow, or AI summaries as primary authority

Fetch priority:
1. `WebFetch("https://markdown.new/<target-url>")`
2. `WebFetch("https://r.jina.ai/<target-url>")` if needed
3. Raw `WebFetch("<target-url>")` only for JSON/API endpoints or authenticated pages
4. Use `gh` CLI when GitHub is the official source

Source priority:
1. Official docs
2. Official migration guides, changelogs, or official blog posts
3. Standards references, such as MDN or specifications
4. Compatibility references, such as caniuse or node.green

If official sources conflict, surface the conflict, cite both sources, and identify which guidance matches the detected version.

### 3) IMPLEMENT

Implement the documented pattern for the detected version.

Rules:
- Use documented API names and signatures
- Prefer the current recommended pattern
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

When useful, summarize work like this:

    STACK DETECTED:
    - ...

    OFFICIAL SOURCES:
    - ...

    IMPLEMENTATION NOTES:
    - ...

    UNVERIFIED:
    - none

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