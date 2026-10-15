# WS3 composed workspace verification

Tested revision: `00d01d7696d641aa046208f1f7bab99c6ef9c1a2` on `codex/workspace-proof-m8`.
Host: macOS-26.7.1-arm64-arm-64bit-Mach-O. All required composed local checks pass.
The JSON record retains exact commands, exits, decisive output, hashes, source tree IDs, move identities and platform limits. Full logs and supplementary probe source remain disposable under `/private/tmp/ws3-m8-logs/` and `/private/tmp/ws3_m8_*.py`; these local paths are not durable repository evidence.

## Results

- All ten moved Git trees match base `b98f8214712fcf477b1394eca916db9fed18d2df`. Physical blob bytes and Git modes match across all 2,477 tracked entries, including symlink targets when present. All ten old paths are physically absent and no root `skills/*-workspace` directory remains.
- The eight-case cleanup CLI suite and an independent disposable public-CLI fixture passed. The latter checks four emitted roots and seven protected trees, nested payload and real-skill boundaries, archives, snapshots, linked workspaces/iterations, and empty-override failure without writes.
- New create-skill grader tests: 5 passed. Existing public grader suites: spec-to-tasks-grader 38, prd-ralph-loop-grader 13, handoff-grader 20, exec-plans-grader 35.
- Eight grader usage checks passed with expected exit 1 and category-level examples. These are successful negative invocations, not suite failures. Syntax, create-skill definition and evaluation JSON, actual source-category validation, and 14 registry tests passed.
- Full Bash and PowerShell installer suites passed serially with disposable profiles. Bash ran 34 top-level test functions. macOS PowerShell reported its unsupported-junction skip; native Windows behavior remains unverified for this revision.
- Generated-hook freshness (38 files), OKF lint, 72 affected Markdown local links, whitespace, unchanged tracked source after tests, and protected root AGENTS.md diff passed.

## Reporting correction

The temporary wrapper initially marked the Bash suite as failed because it expected an undocumented `all tests passed` message. The actual suite exited 0 after its assertions and does not print that message. The JSON retains the initial wrapper result and corrected interpretation. No suite, assertion, implementation or input was changed, and the successful suite was not rerun.

## Remaining coordinator work and limits

`workspace-discovery.md` lines 3, 26 and 28 describe the pre-move baseline as current. The coordinator agreed to label this document explicitly as the historical pre-migration snapshot at `c8d36350`/`b98f8214`, preserving ownership evidence. This documentation correction, the final KB/plan reconciliation and serial integration remain pending; the coordinator owns milestone acceptance.

No real benchmark cleanup, retained-run grading, real-home install, live evaluation, human-only orchestration, push or CI was performed. Historical workspace artifacts were preserved byte-for-byte. Source and disposable fixture results do not establish installed provider delivery or native Windows acceptance.
