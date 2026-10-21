No serialization or ownership transfer needed. Workers can update their separate area docs in parallel and retain ownership.

Shared canonical documents need one integration owner or explicit serial dependency. Here, neither worker touches one. Workers notify the coordinator of durable findings; the coordinator reconciles admitted claims and runs the final documentation pass after both finish.