# Local runtime prerequisites

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** docs/software-factory/research/local-runtime-prerequisites

## Question

What does local execution of the current TypeScript versions of Restate and DBOS require beyond the workflow runner? Verify which pieces execute in-process, which require a separate engine or database, and whether an embedded local-storage mode is documented. Identify any documented native-Windows constraint relevant to the accepted macOS/Linux/Windows target.

Use current primary documentation or official source. This is a prerequisite fact check for the operating discussion, not production runtime selection. Do not install or execute engines. Record source-supported facts, inference, and unverified gaps separately. The later recovery ticket still owns full suitability and acceptance proof.

---

<!-- The delegated researcher claims this ticket, writes findings in its Research Dir, appends Resolution, and closes it. -->

## Resolution

Current official docs distinguish the workflow runner from durable state services. Restate TypeScript handlers run in the application process via `restate.serve`, while a separate Restate Server handles registration, ingress, and durable state. The server is available as a self-contained binary with no external dependencies; Docker is optional for the documented native installations. DBOS TypeScript launches its library in the application process but requires a Postgres system database, local or hosted. Current DBOS TypeScript configuration documents Postgres URLs and no embedded SQLite mode; SQLite's documented default applies to Python. DBOS also documents a bundler restriction, so a generic Node packaging capability does not prove it can be bundled into one executable.

Native Windows support/constraints remain unverified for both local server/helper distributions. Restate's installation page lists macOS/Linux binaries; its CLI source's Windows path branch does not prove native server support. No repository SDK version is pinned, so current docs were used and version-specific guarantees remain open. See [findings](../research/local-runtime-prerequisites/findings.md) for evidence URLs and limits. This research resolves prerequisites, not runtime selection or factory recovery correctness.
