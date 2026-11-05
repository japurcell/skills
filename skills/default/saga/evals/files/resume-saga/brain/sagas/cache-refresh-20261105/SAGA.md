# Saga: cache refresh
- Saga directory: brain/sagas/cache-refresh-20261105
- Repo: disposable fixture @ main
- Status: in-progress

## Problem statement
Add an opt-in asynchronous mode to the cache refresh endpoint while preserving synchronous behavior for existing clients.

## Saga exit criteria
1. Existing clients retain synchronous refresh behavior.
2. Clients can request asynchronous refresh and receive an observable completion status.

## Milestone index
1. 01-contract - define request and response behavior; depends on none.
2. 02-implementation - implement and validate the mode; depends on 01-contract.
