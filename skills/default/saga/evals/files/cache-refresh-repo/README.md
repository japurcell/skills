# Sample application

This disposable repository is a small Python service. A `/cache/refresh` route currently refreshes every tenant synchronously. The requested feature is an optional asynchronous refresh mode controlled by a per-request flag. Existing clients must keep the synchronous behavior by default. The repository has not yet selected an implementation approach.

Planning-only benchmark fixture. Do not treat this file as permission to implement the feature.
