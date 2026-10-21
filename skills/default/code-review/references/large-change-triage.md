# Large Change Triage

Use when a change exceeds 1000 changed lines or 15 files.

## Goals

Reduce token use while preserving review coverage.

## Steps

1. **Classify files**
   - production/source code
   - tests
   - docs/specs
   - generated files
   - lockfiles/assets
   - config/build/deploy files

2. **Deprioritize low-signal files**
   - Skip generated files, lockfiles, and binary/static assets unless directly relevant.
   - Do not skip tests when running the test review.
   - Do not skip docs/specs needed to understand intended behavior.

3. **Group by domain**
   Group changed files by package, feature, layer, or directory.

4. **Review chunks**
   Run subagents on coherent chunks instead of one giant diff.
   Include:
   - file list for the whole change
   - relevant hunks for the chunk
   - nearby context only when needed
   - applicable standards/spec snippets

5. **Cross-chunk issues**
   Separately check for integration risks across chunks:
   - API/schema contract mismatches
   - inconsistent behavior between layers
   - duplicated helpers or divergent patterns
   - partial migrations
   - non-atomic rollout or compatibility problems
