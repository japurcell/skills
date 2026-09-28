# RTK 0.50.0 release facts

Verified 2026-09-28 against the official RTK GitHub release, its tagged documentation, and its release assets.

## Findings

- **Stable release:** `v0.50.0` is a non-prerelease release dated 2026-09-24, published from commit `1d87b8e`; GitHub marks the commit signature verified. The release notes include the `suppress_hook_warning` config option and Codex direct command rewrite. [Release](https://github.com/rtk-ai/rtk/releases/tag/v0.50.0)
- **Warning control:** `RTK_SUPPRESS_HOOK_WARNING=1` suppresses only the missing-hook warning, not the outdated-hook upgrade prompt. Accepted true values are `1`, `true`, `yes`, and `on`. `0`, `false`, `no`, or `off` force the missing-hook warning on, overriding `hooks.suppress_hook_warning`. The persistent config equivalent is `[hooks] suppress_hook_warning = true`. [Tagged configuration guide](https://raw.githubusercontent.com/rtk-ai/rtk/v0.50.0/docs/guide/getting-started/configuration.md)
- **Agent invocation implication:** RTK's tagged configuration guide says agents without a hook, including Codex CLI, get `awareness.level = "full"`, which tells the agent to prefix commands with `rtk`. Such explicit invocations still run RTK, and therefore encounter its no-hook warning unless the environment variable or config suppresses that specific warning. Suppression does not disable RTK, its filters, or its other diagnostics. The docs do not promise unchanged exit codes; this ticket's hook-warning change should preserve existing command and diagnostic behavior and avoid altering exit-code paths. [Tagged configuration guide](https://raw.githubusercontent.com/rtk-ai/rtk/v0.50.0/docs/guide/getting-started/configuration.md)
- **Official binary assets:** The release publishes macOS Intel and Apple Silicon, Linux x86_64 musl and aarch64 GNU, and Windows x86_64 MSVC archives, plus Linux `.deb`/`.rpm` packages. `checksums.txt` is present. [Release asset listing](https://github.com/rtk-ai/rtk/releases/expanded_assets/v0.50.0)

| Asset | SHA-256 |
| --- | --- |
| `rtk-aarch64-apple-darwin.tar.gz` | `fe54761a9950266e3a78ddb66a8af5e067251169da306a288e0751de63d836fe` |
| `rtk-x86_64-apple-darwin.tar.gz` | `ac23e20024ab3c71e7f50069f8b34190aec1b2d8f0c2cc19834039b3dac73373` |
| `rtk-aarch64-unknown-linux-gnu.tar.gz` | `d1cc49dfa2cd443fc32625444b59fe616b6c80478cca210985118347174dd758` |
| `rtk-x86_64-unknown-linux-musl.tar.gz` | `bc2b8902b0d9c796c82ef45f16ae2307e17757afeca5ee156235a3dc7bda5f89` |
| `rtk-x86_64-pc-windows-msvc.zip` | `cb03399305135dd59ee23eb59a3260ccdeea5a8e08fbc7a271b115b85583a6c9` |
| `rtk_0.50.0-1_amd64.deb` (`rtk_amd64.deb`) | `5ce4262814d7941f25f9055ffec751d95f3296df8465a9aabca52b498dd71acd` |
| `rtk-0.50.0-1.x86_64.rpm` (`rtk.x86_64.rpm`) | `31e88c8a3c6a359a87a46e207042444ef62cbc0bce397a8318e205e7d17222fc` |

- **Installation paths:** Tagged docs recommend the release archives for all three OS families; `install.sh` supports Linux/macOS x86_64 and aarch64, resolves latest release or accepts `RTK_VERSION`, downloads `checksums.txt`, and verifies SHA-256 before install by default. Docs also list Homebrew for macOS/Linux and winget for Windows. [Tagged installation guide](https://raw.githubusercontent.com/rtk-ai/rtk/v0.50.0/docs/guide/getting-started/installation.md), [tagged install script](https://raw.githubusercontent.com/rtk-ai/rtk/v0.50.0/install.sh)

## Decision-relevant summary

The stable tag and checksummed platform artifacts are available, so the pinned prerelease can be replaced with `v0.50.0`. When explicit agent `rtk` commands are used, set `RTK_SUPPRESS_HOOK_WARNING=1` in that agent's command environment or persist `[hooks] suppress_hook_warning = true`; this silences only the missing-hook notice and leaves RTK operation intact. Do not claim an exit-code guarantee beyond preserving existing paths.
