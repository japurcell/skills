# T7c. Resolve native bundle verification

The Windows qualification run at `f629beff` rejected administrator-group-owned workspaces. A standard-user rerun at `c27a2f8e` confirmed matching caller and owner and passed the exact batching cases. It exposed three diagnostic decoding errors and one ACL case that accepted the purported shared default. The raw diagnostics are in GitHub Actions run 44495020838, job 135459880408.

The native-bundle implementer owns the installed Ruminate caller and bundle fixtures related to these observations. Reproduce through the installed command or documented caller. Verify that positive fixtures create genuinely user-owned private directories and that a negative fixture creates the intended unsafe permissions before testing rejection. Preserve the strict owner and ACL rules, actual byte readback, and checks for no writes. Check the encoding of child output/diagnostics independently of the host console encoding.

Run `rtk proxy python3 -m unittest discover -s skills/default/brain-install/tests` on macOS, then have the coordinator rerun the four Windows ACL cases and relocated project workflow on native Windows. Record the commit, results and limits here. Stop once the public cases pass, including the negative controls. See the [batching contract](7-conversation-batches.md).
