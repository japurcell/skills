# Native popup and sound prototype

**Type:** prototype
**Status:** claimed by subagent-root-native
**Blocked By:** native-toolkit-feasibility.md
**Research Dir:** not applicable

## Question

Do real desktop windows and gentle direct audio satisfy the accepted interaction on macOS, Windows, and Linux through WSLg, without requiring admin access? Ubuntu desktop remains an untested optional environment; a separate live run is not part of current acceptance.

## Current evidence

- [Native experiment and verified limits](../phase-4-native-desktop-prototype.md).
- macOS: user confirmed visible popup and gentle audible success/failure previews. Quit crash reproduced, fixed, and user confirmed the actual button now closes without error.
- [Run guide](../native-platform-run-guide.md) and source bundle prepared for Windows, macOS, and Linux/WSLg; optional Ubuntu instructions remain available. Windows and WSLg runtime checks are recorded in the run guide and platform evidence. Native Ubuntu-specific behavior was not tested, but a separate Ubuntu live run is not required.
- Keep open for the latest-source Windows Preview/focus smoke and unresolved product/production accessibility choices. macOS Milestone 2 is met for the observed host and available environment. Do not interpret source portability as production approval.
