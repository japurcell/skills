1. Parsed eval scenario: PRD #6000, W4 ready, issues #6101/#6102 implemented and reviewed, both use shared verification command `bundle exec rspec spec/requests/admin/export_spec.rb`, verification fails with missing `bundle` binary.
2. Applied SKILL rules: verified shared command group coverage rule (line 210), stop conditions for unavailable verification tools (line 199-204), verification strength rules (line 215-219).
3. Determined: shared group blocks both issues, missing `bundle` is a required stop, diff inspection does not satisfy contracted verification.
4. Composed controller response enforcing framework verification requirement, blocking both issue closures, and requesting environment setup.
