# Web instructions

Exception: only changes confined to web presentation, such as CSS spacing or colors, may complete with `npm run verify:web` from the root instead of `npm run verify:all`. This exception does not cover web behavior, service changes, or shared API contract changes. Those changes require `npm run verify:all`, including when every edited file is under apps/web.

Preserve keyboard navigation and visible focus in controls.
