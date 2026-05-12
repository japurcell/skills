---
name: issue-to-spec
description: Given a Github issue, build a spec file to define the requirements.
disable-model-invocation: true
---

# Issue to spec

## Inputs

You receive these parameters in your prompt:

- **github_issue** (required): The Github issue number to read and build a spec for.

## Steps

1. Read Github issue `$github_issue` into context using gh-cli including all comments.
2. Call the create-spec skill and pass it the Github issue content as arguments.
