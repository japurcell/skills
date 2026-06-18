Append the returned implementer `Progress block` for `mode: review_fix` to `progress_file` **before** acting on it, then apply Status Rules (`DONE` means continue).

Rerun finalization on the combined final state after this review fix: run fresh `code-simplifier` and append its `Progress block`; then rerun review (fresh requirements collection, then fresh `addy-code-reviewer`) and append those `Progress block` entries.

Keep `passes: true` blocked: do not set it yet. Set `passes: true` only after review is clean and required final checks/verification pass. If review still finds issues and review-fix iterations are below limit, increment count and dispatch fresh implementer `mode: review_fix`, then rerun simplify/review again.
