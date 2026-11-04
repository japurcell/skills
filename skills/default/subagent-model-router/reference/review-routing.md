# Review Task Facts

Use this file only when review type or risk classification is unclear.

Classify the review as `mechanical` for non-semantic changes with straightforward verification, `substantive` for behavior, tests, guard logic, or meaningful refactoring, or `security` for security-sensitive review. Supply `risks.security_sensitive`, `risks.high_stakes`, and `task.prior_important_miss` only when evidence supports those facts. File count alone is not a risk fact.

Set `security_sensitive` for authentication, authorization, secrets, credentials, cryptography, and trust-boundary changes. Set `high_stakes` for high-stakes correctness and subtle concurrency, cache-consistency, or false-pass risks. Set `unusually_difficult` for unusually difficult review over a large or highly connected codebase. Record a prior important miss on materially similar review work, repeated reasoning failures, and a user request for best quality in their corresponding fields.
