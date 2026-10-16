# T5b-M composed gate evidence

Observed on 2026-10-16 in `/Users/adam/.codex/worktrees/design-b-t5b/skills`, branch `codex/design-b-t5b`. Native platform: macOS 26.7.1 arm64, Git 2.54.0 (Apple Git-157), Python 3.14.6 and 3.13.14, SQLite 3.51.0, RTK 0.51.0. All fixture repositories, installed bundles, homes, dispatchers and bare endpoints were disposable. No external push, real-home deployment, hook trust/enablement change or global Git mutation occurred.

## Branch composition and ownership

The primary froze clean base `15ba7629ea10aab52739d5a6c6dabc5e352ca755` and assigned exclusive private-worktree ownership to this fresh merger. Original candidate `835d0e110de8db845a3665ce69a977bc7eec4789` was exactly one commit after `cce735f0b0c81f514e6f38f730c291571fc7c8d3`. Its rebase produced source commit `dee1f6439c186aed34fe1c53acfc28d2a3f2324b`, directly after that frozen base. The original implementer stopped edits before dispatch. The primary reviewed the canonical/test composition diff and independently confirmed both outgoing modules and original T5b evidence unchanged.

This completes the private T5b-M composition proof described by [the ExecPlan](ExecPlan.md). The primary alone owns fast-forwarding the base, reconciling plan/delegation status, T5-I acceptance and the final coordinated knowledge-maintenance pass. This report does not accept T5-I, T6, T7 or the full milestone.

## Canonical conflict choices

- `hooks/runtime/scan_cli.py` retains accepted `staged_gate=is_gate` selection, changed-staged-file help and `changed_staged_files` metadata for pre-commit. It adds the candidate publication collector, publication budget, transaction identities, truthful audit metadata and cancellation handling. It never restores the old `full_index` engine flag.
- `hooks/runtime/scan_gate.py` retains `selected_staged_v1`, the base removal of the obsolete full-index collector and strict caller-owned admission. Its action-specific publication schema/identity/count validation remains the candidate implementation; its pre-commit scope-description ternary is `changed_staged_files`.
- `hooks/runtime/scan_status.py` admits historical `selected_index_v1` index reports, current `selected_staged_v1` index reports and `publication_v1` outgoing reports. Historical display never grants gate admission. The real commit mutation case still proves old `selected_index_v1` cannot authorize the current gate.
- `scripts/test-scan-secrets-git-gates.py` retains every outgoing case and all approved staged controls: unchanged fake fixtures permit unrelated commits; unchanged secret lines in changed files block; selected/alternate/partial/split indexes, SHA-256 object verification, unresolved indexes, new/renamed credential paths reusing old bytes and source-free installed selection remain covered. The installed staged fixture retains its copied-source deletion and expects the combined 16-file closure.
- Generated conflicts in all three providers' scanner and diagnostics outputs were resolved only by `scripts/generate-hooks.py --write`, followed by `--check`. Canonical publication and transaction modules stayed byte-identical to the frozen candidate, preserving full immutable graph/message/blob/path coverage, complete remote-old subtraction, hash/type/size checks, distinct-object/logical/capture/temp accounting, private bounded SQLite validation and retained findings.

The first conflict-replacement helper failed an assertion and then a syntax check during resolution. Canonical files were reconstructed from exact Git versions, the narrow composition diff was reviewed and all resolved Python compiled before the first suite. No product test failed and no assertion was weakened, removed or skipped for this composition.

## Serial verification against the composed source

Working directory for every command: `/Users/adam/.codex/worktrees/design-b-t5b/skills`. Each command used `rtk proxy`, `login:false`; native process cleanup and private-worktree mutations used scoped sandbox escalation. Suites ran one at a time. No edits or other suites overlapped generator snapshots or timing checks.

| Command after `rtk proxy` | Observed result |
| --- | --- |
| `python3 scripts/generate-hooks.py --write` then `--check` | Canonical regeneration; all 62 generated assets current |
| `python3 scripts/test-scan-secrets-git-gates.py` | 62/62 pass, 46.280 seconds, Python 3.14.6 |
| `python3 scripts/test-scan-secrets-cli.py` | 35/35 pass, 17.292 seconds |
| `python3 scripts/test-scan-secrets-status.py` | 29/29 pass, 14.933 seconds |
| `python3 scripts/test-install-scan-secrets.py` | 21/21 pass, 39.982 seconds; real Bash and macOS PowerShell installers in disposable homes |
| `python3 scripts/test-generate-hooks.py` | Isolated 26/26 pass, 17.839 seconds |
| `python3 scripts/generate-hooks.py --check` | All 62 generated assets current after the generator suite |
| `/Users/adam/.pyenv/versions/3.13.14/bin/python3 scripts/test-scan-secrets-git-gates.py` | 62/62 pass, 44.848 seconds, Python 3.13.14 |
| `git diff --check` | Pass |

The gate suite grew from frozen candidate 59 to composed 62 by retaining the accepted staged repair additions. It exercises standalone gate processes, actual commits and local pushes through fixture dispatchers, source-free installed commands, caller-output mutations and real installers. The separate outgoing and staged policies, B3 exits, required audit, informational status and declared accounting units pass together. Existing explicit checks retain pending semantics. No new suite or feature was added by this merger.

## Composed runtime fingerprints

Neutral build identity: `09c5d1e64561b2c42789f95eaee3fa031fa743b84ef40f085e01f0bfddff9fab`. It is SHA-256 in entrypoint, CLI, status and listed-module order over each basename, NUL and exact source bytes. The composed runtime closure is 16 files; provider helper closure remains eight; generated ownership remains 62. This source identity supersedes the original private candidate's runtime fingerprint for composed acceptance while preserving the original record as history.

| File | SHA-256 |
| --- | --- |
| `scripts/scan-secrets.py` | `ea9f6adf225889e0ff9297d32e88e9660cea6a9d917ca87f6d95ada6d3afc497` |
| `hooks/runtime/scan_cli.py` | `b1e16a788d2ee0acec65d22a54951a855b52e00e5618c84b8a100003d65c05cb` |
| `hooks/runtime/scan_status.py` | `c52232bf1e36c9d14cbd42f0cd76cc74b124dfefce86c17d6bb4affd8efed2ce` |
| `hooks/runtime/scan_types.py` | `56b06c26769b80b03983430b795a9f8b96c70d8ae399c725715ff952c1cd39d6` |
| `hooks/runtime/scan_reporting.py` | `c57d577217aed68e7e0e191c3225195a1950e0b4fd18c8524f93984a2de2d8c9` |
| `hooks/runtime/scan_allowlist.py` | `80eb5a115707ad03c227b6e3c1c43da463b0ce303a60909f398eab6dd9c7c7e7` |
| `hooks/runtime/scan_stream.py` | `2b91062b6440457ca26488d9dba43e2a4bda9d2a7dc309e256da1c0b6c9b707b` |
| `hooks/runtime/scan_git.py` | `02832f17c495cbd9ed6f7b54772202a0c9f85cc379e5090860cb838dafdb4041` |
| `hooks/runtime/scan_engine.py` | `33bbfb091672a9ef5b03d04c291e9e91ec063945cbbfbc08a0007ab2c3ab2249` |
| `hooks/runtime/scan_native_file.py` | `660222d89c1b01d3ef77a34920362c99d2567a11c98cdddc24db542e34a788fb` |
| `hooks/runtime/scan_audit.py` | `86b5527ad96a9495079b4e3a5fdb6ed8562a900744665c39b9fdd9000ca18451` |
| `hooks/runtime/scan_budget.py` | `0ce123e105ef306fef10c7be66e1666ef890f55463b61360cd9c170fefd40ca0` |
| `hooks/runtime/scan_repository.py` | `9f7dd26815fcbeaa6bd2711f942bdf9d788de73d153de5b62cacc198ece2730a` |
| `hooks/runtime/scan_gate.py` | `19a8cbec8f426d6d096975968e7ae80860fa61684f42580d3715b1b667296186` |
| `hooks/runtime/scan_transaction.py` | `005b2bb173cadf708ccc0f1041404c90797421843a8a88d07e2c626497c90894` |
| `hooks/runtime/scan_publication.py` | `bd138d1f306dd1b28f57fe78259de93248360e2b79da6b14a7cd12893bd70a47` |

## Historical evidence integrity

These files are byte-identical to their respective original candidate or frozen-base versions:

| Evidence | SHA-256 |
| --- | --- |
| [t5b-evidence.md](t5b-evidence.md) | `d47579f82e673adaa7adfc2329c07358ddb751d0e1bb9237f7b03eed8dd8afb0` |
| [t5a-evidence.md](t5a-evidence.md) | `266d47930fd45d340e0754b543abf8d637abdbec52698fb24ba6622fec5653be` |
| [t5a-staged-repair-evidence.md](t5a-staged-repair-evidence.md) | `99c42e4e3722168fbb8e23030d3998f875e7e556a47b91a1451201174fcd73e5` |

The earlier overlapping generator timing failure remains recorded unchanged in the original T5b evidence. This isolated composed generator pass does not erase that observation.

## Limits and next action

This is local native macOS source and disposable installed proof. Native Windows/Linux, hosted CI, authenticated remote delivery and live provider event delivery remain unverified. Supported publication paths still require each component and full encoded path at most 4096 bytes with no CR/LF/backslash or gitlinks; unsupported paths remain explicit incomplete failures. LFS pointers remain incomplete until T6 verifies payloads. Functional streaming/accounting tests are not production capacity or benchmark acceptance.

The next action belongs to the primary: independently verify the clean private tip/evidence identity, fast-forward the frozen base if accepted, reconcile task status and perform the separate T5-I acceptance. This merger stops all edits and Git mutations after its evidence commit. No canonical knowledge-base or skill file changed.
