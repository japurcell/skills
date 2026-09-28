# RTK 0.50.0 Release Facts

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** ../research/rtk-050-release-facts

## Question

What do official RTK 0.50.0 release artifacts and source say about `RTK_SUPPRESS_HOOK_WARNING`, supported platforms, installation, and behavior when agents run explicit `rtk` commands? Identify facts needed to replace the pinned prerelease path without losing other diagnostics or exit codes.

## Resolution

Verified stable `v0.50.0` release dated 2026-09-24, signed release commit `1d87b8e`, and official checksummed macOS, Linux, and Windows assets. The environment override and TOML setting suppress only the missing-hook warning; the outdated-hook prompt and RTK command processing remain. Agents without hooks such as Codex are documented to use explicit `rtk` commands, so configure suppression in their execution environment or RTK config to avoid repeating this advisory. Exact asset hashes and source links are in [the research note](../research/rtk-050-release-facts/README.md). The release's documentation does not assert exit-code semantics, so preservation of those paths remains an implementation constraint rather than a verified release fact.

---
