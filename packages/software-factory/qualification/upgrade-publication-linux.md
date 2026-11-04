# Linux x64 public install and upgrade qualification

- Fixture: `qualification/upgrade-publication-linux-native.qualification.mjs`.
- Scope: disposable local Git repositories, a private home, authenticated locally packaged releases, an offline cache copy, and selected Node/Python artifacts. No provider is selected or called. Agent attempts and native sessions must remain zero.
- Contract source: T16b upgrade-publication author checkpoint `7ae359c3`; coordinator must integrate that source before native execution. This fixture is additive and leaves the existing Darwin qualification files unchanged.
- Seam: public `install.py install`, `upgrade`, `inspect-upgrade`, `abandon-upgrade`, and `resume-upgrade`; read-only installed files, durable receipts, SQLite completion/claim state, and installed CLI help provide the observations. The existing exported maintenance seam is used only for expired-preparation/known-live-owner controls.

Run from the repository root after installing the locked development dependencies and building the package. Put Node v24.22.1 Linux x64 on `PATH`, then run:

```sh
rtk proxy env \
  FACTORY_TEST_PYTHON=/absolute/python3.13 \
  FACTORY_ATOMIC_PYTHON=/absolute/python3.13 \
  FACTORY_TEST_NODE_ARCHIVE=/absolute/node-v24.22.1-linux-x64.tar.xz \
  FACTORY_TEST_NPM_CACHE_SEED=/absolute/offline-npm-cache \
  node --test packages/software-factory/qualification/upgrade-publication-linux-native.qualification.mjs
```

Prerequisites are mandatory: native Linux x64, runner and PATH Node v24.22.1, Python 3.13.14, matching atomic-helper interpreter, an existing `_cacache` seed, and the Linux archive SHA256 `6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6`. Missing or wrong prerequisites fail. There are no skips or fallback platforms. The coordinator owns registration and the native Actions invocation.

The scenario first installs an owned v7 release `1.2.3`, checks installed Node/npm/TypeScript and CLI help, and upgrades through the authenticated public launcher to `1.2.4`. It verifies original receipt bytes and completion history, old subtree inode preservation, retained integral backup, claim-free ready state, authoring/source/index/cache preservation, and exact stage/marker cleanup. Failed offline preparation, unconfirmed or live-owner abandonment, altered original receipt, and wrong-release abandonment must refuse while retaining evidence.

A second target, `1.2.5`, is interrupted after each durable receipt: `01-old-install`, `02-new-install`, `03-old-toolchain`, and `04-new-toolchain`. Every attempt uses the same operation ID through explicit public resume. No later receipt may exist at the selected interruption; a next rename without its receipt remains an intentional recovery boundary. Every crash must leave incomplete state, one claim, unchanged prior completions and earlier receipt bytes, and a retained backup. A live original launcher must block recovery after the first move.

The final attempt stops after ready is committed while the marker remains. Public recovery must refuse first with the completing controller live, then with only the completing launcher live after controller death. Once both close, explicit recovery must remove the exact marker/stage and retain exactly one completion for `1.2.5`, all earlier receipts/completions, and user/cache bytes.

Signals target only fixture-owned processes. Observation uses `/proc/<pid>/stat` start time and parent, `/proc/<pid>/exe`, and direct task children; identity is rechecked before every signal. The controller is stopped and helper closure observed before killing it. This is a bounded fixture mechanism, not a new production process-control API or general descendant-ownership qualification. Linux documents the stat/executable fields and the need to stop inspected processes for precise child enumeration in its [proc filesystem documentation](https://docs.kernel.org/filesystems/proc.html).

Existing bounds remain: 600 seconds for public install/upgrade/recovery commands, 120 seconds for refusal/inspection commands, 180 seconds to observe each receipt or ready-marker boundary, and 15 seconds for owned helper closure. This full scenario is separate from existing selector limits; the coordinator must give its dedicated native step an explicit overall budget without changing older tests.

## Observed local evidence

- Platform: macOS arm64. Native Linux qualification has not run and is not established.
- Pinned Node v24.22.1 `--check` passed for the new fixture.
- Direct pinned Node `--test` invocation failed at `native Linux qualification required`: one failed test, zero passes, zero skips, 39.391 ms; log `/tmp/factory-linux-upgrade-wrong-host.log`. This proves the host guard refuses this machine; it is not a passing qualification result.
- Native Linux first-install publication, all four controlled receipt crashes/resumes, ready-marker recovery, and only-completing-launcher refusal remain unproven until coordinator Actions execution on the integrated exact head.
- Reflection: the platform and ownership distinctions are enforced in the fixture and recorded here; no additional durable brain note is needed.
