# Research delegation and delivery audit

Three independent researchers inspected the supplied repositories. Each owned one report, ran no upstream code, and completed within the 12-minute warning threshold. The coordinator reviewed the findings, checked representative source claims, reconciled uncertainties, researched Shopify and harness interfaces, and created the prototypes.

The selected route used the catalog's lowest-cost capable Standard model. Runtime pricing and actual executed model settings were not independently reported. Selected and submitted settings matched; execution settings remain explicitly unconfirmed.

```yaml
dispatches:
  - subtask_id: factory_research
    artifact: research/super-simple-software-factory.md
    selected: {model: gpt-6-luna, reasoning_effort: max}
    submitted: {model: gpt-6-luna, reasoning_effort: max}
    executed: {model: unconfirmed, reasoning_effort: unconfirmed}
    runtime_limit:
      value: 12 minutes
      mechanism: Coordinator wall-clock checks and non-interrupting status warning
    status: completed
    output_verified: true
    routing_compliant: true
  - subtask_id: validation_research
    artifact: research/no-mistakes.md
    selected: {model: gpt-6-luna, reasoning_effort: max}
    submitted: {model: gpt-6-luna, reasoning_effort: max}
    executed: {model: unconfirmed, reasoning_effort: unconfirmed}
    runtime_limit:
      value: 12 minutes
      mechanism: Coordinator wall-clock checks and non-interrupting status warning
    status: completed
    output_verified: true
    routing_compliant: true
  - subtask_id: noodle_research
    artifact: research/noodle.md
    selected: {model: gpt-6-luna, reasoning_effort: max}
    submitted: {model: gpt-6-luna, reasoning_effort: max}
    executed: {model: unconfirmed, reasoning_effort: unconfirmed}
    runtime_limit:
      value: 12 minutes
      mechanism: Coordinator wall-clock checks and non-interrupting status warning
    status: completed
    output_verified: true
    routing_compliant: true
```

Verification is bounded to source inspection, citations, and consistency with the design requirements. It does not mean upstream execution was tested. Reports preserve their snapshot limitations, including no-mistakes' mixed main-branch views and Noodle's unresolved stage-group semantics.

## Delivery verification

- All twelve browser walkthroughs reached their intended completed, awaiting-approval, or needs-attention state.
- The same fixture events support live and historical inspection; configuration controls update the separate illustrative draft.
- Notes persist after reload. JSON export was inspected; valid duplicate import merges once and invalid input reports an error. HTML-like note text remains literal.
- Selected-text capture, component anchors, editing, resolution, and Escape dismissal were exercised.
- A multi-view overwrite bug was reproduced in the browser. Storing each note independently fixed it; a final two-tab check preserved both graph notes and both runner notes after reload on 2026-10-12.
- Desktop layouts and compact 390px frame layouts were inspected. All four documents had equal content and viewport widths at the compact size. Diagrams scroll within their own container.
- JavaScript syntax, embedded JSON, and local document links were validated. These disposable prototypes have no added regression suite.
- The final preview uses localhost; disposable QA notes remain on the separate 127.0.0.1 origin.

## Knowledge maintenance

The coordinated `update-agent-docs` pass found no new durable, non-obvious repository rule to admit. Research conclusions remain in this active design effort. No canonical KB documents or protected AGENTS.md sections changed. The idea inbox now links to this review package.

```text
Added: None
Changed: None
Split or moved: None
Deduplicated: None
Index updates: None
Remaining doc quality TODOs: None
```
