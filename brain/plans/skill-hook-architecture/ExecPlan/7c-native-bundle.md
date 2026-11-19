# T7c. Resolve native bundle verification

The Windows qualification run at `f629beff` rejected administrator-group-owned workspaces. A standard-user rerun at `c27a2f8e` confirmed matching caller and owner and passed the exact batching cases. It exposed three diagnostic decoding errors and one ACL case that accepted the purported shared default. The raw diagnostics are in GitHub Actions run 44495020838, job 135459880408.

The native-bundle implementer owns the installed Ruminate caller and bundle fixtures related to these observations. Reproduce through the installed command or documented caller. Verify that positive fixtures create genuinely user-owned private directories and that a negative fixture creates the intended unsafe permissions before testing rejection. Preserve the strict owner and ACL rules, actual byte readback, and checks for no writes. Check the encoding of child output/diagnostics independently of the host console encoding.

Run `rtk proxy python3 -m unittest discover -s skills/default/brain-install/tests` on macOS, then have the coordinator rerun the four Windows ACL cases and relocated project workflow on native Windows. Record the commit, results and limits here. Stop once the public cases pass, including the negative controls. See the [batching contract](7-conversation-batches.md).

## Current result (2026-11-19)

The documented caller captures UTF-8 child diagnostics and writes them through its own stderr encoding. The Windows junction fixture keeps native command output as bytes. The negative ACL fixture replaces the entire parent DACL with protected, non-inheritable trusted ACEs and proves a newly created probe has an Everyone ACE before extraction. It requires an actual rejected empty output file. The strict owner and ACL rules are unchanged.

On macOS, `rtk proxy python3 -m unittest discover -s skills/default/brain-install/tests` passed 58 tests with four Windows-only skips. Native Windows validation is still open: the coordinator must run the four Windows ACL cases and relocated caller workflow as a standard user and retain the output. The probe deliberately fails if the runner cannot produce the unsafe ACL, so a passing suite proves the setup as well as rejection.

Native run 44496566199, job 135465141445, passed the other standard-user cases but the negative probe found inherited private ACEs. Python's mode-700 directory carries explicit inheritable ACEs, so `icacls /grant:r` did not establish the intended fixture. Candidate `8dfa8663` replaces the whole DACL and is awaiting native qualification.

The Windows matrix now uses a disposable ordinary account and user-owned scratch directory for the bundle suite. Its launcher is derived from the previously proven standard-user CI trial; the updated launcher and final integrated matrix still need native verification. The macOS bundle suite at `8dfa8663` passed 58 tests with four skips.
