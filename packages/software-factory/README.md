# Software factory development package

This package implements `docs/software-factory/ExecPlan.md`. Development source stays outside published skills. It currently provides build/test infrastructure, native foundation qualification, transactional ownership/accounting, bounded filtered capture, and command-only foreground workflows through `invoke` and paged `history`. Startup requires an explicitly prepared shared toolchain; it never installs dependencies. See the [invocation contract and evidence](qualification/invocation.md). Bounded shutdown, manual clearance and real harness adapters remain unfinished.

Explicit setup from repository root:

    rtk proxy npm --prefix packages/software-factory ci --ignore-scripts
    rtk proxy python3 scripts/test-software-factory.py --suite fixtures

The second command typechecks, builds `dist/cli.js`, and tests the fake harness, dirty Git fixture, development help and test-filter failure behavior. Run `--suite lifecycle` for public invocation E2E checks. Fixtures never launch a provider or modify global Git configuration. `test:all` deliberately fails while required suites remain unimplemented, currently starting at adapters. It does not silently pass empty suites. Native qualification is separate; see [runtime evidence](qualification/runtime.md) and [hosted results](qualification/native-results-2026-10-21.md).

Development dependencies are exact and locked: TypeScript 7.0.2, Node types 24.19.2, and Playwright 1.64.1. No browser is installed automatically. Dependency caches, built files, browser results and node_modules are ignored. Nothing installs into a real target repository or account as part of testing.
