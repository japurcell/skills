---
name: official-sources
description: Use when code or guidance depends on a named framework, library, SDK, platform, or versioned API. Detect versions, verify non-trivial API choices with official sources, and cite them.
---

# Official Sources

## Use when

Answering or editing code/guidance involving a named framework, library, SDK, platform, or versioned API.

## Procedure

1. **Detect version.** Check available project files such as `package.json`, lockfiles, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, `composer.json`, `Gemfile`, `*.csproj`, etc. State detected stack/version.

2. **Ask if needed.** If version is missing and materially affects the answer, ask the user. Do not silently guess. If impact is minor, state assumptions.

3. **Verify non-trivial choices** against sources for the detected version. Prefer:
   1. Official docs or official repo docs
   2. Official migration guides, changelogs, release notes, or blogs
   3. Standards docs, e.g. MDN/specs
   4. Compatibility refs, e.g. caniuse

4. **Avoid weak sources.** Do not rely on tutorials, Stack Overflow, forums, or AI summaries as primary authority.

5. **Use tools efficiently.** If web/search/fetch tools are available:
   - Fetch the specific relevant page, not a docs homepage.
   - Prefer low-token text/markdown views when available and safe: `https://markdown.new/<target-url>`, `https://r.jina.ai/<target-url>`
   - Use 1–3 authoritative URLs per decision; stop once verified.
   - If Microsoft docs 301, retry the final versioned URL once, then stop.

6. **Implement documented patterns.** Use documented names, signatures, and recommended patterns. Avoid or flag deprecated, private, undocumented, or version-mismatched APIs.

7. **Handle conflicts.** If official docs conflict with existing project conventions, state the conflict and ask whether to follow docs or project convention.

8. **Mark gaps.** If official docs cannot be found or accessed, write: `UNVERIFIED: <point>`.

## Optional cache

If file access is available, reuse/save research in `.agents/scratchpad/official-sources-cache.json`, keyed by `stack + version + topic`. Reuse exact matches only.

## Output when useful

- `STACK DETECTED:` stack/version or uncertainty
- `SOURCES:` full URLs that affected decisions
- `NOTES:` key documented choices
- `UNVERIFIED:` none or list

## Final check

- Version detected or uncertainty stated
- Official sources used for non-trivial API decisions
- Deprecated/undocumented/version-mismatched APIs avoided or flagged
- Citations included only where they affect the answer
