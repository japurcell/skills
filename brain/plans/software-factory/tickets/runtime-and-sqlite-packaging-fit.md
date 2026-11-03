# Managed runtime and SQLite packaging fit

**Type:** research
**Status:** closed
**Blocked By:** operating-and-installation-model.md
**Research Dir:** ../research/runtime-and-sqlite-packaging-fit

## Question

Which single managed JavaScript runtime and SQLite integration best fit the accepted simple foreground TypeScript factory without introducing multiple runtime paths or a native-addon distribution matrix unnecessarily?

Compare Node.js LTS with built-in SQLite, Node.js LTS with better-sqlite3, and Bun with built-in SQLite using current primary sources. Establish actual release/API stability, native macOS/Linux/Windows distribution, TypeScript authoring/runtime implications, transactions/WAL/backup support, blocking behavior, and packaging/maintenance tradeoffs. The factory uses one repository SQLite history/accounting/ownership store shared by foreground invocations and a separate on-demand SSE dashboard. Runtime/dependencies are isolated and skill-managed; no global runtime requirement, permanent service, database server, durable workflow resume, or automated installation is authorized.

Distinguish documented support from native qualification and performance evidence. Recommend one path based on total complexity, robustness and maintainability, not benchmark folklore or similarity to SSSF. Do not manufacture a release pin from projected dates. No implementation, installation or live runtime tests are authorized; source research only. Findings inform the lifecycle decision and do not adopt a runtime.

## Research resolution

Closed on 2026-10-15 as source research. The recommendation is Node LTS with built-in `node:sqlite`: it has official macOS/Linux/Windows runtime artifacts, stable TypeScript type stripping in the current LTS, and the needed SQLite transaction, WAL, iterator, and backup capabilities without a separate addon. The material caveat is that the Node 24 `node:sqlite` API is still a release candidate. `better-sqlite3` offers more transaction ergonomics and an online backup API, with upstream prebuilds for common target platforms but a native target matrix and fallback build prerequisites. Bun packages as one executable and has built-in TypeScript and SQLite, but its SQLite docs have no module-specific stability level and document platform-specific WAL cleanup behavior. All three database APIs are synchronous; retained history is unbounded and separate-worktree invocations may write concurrently, so query responsiveness and lock behavior need later qualification. The accepted idle-only backup policy makes an online backup method a convenience rather than a deciding requirement. No exact runtime pin or design acceptance is recorded. See [research findings](../research/runtime-and-sqlite-packaging-fit/findings.md).

---

## Subsequent product decision

On 2026-10-15 the human accepted [Node LTS with built-in SQLite](recovery-and-runtime-selection.md#accepted-node-lts-and-built-in-sqlite), including the disclosed API-maturity tradeoff. The research resolution above records the evidence available when research closed; it does not supersede that later acceptance. Exact version pinning and native qualification remain outstanding.
