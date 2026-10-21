# Stage evidence: <target> / <route> / <checkpoint>

Use only for authorized target document writes. A checkpoint is a recorded intermediate state, not a deployment claim. Record author, date/time, full target revision and dirty changes, approved plan revision/owner/date, stage scope, OS/architecture/configuration, permitted resources, evidence/log locations and which earlier checks are superseded or not repeated. Record actual observations; a proposed command is `Not run`.

## Toolchain, solution and contract gates

Record requested and actually selected SDK/runtime versions, roll-forward behavior, resolved direct/transitive packages, local tools, workloads and image identifiers. Do not replace recorded selection with a later minimum pin. Record exact working directories, commands, non-sensitive environment and execution dates.

| Gate | Command/check and working directory | Expected behavior | Actual result/exit/counts | Revision/date/log | Status and owner |
| --- | --- | --- | --- | --- | --- |
| <each solution and separately built tool> | <real target command> | <build/test contract> | <observed or Not run> | <evidence> | <Passed/Failed/Blocked/Deferred/Not applicable> |
| <test discovery and coverage> | <target test command and collection method> | <nonempty tests and baseline comparison> | <pass/fail/skip, warnings, coverage> | <evidence> | <status and owner> |
| <startup, API/docs, auth, jobs, frontend> | <bounded target check> | <observable contract> | <observed response/output> | <evidence> | <status and owner> |

Include each host and tool, not just one compiling project. Explain each not-applicable decision using inspected usage. Verify actual startup and relevant API/documentation endpoints, authentication/authorization state transitions, background jobs, browser behavior and crossed-version behavior changes. Select test sequencing from resource isolation constraints; parallel tests sharing state do not prove repeatability.

## Providers, publish, images, failures and recovery

| Surface | Isolated setup and owner | Exact check/order | Observable evidence | Failure/cleanup/recovery |
| --- | --- | --- | --- | --- |
| <database provider/context> | <disposable resource, no credentials> | <review script; execute provider migration before host initialization; test persistence in fresh scope> | <schema/history and actual stored/read values> | <owned resource cleanup; approved recovery> |
| <frontend and backend publish> | <unique output/configuration> | <target frontend build then publish; verify assets/config/assemblies> | <served bundle and selected runtime> | <preserve unrelated outputs> |
| <container image> | <owned image/process, dynamic ports> | <bounded readiness/HTTP smoke; culture/timezone; graceful shutdown> | <real status/body/runtime/exit> | <timeout logs; exact owned cleanup> |

Model/snapshot inspection and reviewed SQL are useful evidence but not proof of executed migrations. Each provider needs its own executed checks; SQLite and SQL Server scripts are not interchangeable. Record initialization order to avoid creating tables without migration history. Check relevant UTC/non-UTC timestamp and durable auth contracts using new service/database contexts rather than cached objects.

Inspect target scripts before using them: a publish script may delete frontend outputs, direct backend publishing may omit asset generation, and a development-server mode may hide missing bundles. Choose the target's real published-assets configuration. For image checks, verify globalization libraries and timezone data independently, use valid disposable configuration without contacting live identity systems, bound readiness, and distinguish genuine expected responses from synthetic success/error fallbacks. Record Docker/provider/runtime prerequisites as blocked when missing.

Record new and baseline warnings, audit/restore findings, test failures/skips, coverage numerator/denominator and collection variability. Investigate generated-code changes rather than blanket exclusions. Do not suppress failures, weaken tests or delete historical evidence to make a gate pass. Record the actual failure, corrective change, changed revision, affected rechecks and any required approval renewal. Recovery uses approved source/image checkpoints and owned cleanup, not an automatic database downgrade.

## Local versus deployment readiness

Local readiness: <Ready/Not ready/Not assessed>, limited to <explicit local gates at revision>. Deployment readiness: <Verified/Unverified/Blocked/Deferred>, limited to <named environment and actual checks>. Explain unresolved gates, owner, next evidence and whether each blocks the approved local scope. Deferral never turns a gate green.

Keep earlier evidence tied to its stage/revision; after hardening or dependency changes, list checks repeated and checks not repeated. Do not combine earlier provider/startup/image checks with later test results into an invented all-green final run. Exclude secrets; sanitized configuration proves only the tested local behavior. An accepted proxy/security exception is not proof that spoofed traffic is rejected.

## External owner checklists

Provide an explicit checklist as gate rows for each applicable external owner, even when outside local implementation scope. Name the owner, required decision/check, actual evidence, status and local blocking policy. Do not inherit another project's deployment choices.

| Owner/surface | Required decision or check | Evidence/status | Blocks local scope? | Next action and owner |
| --- | --- | --- | --- | --- |
| <CI/CD owner> | <agent SDK/runtime/tools, real build/test/publish pipeline, artifacts/secrets> | <observed or Deferred> | <plan decision> | <named action> |
| <server administrator> | <hosting runtime/module, config, permissions/keys, startup/assets/timezone/shutdown> | <observed or Deferred> | <plan decision> | <named action> |
| <cloud/platform owner> | <architecture/image pull/resources/network/secrets, database/identity/mail, jobs/keys, health/globalization/stop> | <observed or Deferred> | <plan decision> | <named action> |

For AWS targets, assess Fargate and Lambda suitability separately. Local image readiness is not live Fargate verification. A long-lived worker or server does not become Lambda-ready without reviewed decomposition or an adapter; an article alone does not prove unchanged deployment. For other platforms, replace these examples with their actual owner gates. Never claim unperformed Jenkins, IIS, Fargate, Lambda or external-service checks passed.

## Stage decision and next boundary

Record whether the approved next stage may proceed, which execution-critical evidence remains fresh, any material deviations requiring renewed approval, and the safe stopping/recovery point. Link the concrete target plan and candidate lessons if authorized. Lesson capture does not approve changes to shared guidance.
