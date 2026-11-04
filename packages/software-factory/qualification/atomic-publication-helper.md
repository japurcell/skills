# Atomic publication helper - limited native evidence

This standalone helper is not integrated into release or maintenance. It emits no receipt and does not flush directories. The caller must authenticate the complete stage and runtime, hold the operation claim, validate inventories and intent, flush both parents, and record receipts only after its own checks. Unknown means preserve the claim and evidence without retry, adoption or rollback.

On 2026-11-03, Darwin arm64, Node 24.22.1 and Python 3.13.14, the focused test exercised a benign absent destination and existing empty directory, nonempty directory, regular file and symbolic link, plus identity/digest refusal, request framing, timeout, ambiguous output, owned-descendant cleanup and unrelated-process survival. The original 13 cases plus profile and separate-parent controls live in `qualification/atomic-publication-native.qualification.mjs`, outside Node default discovery. These checks do not establish general filesystem, crash durability, adversarial concurrency, interpreter lifetime, or product acceptance. Run the unconditional public selector from `packages/software-factory` with `FACTORY_ATOMIC_PYTHON` naming the qualified interpreter:

```
FACTORY_ATOMIC_PYTHON=/Users/adam/.pyenv/versions/3.13.14/bin/python3.13 /tmp/factory-qualified-node-342t16a/node-v24.22.1-darwin-arm64/bin/node scripts/test.mjs qualification --area atomic-publication
```

The explicit test fails without its Python prerequisite or on an unsupported host. The callable `atomicPublicationSupportProfile()` reports `darwin`, `linux-x64`, or `unsupported` as a code-path profile only, not native qualification. The Linux x64 suite also requires `/dev/shm` to be writable and on a different device from the selected temporary directory; it fails if that prerequisite is missing. It tests a cross-device refusal using disposable directories. On an actual Linux x64 runner use the selected trusted Python 3.11 or newer and Node 24.22.1, from `packages/software-factory`:

```
FACTORY_ATOMIC_PYTHON=/absolute/path/to/selected/python3.13 node scripts/test.mjs qualification --area atomic-publication
```

Linux invokes `renameat2(RENAME_NOREPLACE)` through the process C library, checks both parent devices and the source device before invoking the native primitive, and fails closed if its symbol, kernel, filesystem or access cannot satisfy the operation. This is not a Linux native pass: native Linux, process closure, durable rename and product acceptance remain open. Windows returns unsupported and has no positive claim; its handle, filesystem, ACL, durability and process-lifetime gates remain open.

The helper reads its authenticated descriptor through `/dev/fd/3`. The selected Python 3.11+ interpreter and its runtime dependencies are operator-trusted. The interpreter is checked after helper authentication immediately before spawning its canonical path; that path lookup is not atomic with the preceding identity check under independent same-user mutation. The caller must bind the selected runtime and refuse observed mismatches. The wrapper terminates a remaining invocation-owned process group within the existing deadline and returns unknown if it observed a lingering group or cannot confirm closure; it does not signal unrelated processes. Similarly, POSIX checks do not make source-name lookup identity-conditional. A changed source can be relocated before the mismatch is detected; the helper reports unknown and does not undo the move.

The macOS flag value is `RENAME_EXCL` in the local SDK `sys/stdio.h`; Apple documents `renameatx_np` in its [APFS guide](https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/ToolsandAPIs/ToolsandAPIs.html). Linux documents the no-replace and filesystem behavior in [rename(2)](https://man7.org/linux/man-pages/man2/rename.2.html). Native call failure never falls back to plain rename or copy/delete.
