# Software factory design review

The [wayfinder map](map.md) records confirmed requirements and routes the remaining planning sessions toward an implementation-ready specification. Open decision tickets live in [tickets/](tickets/).

The [progress handoff](handoff.md) records current status, the next planning session, and verification limits.

**Current execution decision, 2026-10-15:** [SSSF-style continuation](tickets/workflow-versioning-and-run-changes.md#resolution). Explicitly invoke the current script from its entry point, optionally joining history and compatible agent context. SQLite stores observable history, not restorable workflow execution. Old durable-runtime comparisons and prototype Continue/wait examples are historical; the accepted layout remains unchanged.

## Swimlane design review

**Layout accepted, 2026-10-15:** open the [observability prototype](http://localhost:8765/prototypes/observability-prototype.html), or its [standalone HTML](prototypes/observability-prototype.html). It follows the supplied [SSSF screenshots](prototypes/screenshots/): run index with miniature live timelines, full run timeline, then phase request/configuration/events/outputs. All workflow inputs now belong to configuration and CLI arguments. The web UI has no execution controls. View filtering and freezing affect observation only; prototype review notes are separate design feedback.

Select a run card, then a phase. Synthetic output arrives every two seconds in the active run, including on its index card. Freeze this view holds an observation snapshot while recording continues. Waiting and interrupted examples explain why work has stopped without accepting a response. Notes save in this browser and export as Markdown. The simulation proves no runtime or adapter guarantees. The [layout resolution](tickets/swimlane-interaction-design.md#resolution) records acceptance. [Detailed observability UI design](tickets/detailed-observability-ui-design.md) owns the later visual, interaction, responsive, accessibility, and scale review before specification acceptance.

The [hook incident report](hook-scan-limit-incident.md) explains the scan-size failure encountered when reviewing the screenshots, source/deployment differences, and a repair/validation path for the owner. The hook was disabled by the user; no scanner repair or successful security scan is claimed.

### Earlier comparison, retained for existing review notes

Open the [swimlane interaction prototype](http://localhost:8765/prototypes/swimlane-prototype.html?variant=A), or open its [standalone HTML file](prototypes/swimlane-prototype.html). This comparison predates the observability-only direction. Its execution controls are historical, not current requirements.

Use the bottom switcher to compare three layouts with the same data:

- **A / Nested timeline:** scopes and steps arranged against observed elapsed time. Recommended starting point for seeing concurrent work.
- **B / Scope lanes:** workflow-defined scopes become columns, with work cards inside. Easy task scanning; wide workflows require horizontal scrolling.
- **C / Session console:** conversations and recorded activity take priority. Useful for following agents, with less immediate visibility of the whole workflow.

This earlier recommendation was superseded by the accepted observability layout. The [Swimlane interaction design ticket](tickets/swimlane-interaction-design.md) retains the comparison and its verification limits.

Try the repository change, review-only, and custom branch/loop examples in the left navigation. Selecting an example resets that simulation. Select steps to inspect output, context, profiles, evidence, and earlier attempts. Use **Play events** or **Next saved event** to advance; permission and checkpoint waits require explicit responses. Try **Simulate runner crash**, **Continue**, and the history slider. All commands and permissions are simulated. No command shown by this prototype should be treated as an installed CLI.

Use **Comment** for a layout or **Comment on this step** for contextual feedback. **Review notes** exports Markdown for sharing in chat. These notes use separate browser storage from the earlier architecture documents, and support export rather than import. Simulation state is in memory and resets on reload; only review notes persist. Export notes before changing browser, hostname, or port.

Use the preview command below if the local server is not running.

## Earlier architecture comparisons

The [local durable runtime comparison](research/embedded-runtime-comparison.md) compares embedded TypeScript candidates, Restate, DBOS, Python alternatives, a factory-owned executor, SSSF's recovery boundary, and human-triggered Continue.

Open [the interactive comparison](prototypes/index.html), then explore:

- [Repo runner](prototypes/repo-runner.html): ordinary code recipes and one local execution owner.
- [Durable graph](prototypes/durable-graph.html): persistent checkpoints, dependencies, attempts, and recovery. This was the initial recommendation; the Wayfinder tickets own subsequent executor decisions.
- [Event factory](prototypes/event-factory.html): independent workers coordinated through an event ledger.

## Reviewing and commenting

Select a diagram component to inspect its responsibility and failure behavior. Use **Run lab** to step through success and failure scenarios. **Workflow design** changes an illustrative configuration; it does not change the fixed run-lab fixture.

Use a section's **Comment** button, **Comment on component**, or select text and choose **Comment on selected text**. Open **Notes** to edit, resolve, or reopen comments. Comments save in this browser, at this origin or file location. Separate notes persist independently across open designs; concurrent edits to the same note use the latest saved version.

Use **Export JSON** for a portable backup and later import. Use **Export Markdown** for readable feedback to share in this chat. To restore JSON, open **Import JSON**, paste the exported document, and choose **Merge notes**. Nothing is sent automatically. Export before changing browser, hostname, port, or file location.

The HTML files contain their own styles, scripts, and simulated data. No build or external library is required. Keep the folder together for navigation and research links. Browser storage behavior for directly opened files varies; a stable local preview origin keeps the review collection together.

To restart the preview from the repository root:

```sh
rtk proxy python3 -m http.server 8765 --bind 127.0.0.1 --directory docs/software-factory
```

Then open [the local comparison](http://localhost:8765/prototypes/index.html).

## Evidence and limits

Read [the research synthesis](research.md) for source findings, requirements, uncertainties, and first implementation experiments. Detailed reports cover [SSSF](research/super-simple-software-factory.md), [no-mistakes](research/no-mistakes.md), [Noodle](research/noodle.md), [Shopify and the video](research/shopify.md), and [harness integration](research/harness-adapters.md).

All factory runs, agent responses, usage figures, and recovery behavior shown in these HTML documents are simulations. No upstream runtime or test suite was executed. The proposed architectures require implementation experiments before production claims are justified.

Earlier architecture-document verification covered all twelve scenario paths, history drilldown, configuration controls, component selection, quote capture, comment editing/resolution, reload persistence, JSON export/import, invalid imports, and concurrent design views. Compact rendering used 390px frames with 375px content width and no document overflow. Inline JavaScript syntax, embedded data, and local links were checked. See [the delivery audit](delegation.md). The newer swimlane prototype has its own bounded browser verification record in its ticket; it does not inherit this earlier coverage.
