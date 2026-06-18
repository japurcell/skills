---
name: official-sources
description: Verifies framework-, library-, SDK-, and versioned API work against official docs. Use whenever a task names a stack or version, asks for official/current/best-practice guidance, depends on documented framework behavior, or you fetch docs/web pages to confirm implementation details before coding, reviewing, debugging, or upgrading.
---

# Official Sources

## Overview

Use for named-stack work where memory, tutorials, or stale patterns are risky. Detect version, verify against official docs, implement documented pattern, cite non-trivial choices.

## When to Use

- Task names framework, library, SDK, platform API, or versioned dependency
- User wants official, current, verified, best-practice, or migration guidance
- Work is stack-specific: coding, review, debugging, upgrades, boilerplate, reusable patterns
- Decision depends on documented behavior such as routing, forms, auth, state, data fetching, config, platform APIs, or migrations
- You fetch docs or other web pages to verify implementation details
- Not for framework-agnostic, version-independent work
- If user explicitly accepts speed over verification, say guidance is unverified if you skip docs

## Workflow

1. **Detect stack and version.** Read relevant project files such as `package.json`, `requirements.txt`, `pyproject.toml`, `composer.json`, `go.mod`, `Cargo.toml`, `Gemfile`, `*.csproj`, and `Directory.Packages.props`. State exact version. If version is missing or unclear, explicitly ask user for exact version before recommending pattern. If they cannot provide it, stop at version status plus `UNVERIFIED`. Do not guess.
2. **Fetch official docs.** Read feature page, not docs homepage. Fetch priority: `markdown.new/<url>`; `r.jina.ai/http://<url>`; raw fetch for JSON, API, or auth-gated pages; `gh` when GitHub is official source. Official docs are primary. Official migration guides, changelogs, or blog posts are secondary. Standards refs such as MDN or specs, plus compatibility refs such as caniuse or node.green, support but do not replace official docs.
3. **Implement documented pattern.** Use documented API names and signatures, prefer recommended pattern for detected version, avoid deprecated APIs. If docs do not cover pattern, mark it `UNVERIFIED`. If docs and codebase disagree, surface choice between documented current pattern and existing codebase pattern instead of silently picking one. If multiple official patterns are valid but depend on missing repo context, do not choose from version alone; present explicit options and ask which context applies.
4. **Cite non-trivial decisions.** Cite deep links for API, architectural, migration, deprecation, and compatibility-sensitive choices. Quote briefly only when reason is not obvious.

## Specific Techniques

- If official sources conflict, cite both and explain which one matches detected version.
- If docs leave more than one valid path, write explicit options and name missing context that decides between them.
- When useful, format answer as:
  - `STACK DETECTED`
  - `OFFICIAL SOURCES`
  - `IMPLEMENTATION NOTES`
  - `UNVERIFIED`
- Use `UNVERIFIED: I could not find official documentation for this pattern.` when docs do not confirm pattern.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "I know this API already." | Versions drift. Check docs for version in repo. |
| "Docs homepage is enough." | Feature pages remove ambiguity and usually show current API. |
| "Tutorial/blog/AI summary is fine." | Third-party sources can help later, not as primary authority. |
| "Existing code already does it this way." | Surface doc/codebase conflict instead of inheriting stale pattern silently. |

## Red Flags

- Stack-specific guidance given without version detection
- Official docs skipped even though task depends on named framework or API behavior
- Deprecated or undocumented APIs recommended
- Third-party source treated as primary authority
- Non-trivial decision given without citation
- Missing-version case handled by guessing

## Verification

- [ ] Relevant stack and version detected or user asked to clarify
- [ ] Official feature docs fetched, with secondary sources only as support
- [ ] Recommended pattern matches detected version
- [ ] Non-trivial decisions cite official sources
- [ ] Conflicts and unverifiable parts surfaced explicitly
