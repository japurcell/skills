---
type: Research Findings
description: Official Python and SQLite facts about local state durability and publication boundaries
---

# State durability facts

## Scope and version

Python reference checked against the current Python 3.14 documentation (3.14.7). The repository task does not specify a Python runtime version, so version-specific behavior should be checked against the deployed interpreter. SQLite references describe current SQLite behavior; durability still depends on runtime settings and filesystem/VFS behavior.

## 1. Python `sqlite3` availability

**Facts.** `sqlite3` is the Python standard-library DB-API interface to SQLite, a disk-based embedded database requiring no separate server. CPython builds its `_sqlite` extension against SQLite; current Python configure docs say SQLite 3.15.2 is required to build the `sqlite3` module. CPython documents optional standard-library modules as potentially omitted from custom builds when build dependencies are absent, and notes distributors should advise users if modules are missing. Loadable SQLite extension support is a separate feature and is disabled by default on some builds/platforms, including macOS system SQLite builds. [Python `sqlite3`](https://docs.python.org/3/library/sqlite3.html), [CPython configure: optional modules](https://docs.python.org/3/using/configure.html)

**Implications.** The standard-library API avoids a third-party Python package dependency, but availability is not universal across custom/minimal Python distributions. Runtime capability detection and fallback/error behavior remain necessary. Do not infer availability of optional SQLite extensions from availability of `sqlite3` itself.

## 2. Local cross-process transactions and durability

**Facts.** SQLite coordinates connections in separate threads or processes using filesystem locks and serializes writes so only one writer commits at a time. Readers and writers can coexist under WAL mode, while rollback-journal mode has different reader/writer blocking behavior. SQLite describes transactions as atomic through program crash and, subject to operating-system/filesystem assumptions, OS crash or power loss. Durability settings matter: in WAL mode with `synchronous=NORMAL`, a committed transaction can roll back after OS crash or power loss; `FULL` adds a WAL sync after each commit. WAL requires all database users on the same host and does not work over a network filesystem. Broken filesystem locking, especially on some NFS/network filesystems, can allow concurrent conflicting writes and risk corruption. [SQLite isolation and concurrency](https://www.sqlite.org/isolation.html), [SQLite WAL](https://www.sqlite.org/wal.html), [SQLite synchronous pragma](https://www.sqlite.org/pragma.html), [SQLite corruption risks](https://www.sqlite.org/howtocorrupt.html)

**Implications.** For local processes sharing a database on a supported local filesystem, SQLite supplies transaction coordination without an application-level write lock. Do not extend that conclusion to cross-host WAL, unreliable locks, or power-loss durability without accounting for journal mode, `synchronous`, VFS and storage behavior.

## 3. External Markdown files and SQLite transactions

**Facts.** SQLite transaction atomicity covers changes to SQLite database files participating in its transaction. SQLite can atomically coordinate multiple attached SQLite database files in rollback-journal mode, with documented caveats, but its documented mechanism does not include arbitrary external files such as Markdown paths. [SQLite atomic commit](https://www.sqlite.org/atomiccommit.html)

**Implications.** A SQLite `COMMIT` cannot by itself make a database update and one or more ordinary Markdown-file updates a single atomic unit. Any design that writes both needs an explicit recovery/reconciliation protocol or must treat one side as derived/publication state. This is a boundary statement, not a recommendation of a particular protocol.

## 4. `os.replace` publication guarantees

**Facts.** Python documents `os.replace(src, dst)` as replacing an existing file destination when permitted; on POSIX, successful rename is atomic. It may fail when source and destination are on different filesystems. The API documents one rename operation, not a transaction over a set of paths. [Python `os.replace`](https://docs.python.org/3/library/os.html#os.replace)

**Implications.** Preparing a temporary file and replacing one destination can give readers an atomic name switch on POSIX, provided the operation succeeds and source and target meet filesystem constraints. Sequential replacements of several Markdown files are individually atomic at best; observers or crashes can see a partially published set. The API documentation alone does not promise power-loss durability for file contents or directory metadata, nor cross-platform identical atomic semantics.
