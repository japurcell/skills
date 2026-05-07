**The manager stops and handles the concern first.** In this workflow, `DONE_WITH_CONCERNS` means: read the concerns **before any downstream step or tracking update**. Since the concern is a possible **scope mismatch**, the manager treats it as unresolved work, usually **re-dispatches the implementer to fix or confirm scope**, and **does not update tracking yet**.

Tracking only happens later, after the concern is resolved and the task makes it through the remaining workflow to a final reviewer `DONE`.
