Do **not** update tracking yet. The manager should read the simplifier’s concern, treat it as unresolved scope/correctness risk, and send the work back to the **implementer** to verify or tighten the extracted helper so behavior can’t silently change.

After that fix, rerun simplification/review on the affected files, and only mark the wave done once downstream agents return **DONE**.
