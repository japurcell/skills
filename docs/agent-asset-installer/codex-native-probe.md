# Codex native containment and trust probe

Observed 2026-09-30 UTC on macOS 26.7 arm64 with existing Codex CLI 0.159.0. This bounded experiment follows the integrated [isolation research](codex-isolation-research.md) and `docs/agent-asset-installer/client-validation.md` at source checkpoint `74f9bcb5`. It changes no installer source, installs no dependencies, and does not satisfy native client acceptance.

## Achieved proof

The host supplies `/usr/bin/sandbox-exec`. Its installed manual identifies it as deprecated; Apple's installed sandbox profiles explicitly call their syntax private and subject to change. This result establishes a local experiment boundary on this host, not a portable supported isolation product.

A unique `/private/tmp/codex-native-isolation-cox5fdna` tree held `state/` and a separate `outside/` sentinel directory. Before launching Codex, a Python child ran under an explicit deny-default sandbox. Read/execute access was limited to system runtime trees, the exact bundled Python runtime, the installed Codex binary directory, and allocated state. File writes were permitted only inside allocated state, with normal character-device exceptions. Mach services, personal file contents, and other operations remained denied. Only one allocated `localhost:PORT` outbound endpoint was permitted.

The actual containment probe returned exit 0 with these results: inside read/write succeeded; its allocated loopback connection succeeded; outside sentinel read/write/create, a different active loopback listener, and a TEST-NET external connection all failed with `EPERM` (errno 1). The outside sentinel remained byte-identical and no outside file was created. The listeners were closed by their owning context managers. No model or client process ran before those assertions passed.

The minimal child environment included only allocated `HOME`, `CODEX_HOME`, `CODEX_SQLITE_HOME`, `TMPDIR`, XDG cache/config/data locations, system-only `PATH`, locale and terminal type. It inherited no credentials, proxy configuration, shell initialization, or personal Codex configuration. The disposable `config.toml` set `cli_auth_credentials_store = "ephemeral"`, a unique `loopback_fixture` provider, `requires_openai_auth = false`, `wire_api = "responses"`, zero request/stream retries, and a loopback base URL. There were no provider keys, authorization headers, trust records, hooks, plugins or MCP servers.

Within that same confinement, both `codex --version` and `codex --help` returned exit 0 with empty stderr. The exact version was `codex-cli 0.159.0`. This demonstrates help-only startup and disposable-home helper compatibility, improving on the earlier unconfined-home PATH-alias warning. It does not prove a model session or normal trust persistence.

## Normal UI and exact blocking gate

The ordinary TUI initially refused its background server with `Operation not permitted (os error 1)` and explicitly suggested `--no-daemon`. No broader service access was granted. The supported foreground invocation `codex --no-alt-screen --no-daemon` then reached the normal `Folder access` screen for the disposable project. Its first choice was `Trust and continue` and its second was `Quit`.

Selecting the first choice through the actual PTY, without writing trust configuration, produced:

    Failed to set trust for <disposable project>:
    config/batchWrite failed in TUI: config/batchWrite failed: failed to load
    configuration: Failed to synchronize managed preferences (code -32603)

The native trust decision was not saved: the disposable config contained neither `trust_level` nor a project trust entry afterward. Escape exited the foreground wrapper with code 0. The experiment stopped at this concrete gate. Granting shared preference services or reading personal preference/configuration state to make trust succeed was not attempted. The exact failing preference operation was not isolated; the message is evidence of failure, not proof of one specific denied Mach service.

No prompt was submitted, no model fixture or external provider was invoked, and no native hook review, skill activation, reference read, agent spawn, or event delivery occurred. Distinctive assets were not installed because the prerequisite normal trust gate failed before the discovery experiment. Predetermined fixture output and direct script execution were not used as substitutes.

## Reproduction details and limitations

The successful containment profile used `(version 1)`, `(deny default)`, Apple's inspected `dyld-support.sb` import, process execution/fork, baseline syscall/bootstrap, sysctl read and file-metadata traversal. Runtime read/map allowlists covered `/System`, `/usr`, `/bin`, `/sbin`, the exact desktop Python dependency directory and `/Users/adam/homebrew/Caskroom/codex/0.159.0/bin`. The profile allowed read/write under the unique `state` directory, normal `/dev/null`, `/dev/random`, and `/dev/urandom` access, and `(allow network-outbound (remote ip "localhost:PORT"))`. Numeric `127.0.0.1:PORT` syntax was rejected by this sandbox parser. The base-profile SHA-256 was `318813f1faa8ce53166973935e62f78423ef95925e20c7d426f4195c8dc01c59`.

The UI profile additionally allowed read/write/ioctl only on `/dev/tty` and the exact allocated PTY device. RTK pipes child stdout, so the harness attached the Codex child's standard streams directly to that already allocated PTY; otherwise Codex returned `stdout is not a terminal`. The UI-profile SHA-256 was `9b1a34dab66d5f22ff786bdcac8a6ac4f8cfbcc568f469a7bb5e7091a5f77ab0`. The minimal profile without Apple's dyld bootstrap support aborted even a system binary; no client experiment proceeded until the sentinel probe passed with the inspected bootstrap rules.

The outer tool sandbox denied creating even the disposable loopback listeners. Normal tool escalation ran the explicitly confined harness; it did not remove the nested client sandbox. The only outbound connection that succeeded was the disposable listener used in the containment test. The later client profile retained that single now-closed port, so no live model endpoint existed during UI inspection.

The missing prerequisite is a demonstrably isolated environment in which normal Codex managed-preference synchronization and native trust persistence work without access to personal preferences/credentials or weakening managed policy. A disposable OS account/VM with independently established confinement is a candidate, not a completed or authorized provisioning step. Once that prerequisite exists, repeat normal project trust, separate `/hooks` review, distinctive installed skill/reference/agent activation and actual native hook events through a bounded local provider.

## Cleanup and evidence boundary

All foreground client invocations exited, no model server was started, and both containment listeners closed. A targeted `lsof -t +D` check returned no process holding files in the unique experiment tree. The outside sentinel remained unchanged and its forbidden-created neighbor remained absent after the UI attempt. The unique experiment tree and helper pointer are removed after recording this note; no credentials were read or retained. Only this concise research note is preserved. No source, canonical documentation, base-worktree, M7, commit or push operation is part of this probe.
