# Closed Windows startup helper source audit

Observed 2026-10-21 PDT. Independent read-only audit supports implementing and natively qualifying the closed modes below. It found no application-source path launching external programs in those modes. No executable was launched, dependency installed or runtime source changed. This is neither native qualification nor exact source-to-binary equivalence. [Artifact provenance](windows-startup-artifacts-2026-10-21.md) retains official releases and exact archive/executable hashes.

## Git metadata call graph

Exact Git for Windows source: `2b8a3ab140826ac423c2845ef81d4c6ac4f7bf3c`. Windows `compat/mingw.c:4321` wmain performs std-handle redirection/environment/console initialization, then common-main/common-init initialize Git, gettext/repository state and trace2. `git.c:917` cmd_main parses fixed --no-pager and --no-lazy-fetch; run_argv:837 -> handle_builtin:749 -> run_builtin:466 -> selected builtin -> exit before alias/external fallback. `--no-pager` fixes use_pager=0; --no-lazy-fetch sets fetch_if_missing=0 and GIT_NO_LAZY_FETCH=1.

- Fixed rev-parse --show-toplevel, --path-format=absolute --git-common-dir, and --path-format=absolute --git-dir perform repository discovery/default configuration, then print paths directly. No selected arguments reach revision/object parsing. See [versioned rev-parse source](https://github.com/git-for-windows/git/blob/2b8a3ab140826ac423c2845ef81d4c6ac4f7bf3c/builtin/rev-parse.c#L704).
- Fixed worktree list --porcelain -z dispatches list:1081 -> get_worktrees -> show_worktree_porcelain:963. Porcelain avoids human abbreviation/commit-description logic. [worktree.c:185](https://github.com/git-for-windows/git/blob/2b8a3ab140826ac423c2845ef81d4c6ac4f7bf3c/worktree.c#L185) enumerates current/linked registrations; add_head_info:41 resolves raw HEAD refs. refs.c:2075 follows bounded symbolic refs through compiled-in files/packed/reftable readers, without object peeling/fetching. Lock/prunable annotations read filesystem state without pruning or registration mutation.
- Configuration includes read files with maximum depth10. includeIf.onbranch uses raw ref resolution; includeIf.hasconfig scans URL strings. Default configuration records values. These paths do not read/refresh the index, query fsmonitor, start maintenance, or execute editors/askpass/hooks/filters. See [config.c](https://github.com/git-for-windows/git/blob/2b8a3ab140826ac423c2845ef81d4c6ac4f7bf3c/config.c#L142) and [raw refs](https://github.com/git-for-windows/git/blob/2b8a3ab140826ac423c2845ef81d4c6ac4f7bf3c/refs.c#L2075).

Use an allowlisted factory-owned environment. Windows startup processes GIT_REDIRECT_STDIN/STDOUT/STDERR before main; exclude them. Exclude GIT_ASK_YESNO (a command in mutation retry paths) and GIT_STRACE_COMMANDS. Trace2 can take configured file/socket destinations before command-line config: set fixed GIT_TRACE2=0, GIT_TRACE2_EVENT=0, GIT_TRACE2_PERF=0, rather than merely dropping inherited trace variables. Exclude other inherited GIT_* and loader/search controls except explicit fixed values. Metadata source proof needs no hook/filter suppression; preserve accepted configuration semantics. Arbitrary Git, checkout/worktree add, selected-ref/object peeling, caller flags and PATH wrappers remain excluded.

## Compiler call graph and package binding

Exact TypeScript source: `2bd066d87f5bafd315be9f40889d0a60b9e58e0b`. Windows loader/Go initialization -> cmd/tsgo/main.go:17 runMain -> fixed first argument -p -> sys.go:62 newSystem -> execute/tsc.go:52 CommandLine -> ParseCommandLine -> tscCompilation:121 -> explicit generated config -> performCompilation:333 -> compiler.NewProgram:274 -> source/module/package JSON parsing and typechecking -> compiled-in transforms/printer/filesystem emission. Source text is parsed, not executed/imported as JavaScript. Production exec.Command("npm",...) belongs to cmd/tsgo/lsp.go:59; fixed -p excludes runLSP and its automatic type acquisition. See [dispatch](https://github.com/microsoft/typescript-go/blob/2bd066d87f5bafd315be9f40889d0a60b9e58e0b/cmd/tsgo/main.go#L17), [compilation](https://github.com/microsoft/typescript-go/blob/2bd066d87f5bafd315be9f40889d0a60b9e58e0b/internal/execute/tsc.go#L333), [LSP launch](https://github.com/microsoft/typescript-go/blob/2bd066d87f5bafd315be9f40889d0a60b9e58e0b/cmd/tsgo/lsp.go#L59).

Actual PE buildinfo was decoded without execution: go1.26.4; microsoft_systemcrypto=1; microsoft_toolset_version=go1.26.4-1-microsoft; buildmode=exe; compiler=gc; tags=noembed; trimpath=true; CGO_ENABLED=0; GOARCH=amd64; GOOS=windows; GOAMD64=v1; vcs.revision matches the exact source; vcs.modified=true.

Consequently internal/bundled/noembed.go:22-49 resolves the executable and reads adjacent packaged libraries. Bind the entire platform package/library inventory, not tsc.exe alone. [Herebyfile.mjs:221-225](https://github.com/microsoft/typescript-go/blob/2bd066d87f5bafd315be9f40889d0a60b9e58e0b/Herebyfile.mjs#L221) adds noembed; :1928-1935 generates/copies libraries and builds native packages with CGO_ENABLED=0. The PE imports only kernel32.dll. The generated config must be complete and invocation-owned: no extends/references/plugins/watch/incremental/composite/build/profiling/tracing/arbitrary options or caller compiler host. Exclude TS_GO_DEBUG_STACK_LIMIT and inherited runtime/loader debug controls.

## Git dependency identity

Bind official archive layout, canonical executable/dependency paths and installation trust. Hashing git.exe alone does not cover replacement DLLs. Non-system imported closure under mingw64/bin:

| Member | SHA256 |
| --- | --- |
| libiconv-2.dll | 7a282a854e01be726c6cccfe46f548c716aa45b3014818468253aaa4efbcd067 |
| libintl-8.dll | 0537c3dd2378218508ebe3cc416d72a99ee2d24ae1c5525e23458f32544ef861 |
| libpcre2-8-0.dll | c135a87ed0f11eae8ffc4cb469671ff0b3f5d71fab5fb024e9b1e7241ca25b52 |
| libwinpthread-1.dll | 851f61482ad5b6aac7c6abc54bbe31d24f89e0ca683a75fcec2d47f86b2d2242 |
| zlib1.dll | 93e9243a44c29200eeacaf9658efe2558581770e4b11ca4b500e18e424a6e3b5 |

Native qualification must verify actual loaded module paths. This is a future profile admission requirement, not a reproduced vulnerability in an implemented profile.

## Promotion boundary and native proof

Official release digests plus versioned application-source audit and native adversarial qualification can support a narrow helper contract with ordinary trust in official libraries/runtime/toolchain. The dirty build flag and unreviewed Microsoft Go/dependency mappings prevent claiming exact source-to-binary equivalence. That stronger claim would need official build attestation/logs identifying toolset and modified/generated inputs; it is not a prerequisite to designing the closed mode.

Implement only a private operation discriminator with exact argv/config/cwd/artifact identity, ignored stdin, captured pipes and fixed environment. Revalidate repository/worktree under exact claim. Observe direct exit and stream closure; timer/kill submission is not completion. Recorder/identity/termination uncertainty retains occupancy and prevents activation. No public noChildren flag, wrapper admission, automatic downloads, Job Object subsystem or tracker.

Native matrix: normal/linked/relative and files/reftable/unborn/malformed registrations; hostile includes/hooks/filters/fsmonitor/pager/remote/credential canaries; PATH wrapper/shim and binary/DLL/package/library tampering/replacement; source/package text that looks executable; hostile authored tsconfigs; success/error/no output; one build; bounded diagnostics; interruption/capture failure before spawn and during compile; actual loaded modules; arbitrary detached command children remain unknown. Checkout remains outside the helper scope. Foundation CI is insufficient proof.
