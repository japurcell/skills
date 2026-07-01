---
name: official-sources
description: Verify named framework/library/SDK/API code against official sources for the detected version; cite non-trivial decisions and avoid deprecated or undocumented APIs.
---

# Official Sources

Use when code or guidance depends on a named framework, library, SDK, platform, or versioned API.

## Rules

1. **Detect versions**
   - Check available project files such as `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, `composer.json`, `Gemfile`, `*.csproj`, lockfiles, or equivalent.
   - State the detected stack/version.
   - If the version is missing and materially affects the answer, ask the user. Do not silently guess.

2. **Use official sources**
   - Verify non-trivial framework/library/API decisions with official sources for the detected version.
   - Prefer docs that match the detected installed version. Do not apply latest-version guidance to older versions without noting the mismatch.
   - Prefer, in order:
     1. Official docs or official repository docs
     2. Official migration guides, changelogs, release notes, or blogs
     3. Standards docs, e.g. MDN/specs
     4. Compatibility references, e.g. caniuse
   - Do not use tutorials, Stack Overflow, or AI summaries as primary authority.

3. **Use available tools**
   - If web/search/fetch tools are available, fetch the specific official page for the API/pattern, not just the docs homepage.
   - If file access is available, reuse/save research in `.agents/scratchpad/official-sources-cache.json` keyed by stack, version, and topic.
   - Reuse cached research only when stack, version, and topic match. Otherwise re-verify.
   - If no web/fetch tools are available, or official docs cannot be found after reasonable effort, mark the point `UNVERIFIED`.

4. **Implement documented patterns**
   - Use documented names, signatures, and recommended patterns for the detected version.
   - Avoid deprecated or undocumented APIs.
   - If official docs conflict with existing code patterns, surface the conflict and ask whether to follow docs or existing project conventions.

5. **Cite decisions**
   - Cite full URLs for non-trivial framework/API choices, especially hooks, routing, forms, auth, config, migrations, deprecations, compatibility, or architecture.
   - If unverified, write: `UNVERIFIED: I could not find official documentation for this pattern.`

## Output, when useful

- `STACK DETECTED:` stack and versions
- `SOURCES:` URLs used
- `NOTES:` key documented choices
- `UNVERIFIED:` none, or list unverifiable points

## Final check

- Version detected or uncertainty stated
- Official source used for non-trivial API decisions
- Documented pattern implemented
- Deprecated/undocumented APIs avoided or flagged
- Sources cited where they affect the answer
