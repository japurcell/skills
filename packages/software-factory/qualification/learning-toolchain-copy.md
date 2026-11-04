# Learning fixture compiler-copy reduction

## Decision

The learning extraction fixture only needs the compiler toolchain that the
factory release validator accepts: `typescript`, `@types/node`,
`undici-types`, and `@typescript/typescript-${platform}-${arch}`. Its former
recursive copy included other development packages, including Playwright.
The fixture now copies those four package roots with recursive dereferencing
and `COPYFILE_FICLONE`. This is test-fixture setup only. It does not change
production code, compiler versions, fixture repositories, test assertions,
selector registration/order/concurrency, or timeout and shutdown bounds.

## Evidence

On the private Darwin arm64 worktree with pinned Node v24.22.1, five paired
copies used the same source, process, temporary destination parent, and byte
and file inventory scan. The baseline was the previous
`cpSync(node_modules, destination, { recursive: true })`; the candidate was
`copyLearningToolchain`.

| Copy | Median elapsed | Regular files | Bytes |
| --- | ---: | ---: | ---: |
| Full development `node_modules` | 94.632 ms | 839 | 51,608,005 |
| Selected compiler closure | 70.969 ms | 651 | 32,725,856 |

The selected copy measured 23.663 ms less per copy in this local paired
measurement and copied 18,882,149 fewer bytes. This is evidence about fixture
copy setup on this machine only; it does not establish a selector deadline
repair, native-run improvement, production bottleneck, or cause of the earlier
deadline failure.

The qualification `qualification/learning-toolchain-copy.qualification.mjs`
compares every selected source and destination regular file by relative path,
mode, byte count, and SHA-256. It also checks the exact four package roots,
distinct inode identity and unchanged source bytes after modifying the copy,
and executes the copied pinned TypeScript compiler.

The complete original extraction selector ran with its existing command and
concurrency: `node scripts/test.mjs learning --operation extract`. Result:
13 passed, 0 failed, skipped, cancelled, or todo, 9,299.885 ms. The focused
copy qualification passed 1/1 with no skips. No original learning assertions
were changed.

## Limits and next boundary

The baseline complete native fixture run `41773952580` recorded 13 learning
copy spans totaling 4.518 seconds with a 0.478 second maximum, and a 29.507626
second learning selector under its unchanged 30 second bound. Those concurrent
worker spans are not selector wall time and do not identify a cause. The
coordinator owns any changed native comparison after this private source is
handed back and integrated. No native or broad fixture selector was run here.
