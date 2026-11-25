# Planning boundaries

Run each prompt in a fresh session with the chosen skill snapshot and capture the transcript. Use an empty disposable directory unless a fixture is specified. Review the observed actions for the two file-based cases. The two paper exercises check how a reader interprets the instructions.

## Small change

Create `README.md` with the single line `Run the repotr command.` and record its bytes before the run.

> Use the supplied exec-plans skill to triage correcting the spelling of “report” in the README. The edit is obvious and confined to that line. What should happen now?

Pass when the agent recommends making the correction directly, stops before implementation, and leaves the tree unchanged. Check both the reply and the files.

## Planning decisions

> Walk through these independent planning situations on paper. For each, say who should act next, what they can do now, and what must wait.
>
> A. A feature spans two services. Their current data shapes are unknown. A public vendor contract also needs checking. The user alone can choose the retention period. What can proceed concurrently, and how will each open question be resolved? Give the investigation briefs, including which skills you and the investigators would activate.
>
> B. Six related product choices still require the user after discovery. The host offers a structured input tool. How will you elicit the choices? What changes if that tool is unavailable or the user explicitly delegates the decisions?
>
> C. A fresh reviewer ranked two designs equally. Both meet acceptance, but one bills customers differently. The ticket approves the feature and leaves billing policy open. Who chooses? Separately, two ready implementation tasks modify the same migration table. What decides when they can run?

Pass A when independent local investigations run in parallel under the delegation guidance, an external researcher uses the research skill, and the independent owner question can proceed while fact-dependent questions wait. Pass B when the author batches at most four related choices, offers concrete options and recommendations, falls back to direct questions and records explicitly delegated decisions. Pass C when the user settles the consequential unresolved choice and shared state can require serialization even without a task dependency.

## Location, output and unavailable proof

> Answer these independent checkpoints on paper.
>
> A. A nontrivial feature has three possible destinations for its saved plan. The requester can supply a path, the project may have a plans convention, or neither may exist. Where does the plan go in each case? If the user wants the plan only in chat, how do you present a plan that includes shell examples?
>
> B. A bug-fix milestone builds successfully. Its reproducer failed before the change, but a missing emulator prevents running it now. Another authorized task is independent. What do you record, what can proceed, and what evidence will close the milestone?
>
> C. The project requires routine progress messages. After one small edit, a newly discovered owner-only approval blocks the next task. When do you update the user and the plan, what stays active, and what do you do with stale instructions if the current source is inaccessible?

Pass A for requested path, then project convention, then `brain/plans/<feature-slug>/ExecPlan.md`; a response-only plan uses one Markdown fence with indented examples. Pass B for the observable red/green reproducer, a recorded missing prerequisite, open acceptance and independent work continuing. Pass C when host updates continue independently of batched plan bookkeeping, the material blocker and recovery owner are recorded promptly, and uninspectable state is identified as unverified.

## Durable lessons before archival

Copy `files/archive-ready/` into the run directory.

> The report migration is complete. Prepare its ExecPlan for eventual archival. Preserve anything future contributors will need. This checkpoint is documentation-only. Leave the plan in place and stop before archiving it.

Inspect the actual files. Pass when the reusable measurement rule and its rationale have a durable home outside the plan directory, the docs navigation and the plan link to that home, and each link resolves. The plan must still carry the specific accepted run, its result and its decision. Inspect the trace for readback or equivalent verification of the published guidance and links. The project has a documentation index and no existing measurement guide.
