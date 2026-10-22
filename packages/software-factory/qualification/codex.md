# Codex 0.163.0 bounded adapter qualification

Unpushed provider checkpoint, incomplete and unqualified pending verified per-launch dual-stream common integration and remaining live checks. This document records evidence, not a support claim for every Codex configuration, model, operating system, plugin or native child mode.

## Exact artifact and native configuration

The inspected executable is `/Users/adam/homebrew/Caskroom/codex/0.163.0/bin/codex`, version `0.163.0`, SHA256 `8813367285524ac798dd96d1b071aea30d58708c7226fd236cd275cf1cfdee31`, macOS arm64. `createCodexAdapter({executable, sha256, environment})` requires an absolute executable and verifies the caller-pinned digest before launch. The caller supplies the native environment explicitly; native authentication stays outside code and logs. Native `login status` reported `Logged in using ChatGPT`; no token was inspected.

The selected model/reasoning pair is exactly `gpt-6-luna` / `low`; other pairs refuse before dispatch. The current candidate permits only `read-only` until workspace-write proof exists. Native skill delivery and session reuse refuse. All requested required capabilities must be available. The argv is an array launched without a shell or terminal:

    <executable> --no-daemon exec --json --color never --disable multi_agent --disable multi_agent_v2 --sandbox <permissions> --config 'approval_policy="never"' --model gpt-6-luna --config 'model_reasoning_effort="low"' --cd <worktree> -- <JSON instruction packet>

`--no-daemon` is confirmed by the installed main help and accepted before `exec`; it keeps the invocation independent of a shared background server. Both child-agent feature names were confirmed in the exact installed `features list`. This mode explicitly disables them; it claims only local owned process-group control. There is no universal descendant or native remote-child guarantee. Native configuration, enabled hooks, hook trust, execpolicy rules, discovered instructions, discovered skills, plugins and account restrictions remain in effect. The mode never uses `--ignore-user-config`, `--ignore-rules`, hook-trust bypass, sandbox bypass, implicit-last resume, auto-install or auto-update flags. `approval_policy="never"` supplies no approval bridge and never authorizes an expansion.

The instruction packet contains the effective prompt, ordered requested skill names/files/instruction bytes/resource bytes, explicit saved correction context and control-envelope instructions. This is instruction delivery. Supplied skill names never become evidence of native loading or compliance. Native discovered resources can add context; this adapter does not claim isolation from existing native configuration. Exact effective native configuration must be requalified when it changes.

## Protocol and native observations

The [official non-interactive reference](https://learn.chatgpt.com/docs/non-interactive-mode), fetched 2026-10-22 UTC, describes exec JSON events and structured/final channels. The installed `exec --help` independently confirmed `--json`, `--output-schema`, `--output-last-message`, sandbox selection, explicit resume/fork and `--ignore-user-config` authentication behavior. The removed `--full-auto` option is never emitted. The common public payload contract uses a named callable validator rather than JSON Schema, so this adapter requests a JSON control envelope and validates decoded final data through that common contract. It does not invent a schema conversion.

The authoritative capture is stdout JSONL. Final decoding requires one fresh `thread.started`, one `turn.started`, a completed `agent_message` and terminal `turn.completed`; it parses only the last completed assistant message. Tool text, log records, native errors and turn completion cannot supply a result. Missing completion, malformed JSON and error/failed-turn records reject. Records after terminal completion reject. The runner bounds and saves original/filtered raw captures before decoding.

Exact native success observed:

    thread.started {thread_id:"01a16243-88ed-7f53-b2cc-ffada6aa4a26"}
    turn.started
    item.completed {item:{type:"agent_message",text:"{\"kind\":\"result\",\"payload\":{\"summary\":\"qualified\"}}"}}
    turn.completed {usage:{input_tokens:22514,cached_input_tokens:7168,cache_write_input_tokens:0,output_tokens:15,reasoning_output_tokens:0}}

Exit was 0. The harmless prompt requested no tools or file reads in a disposable Git repository. Normal native session-artifact creation required narrow execution escalation; the first restricted attempt failed before provider dispatch with native state/app-server errors. That failed startup is not counted as a successful native call.

Thread identity appears only in `thread.started`; turn records omit it. A parser closure created by each `start` associates that attempt's terminal turn with its thread. A shared mutable current-thread slot would cross-wire concurrent calls. Reported usage currently remains unknown: the emitted aggregate does not establish its child-inclusion scope. Reported loaded skills remain unknown; the stream did not emit reliable loading evidence. Parent native identity is null for this fresh root; no child-parent records are fabricated.

A harmless denied write was observed with read-only sandbox and approval policy never. The requested file was absent. Native stderr contained:

    WARN codex_sandboxing::violation: recorded sandbox violation: resource=filesystem backend=seatbelt reason=operation_not_permitted path=unknown

However the CLI exited 0 and stdout still contained an ordinary successful assistant envelope and `turn.completed`. Therefore native exit/final result alone cannot prove permission success. The per-launch parser observes both streams and treats the exact native sandbox-violation diagnostic as terminal failure; other stderr warnings remain raw evidence. Before the shared dual-stream seam is integrated this denial remains a demonstrated blocker, not a passing provider check.

## Freshness, correction and stopping

Every ordinary call, independent review, later invocation and requested correction starts a fresh native process/thread. `canReuse` returns false and direct supplied native reuse refuses. The common runner can select its single permitted fresh correction with the same validated profile and explicit saved context; the adapter never retries. Stop delegates only to the runner's existing owned-scope stop callback. Native group absence must be proved by the runner; optional telemetry cannot prove cleanup.

## Verification status

Pinned Node is `24.22.1`; package dependencies were installed from the existing offline lockfile cache with scripts disabled. Source/declaration build passes. Five public constructor/parser checks pass for final/error boundaries, literal instruction/resource delivery, exact executable digest and arguments, unsupported combinations, per-launch concurrency isolation and native stderr denial detection. The final full provider run observed 13 cases: 5 passed, 8 failed, zero skips/cancellations. All eight failures expose `Codex requires per-launch event parser support`; these are dependency failures, not accepted provider behavior. The eight public workflow subprocess cases remain blocked by the unchanged old runner, which does not consume launch-scoped parsers. The cases stay enabled and reject this compatibility failure instead of treating generic failure as successful denial/stop proof. No shared file was edited by this provider task.

The maintained provider fixture runs a real executable subprocess through `WorkflowContext.agent` and inspects saved attempts/sessions/captures. Added scenarios cover success, malformed output, native errors, permission denial, fresh correction/review, concurrent sessions and timeout stop. Their final result awaits the parent-owned seam. Registration is parent-owned; direct focused command from `packages/software-factory`:

    <pinned-node> scripts/build.mjs
    <pinned-node> --test test/codex-adapter.test.mjs

Remaining authorized native checks: one same-invocation malformed-result/fresh-correction pair with instruction/resource delivery, then one harmless workspace-write marker plus bounded native stop. No broad model, native skill, native reuse, Windows or remote-child qualification is claimed.

## Checkpoint and next owner action

Provider writes stop at this checkpoint for the parent-owned shared stream-seam integration and independent review. The parent must supply a verified common commit implementing optional launch-scoped `mapEvent(line, channel)` and selected `eventChannels`, then request resumption. Rerun the complete 13-case provider file, strict source/qualification typechecks and fresh build against that integrated source before any additional live call. Current native call accounting is three attempts: one restricted startup failure, one harmless success, and one harmless read-only denial. No further native call ran after the parent's pause. Remaining allowance is at most three calls.

After the common gate passes, run a two-call same-invocation read-only invalid-result/fresh-correction pair with supplied skill/resource bytes. Then, if feasible, run one harmless workspace-write marker followed by owned-scope timeout/stop to establish editing authority and native group absence together. Workspace-write capability remains refused until this native proof exists. `/tmp/factory-codex-live-proof.mjs` is a prepared disposable proof driver, not executed evidence; inspect and adapt it after integration rather than treating it as a maintained suite. Native raw evidence from the existing calls is under `/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/factory-codex-live-i4zpt9ab/` (`stdout.jsonl`, `stderr.txt`, `denial.stdout.jsonl`, `denial.stderr.txt`, `command.json`). Those files contain only harmless prompts and native output, never authentication material.

Reflection review completed using the brain index and existing testing/security notes. The durable protocol findings are encoded in provider checks and this qualification document; no brain, skill, shared type/store/runner or registry edit is needed from this bounded task.
