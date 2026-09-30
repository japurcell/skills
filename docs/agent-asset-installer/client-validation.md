# Platform and native client validation

Observed 2026-09-30 UTC on macOS 26.7 arm64. This is measured local subprocess evidence plus explicitly unmet native gates. Milestone 6 remains in progress; acceptance is not met.

## Local environment

The command host reports Python 3.14.6, Apple Git 2.50.1, Bash 3.2.57, PowerShell 7.6.6, and RTK 0.50.0. Separate installed interpreters are Python 3.13.14 and the desktop runtime Python 3.12.14. Python 3.11 and native Windows/Linux runners are unavailable. CI requests Python 3.11 and 3.14 but has not run from this private branch. Syntax parsing with a 3.11 grammar is not a 3.11 runtime result.

Codex CLI 0.159.0 is present. The earlier [prerequisite inspection](codex-cli-prerequisites.md) encountered a refused PATH-alias write even for help. No model session was started here. Other advertised clients are unavailable locally. No dependencies, clients, credentials, or real-home configuration were installed or changed.

## Automated evidence and limits

Final local results: all 100 public cases pass on Python 3.14.6 (134.756 seconds); the repaired 28-case team group and final version-2 exported-bundle consumer pass on 3.12.14 (11.818 and 1.077 seconds). The earlier 98-case checkpoint passed on 3.13.14 (136.662 seconds), before the final paired-format repair. Independent review approves the implemented source after reproducing and rechecking both required fixes, actual old-CLI migration in three policy configurations, and eight malformed current-record cases with no writes. The existing PowerShell installer suite passes on macOS and explicitly reports unsupported junction creation. Generator freshness passes for 35 outputs and all 25 generator cases pass. OKF/whitespace checks pass. Fifteen installer/test files parse with Python 3.11 grammar; that does not replace an actual 3.11 run.

`python3 scripts/test-agent-assets.py --group clone` creates a real committed installation, packages the Git history as a bundle, removes the disposable source, and clones with `core.autocrlf=true` and `false`. Before any repair or installation in either clone, it runs read-only `status --check`, checks unchanged file bytes/mtimes including Git metadata, literal LF/CRLF/binary content, and recorded SHA-256 values. A separately committed damaged binary must fail audit with drift and stay damaged. Relocated Unicode, apostrophe, ampersand, and space paths exercise the three installed startup commands from nested working directories. The fixture uses empty child-process homes and external disposable state.

Local Bash execution of Codex/Copilot registrations and the Gemini portable Python bootstrap proves protocol execution, useful context, and audit output. It does not prove native client discovery, trust, or event delivery. The Windows clone job instead executes Copilot's PowerShell field and Codex/Gemini's Windows command fields through their shells; those runs have not occurred locally. Codex's Windows command uses `py -3`, so its selected launcher interpreter is distinct from the interpreter running the audit suite.

The native Windows boundary group checks production refusal without changes and retained interrupted-operation evidence. It does not exercise a safe Windows writer. The separate `UNMET native Windows mutation acceptance` jobs run the entire existing suite, without suppressed failures, and are expected to fail until an actual safe implementation exists. Existing `ready-ideas-windows.yml` PowerShell coverage remains unchanged. The aggregate `test-all.py` is POSIX-only.

The clone defect fixed in this milestone was conversion of `.gitattributes` itself: default autocrlf changed the owned LF markers. Newly owned blocks now declare a narrow, recorded LF rule for that file when no compatible policy exists. New matching version-2 selection/lock records require an `attribute_file_policy` lock field (LF for an owned team block, null otherwise), recording the required policy even when its rule is borrowed; review reproduced a false passing audit when borrowed LF was later overridden with CRLF, and the public regression now requires drift without writes. Strict verification still rejects byte edits and conflicting effective transforms; it does not normalize payloads or renormalize the repository. Authentic older records can restore/update into the new requirement. Detached hook maintenance can briefly outlive the launcher; fixture cleanup waits with a bounded retry instead of disabling maintenance.

Offline record-authority limit: matching version-1 records predating this requirement remain accepted and explicitly migrate to version 2. Missing/mistyped policy in a current lock or mixed record versions fails with `ASSET_RECORD_INVALID` and no writes. A coordinated rewrite of both versions, removal of modern policy, and recomputation of the selection fingerprint can imitate a genuine legacy pair. Audit does not cryptographically authenticate records or fetch historical source; review committed records together with payload changes. Explicit restore/update still preflights current metadata policy and refuses a CRLF conflict without writes. An adversary allowed to rewrite the entire committed authority is outside the offline audit integrity claim.

## Client gates

| Surface | Installed representation | Completed evidence | Required native evidence |
| --- | --- | --- | --- |
| Codex local CLI | `.agents/skills`, `.codex/agents`, `.codex/hooks.json` | Exact files, strict TOML, direct startup/tool hook protocols | Fully disposable containment, normal project trust, separate current hook-definition review, explicit skill activation, custom-agent spawn, native event delivery before and after relocation |
| Copilot CLI | `.agents/skills`, `.github/agents`, `.github/hooks/agent-assets.json` | Exact files and direct startup/tool/end protocols | Installed client/version, normal trust, skill/agent activation, native event delivery and relocation |
| Copilot VS Code | Same repository paths | Adapter files only | Exact extension/version, disposable editor profile, native trust/loading/events; CLI evidence cannot substitute |
| Gemini CLI | `.agents/skills`, `.gemini/agents`, `.gemini/settings.json` | Exact files and direct startup/tool/end protocols | Installed client/version, disposable profile, normal trust/loading/events and relocation |
| Claude Code | `.claude/skills` and supporting references | File placement and preservation | Exact client/version, native skill activation and reference reads only |
| Cursor | `.agents/skills` and supporting references | File placement and preservation | Exact client/version, native skill activation and reference reads only |
| OpenCode | `.agents/skills` and supporting references | File placement and preservation | Exact client/version, native skill activation and reference reads only |

No IDE, cloud, or hosted-client support is inferred. Skills-only adapters do not advertise agents/hooks. Native loading on every surface above remains unverified.

## Codex isolation and normal trust

[Codex isolation research](codex-isolation-research.md) records the source-backed candidate: a disposable `CODEX_HOME`, SQLite/cache/temp locations, ephemeral authentication storage, and a loopback custom Responses provider without credentials. That candidate is not demonstrated containment. A profile or `exec --ephemeral` alone does not isolate all home, cache, policy, or credential access. A verified external process boundary and write audit must precede any model session.

Project approval and hook-definition review are separate native gates. Complete both through the normal UI; do not fabricate trusted-project records or hook hashes, bypass trust, copy personal credentials, or infer delivery from direct script invocation. Current official [hook documentation](https://learn.chatgpt.com/docs/hooks) describes trusted project layers and review of non-managed definitions. Exact installed 0.159.0 behavior must still be measured. No client experiment is reported as passed here.

## Windows implementation gate

[Windows filesystem research](windows-filesystem-research.md) identifies a possible rooted `NtCreateFile` and retained-source/parent-relative rename composition. Individual API contracts do not establish the complete mutation boundary. The user-mode directory/reparse option combination, reparse mutation through attribute-only handles, existing-target rename sharing, stage identity verification, and namespace reacquisition after process death still need native experiments and a defensible implementation. This is unfinished implementation, in addition to unavailable execution evidence. Production retains `ASSET_PLATFORM_UNSUPPORTED`; no path-only fallback was added.
