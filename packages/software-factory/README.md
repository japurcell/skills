# Software factory development package

This package implements `docs/software-factory/ExecPlan.md`. Development source stays outside published skills. It currently provides build/test infrastructure, native foundation qualification, transactional ownership/accounting, bounded filtered capture, command-only foreground workflows through `invoke`, paged `history`, bounded shutdown and exact-claim owner clearance. Startup requires an explicitly prepared shared toolchain; it never installs dependencies. See the [invocation contract](qualification/invocation.md) and [lifecycle evidence and limits](qualification/lifecycle.md). Real harness adapters remain unfinished.

Explicit setup from repository root:

    rtk proxy npm --prefix packages/software-factory ci --ignore-scripts
    rtk proxy python3 scripts/test-software-factory.py --suite fixtures

The second command typechecks, builds `dist/cli.js`, and tests the fake harness, dirty Git fixture, development help and test-filter failure behavior. Run `--suite lifecycle` for public invocation E2E checks. Fixtures never launch a provider or modify global Git configuration. `test:all` deliberately fails while required suites remain unimplemented, currently starting at adapters. It does not silently pass empty suites. Native qualification is separate; see [runtime evidence](qualification/runtime.md) and [hosted results](qualification/native-results-2026-10-21.md).

Development dependencies are exact and locked: TypeScript 7.0.2, Node types 24.19.2, and Playwright 1.64.1. No browser is installed automatically. Dependency caches, built files, browser results and node_modules are ignored. Nothing installs into a real target repository or account as part of testing.

Use `inspect-owner` before explicit `clear-owner`; clearance requires the exact claim/token, operator confirmation and a note. Both accept `--common-dir PATH` to inspect an existing store without Git. Known-live owners cannot be cleared. Unknown descendants retain ownership until informed cleanup; clearance never changes the old outcome or refunds uncertain work. Windows workflow startup remains unqualified and may be blocked by conservative Git/compiler cleanup. Passing native foundation CI does not establish Windows product support.
