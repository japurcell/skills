# Software factory development package

This package implements `docs/software-factory/ExecPlan.md`. Development source stays outside published skills. It currently provides build/test infrastructure, local runtime qualification, transactional ownership/accounting, and bounded filtered capture. Runtime CLI commands refuse startup until implemented.

Explicit setup from repository root:

    rtk proxy npm --prefix packages/software-factory ci --ignore-scripts
    rtk proxy python3 scripts/test-software-factory.py --suite fixtures

The second command typechecks, builds `dist/cli.js`, and tests the fake harness, dirty Git fixture, development help and test-filter failure behavior. Fixtures never launch a provider or modify global Git configuration. `test:all` deliberately fails while required suites remain unimplemented. It does not silently pass empty suites. Native qualification is separate; see [runtime evidence](qualification/runtime.md).

Development dependencies are exact and locked: TypeScript 7.0.2, Node types 24.19.2, and Playwright 1.64.1. No browser is installed automatically. Dependency caches, built files, browser results and node_modules are ignored. Nothing installs into a real target repository or account as part of testing.
