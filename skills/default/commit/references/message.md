# Commit message

## First line

Use Conventional Commit format:

```text
<type>: <subject>
```

or:

```text
<type>(<scope>): <subject>
```

Rules:

- Subject is imperative.
- Max 72 characters.
- No trailing period.

## Type

Choose the first matching type:

1. `docs`
2. `test`
3. `fix`
4. `feat`
5. `refactor`
6. `perf`
7. `chore`

Use `fix` only for bug fixes.

## Subject fallback

If no better subject is clear:

1. `update <file-basename>`
2. `update <directory>`
3. `update changed files`

## Body format

```text
<type>(<scope>): <subject>

Summary:
- <what changed>

Rationale:
- <why>

Tests:
- <command or "not run (reason)">

Session: <optional session note>
Refs #123
Fixes #456
Co-authored-by: <name> <email>
```

Rules:

- Keep one blank line after the subject.
- `Summary`, `Rationale`, and `Tests` are required.
- Each required section needs at least one bullet.
- Omit `Session:` if no reliable session data exists.
- Use `Fixes` only when the user explicitly intends this commit to close that specific issue; otherwise use `Refs`.
- Keep issue and co-author trailers contiguous, without blank lines between them.
- Add one `Co-authored-by` trailer for each resolved contributor. Resolve identity before drafting: explicit user instruction (including opt-out or identity), then documented repository policy, then verified agent defaults. Pass each emitted identity once to the validator's repeatable `--co-author` option. Preserve other established contributors and deduplicate identical identities. Do not infer contribution merely from running Git, guess unknown identities, or map unknown agents to Codex. If a contributing agent's identity cannot be verified, stop and report the blocker. User instructions override conflicting repository policy; repository policy overrides defaults. No current-agent contribution suppresses only that agent's automatic default. An applicable opt-out or policy may exclude attribution; omit options and trailers when the resolved set is empty.

## Contributor attribution

Use the verified default for each contributing agent unless user instructions or documented repository rules resolve attribution differently:

```text
Co-authored-by: Codex <noreply@openai.com>
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

The Codex CLI identity is verified in the official [OpenAI Codex source](https://github.com/openai/codex/blob/main/codex-rs/git-utils/src/baseline.rs), which uses the exact name and address in its baseline commit metadata. This is a default for Codex CLI, not every OpenAI product or host. Prefer a verified identity supplied by the active host when available; otherwise use this Codex identity. Never substitute one agent's identity for another.

The Copilot CLI identity was verified in an actual Copilot CLI 1.0.109 commit and appears in the official [Copilot CLI repository's attribution implementation discussion](https://github.com/github/copilot-cli/issues/975). GitHub's [Copilot CLI configuration reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) documents the `includeCoAuthoredBy` setting that controls automatic attribution. This is a default for Copilot CLI, not every GitHub product or host. Prefer a verified identity supplied by the active host when available; otherwise use this Copilot identity. Never substitute Codex's identity for Copilot or map an unknown agent to either one.

Pass `--co-author 'Name <email>'` once for every matching trailer. The validator requires every supplied identity exactly once and rejects unlisted trailers. With no `--co-author` options, no attribution is required.
