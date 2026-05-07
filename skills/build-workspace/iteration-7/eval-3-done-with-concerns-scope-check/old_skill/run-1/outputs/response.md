**The manager stops and handles the concern first.** In that build workflow, `DONE_WITH_CONCERNS` means the manager must read the concerns **before any downstream step or tracking update**. Since “the changes may not match the requested scope” is a **scope concern**, the manager treats it as unresolved work, usually **re-dispatches the implementer** to correct or confirm scope, and **does not update tracking yet**.

Clean tests and a clean build do **not** override that. Tracking only gets updated after the concern is resolved and the workflow reaches a final plain **`DONE`**.
