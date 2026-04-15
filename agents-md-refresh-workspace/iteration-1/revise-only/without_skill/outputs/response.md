# AGENTS.md Update — Learnings Applied

## Changes made

I updated `AGENTS.md` with two new learnings while keeping the existing structure intact:

1. **`cargo clippy --all-targets` before pushing** — Replaced the basic `cargo clippy` entry with `cargo clippy --all-targets` and noted it catches most CI failures. Added a concise pre-push checklist subsection.

2. **Integration tests need Docker** — Added a new "Integration tests" subsection documenting that Docker must be running on the host before running integration tests.

## What changed

- Updated the `cargo clippy` line to `cargo clippy --all-targets` with a note about CI
- Clarified `cargo test` runs unit tests (distinguishing from integration tests)
- Added **Pre-push checklist** subsection with the recommended order
- Added **Integration tests** subsection noting the Docker dependency

No structural reorganization was done — just targeted additions under the existing `## Build & Test` section.
