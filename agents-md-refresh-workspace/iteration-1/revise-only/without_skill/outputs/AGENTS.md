# Project Guide

Rust CLI tool for processing log files.

## Build & Test

- `cargo build` — debug build
- `cargo test` — run unit tests
- `cargo clippy --all-targets` — run before pushing; catches most CI failures

### Pre-push checklist

1. `cargo clippy --all-targets` — catches most CI failures early
2. `cargo test`

### Integration tests

- Integration tests require **Docker** running on the host.
- Make sure the Docker daemon is started before running integration tests.

## Style

- Follow standard Rust conventions (rustfmt)
- Use `thiserror` for library errors, `anyhow` for binary errors
- Prefer iterators over manual loops
