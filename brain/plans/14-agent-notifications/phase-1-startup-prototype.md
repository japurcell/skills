# Startup prototype

- Goal: review the chosen hybrid lifecycle before selecting a native architecture.
- Status: initial browser prototype exercised. User then confirmed Quit queuing and replaced automatic success expiry with a persistent stack. See [current stack revision](phase-2-alert-stack.md). This is not native feasibility proof.
- [Open single-file prototype](../../../../../../visualizations/2026/10/22/01a16214-d358-76a3-b29a-244a36c7786e/hybrid-startup-prototype.html)
- [Verified desktop preview](../../../../../../visualizations/2026/10/22/01a16214-d358-76a3-b29a-244a36c7786e/hybrid-startup-preview.png)
- [Prototype decision ticket](tickets/hybrid-startup-prototype.md)
- All planning documents live in this numbered brain plan directory, per user direction. Disposable code stays in the visualization artifact directory.

## Behavior under review

- First event starts one simulated instance. Later events reuse it; a burst adds four pending alerts.
- Optional login startup is simulated and changes no OS settings.
- All alerts now persist in a stack until dismissed. Snooze cycles to the back; dismissal deletes with brief Undo.
- Accepted Quit policy: queue alerts until manual reopening and preserve the existing stack.
- Simulated crashes retain the stack; the next event restarts the app and restores it.
- Pending demo alerts/preferences use browser key `PROTOTYPE-agent-alerts-hybrid-v1`. Reset removes only that key. Reload resets simulated runtime while preserving pending alerts.
- Guided walkthroughs reset pending demo alerts/preferences to known states. This is labeled in the UI.
- Design tokens: slate `#203b57`, blue `#145b9f`, pale blue `#dce8f3`, paper `#ffffff`, ink `#203247`, muted `#52667c`. System Avenir Next/Segoe UI, left-aligned controls, desktop preview and persistent pending stack. Restraint keeps attention on alert panels.

## Initial verification (historical, before stack revision)

- Browser UI: cold/warm events showed one instance and one start; success expiry kept its unreviewed history entry.
- Quit/pause: later event queued with zero instances; Open app delivered the queued alert.
- Restart policy: next event reopened the app after explicit Quit.
- Crash/burst: history remained and the next burst used one restarted instance.
- Login option: simulated login started the app before another event. Reload retained seven history entries and the option while resetting runtime counts.
- Guided cold/warm sequence completed; focus moved through steps and returned to the scenario selector.
- Dismiss and Mark all reviewed preserved history; no browser console warnings/errors were observed.
- Inline JavaScript passed `node --check`. All local Markdown links in this plan resolved after relocation.
- Desktop screenshot reviewed. Responsive CSS is present; narrow viewport and screen-reader behavior have not been exercised.
- No automated tests were added to throwaway prototype code, per prototype skill. No real hooks, login registrations, native sound/window placement, latency, resource use, or concurrent OS processes were tested.
- The expiry and restart-after-Quit scenarios above describe the initial trial only; they are superseded by user choices and are not current behavior. Current checks are in the stack revision note.

## Run and recovery

- Double-click the HTML file; it needs no dependencies. Browser storage support for local files can vary; UI reports storage failures.
- Current browser preview: `http://127.0.0.1:8894/hybrid-startup-prototype.html`.
- To serve again, run `rtk proxy python3 -m http.server 8894 --bind 127.0.0.1 --directory /Users/adam/.codex/visualizations/2026/10/22/01a16214-d358-76a3-b29a-244a36c7786e` from the repository root. This is a static preview server, not the notification app.
- Existing preview server uses exec session `31905`; stop it with Ctrl-C when no longer needed. No system startup setting was changed.
- Native architecture and sounds are future prototypes. Do not promote this HTML into production.
- Reflection: findings are task-specific and captured here; no separate durable brain topic or skill edit is needed.
