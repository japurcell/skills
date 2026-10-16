# T8b-M serial composition evidence

Date: 2026-10-16. This receipt records composition of unfinished T8b source. It does not accept provider migration, final installed workflows or Milestone 4. The primary owns the active ExecPlan and coordinated documentation pass.

## Inputs and authorized scope

Worktree: `/Users/adam/.codex/worktrees/design-b-t8b/skills`; branch: `codex/design-b-t8b`. The original T8b owner relinquished Git/source/test ownership during this serial composition and remains paused until the primary returns ownership. No nested delegation occurred.

The clean provisional input was `141fd4065804f1425357f2a38eb8629885658268`, with parent `0bf18e9764b9a2e00763e089af2c41a7710f6141`. The exact target was `bb53a1370018475dd70d21e63e931e58215fed17` on `codex/hook-resilience-design-b`, containing accepted cancellation repair `3ff06db82a28764c0e67ee80a1e044886abc8fce`. The initial 24-row checkpoint receipt matched every file SHA-256 and mode before rebase. The base branch was not mutated.

RTK 0.51.0 and Python 3.14.6 were observed. Commands used `login:false`; mutations and generator execution outside the original writable root used scoped escalation. Git hooks were disabled only for private history operations through the per-command `core.hooksPath=/dev/null` option. No hook was installed, enabled or trusted; no real home, publication or deployment was touched.

## Commands and observed results

All commands below ran from the private worktree. Each process completed before its dependent command began. The generator suite ran with no overlapping functional tests, generator processes or repository edits.

1. `rtk proxy git status --short --branch` showed the clean `codex/design-b-t8b` branch. An inline standard-library Python verifier compared all 24 checkpoint SHA-256/mode rows and reported no mismatch.
2. `rtk proxy git -c core.hooksPath=/dev/null rebase --onto bb53a1370018475dd70d21e63e931e58215fed17 0bf18e9764b9a2e00763e089af2c41a7710f6141 codex/design-b-t8b` stopped with exactly six generated-file conflicts, one for each scanner/diagnostics output below. No canonical source conflict occurred.
3. `rtk proxy python3 scripts/generate-hooks.py --write` exited 0 and printed exactly those six generated outputs. Their complete bytes compared with the provisional input differ only in their single `DIAG_BUILD` line. No generated text was synthesized by hand.
4. `rtk proxy git add -- .codex/hooks/scan-secrets.py .codex/hooks/hooks-diagnostics.py .copilot/hooks/scripts/scan-secrets.py .copilot/hooks/scripts/hooks-diagnostics.py .gemini/hooks/scripts/scan-secrets.py .gemini/hooks/scripts/hooks-diagnostics.py`, then `rtk proxy git -c core.hooksPath=/dev/null -c core.editor=true rebase --continue`, completed the single-commit rebase. Interim tip: `2ab342ca` (subsequently amended to retain this receipt).
5. `rtk proxy python3 scripts/generate-hooks.py --check` exited 0: `Generated hooks are current (65 files).`
6. `rtk proxy python3 scripts/test-generate-hooks.py` exited 0: `Ran 26 tests in 18.056s`, `OK`. Its subprocess was actually awaited through completion.
7. `rtk proxy python3 scripts/generate-hooks.py --check` again exited 0: `Generated hooks are current (65 files).`
8. `rtk proxy python3 /tmp/design-b-t8b-m-verify.py` exited 0 after the suite. It verified all checkpoint rows, accepted cancellation rows and neutral runtime rows; compared retained cancellation/runtime bytes with the target Git tree; checked the exact provisional changed-file set; proved each generated difference was only `DIAG_BUILD`; recomputed the ordered neutral build; and parsed the registry with `ast.literal_eval`. The registry has 61 commands and exactly one cancellation-suite registration. Its temporary JSON receipt SHA-256 is `531ac94a1db6f32cf1263ce63e17cfa73af7ccbb2bff67fe2ab484b6f81ac26e`. The durable identities are retained below.

No cancellation, installer, gate, LFS, capacity, Python 3.13 or aggregate suite was rerun here. Their accepted inputs remain exact, and the original T8b owner retains responsibility for final frozen composed proof on both Python versions.

## Preserved provisional T8b identities

All 18 rows below have identical before/after SHA-256 and modes. They include canonical migration source, the three active templates, fixtures, public tests and the original pending evidence. No semantic source repair was necessary or attempted.

| Path | Before = after SHA-256 | Mode |
| --- | --- | --- |
| `.codex/global-hooks.json` | `e36f7d84f3845ef20de8feb6a0c4bcc803bd93452baa0552e82237e69afa7a7e` | `0o644` |
| `.copilot/hooks/hooks.json` | `e8228b9a31fa6813a1b94bef1f35e87e4ee8637e54c82e869f8085629cc4e5cc` | `0o644` |
| `.gemini/global-settings.json` | `73b93c66397830f961f999ba2b290b812415598c74a2db62ac94ac6072d53c44` | `0o644` |
| `docs/hook-resilience-design-b/t8b-evidence.md` | `659938b3b8456d5a039e515658f7b76db34c859aed579f596909da7e748422a0` | `0o644` |
| `hooks/families/diagnostics.py` | `2d9177d738adec5ff4fab6f2a178171b7d21195aac70f7998433b72e51c3b668` | `0o644` |
| `hooks/registrations.py` | `7bccdfa429cc64cc3fd3b6efc0a41160a7a308f524fb5e2394a94be9a4b42704` | `0o644` |
| `scripts/fixtures/provider-hooks-pre-status/codex.json` | `15d1f58f3c245e1cc514b1e3e0992d131cdac249f55f59ace10b5750ef17bb08` | `0o644` |
| `scripts/fixtures/provider-hooks-pre-status/copilot.json` | `a05b4871cdf151486f1f2e4a2a4f2e05bbefb580cf43dc4649529ef54a11ccac` | `0o644` |
| `scripts/fixtures/provider-hooks-pre-status/gemini.json` | `6686efb4dc6477391c0ae2347ca87618efff1843553c252ada102da3d0bf221e` | `0o644` |
| `scripts/fixtures/provider-hooks-pre-status/provenance.json` | `e08bd1bbe5fdb399997b9487d94496935b977d144928bb65ee656e78d57e820b` | `0o644` |
| `scripts/install-codex-hooks.py` | `6b570941c1526def711b1333e9dc6322c04555e0edd16c3815f65e7ca2d3bb91` | `0o755` |
| `scripts/install-provider-hooks.py` | `136b6ce73596a8638427cae8b74549072160caaa98766db2d5055422d377ac09` | `0o755` |
| `scripts/test-hook-diagnostic-recovery.py` | `34d66f12c2d617197414a9e5d4267e88709c45d8a4f75b9b3e2e6ddfae3c3c37` | `0o755` |
| `scripts/test-install-codex-hooks.py` | `11b40db0e40f2cbca532c189294d44780a6b04b54e5fac0878669acb8ab1465d` | `0o755` |
| `scripts/test-install.ps1` | `3870d09a1760b7923f5833faed4f7d33ed8dda555650eeaa1b3565b90ca71567` | `0o755` |
| `scripts/test-install.sh` | `240d54a97cfaf93dedf8437dc2a8986e155b1f8d007fbeff4107abd2f9830cf6` | `0o755` |
| `scripts/test-scan-secrets-lifecycle.py` | `0f14d04233925d576f31e73db4098f7afb768aae9c27abed149ade6d937836ec` | `0o755` |
| `scripts/trusted_hook_launch.py` | `74be015faa4ab45eb5aa8135bb170657faae3ae47fa29707952d83fbf1e5df37` | `0o644` |

## Canonically regenerated output identities

All six modes remain `0o755`. Every byte outside each `DIAG_BUILD` line equals the provisional T8b input. Changes to fingerprint inputs are the accepted status cancellation renderer plus already present T8b diagnostics/templates/registration source; the canonical diagnostics fingerprint includes all `hooks/**/*.py` inputs.

| Path | Provisional SHA-256 | Composed SHA-256 |
| --- | --- | --- |
| `.codex/hooks/hooks-diagnostics.py` | `bfe214b27ff4afc9c48443811283c0241451786c1de640cca74edd54d199ca2d` | `881ff11f7ca8c63e387724b2649ccbf7cbc3c227fa85af8554146d2ced4e499f` |
| `.codex/hooks/scan-secrets.py` | `8e8793e114ee175b30f765e3d2cac04fadadffb050f779c39ce771c6b2ad9bea` | `228e0f5ae0d24e6837ec750ec40183448d48eeec7062fc33b99700be38c596a9` |
| `.copilot/hooks/scripts/hooks-diagnostics.py` | `e3022ebd1639025c880b05cc4d38016a29baad5ef720a6a70d8de84bdc2a7a72` | `ac25dfa01fb2f8e830d20451d2dfb0a601811f66a0f4b8d722e20fbb5ee990a2` |
| `.copilot/hooks/scripts/scan-secrets.py` | `dd6c915408804fcecd79576ac3d0a72945e326d8f0f46a84674e5e4be1e1a274` | `c4c2d52bb602f4d994d2e9d53b795f7a51371eb44d192d46cce2b10370b60327` |
| `.gemini/hooks/scripts/hooks-diagnostics.py` | `e765333db3755d23b981017a6f41540096d164b3265eebdd8adca8f8e1b0ab4e` | `b822ecba8fa3945eac657e1eb4492d63936eba99cb9639c87c44a9c040434a64` |
| `.gemini/hooks/scripts/scan-secrets.py` | `8a2c6a1ffcf13ce9265646e1c589ffe2df514b80763260bbd631a40763cd57e9` | `c8433aae0703b850555a95e5224e69b07cd55c5d5bc879ad9d5adc619295b0e9` |

| Provider | Provisional DIAG_BUILD | Composed DIAG_BUILD |
| --- | --- | --- |
| Codex | `329ab64effd963b03795117700171d5e5f02e4b401a1bbaa8d2a5e00cdaa4651` | `caaf4659ffb0cea1cc88ce6b697e7e291bc1955530922e4ec7ad0a551108f7f3` |
| Copilot | `e05db242daae66d7088d6a391fb4489247fb7b96aef090d34e8065d4956dff23` | `d0fabc0366a96f143aed71bcb08b6b589dd083286b3f176fdd3deedff244c953` |
| Gemini | `05c995a83866934f972589cc38a3633f9c07e6d41f9e835fe06dd30e5d8ccc6f` | `cd02df88916785a855ab7f2beee448dcc1c976f5367b6e02adbe00aea703294e` |

## Accepted cancellation preservation

All eight rows below exactly match the accepted cancellation promotion receipt and target Git tree, including executable modes. The six intentionally regenerated outputs are excluded from this comparison. The pre-existing lifecycle suite is also excluded from the cancellation receipt comparison because T8b intentionally changes it; it instead exactly matches the provisional T8b row above.

| Path | Before = after SHA-256 | Mode |
| --- | --- | --- |
| `.codex/hooks/scan-status.py` | `126de1936d82b294e15306d99ab1a35e312d9d55e239c5941d6266ef96cf84f3` | `0o755` |
| `.copilot/hooks/scripts/scan-status.py` | `b85e4efd4d159746f0ff37b3c2800638a5d39173fa3031aa104e87f0677635da` | `0o755` |
| `.gemini/hooks/scripts/scan-status.py` | `0fc85f1e234497eca04264bbaa0a7bf2008fe6c3c6cf26ad910558324fb16251` | `0o755` |
| `hooks/families/scan_status.py` | `c62d7b96fed9fef2fa3a406de73d77008de63ed3e34d86fb406f80f61a0eab25` | `0o644` |
| `scripts/test-all.py` | `c5c534c9e9430c0a06eb34c5519b5718008fff82526dc5b95c3f617603bad79a` | `0o755` |
| `scripts/test-scan-status-cancellation.py` | `1a3853d0a248ca6bb4d0a50124a7623737cf3c78284fc5c00ccc2f8c191b455d` | `0o755` |
| `scripts/test_test_all.py` | `711f44c44bda33e88324a3b8c5acaeaa7f5f84721fd320b394d2f5a36c939b71` | `0o644` |
| `docs/hook-resilience-design-b/t8a-c-evidence.md` | `fb8035f7f9639641685b3973c87498da8fe56b39408303e62acba5ac2d59e5c5` | `0o644` |

## Neutral runtime preservation

All 22 source hashes below match both the neutral runtime receipt and the target Git tree. Recomputing the runtime's ordered basename + NUL + bytes fingerprint gives `82e125f8e74728baf01a0e1d792d4ec131f9a309d90b861b16287482dde9b029`, unchanged. This is static identity proof; no new scanner behavioral or capacity proof is inferred.

| Path | Before = after SHA-256 | Mode |
| --- | --- | --- |
| `scripts/scan-secrets.py` | `ea9f6adf225889e0ff9297d32e88e9660cea6a9d917ca87f6d95ada6d3afc497` | `0o755` |
| `hooks/runtime/scan_cli.py` | `b2000e9789fd44bb27bbf8dcc84d742af2bc5f11afdcbb5a2344aac11c12a1e1` | `0o755` |
| `hooks/runtime/scan_status.py` | `c70549592deb0db92ab44a6e5dac4352343f89afec903fc34647eff056d136fc` | `0o755` |
| `hooks/runtime/scan_types.py` | `57f6116d711302a3c106556caa4f6ed98aa60a7b2e5a8f6cd78081b914e6581e` | `0o755` |
| `hooks/runtime/scan_reporting.py` | `c57d577217aed68e7e0e191c3225195a1950e0b4fd18c8524f93984a2de2d8c9` | `0o755` |
| `hooks/runtime/scan_allowlist.py` | `80eb5a115707ad03c227b6e3c1c43da463b0ce303a60909f398eab6dd9c7c7e7` | `0o755` |
| `hooks/runtime/scan_stream.py` | `2b91062b6440457ca26488d9dba43e2a4bda9d2a7dc309e256da1c0b6c9b707b` | `0o755` |
| `hooks/runtime/scan_git.py` | `36eae03a2429bf3a9bc6c6ed4913c1f882fbba72d1bd5b7ee64f0ab5660a57da` | `0o755` |
| `hooks/runtime/scan_engine.py` | `33bbfb091672a9ef5b03d04c291e9e91ec063945cbbfbc08a0007ab2c3ab2249` | `0o755` |
| `hooks/runtime/scan_native_file.py` | `660222d89c1b01d3ef77a34920362c99d2567a11c98cdddc24db542e34a788fb` | `0o644` |
| `hooks/runtime/scan_audit.py` | `86b5527ad96a9495079b4e3a5fdb6ed8562a900744665c39b9fdd9000ca18451` | `0o755` |
| `hooks/runtime/scan_budget.py` | `0ce123e105ef306fef10c7be66e1666ef890f55463b61360cd9c170fefd40ca0` | `0o755` |
| `hooks/runtime/scan_repository.py` | `adfea4ca41a50ddd31d0fd15fb1b45c7ece29881a15321a84ece0fdc68b76775` | `0o755` |
| `hooks/runtime/scan_gate.py` | `a8c36bcfad6aec72ac0ce9d9325a25cf9854eee7c9f15eda136251166b4381db` | `0o755` |
| `hooks/runtime/scan_transaction.py` | `005b2bb173cadf708ccc0f1041404c90797421843a8a88d07e2c626497c90894` | `0o755` |
| `hooks/runtime/scan_lfs.py` | `bcd53cb7738e43f52e6097fbfeaf461b130f15b35f2912a7fba2d53b5aa6112b` | `0o755` |
| `hooks/runtime/scan_private.py` | `3b910c861215f34cc69d1aa065a24a398d0e20fee39ee2a386be09d66b19a8e0` | `0o755` |
| `hooks/runtime/scan_publication.py` | `6e07c3ec4763671781963e4e12b237acf817e5f04f1a74376666ecbcebfe9bce` | `0o755` |
| `hooks/runtime/scan_dispatch.py` | `99f5dcffe05e6b97f7fdac636154bfb9c65d03833963383ab6576236398dbe30` | `0o755` |
| `hooks/runtime/scan_repo_install.py` | `fbf1021aaa0685b2e6581feea7c91e9466e0cc7dc2c6e1c1f30d689be096c0d3` | `0o755` |
| `hooks/runtime/scan_repo_state.py` | `69ea57e1af5a29eea6d1dbc2c950e14019bb3d7f90d5bdbe84bc62333dac402a` | `0o755` |
| `hooks/runtime/scan_repo_dispatch.py` | `6a21dd7ab4921e429031b956b2331b6af1db767ed16f54d41fb15c52c04f4078` | `0o755` |

## Handoff and limits

This receipt is retained by amending the same provisional T8b node after rebase. Exactly one T8b commit remains above the exact target base, with the original 24-file change scope plus this receipt. The final rewritten tip and receipt digest are reported separately to avoid a self-referential hash. The private worktree remains active and is not archived. After clean-state verification, the merger relinquishes all Git/source/test ownership to the primary; only the primary returns it to the original T8b owner.

The original `t8b-evidence.md` remains byte-for-byte unchanged and PENDING, including its two auto-review rejections with no mutation and the exploratory test-overlap observation. Its echo-path/duplicate-JSON candidates and fixture refinement remain original-owner work. Composition success supplies no final migration acceptance.

Native Windows execution, actual host timeout/SIGKILL behavior, pre-handler cancellation, authenticated provider delivery, live deployment and publication remain unproved. No background checkpoint, scanner policy change or new acceptance policy was introduced.
