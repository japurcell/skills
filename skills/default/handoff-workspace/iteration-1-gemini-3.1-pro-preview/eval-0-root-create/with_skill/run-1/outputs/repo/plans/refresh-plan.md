Retry plan:
1. Keep the first retry at 0.5s.
2. Add bounded jitter after the first failure.
3. Re-run the focused auth refresh test before broader validation.
