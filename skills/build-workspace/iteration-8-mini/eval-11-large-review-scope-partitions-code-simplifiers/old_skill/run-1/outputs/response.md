Steps (concise):

1. Run addy-context-engineering and subagent-model-selection to pick appropriate models/context.
2. Split the 8 review_scope_files into two logical groups (auth: src/auth/* + tests/auth/login.test.ts; billing: src/billing/* + tests/billing/invoice.test.ts).
3. Launch two parallel code-simplifier subagents (one per group) using the simplifier-prompt.md. For each subagent pass exactly:
   - touched_files: the group's file list
   - implementer's verification context (tests run, env, commands, results)
   - uncommitted_files: output of
     git status --porcelain | grep -v '^ D' | awk '{print $2}' | grep -v '/.gitignore$'
4. Wait for each simplifier to return DONE. If DONE_WITH_CONCERNS, resolve those (re-dispatch implementer if correctness/scope) before sending files to the code-reviewer.
