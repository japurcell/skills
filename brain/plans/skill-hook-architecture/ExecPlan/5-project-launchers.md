# M5. Project brain launch registrations

Status: open
Acceptance: not met

## Assignment

T5 belongs to the milestone implementer. Work from the repository root on a branch based on the committed plan. Integrate after M3 so generator changes build on current output ownership. Reproduce any defect through the caller before editing. Stop when the behavior below is delivered, checks are recorded and any native evidence gap is named.

## Source and interfaces

- `skills/default/brain-install/scripts/install.py`
- `skills/default/brain-install/tests/test_install.py`
- `scripts/generate-hooks.py`

## Definition and rollout

One build-time definition produces the brain-owned registration fields for two events across three providers, in both repository and portable configurations. Keep provider-specific event metadata, timeouts, command field names and shell quoting. Freeze the exact 20 current decoded command strings from the pre-change revision in an independent rollout fixture keyed by document, event and shell field. Also check all other owned metadata. The generator cannot rewrite its expected fixture.

## Mixed documents

Locate owned registrations by provider, event and complete known registration identity, including recognized historical interpreter forms. Preserve unowned settings, handler order, customized or ambiguous entries and file modes. Require an explicit conflict on ambiguity or a customized candidate. Identify a handler by content, never by array position. A missing owned entry in an otherwise valid document may be added without disturbing other handlers. Keep --check read-only. Only the checked-in source documents are generation targets.

## Publication

Read and merge the current documents under the generator’s writer lock. Stage validated replacements, retaining original bytes for rollback. Before each replace, check the destination still matches the input snapshot. On a changed snapshot, stop and report a conflict. Roll back only contents still matching this transaction’s published bytes. Preserve unrelated edits visible at read or conflict detection. The lock serializes generator writers; external editors that ignore it are outside an atomic multiwriter guarantee.

## Acceptance

Compare all 20 commands independently before enabling writes. Test an unrelated handler inserted first, two possible owners, changed owned metadata, unchanged re-runs, an unrelated edit between staging and publication, and a later failure during a multi-file write. Run actual launches from nested and non-Git directories and exercise the installed portable configuration.

## Verification

Run from the checkout root. Each command must exit zero. Inspect the files or output specified above.

- `rtk proxy python3 scripts/tests/hooks/test-generate-hooks.py`
- `rtk proxy python3 scripts/generate-hooks.py --check`
- `rtk proxy python3 scripts/tests/hooks/test-brain-hooks.py`
- `rtk proxy python3 -m unittest discover -s skills/default/brain-install/tests`

## Progress

- [ ] [milestone-5] Implement T5 and exercise the public entry points.
- [ ] [milestone-5] Verify integrated behavior and record platform evidence.
