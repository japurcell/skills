I’m writing the dry-run decision artifact now.

Reading back the written decision file.

Source of truth: `prd.json` is official; `progress.txt` is supplemental resume data only.
Resolved progress file: `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/overlap-serialize-fixture/progress.txt`.
Active wave: `parallelBatch` 2, ready stories `US-002` and `US-003`.
Safe dispatch plan: serialize the wave because both stories likely touch the same owner file `src/ui/BillingSettingsPage.tsx`; dispatch `US-002` first by priority, then `US-003` after `US-002` resolves.
