# Script/Config/Test Dedup Review

## Findings
- Repeated shell snippets for setup/validation across run scripts.
- Duplicated config fragments with small key/value differences.
- Repeated test fixture/bootstrap setup logic.

## Consolidation Actions
- Create a shared shell helper for common setup and guard checks.
- Centralize repeated config defaults in one source and import/compose where supported.
- Extract test bootstrap setup into one reusable fixture helper.

## Verification Steps
- Targeted check: execute the updated helper path in a focused script/test run.
- Broad check: run full repository validation command set (lint/test/build as applicable).
- Compare pre/post outputs for unchanged behavior on representative cases.
