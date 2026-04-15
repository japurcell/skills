# AGENTS.md Refresh — Results

## Phase 0: Discovery

- **Files found**: 1 (`./AGENTS.md`, 13 lines)
- **Contradictions**: None
- **Structural refactor needed**: No — file is short, well-organized, and user requested learnings only

## Phase 1: New Learnings

Two learnings added to the **Build & Test** section of `./AGENTS.md`:

### Target: ./AGENTS.md

```diff
- - `cargo clippy` — lint
+ - `cargo clippy --all-targets` — run before pushing; catches most CI failures
+ - Integration tests (`cargo test` targets with `#[ignore]`) require Docker running locally
```

**Rationale**:
1. **Clippy with `--all-targets`**: Replaces the generic `cargo clippy` entry with the more comprehensive flag. This is actionable (run it before every push) and recurring (prevents CI failures across all future work).
2. **Docker requirement for integration tests**: A concrete environment prerequisite that agents need to know before running the full test suite. Avoids wasted time debugging "connection refused" failures.

## Phase 2: Refactor

Skipped — the file is 14 lines post-edit (well under the ~120-line threshold), has no mixed scopes, no duplicates, and no orphan links.

## Combined Preview (Final State)

```markdown
# Project Guide

Rust CLI tool for processing log files.

## Build & Test

- `cargo build` — debug build
- `cargo test` — run all tests
- `cargo clippy --all-targets` — run before pushing; catches most CI failures
- Integration tests (`cargo test` targets with `#[ignore]`) require Docker running locally

## Style

- Follow standard Rust conventions (rustfmt)
- Use `thiserror` for library errors, `anyhow` for binary errors
- Prefer iterators over manual loops
```

## Summary

✅ Applied 2 learnings to `./AGENTS.md` — no structural changes needed.
