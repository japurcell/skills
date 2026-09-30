---
type: Research Findings
description: SQLite pragma and Python file-publication semantics relevant to local state durability
---

# SQLite setting facts

Primary docs checked 2026-09-30: current SQLite pragma/C API references and Python 3.14 `os` docs. These state setting/API semantics; they do not certify a particular filesystem, VFS, storage device, or application protocol.

## SQLite journal and durability settings

- **DELETE journal + `synchronous=FULL`:** DELETE is SQLite's default journal mode; it deletes the rollback journal at transaction end, and that unlink is the commit action. FULL invokes the VFS `xSync` to sync file contents. SQLite says this prevents database corruption after OS crash/power failure, but rollback-journal FULL is not necessarily power-loss durable: depending on filesystem behavior, the last committed transaction may disappear after a power loss immediately following commit. [SQLite `journal_mode` and `synchronous` pragmas](https://www.sqlite.org/pragma.html)
- **DELETE journal + `synchronous=EXTRA`:** EXTRA has FULL's behavior plus a sync of the directory containing the rollback journal after unlinking it to commit a DELETE-mode transaction. SQLite describes this as providing additional durability if power fails close to commit; without the directory sync, the database is not corrupted, but the last transaction can be lost on some filesystems. EXTRA is no different from FULL in WAL mode. [SQLite `synchronous` pragma](https://www.sqlite.org/pragma.html)
- **Scope/assumptions:** `journal_mode` and `synchronous` are SQLite database-connection settings (the pragma forms support schema selection); DELETE is default unless changed, and journal behavior can vary with other SQLite modes/settings. The documented claims rely on the VFS and filesystem honoring sync/locking expectations. SQLite docs do not certify storage hardware that lies about flush completion. SQLite distinguishes an application/process crash from OS crash/power loss: transactions survive application crashes regardless of synchronous mode, while OS/power-loss guarantees depend on journal/sync settings. [SQLite `pragma.html`](https://www.sqlite.org/pragma.html), [SQLite locking and atomic commit](https://www.sqlite.org/atomiccommit.html)
- **macOS `fullfsync`:** `PRAGMA fullfsync=ON` requests Apple's `F_FULLFSYNC` sync method for all sync operations; default is OFF. SQLite currently documents that only macOS supports `F_FULLFSYNC`. This changes the sync method, while EXTRA's additional directory sync remains a separate operation. `checkpoint_fullfsync` governs checkpoint syncs and is irrelevant when `fullfsync` is on. Docs do not promise behavior for every filesystem/device or prove a particular runtime build uses the expected VFS. [SQLite `fullfsync` and `checkpoint_fullfsync` pragmas](https://www.sqlite.org/pragma.html)

## Constraint enforcement and lock waiting

- **Foreign keys:** Enforcement is connection-specific and must be set while no transaction or savepoint is pending; setting `PRAGMA foreign_keys` inside one is a no-op. SQLite's documented default is OFF (since 3.6.19), but compile-time `SQLITE_DEFAULT_FOREIGN_KEYS` can change it and the default may change in the future. SQLite advises applications to set the required value instead of relying on defaults. [SQLite `foreign_keys` pragma](https://www.sqlite.org/pragma.html)
- **Busy timeout:** `PRAGMA busy_timeout=N` sets/replaces the busy handler for that database connection; only one handler can be active on a connection. While a lock blocks access, SQLite sleeps in intervals until at least N milliseconds of accumulated sleep, then returns `SQLITE_BUSY` to the caller. This is a lock-wait bound, not a transaction deadline or whole-operation wall-clock timeout, and other processing time is outside the accumulated sleep. A custom busy handler is overwritten. [SQLite `busy_timeout` pragma](https://www.sqlite.org/pragma.html), [SQLite `sqlite3_busy_timeout()`](https://www.sqlite.org/c3ref/busy_timeout.html)

## Python filesystem publication calls

- **`os.fsync(fd)`:** Python says this forces writes for the file descriptor to disk; on Unix it calls native `fsync()`, on Windows `_commit()`. With a buffered Python file, call `flush()` first, then `os.fsync(f.fileno())`. This describes one descriptor; Python's API docs do not promise that syncing a data file also syncs its parent directory entry or guarantees physical-device behavior. [Python 3.14 `os.fsync`](https://docs.python.org/3/library/os.html#os.fsync)
- **`os.replace(src, dst)`:** Replaces a file destination if permitted. Cross-filesystem moves may fail. A successful rename is atomic on POSIX; this atomicity applies to one rename operation. Python does not document multi-path transactions or power-loss durability for a rename. SQLite documents multi-file atomic commit for attached SQLite database files; by that documented scope, ordinary Markdown writes are outside a SQLite transaction (inference). Successive file replacements can leave a mixed set after interruption. [Python 3.14 `os.replace`](https://docs.python.org/3/library/os.html#os.replace), [SQLite multi-file commit](https://www.sqlite.org/atomiccommit.html)

## Evidence boundary and unknowns

These official docs support distinctions among process failure, OS crash, and power loss, but do not provide empirical assurance for the product's target filesystem/device or custom SQLite VFS. They also do not define a durability guarantee for a combined SQLite plus external-Markdown publication sequence. Per-device `F_FULLFSYNC` behavior and directory-sync support outside the named SQLite behavior remain platform/filesystem questions. No probe or live filesystem failure test was performed.
