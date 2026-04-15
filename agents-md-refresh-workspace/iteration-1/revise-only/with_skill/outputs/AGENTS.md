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
