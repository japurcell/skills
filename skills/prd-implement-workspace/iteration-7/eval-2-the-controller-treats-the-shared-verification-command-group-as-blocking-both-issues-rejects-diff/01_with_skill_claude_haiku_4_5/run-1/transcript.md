Skill file: /home/adam/dev/personal/skills/skills/prd-implement/SKILL.md

Key reasoning: The eval tests shared verification command group atomicity (SKILL.md lines 233-244, especially line 243). When multiple child issues are covered by a single shared verification group, the group's pass/fail outcome applies to all covered issues. The controller correctly identifies that the shared group `bundle exec rspec spec/requests/admin/export_spec.rb` failure blocks both #6101 and #6102, rejects diff inspection as a substitute, keeps both issues open, and stops. This satisfies all five assertions.
