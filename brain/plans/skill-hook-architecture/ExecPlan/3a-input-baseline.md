# T3a, characterize the three readers

The hook maintainer uses isolated copies of revision `069b3f22` and the byte-stream matrix below. Record the original public outputs, stderr, mock RTK input, and whether each pipe closes or remains open. Identify the reader from its entry point (`_read_json_input_text`, `read_hook_input` or Codex `read_json_input`). Stop after capturing expected outcomes on the available platforms.

The hook implementer owns the parity fixture and its reference evidence. Exercise actual consumer processes against the reference checkout. Record a rerunnable check, input bytes, exact observed decisions and OS limits. Windows observations may be collected separately by a Windows runner. Leave all three production readers as they were.

Use the [milestone contract and verification commands](3-hook-input.md) and the [integration plan](../ExecPlan.md). Record results and remaining evidence here.
