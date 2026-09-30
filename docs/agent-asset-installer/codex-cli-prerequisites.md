# Codex CLI acceptance prerequisites

Observed on 2026-09-29 local date, macOS arm64, using installed Codex CLI 0.159.0. This is prerequisite inspection, not native discovery or hook-delivery proof.

`/Users/adam/homebrew/bin/codex` points to the Homebrew Caskroom 0.159.0 binary. `codex --help` and `codex exec --help` are inspected without starting a model session. The CLI attempts PATH alias setup even for help; the sandbox refuses that attempt and help remains available. No approval bypass, account configuration change, or live client operation is performed.

The installed help offers `exec --ephemeral` to avoid session persistence and `--ignore-user-config` to omit the base user configuration. Auth still uses the existing Codex home. `--profile` adds a file within that home rather than providing an independent profile directory. These flags alone therefore do not prove a fully isolated client profile. Native acceptance must demonstrate isolation before starting the client.

[Official hook documentation](https://learn.chatgpt.com/docs/hooks) specifies additive matching hooks, trusted project configuration, and separate review of the exact non-managed hook definition. New or changed definitions require review. The plan requires the normal native trust flow and does not use `--dangerously-bypass-hook-trust`.

[Official advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced) states that untrusted projects omit their project configuration, hooks, and rules while user layers remain independent. A project trust decision and hook trust are separate acceptance prerequisites. Do not count a direct installed-script subprocess as event delivery.

[Official non-interactive guidance](https://learn.chatgpt.com/docs/non-interactive-mode) documents ephemeral runs and omission of base user configuration. Keep these options distinct from proof that all client writes and personal hooks are isolated. Exact auth/profile mechanics and native trust persistence still need verification in milestone 6. Other advertised clients and native Windows/Linux runners remain unavailable locally.
