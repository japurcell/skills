Before dispatch, resolve write ownership for shared canonical documents (`file map` and `known-issues`), even across private worktrees. Do not let both workers edit them concurrently. Assign one integration owner (such as the coordinator or one designated worker) or enforce an explicit serial dependency between the two tasks. Source files remain disjoint and can run in parallel.

During execution, each worker edits only its owned source files in its private worktree and unpushed branch, retains scoped verification evidence, and promptly notifies the document owner of durable findings for the file map and known-issues document.

Integrate branches serially, one completed worker branch at a time:
1. Confirm the worker's worktree is clean and rebase its branch onto the latest base topic branch.
2. If conflicts occur or interactions change, stop worker writes, transfer exclusive worktree ownership, resolve conflicts without mutating base, and rerun affected tests.
3. Update and commit any ExecPlan SHA references changed by rebase, then fast-forward base (`git merge --ff-only`) and verify tips match.
4. Reconcile admitted findings into the shared canonical documents and ExecPlan, run the composed-behavior proof on base once prerequisites are integrated, and remove verified clean integrated worktrees and local branches.
