**Next step:** dispatch the **code-simplifier** wave, not tracking. The manager should send the **simplifier prompt** with:

- the exact deduped `review_scope_files` list
- the implementer’s verification context

Because `review_scope_files` has **4 files** and the exact-path build workflow says **≤5 files = 1 simplifier covering the full list**, the code-simplifier wave should be **a single code-simplifier subagent scoped to all four files together**—no partitioning.

After that simplifier returns `DONE`, the manager should dispatch the **code-reviewer** over the **same full-file scope**, and only update tracking after the reviewer also returns `DONE`.
