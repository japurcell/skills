# Local runtime prerequisites: Restate and DBOS TypeScript

Checked 2026-10-12 against current official documentation. No repository SDK version is pinned, so these are current-documentation findings, not version-specific compatibility guarantees.

## Restate TypeScript

- The TypeScript SDK serves handlers in the application process using `restate.serve(...)`; this is the workflow runner process. The endpoint is then registered with Restate. ([Services](https://docs.restate.dev/concepts/services/))
- Durable execution requires a separate Restate Server process/service. The official local cluster guide runs Restate nodes separately from a local service endpoint, registers that endpoint with the server, invokes through server ingress, and persists server state in a Docker volume. This establishes a separate engine/service and persistent server-owned storage; it does not establish a need for an additional database server. ([Local Restate Cluster with Docker](https://docs.restate.dev/guides/cluster))
- That guide uses Docker Compose, but describes a three-node cluster. It does not prove Docker is the only way to run a single-node local server or that the official server distribution supports every host OS.
- Parent verification of the official installation page confirms a standalone `restate-server` binary with no external dependencies. Docker is an alternative, not a requirement for the documented native installations. The download choices list macOS and Linux architectures; native Windows is not established by that page. ([Installation](https://docs.restate.dev/installation))

## DBOS TypeScript

- The DBOS TypeScript library launches in the application process (`DBOS.setConfig`, then `DBOS.launch`). Its documented system database is Postgres. Local setup says to use existing Postgres or start it separately with `npx dbos postgres start`; the CLI example starts a Docker container. The library itself is not a separate engine process, while Postgres is a separate database service/process unless externally hosted. ([Add DBOS to Your App](https://docs.dbos.dev/typescript/integrating-dbos), [TypeScript programming guide](https://docs.dbos.dev/typescript/programming-guide))
- TypeScript configuration documents `systemDatabaseUrl` as a Postgres URL and does not document SQLite as a TypeScript backend. The SQLite default appears in DBOS Python-specific guidance; that does not establish embedded SQLite for TypeScript. No documented embedded SQLite mode for DBOS TypeScript was found in current official docs. ([TypeScript configuration](https://docs.dbos.dev/typescript/reference/configuration), [DBOS AI quickstart](https://docs.dbos.dev/ai/ai-quickstart))
- TypeScript getting-started documentation requires Node.js 20 or later. It provides no native Windows limitation for the TypeScript SDK in the pages checked. ([Add DBOS to Your App](https://docs.dbos.dev/typescript/integrating-dbos))
- The same integration page warns that DBOS and its workflows must remain external to JavaScript/TypeScript bundlers because of the workflow registry. A generic Node single-executable capability therefore does not establish a supported bundled DBOS distribution. ([Add DBOS to Your App](https://docs.dbos.dev/typescript/integrating-dbos))

## Windows and platform limits

- DBOS TypeScript: UNVERIFIED whether all supported features and `npx dbos postgres start` work natively on Windows. Official TypeScript pages checked state Node and Postgres requirements but make no Windows-specific claim.
- Restate: UNVERIFIED whether Restate Server has a native Windows distribution or which host OS versions it supports. The installation page lists macOS/Linux binaries without a Windows option, while the cluster guide uses Docker Compose. The official source repository contains Windows-specific CLI configuration-path code, which proves only that the CLI accounts for Windows paths, not that the server runs natively on Windows. ([Installation](https://docs.restate.dev/installation), [Restate CLI source](https://github.com/restatedev/restate/blob/main/cli/src/cli_env.rs))
- Neither native Windows support nor a native Windows blocker is established here. Docker Desktop/WSL behavior is outside the checked evidence.

## TypeScript runtime packaging boundary

Node.js can execute some TypeScript directly, with documented syntax and module-system limitations, and can package Node applications as single-executable applications that do not require a separate Node installation. These capabilities address the language runtime only; they do not package Restate Server or Postgres, and they do not prove that a customizable workflow bundle works with either SDK. ([Node.js TypeScript support](https://nodejs.org/api/typescript.html), [Node.js single-executable applications](https://nodejs.org/api/single-executable-applications.html))

## Decision-relevant boundary

Restate entails the runner plus a separate Restate Server service, with Restate-owned persistent storage evidenced by the local deployment example. DBOS TypeScript entails the runner plus Postgres for its system database. Current DBOS TypeScript docs do not document embedded SQLite. These are prerequisite facts only; they do not select an engine or prove invocation/recovery behavior for a foreground-only workflow.
