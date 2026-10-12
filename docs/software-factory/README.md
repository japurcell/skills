# Software factory design review

The [wayfinder map](map.md) records confirmed requirements and routes the remaining planning sessions toward an implementation-ready specification. Open decision tickets live in [tickets/](tickets/).

The [progress handoff](handoff.md) records current status, the next planning session, and verification limits.

The [local durable runtime comparison](research/embedded-runtime-comparison.md) compares embedded TypeScript candidates, Restate, DBOS, Python alternatives, a factory-owned executor, SSSF's recovery boundary, and human-triggered Continue.

Open [the interactive comparison](prototypes/index.html), then explore:

- [Repo runner](prototypes/repo-runner.html): ordinary code recipes and one local execution owner.
- [Durable graph](prototypes/durable-graph.html): persistent checkpoints, dependencies, attempts, and recovery. This is the initial recommendation.
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

Browser verification covered all twelve scenario paths, history drilldown, configuration controls, component selection, quote capture, comment editing/resolution, reload persistence, JSON export/import, invalid imports, and concurrent design views. Compact rendering used 390px frames with 375px content width and no document overflow. Inline JavaScript syntax, embedded data, and local links were checked. See [the delivery audit](delegation.md).
