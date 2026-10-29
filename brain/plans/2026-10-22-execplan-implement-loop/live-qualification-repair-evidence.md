# Live qualification repair evidence

Bounded research for T25, T28, and T31. Repository source was read-only during research. No Gemini CLI execution, authentication, model call, or repository edit occurred.

## LQ-1: Version boundary

- skills/default/execplan-implement-loop/scripts/readiness.py accepts a parsed semantic version only when it equals 0.65.0. It uses a bounded [executable, --version] subprocess and rejects malformed output, timeout, truncation, or nonzero exit.
- This is an exact qualification pin. The observed rejection of 0.66.0 does not establish incompatibility. Keep 0.65.0 as the only qualified version until a separately scoped compatibility review proves more.
- The local runner and qualification helper already accept an explicit --gemini executable path. Document selecting the known binary with that option; do not change the global install.
- Pinned primary sources: [Gemini CLI v0.65.0 release](https://github.com/google-gemini/gemini-cli/releases/tag/v0.65.0), [v0.65.0 CLI reference](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/docs/cli/cli-reference.md), and [v0.65.0 package metadata](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/packages/cli/package.json).

## LQ-5: Trust remains unknown locally

- Readiness inventories selected settings and policy files but does not inventory trustedFolders.json; trust remains unknown. gemini --version exits before normal workspace startup and cannot prove trust.
- The pinned [trusted-folders guide](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/docs/cli/trusted-folders.md) documents the trust file, environment signals, and interactive trust prompt. The pinned [settings reference](https://github.com/google-gemini/gemini-cli/blob/v0.65.0/docs/cli/settings.md) gives a default for security.folderTrust.enabled that conflicts with the trusted-folders guide's default. Do not infer effective trust from either default, a saved trust file, or doctor.
- Keep T28 to exact-folder interactive owner steps for the disposable project/ directory. Do not add automatic trust writes, broad /tmp trust, or a readiness probe.
- The v0.65.0 trust-file schema and complete resolver were not audited.

## LQ-8: RTK invocation evidence

- The exact original multiline worker command was not retained, so its shell parse error cannot be attributed to RTK.
- With RTK 1.1.0, representative multiline python -c programs succeeded through rtk test and rtk proxy, and the same literal argv succeeded directly. Each exited 0 and preserved a trailing argument containing a newline. The test printed RTK_ARGV_PROBE_OK; the proxy probe printed the same marker; the direct child printed DIRECT_ARGV_PROBE_OK.
- These bounded probes establish only that those direct-argv shapes work. The caller's shell quote processing determines argv; shell parsing is opt-in through RTK's shell mode. They do not establish the cause of the earlier failure.
- T31 must compare argv/results in an isolated representative reproduction and keep the original cause unknown if it cannot be reproduced. Use direct argv or stdin only when evidence shows the wrapper changes required behavior. Do not add a shell runner.
