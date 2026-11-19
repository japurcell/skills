# T7c. Resolve native bundle verification

The Windows qualification run at `f629beff` rejected administrator-group-owned workspaces. A standard-user rerun at `c27a2f8e` confirmed matching caller and owner and passed the exact batching cases. It exposed three diagnostic decoding errors and one ACL case that accepted the purported shared default. The raw diagnostics are in GitHub Actions run 44495020838, job 135459880408.

The native-bundle implementer owns the installed Ruminate caller and bundle fixtures related to these observations. Reproduce through the installed command or documented caller. Verify that positive fixtures create genuinely user-owned private directories and that a negative fixture creates the intended unsafe permissions before testing rejection. Preserve the strict owner and ACL rules, actual byte readback, and checks for no writes. Check the encoding of child output/diagnostics independently of the host console encoding.

Run `rtk proxy python3 -m unittest discover -s skills/default/brain-install/tests` on macOS, then have the coordinator rerun the four Windows ACL cases and relocated project workflow on native Windows. Record the commit, results and limits here. Stop once the public cases pass, including the negative controls. See the [batching contract](7-conversation-batches.md).

## Current result (2026-11-19)

The documented caller captures UTF-8 child diagnostics and writes them through its own stderr encoding. The Windows junction fixture keeps native command output as bytes. The negative ACL fixture replaces the entire parent DACL with protected, non-inheritable trusted ACEs and proves a newly created probe has an Everyone ACE before extraction. It requires an actual rejected empty output file. The strict owner and ACL rules are unchanged.

The macOS suite ran 58 tests with four Windows-only skips. The Windows fixture now checks that its setup created a shared file before evaluating rejection and confirms an actual rejected file contains zero bytes.

Native run `44496566199`, job `135465141445`, passed the other standard-user cases, but the probe found inherited private ACEs. Python's mode-700 directory carried explicit inheritable ACEs. Replacing only named grants left those entries in place. Candidate `8dfa8663` replaces the whole fixture DACL.

The final Windows qualification at `715d2415` ran 58 bundle tests on Python 3.13, with seven POSIX-only skips. All four ACL cases and the relocated caller passed. The current user's identity matched the workspace owner. The standard-user launcher also passed in the Python 3.12 and 3.14 Windows matrix. [Native job](https://github.com/japurcell/skills/actions/runs/44497720899/job/135469086388) and [platform matrix](https://github.com/japurcell/skills/actions/runs/44497720740).
