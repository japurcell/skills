# Archive Service

Use the archive endpoint to queue archive jobs for approved paths.

Example local smoke test:

```bash
curl -X POST http://localhost:5000/archive \
	-H 'X-Ops-Token: local-dev-token-123' \
	-d '{"target":"/srv/data"}'
```
