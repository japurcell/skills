# Codex 0.163.0 bounded adapter qualification

Unpushed provider qualification checkpoint. The common dual-stream seam and the exact pinned `read-only` and `workspace-write` modes have passing evidence, while requested-resource answer delivery remains unqualified. This document does not claim support for every Codex configuration, model, operating system, plugin or native child mode.

## Exact artifact and native configuration

The inspected executable is `/Users/adam/homebrew/Caskroom/codex/0.163.0/bin/codex`, version `0.163.0`, SHA256 `8813367285524ac798dd96d1b071aea30d58708c7226fd236cd275cf1cfdee31`, macOS arm64. `createCodexAdapter({executable, sha256, environment})` requires an absolute executable and verifies the caller-pinned digest before launch. The caller supplies the native environment explicitly; native authentication stays outside code and logs. Native `login status` reported `Logged in using ChatGPT`; no token was inspected.

The selected model/reasoning pair is exactly `gpt-6-luna` / `low`; other pairs refuse before dispatch. The current candidate permits `read-only` and `workspace-write` after a bounded disposable native write/stop proof. Native skill delivery and session reuse refuse. All requested required capabilities must be available. The argv is an array launched without a shell or terminal:

    <executable> --no-daemon exec --json --color never --disable multi_agent --disable multi_agent_v2 --sandbox <permissions> --config 'approval_policy="never"' --model gpt-6-luna --config 'model_reasoning_effort="low"' --cd <worktree> -- <JSON instruction packet>

`--no-daemon` is confirmed by the installed main help and accepted before `exec`; it keeps the invocation independent of a shared background server. Both child-agent feature names were confirmed in the exact installed `features list`. This mode explicitly disables them; it claims only local owned process-group control. There is no universal descendant or native remote-child guarantee. Native configuration, enabled hooks, hook trust, execpolicy rules, discovered instructions, discovered skills, plugins and account restrictions remain in effect. The mode never uses `--ignore-user-config`, `--ignore-rules`, hook-trust bypass, sandbox bypass, implicit-last resume, auto-install or auto-update flags. `approval_policy="never"` supplies no approval bridge and never authorizes an expansion.

The instruction packet contains the effective prompt, ordered requested skill names/files/instruction bytes/resource bytes, explicit saved correction context and control-envelope instructions. This is instruction delivery. Supplied skill names never become evidence of native loading or compliance. Native discovered resources can add context; this adapter does not claim isolation from existing native configuration. Exact effective native configuration must be requalified when it changes.

## Protocol and native observations

The [official non-interactive reference](https://learn.chatgpt.com/docs/non-interactive-mode), fetched 2026-10-22 UTC, describes exec JSON events and structured/final channels. The installed `exec --help` independently confirmed `--json`, `--output-schema`, `--output-last-message`, sandbox selection, explicit resume/fork and `--ignore-user-config` authentication behavior. The removed `--full-auto` option is never emitted. The common public payload contract uses a named callable validator rather than JSON Schema, so this adapter requests a JSON control envelope and validates decoded final data through that common contract. It does not invent a schema conversion.

The authoritative capture is stdout JSONL. Final decoding requires one fresh `thread.started`, one `turn.started`, a completed `agent_message` and terminal `turn.completed`; it parses only the last completed assistant message. Tool text, log records, native errors and turn completion cannot supply a result. Missing completion, malformed JSON and error/failed-turn records reject. Records after terminal completion reject. Native error and sandbox-denial diagnostics remain generic while the bounded raw captures retain detail for authorized inspection. A native error cannot later relabel the session as succeeded. The runner bounds and saves original/filtered raw captures before decoding.

Exact native success observed:

    thread.started {thread_id:"01a16243-88ed-7f53-b2cc-ffada6aa4a26"}
    turn.started
    item.completed {item:{type:"agent_message",text:"{\"kind\":\"result\",\"payload\":{\"summary\":\"qualified\"}}"}}
    turn.completed {usage:{input_tokens:22514,cached_input_tokens:7168,cache_write_input_tokens:0,output_tokens:15,reasoning_output_tokens:0}}

Exit was 0. The harmless prompt requested no tools or file reads in a disposable Git repository. Normal native session-artifact creation required narrow execution escalation; the first restricted attempt failed before provider dispatch with native state/app-server errors. That failed startup is not counted as a successful native call.

Thread identity appears only in `thread.started`; turn records omit it. A parser closure created by each `start` associates that attempt's terminal turn with its thread. A shared mutable current-thread slot would cross-wire concurrent calls. Reported usage currently remains unknown: the emitted aggregate does not establish its child-inclusion scope. Reported loaded skills remain unknown; the stream did not emit reliable loading evidence. Parent native identity is null for this fresh root; no child-parent records are fabricated.

A harmless denied write was observed with read-only sandbox and approval policy never. The requested file was absent. Native stderr contained:

    WARN codex_sandboxing::violation: recorded sandbox violation: resource=filesystem backend=seatbelt reason=operation_not_permitted path=unknown

However the CLI exited 0 and stdout still contained an ordinary successful assistant envelope and `turn.completed`. Therefore native exit/final result alone cannot prove permission success. The per-launch parser observes both streams and treats the exact native sandbox-violation diagnostic as terminal failure; other stderr warnings remain raw evidence. The integrated dual-stream fixture passes this denial case.

## Freshness, correction and stopping

Every ordinary call, independent review, later invocation and requested correction starts a fresh native process/thread. `canReuse` returns false and direct supplied native reuse refuses. The common runner can select its single permitted fresh correction with the same validated profile and explicit saved context; the adapter never retries. Stop delegates only to the runner's existing owned-scope stop callback. Native group absence must be proved by the runner; optional telemetry cannot prove cleanup.

## Native attempt accounting and acceptance gate

All six authorized native attempts have been spent. Before the last three calls, the pinned executable digest, version, and help were rechecked on 2026-10-22: SHA256 `8813367285524ac798dd96d1b071aea30d58708c7226fd236cd275cf1cfdee31`, `codex-cli 0.163.0`, and `exec --help` advertising `--json`, `--sandbox`, `--model`, `--config`, and `--cd`. The native executable emitted an unrelated PATH-alias warning during these read-only checks. No further native call is authorized under this qualification budget.

Attempts four and five formed one factory invocation in a disposable Git repository. The first read-only call produced an intentionally malformed required result and was saved as invalid. The workflow then requested an explicit format correction with the previous attempt ID and saved context. The second call started a different native thread but returned a refusal rather than the validated JSON envelope and literal `RESOURCE_C7B2` from a requested resource. This leaves requested-resource answer delivery unqualified. Supplied bytes prove instruction delivery only; they do not prove native skill loading or compliance.

Attempt six was one workspace-write call in a separate disposable Git repository. The exact pinned native mode used `--no-daemon` before `exec`, sandbox `workspace-write`, approval policy `never`, `gpt-6-luna`/`low`, and both multi-agent flags disabled. A narrow temporary proof adapter opened this mode only for the disposable probe; the maintained adapter was changed only after inspecting evidence. The native request wrote a harmless unique marker inside the disposable worktree and then ran a bounded sleep long enough for the factory timeout to stop its owned process group. The marker matched the requested nonce, the attempt failed by timeout, cleanup was complete, and a group-existence probe returned ESRCH for the recorded owned PID. The runner claims only its owned local process group; unknown child activity remains an explicit limit. The native request did not touch this repository, global installation, native config, trust, hooks, rules, authentication, or external systems.

All six authorized native attempts are spent. Do not run another native attempt without a new authorization. The provider remains unregistered until independent full security review and parent approval.

## Verification status

The planned same-invocation live calls four and five ran in disposable repository `/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/factory-repository-oQyxUv/repository`. The first fresh native thread `01a1627c-6682-7143-a1b5-108288b47722` returned `INVALID_NATIVE_RESULT` and the factory saved it as an invalid authoritative result. The second fresh thread `01a1627c-79ad-71c1-b77c-d23bfd0aa865` returned a plain-text refusal of the correction instruction rather than the required JSON marker payload; the factory saved a second invalid result and failed with `unresolved invalid agent result`. Both agent attempts were quiescent, `additionalUsed` was one, `occupiedAgents` was zero, and invocation cleanup was complete. Raw and structured evidence is preserved in sibling `native-result.json`. This proves fresh correction dispatch and malformed result handling; it does not prove that requested resource bytes affected the final answer or that native skills loaded. Do not repeat the pair under this budget.

Live attempt six ran in disposable repository `/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/factory-repository-8erNAb/repository`. The native thread `01a1627d-ff8a-7802-a67b-8e6e2a04692d` started a shell command that wrote `CODEX_WRITE_PROOF_92c56550-453e-4334-9de5-62c6da1aa0a4` to `.factory-native-marker` and then slept. The marker contained the exact nonce. The factory recorded `agent timeout: write-stop`, `exit=null; signal=SIGTERM; timeout`, attempt `quiescent=true`, invocation cleanup `complete`, and zero occupied agents. `process.kill(-31252, 0)` returned ESRCH for the recorded owned group. The native session lifecycle remained `running` because the turn was interrupted before its own terminal event; this is not evidence of active local group membership. Raw and structured evidence is preserved in sibling `native-write-stop-result.json`. This qualifies only the exact bounded local workspace-write and owned-stop mode, not universal descendant control.

Pinned Node is `24.22.1`; package dependencies were installed from the existing offline lockfile cache with scripts disabled. Source/declaration build and strict source/qualification typechecks pass. The integrated provider fixture has 14 passing cases, zero failures/skips/cancellations, including final/error boundaries, literal instruction/resource packet bytes, exact executable digest and arguments, read-only and workspace-write validation, per-launch concurrency isolation, native stderr denial detection, generic user-facing diagnostics, and public workflow subprocess behavior. The latest focused run after the security review changes passed 14/14 in 9.539 seconds. Parent-owned integrated registered checks previously passed 166/166 in 54.075 seconds against the same common seam; those were not repeated after the narrow provider change. No shared file was edited by this provider task.

The maintained provider fixture runs a real executable subprocess through `WorkflowContext.agent` and inspects saved attempts/sessions/captures. Added scenarios cover success, malformed output, native errors, permission denial, fresh correction/review, concurrent sessions and timeout stop. Registration is parent-owned; direct focused command from `packages/software-factory`:

    <pinned-node> scripts/build.mjs
    <pinned-node> --test test/codex-adapter.test.mjs

No broad model, native skill, native reuse, Windows or remote-child qualification is claimed. The failed requested-resource answer delivery is a support limit for that capability until separately qualified.

## Checkpoint and next owner action

The parent supplied the verified common stream seam. The provider code, focused fixture, strict typechecks, build, and all six authorized native attempts are complete. A local five-axis review found and fixed native failure relabeling and raw native diagnostic disclosure; independent security review of the four scoped files remains an acceptance gate, followed by parent approval before registration. The failed correction/resource echo must remain a documented support limit. Do not request another native call or broaden the claimed mode within this budget.

The first three native-call captures remain under `/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/factory-codex-live-i4zpt9ab/` (`stdout.jsonl`, `stderr.txt`, `denial.stdout.jsonl`, `denial.stderr.txt`, `command.json`). The latter three calls have the two disposable `native-result.json` artifacts named above. These contain harmless prompts and native output, never authentication material. `/tmp/factory-codex-live-proof.mjs` and `/tmp/factory-codex-write-stop-proof.mjs` were disposable drivers; they are not maintained fixtures.

Reflection review completed using the brain index and existing testing/security notes. The durable protocol findings are encoded in provider checks and this qualification document; no brain, skill, shared type/store/runner or registry edit is needed from this bounded task.
