# T5b outgoing Git publication evidence

Observed on 2026-10-16 in the private managed worktree `/Users/adam/.codex/worktrees/design-b-t5b/skills`, branch `codex/design-b-t5b`, based on `cce735f0`. Platform: macOS 26.7.1 arm64 / Darwin 25.6, Apple Git 2.54.0 (Apple Git-157), Python 3.14.6 and 3.13.14, SQLite 3.51.0, RTK 0.51.0. Every repository, home, temporary dispatcher, installed bundle and local bare endpoint was disposable. No real-home deployment, external push, trust/enablement change, global Git change or production hook installation occurred.

This is the outgoing collector and shared caller-contract node described by [the contract](publication-contract.md) and [source map](publication-source-map.md). It does not accept T5-I, T6 or T7. This private branch preserves its original T5a pre-commit behavior; composition with the separately accepted changed-staged-files repair is the next merger's responsibility. The primary owns active plan reconciliation and the single coordinated knowledge-maintenance pass.

## Delivered contract

`python3 -I -S -B scripts/scan-secrets.py gate pre-push --repo PATH --remote NAME --url URL --json` reads the actual Git four-field stdin transaction exactly once through verified EOF. The optional repository defaults to the current directory. A single absolute two-second acquisition/parse deadline, 1,048,576-byte ceiling and 4,096-record ceiling apply. SHA-1/SHA-256 OIDs are format-specific; malformed/trailing bytes, unavailable input, TTY input and held-open streams are incomplete. Help, version and no-argument routes do not read stdin or inspect Git. Exact bounded original bytes remain on the invocation-owned transaction for later replay; no replay/upload composition is added here.

Destination identity is SHA-256 of `publication-destination-v1` plus NUL-separated encoded remote name and URL. Transaction identity is SHA-256 of `publication-transaction-v1`, NUL, binary destination digest, NUL and exact raw stdin bytes. Raw tuples, credential-bearing URLs and child stderr are never emitted. Verified EOF-empty transactions are complete clean; deletion-only transactions add no local content and need no object-history traversal. Neither launches downstream work.

Every nonzero local tip is selected directly from the captured transaction, including non-HEAD branches, explicit OIDs, multiple updates, force updates, new refs, and annotated tags. No HEAD, upstream or tracking ref is guessed. Only an entire locally available, hash-verified graph rooted at a nonzero remote-old tip in this transaction contributes exclusions. Missing remote-old nodes discard that incomplete graph's exclusions and conservatively traverse local history in full. Required local missing objects, corrupt/type-invalid objects, actual shallow boundaries, grafts, alternates and redirected object stores are incomplete. No fetch occurs.

Publication capture uses a separate private Git view with scanner-owned config, replacement interpretation and lazy fetch disabled, no optional locks, and no arbitrary source-config command helpers. Source metadata ancestry and required object roots are checked. Valid absence of optional `info` parents/config is accepted, and harmless source config comments are not imported or capped by an unused content read. The captured body of each blob, tree, commit and tag is checked against declared type, exact size and format-specific Git OID before its bytes or structural edges are trusted. Commit headers, long identities and optional signature continuations stream with bounded fragments. Parent dedup preserves first-declared typed edges and counts distinct verified objects.

Selected blobs are matched in full, including secrets removed by later commits. Selected commit and annotated-tag messages are policy content. Canonical filename rules run for each relevant tree occurrence before blob storage/content dedup, including new credential-like names reusing already published blob bytes. Baseline content is verified for proof but not gratuitously rematched. Streaming DFS and a single append-only private object spool avoid whole-large-object buffers and breadth expansion of repeated references.

Supported path components and full encoded paths are at most 4,096 bytes. CR, LF, backslash and gitlink shapes are unsupported. These shapes return explicit incomplete `publication_path_unsupported`, never silent skipping or a coverage claim. Byte-limit diagnostics give only the safe numeric measurement/limit; help and recovery describe the boundary without emitting a raw unsupported path. A strict-fsck-valid tree with twenty 220-byte directory components proves this boundary through the public CLI and an actual blocked local push. A known finding encountered before the unsupported path is retained. A first attempted single 5,000-byte basename fixture failed strict Git fsck during setup; it was corrected to legal deep history and is not a product-defect claim.

Recognized Git LFS pointer publication returns incomplete `lfs_unsupported`; pointer text is not payload coverage. T6 owns verified LFS acquisition. T7 owns production repository dispatcher binding, hook composition and exact replay.

## Limits, accounting and persistence

The explicitly selected publication profile defaults to 20,000 distinct verified Git objects, 268,435,456 logical candidate bytes, 120 seconds, 536,870,912 aggregate capture bytes and 805,306,368 peak private temporary bytes. Existing strict schema-1 duplicate/type/unknown/range validation remains. Accepted ranges are respectively 1..100,000 objects, 1,048,576..1,073,741,824 candidate bytes, 1..600 seconds, 1,048,576..2,147,483,648 capture bytes and 1,048,576..3,221,225,472 temporary bytes. An override requires an explicit owner-selected file, read once with its exact-byte digest. No ambient/repository auto budget, warn/skip mode or allowlist grants gate permission. Existing pending checks still select the checkpoint profile.

`git_objects` counts distinct verified OIDs, including verified baseline proof objects; names and duplicate edges are not extra objects. `object_body_bytes` counts those verified bodies. `selected_objects` counts selected graph identities. `path_occurrences` counts logical file occurrences; candidate bytes charge repeated logical blob occurrences separately from deduplicated capture. Message bytes count selected message content. Candidates/inspected snapshots include content scans and path checks. Capture bytes include transaction input plus cumulative Git output/control capture; temporary peak counts simultaneously held request/capture/private metadata/spool/validation database bytes. These are distinct from process RSS or filesystem allocator overhead. Display retains at most 100 findings while inspection proceeds up to the independent 1,000-finding stopping limit; hitting that inspection limit is incomplete.

One publication-only lazy-imported SQLite connection indexes tree basenames with parameterized BLOB keys and scoped uniqueness. It uses an owner-only file, small bounded cache target, disabled mmap, memory SQL temporary store and deadline/progress checks; actual database growth is charged to the private temporary budget. No WAL/rollback sidecars are enabled. SQLite 3.51 through Python 3.14 initially ignored `journal_mode=OFF` while defensive mode was enabled; the implementation explicitly disables defensive mode only on this empty scanner-owned disposable database and verifies the effective OFF result. Only scanner-owned SQL reaches it. Missing SQLite validation safely fails publication; check/help/status do not import SQLite. Python's `autocommit`/`setconfig` APIs require at least 3.12, and native proof here is only 3.13.14/3.14.6. Older installer runtime requirement reconciliation remains T7/K1. API references: [Python sqlite3](https://docs.python.org/3.13/library/sqlite3.html), [SQLite pragmas](https://www.sqlite.org/pragma.html), [SQLite temporary files](https://www.sqlite.org/tempfiles.html).

The existing `scan_secrets_gate_v1` validator is extended action-specifically, rather than introducing another persistence/schema path. Caller-owned expected action/build/repository/budget/transaction/destination identities must match. The fixture dispatcher computes them independently and validates raw process output plus exit status before real Git proceeds. Only exit zero, complete clean coverage, consistent counts/policy and required audit written permit that policy. Findings exit one; incomplete/required infrastructure failure two; invalid invocation/configuration three; cancellation 130. Known findings survive late corruption, capture/limit/cleanup failures and cancellation. Display failure cannot alter the security outcome; failed required audit blocks publication. Audit identifies actual pre-push/publication/outgoing policy. Status accepts the explicit new historical record shape but never authorizes publication.

## Public red and green observations

- Initial public `gate pre-push` was absent and returned invalid invocation; fixture real push could not compose an outgoing gate. The implemented public command and actual local pushes now transfer exactly the checked safe OID and block unsafe refs/objects before transfer.
- Primary review reproduced complete ordinary repositories rejected when optional `.git/info` or `objects/info` parents were absent. Public clean and actual-push controls now pass while unsafe links and required-object failures remain negative.
- A strict ordinary direct tree had three names sharing one blob, exactly two Git objects. A `max_objects=2` gate incorrectly measured three objects from names. Distinct verified OID accounting now passes that control and its packed/missing-remote-old variants, while repeated logical bytes remain charged and lower candidate-byte limits deny.
- An actual deletion from a shallow local repository initially required unsupported local history despite no nonzero local tip. The deletion now succeeds; publication of nonzero local content from that same source remains incomplete.
- A valid source config with 112,300 harmless comment bytes was rejected by an unused 65,536-byte read. Held-parent validation now avoids importing that content; public and actual-push controls pass without permitting config helpers.
- A strict-fsck-valid commit with a 70,232-byte signed header was rejected by an arbitrary 65,536-byte parser cap. Bounded streaming header parsing now accepts long signatures, author delimiter crossing 64 KiB, 70,000-byte email bodies and committer names, with an actual clean push. A later secret message still blocks transfer. Malformed exact first tree/object/type fields remain incomplete.
- Apple Git can return same-length substituted loose bytes with exit zero. Blob and structural commit/tree/tag corruption controls require full OID verification; late corrupt objects preserve prior findings. Missing baseline subgraphs never become partial exclusion proof.
- The documented path-boundary public red returned generic history unsupported for strict-fsck-valid deep paths. It now returns the named safe path diagnostic, blocks actual transfer and preserves earlier findings. No path support expansion or budget increase was made.

## Verification

All commands below ran from the private worktree with `rtk proxy`. Native process-list cleanup checks used scoped escalation. Source edits were paused during generator snapshots. Disposable installed source tests are separate from live provider delivery.

| Command after `rtk proxy` | Observed result |
| --- | --- |
| `python3 scripts/test-scan-secrets-git-gates.py` | Final 59/59 pass in 42.233 seconds on Python 3.14.6 |
| `/Users/adam/.pyenv/versions/3.13.14/bin/python3 scripts/test-scan-secrets-git-gates.py` | Final 59/59 pass in 40.788 seconds on Python 3.13.14 |
| `python3 scripts/generate-hooks.py --write` then `--check` | Final canonical generated assets current: 62 |
| `python3 scripts/test-generate-hooks.py` | Isolated final 26/26 pass in 17.954 seconds; prior overlapping timing failure retained below |
| `git diff --check` | Pass |

The final gate suite covers real commit/push dispatcher composition, non-HEAD/explicit-OID/multiref/new/delete/force/tag/message history, conservative baseline, intermediate removal and same-blob/new-path policy, missing/corrupt/shallow/partial/replacement/graft/alternate/redirect cases, hostile config/environment, strict input/TTY/open pipes/deadlines, SHA-256, audit/display/status separation, closed output, cancellation, descendant cleanup, private SQLite/no-sidecar/temp cleanup, exact object-count and repeated-byte units, large binary and large tree streaming, long signed headers/identities and the explicit unsupported-path boundary.

Immediately before the additive path cause/help change, the same frozen collector/header implementation passed gate 58/58 on Python 3.14.6 (42.868 seconds) and 3.13.14 (41.147 seconds); CLI 35/35 (18.302 seconds), status 29/29 (15.743 seconds), neutral installer 21/21 (39.727 seconds) and generator 26/26 (17.883 seconds). The installer checks run real main Bash and macOS PowerShell installers in disposable homes. Provider capture regressions passed separately for `codex`, `copilot`, and `gemini`, each with disposable HOME/USERPROFILE/XDG roots and native macOS errno-35 resource recovery controls. Earlier compatibility checks, before the later publication-only repairs, passed streaming 22/22 and fixture-preflight 26/26; those earlier runs are not final publication proof. Registry remains exactly 57 suites; no suite was added.

The final generator attempt overlapped a gate run and failed existing Copilot timing assertions: output-cap duration 2.0159 seconds versus its one-second ceiling, then the 300 ms cumulative deadline expired before its first capture. No timing assertion or source was weakened. The isolated rerun result is recorded in the table. A command-name typo before the final generator invocation and a wrong focused unittest class name produced setup errors, then were corrected; neither is a passing result.

Neutral runtime closure grows from 14 to 16 files, including the transaction and publication modules. The exact source/installed inventory controls were updated at the same 64-item bound: 42 synthetic extras plus 16 assets plus six directory/launcher/manifest items fit; one more extra rejects. Provider helper closure remains eight, generated ownership 62. Canonical provider changes came only from the generator.

## Frozen runtime fingerprints

The neutral build identity is computed in entrypoint/CLI/status/listed-module order over each basename, NUL and exact source bytes. Frozen build: `c16fe5d1c0b72a003cb88207bbae6d62c6c564581ca831049ca9d92b2dcfde8f`.

| File | SHA-256 |
| --- | --- |
| `scripts/scan-secrets.py` | `ea9f6adf225889e0ff9297d32e88e9660cea6a9d917ca87f6d95ada6d3afc497` |
| `hooks/runtime/scan_cli.py` | `64be4f79c36167daa89325e36b3e5c018f5acef04cb16c9d08271e11483d3cfa` |
| `hooks/runtime/scan_status.py` | `aa7305d0c703b90bdcaf215b1c083a9fc06491db3f1d1de3cf107e833330a4f5` |
| `hooks/runtime/scan_types.py` | `56b06c26769b80b03983430b795a9f8b96c70d8ae399c725715ff952c1cd39d6` |
| `hooks/runtime/scan_reporting.py` | `c57d577217aed68e7e0e191c3225195a1950e0b4fd18c8524f93984a2de2d8c9` |
| `hooks/runtime/scan_allowlist.py` | `80eb5a115707ad03c227b6e3c1c43da463b0ce303a60909f398eab6dd9c7c7e7` |
| `hooks/runtime/scan_stream.py` | `2b91062b6440457ca26488d9dba43e2a4bda9d2a7dc309e256da1c0b6c9b707b` |
| `hooks/runtime/scan_git.py` | `02832f17c495cbd9ed6f7b54772202a0c9f85cc379e5090860cb838dafdb4041` |
| `hooks/runtime/scan_engine.py` | `8702f6856a0f6e5a497630d95758af4f9ab6a3450dc2356436d81df4755b5764` |
| `hooks/runtime/scan_native_file.py` | `660222d89c1b01d3ef77a34920362c99d2567a11c98cdddc24db542e34a788fb` |
| `hooks/runtime/scan_audit.py` | `86b5527ad96a9495079b4e3a5fdb6ed8562a900744665c39b9fdd9000ca18451` |
| `hooks/runtime/scan_budget.py` | `0ce123e105ef306fef10c7be66e1666ef890f55463b61360cd9c170fefd40ca0` |
| `hooks/runtime/scan_repository.py` | `9f7dd26815fcbeaa6bd2711f942bdf9d788de73d153de5b62cacc198ece2730a` |
| `hooks/runtime/scan_gate.py` | `a477e77a3de47953670959f1088da0aa8b951613b67be889ed302029e124290e` |
| `hooks/runtime/scan_transaction.py` | `005b2bb173cadf708ccc0f1041404c90797421843a8a88d07e2c626497c90894` |
| `hooks/runtime/scan_publication.py` | `bd138d1f306dd1b28f57fe78259de93248360e2b79da6b14a7cd12893bd70a47` |

## Proof limits and remaining ownership

This is native macOS proof on the exact Python/Git versions above. macOS PowerShell does not establish native Windows proof. Native Windows/Linux, hosted CI, live provider delivery and authenticated remote transport remain unverified. Local bare remotes establish real Git ref/object transfer and rejection outcomes. The 9 MB binary, large tree and repeated-object/path cases prove functional streaming/accounting behavior, not production capacity, RSS/headroom or D0/I3 performance acceptance. No benchmark ran concurrently with tests.

T5-I still accepts combined staged/outgoing gates after clean composition. T6 adds verified LFS payload handling. T7 binds production dispatchers and replay and reconciles interpreter prerequisites. The primary reviewed correctness, simplicity, architecture, security and performance; its reproduced metadata/object-count defects and final long-header/path-boundary review informed the retained public controls. No canonical KB or skill files were changed by this node. One possible skill lesson, verifying effective SQLite PRAGMA state instead of assuming the requested value took effect, was reported without creating unsupported policy.
