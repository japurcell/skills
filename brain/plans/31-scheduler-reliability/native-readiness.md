# Native readiness and approved qualification scope

Task date: 2026-11-11, America/Los_Angeles. Native observations were captured against source `df54c117e8b8bccc46420d87ae6e3671c6c14ae1`. Workspace is `/Users/adam/.codex/worktrees/48fd/skills`, on `scheduler-reliability`; Q1-A setup/launch and Q1-B evidence validation are now integrated through `f79e560b39778ac96b236a8e1858d3348c048586`, pending the review-reproduced lexical traversal correction and fresh independent review. No model inference, smoke, or scored call has run.

## Current user decisions

- Trust only the two run-01 Codex pilot projects and their pinned hooks in private Codex state. The exact projects are `/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-current-payload/run-01/cells/codex-baseline/repo` and `/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-current-payload/run-01/cells/codex-candidate/repo`, each using its sibling `provider-home/.codex`. Fresh preparation paths need a new exact setup review before trust changes. Global Guardian and global trust remain unchanged.
- Keep Copilot on the existing process-token route. Do not add private OAuth support or alter its credential store.
- Use verified evidence from each observed pilot run instead of a universal hook-enforcement guarantee. Retain trusted pinned hooks, both smoke checks, real command receipts, forbidden-probe rejection, and invalidation on missing or unexpected evidence.
- Sol with medium reasoning applies only to this plan's implementation and review subagents.
- Live calls still require explicit approval of the final exact payload.

## Codex observations

Installed Codex is 0.167.1. The documented native app-server `hooks/list` request needs no thread, turn, or authentication. Both fresh private cells initially returned no hooks, with diagnostics identifying untrusted projects. After the approved project-trust entries were written only to the two private Codex config files, each request discovered exactly one enabled synchronous project PreToolUse command with the expected definition, policy, manifest and cell arguments. Both definitions remain `trustStatus=untrusted`.

| Cell | Native currentHash | Current result |
| --- | --- | --- |
| codex-baseline | `sha256:0b0a036f0376be1848711dda80faffbf51078691fcf653791e54b2c31142f227` | Project trusted; hook definition untrusted |
| codex-candidate | `sha256:1da67cf32d6e06ff5057dfc6a07dc8393a86beb9cd658600a4cc8c9f645a1747` | Project trusted; hook definition untrusted |

The native hash is not the hook file's byte hash; no hash or trust-store entry was guessed. The documented `/hooks` UI was attempted under each private environment without submitting a prompt. Both TUIs stopped at authentication onboarding, so definition trust could not be completed. No authentication choice or credential copy occurred. All discovery/TUI leaders were reaped; final checks confirmed their process groups absent.

The original inspected source had circular unconditional Codex gates. Accepted Q1-A now supplies pinned private setup discovery and provider-specific smoke launch. B now validates phase receipts and raw evidence, including replay protection and both-smoke scenario gating. Offline Copilot fixtures exercise that path with real child/file operations; actual native qualification remains unestablished. The [exact exec mapping inspection](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-readiness-current/exec-evidence-mapping.md) supports Codex 0.167.1 thread/item pairing while executing selector and hook tool-use correlation remain unsupported. Missing required evidence invalidates qualification.

Official references: [Hooks](https://learn.chatgpt.com/docs/hooks), [app server](https://learn.chatgpt.com/docs/app-server), [configuration](https://learn.chatgpt.com/docs/config-file/config-reference). The docs describe skips, error paths that continue a call, incomplete hook coverage and continuation exceptions. Trusted discovery is metadata evidence; it does not prove callback execution or universal prevention.

Retained no-inference [safe config projection](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-readiness-current/native-config-projection-supported-argv.json) and [layer projection](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-readiness-current/native-config-layer-projection.json) grounded the installed version's private configuration shapes and empty absent system layer. They exposed unsupported app-server `--ignore-rules`; B removed it from both discovery and exec. All three probe groups were reaped without starting a thread or turn. These observations establish configuration compatibility only.

## Copilot observations

Installed Copilot is 1.0.109. `COPILOT_GITHUB_TOKEN`, `GH_TOKEN` and `GITHUB_TOKEN` were absent from the invoking process; only presence was inspected. The installed CLI has no `auth status` command. One documented, non-refreshing `gh auth status --active --hostname github.com --no-refresh --json hosts` probe reported active account state `error`; JSON exit 0 did not mean healthy authentication. No token or credential store was read, copied or changed.

[GitHub authentication docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/authenticate-copilot-cli) describe other OAuth/keychain and gh routes, but this does not establish that those routes preserve the pilot's private HOME/COPILOT_HOME contract. The user selected the existing process-token route. A supported token must reach the actual runner process securely; exporting it in an unrelated terminal does not change this agent's environment. Do not request credential values in chat or put them in artifacts.

The [retained Copilot write mapping](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-readiness-current/copilot-write-mapping.md) grounds raw single Add File patch input, matched call/turn IDs and exact create completion/readback. B supports that confined form and rejects selector contradictions. Retained historical evidence and synthetic fixtures establish no current native provider qualification.

## Preparation and next work

The retained provisional preparation against `df54c117` verified all six baseline hashes and froze eight proposed calls, four smoke plus four scored, 600 seconds each with zero retries. It is not a ready or approved execution payload. Fresh public preflights both exited 2 with their exact blockers retained. The model-attempt ledger remains zero.

The bounded qualification design is complete in the [current T4-Q1 contract](ExecPlan.md#t4-q1-current-observed-run-qualification-implementation-contract). T4-Q1-A is accepted and integrated at `cba7ba04`, with seven focused tests passing and zero remaining fake-provider servers. Its [retained outcome](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-Q1-A/outcome.md) summarizes the red/green and cleanup evidence linked in the plan. T4-Q1-B implementation is integrated at `f79e560b`; its [retained outcome](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-Q1-B/outcome.md) records 33 tests passing in 128.223 seconds plus two strengthened checks and zero remaining fake-provider servers. [Qualification review pass 1](review-qualification.md) is complete with zero Standards findings and one P2 Spec defect accepting lexical patch traversal. T4-Q1-R1 is assigned to `/root/observed_qualification` in `/private/tmp/skills-scheduler-observed-qualification`; correction and fresh independent review remain pending. Implement the qualification path within that contract: establish private setup/discovery without inference; run approved neutral smoke under frozen conditions; require both variant observations before scored scenarios; fail qualification on absent/unsupported telemetry, auth failure, drift, missing receipts, unexpected tools or hook errors. Unsupported native telemetry may yield an invalid smoke and stop dependent scenarios; it is not permission to invent proof, silently switch transports or add model calls. Native model/effort observation remains required.

Private Codex authentication is still needed to reach `/hooks`; Copilot still needs its selected process token. Fresh independent source review must complete before final payload preparation and approval. Native prerequisites remain outstanding. Global auth/trust changes and copied credentials remain outside scope.

## Retained evidence

- [Codex readiness](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-readiness-current/codex.md)
- [Copilot readiness](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-readiness-current/copilot.md)
- [Qualification decision](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-readiness-current/codex-qualification-decision.md)
- [Private trust changes](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-readiness-current/codex-setup-project-trust.json)
- [Final setup state](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-readiness-current/codex-setup-final-state.json)
- [Current source receipt](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-current-payload/source-receipt.json)
- [Offline command ledger](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-current-payload/offline-command-ledger.json)
- [Proposed calls, not approval](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-current-payload/proposed-calls.json)
- [Zero-attempt ledger](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-current-payload/model-call-ledger.json)
- [Concrete setup review](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-current-payload/setup-review.md)
