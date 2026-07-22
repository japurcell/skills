1. Append the review-fix implementer `Progress block` before acting on it. Source of truth stays `prd_file`; `progress_file` is only resume data.
2. No parallel helper wave here. Run fresh `code-simplifier` on combined final state first.
3. Then run fresh `requirements-collector`, and only after that run fresh `addy-code-reviewer`. The review step must wait for both helpers to finish, and `passes: true` stays blocked until review is clean and final checks pass.
