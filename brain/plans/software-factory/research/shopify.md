# Shopify sources and the supplied video

Research date: 2026-10-08 (America/Los_Angeles). This is initial design research, not verification of Shopify's private implementation.

## Supplied video: what it actually represents

The video is **Shopify Just Released The Greatest AI Coding Workflow Ever**, published by **AI LABS**, not Shopify. Its English, auto-generated captions were retrieved through the browser transcript export. It describes AI LABS' reconstruction of Helix, with deliberate changes. It is primary evidence for the author's demonstration, not Shopify's internal implementation. [Video](https://www.youtube.com/watch?v=bBMp5tLxShQ)

Relevant sections: checkpoints and a JSON-backed viewer at [3:01](https://www.youtube.com/watch?v=bBMp5tLxShQ&t=181s); a stop hook at [5:48](https://www.youtube.com/watch?v=bBMp5tLxShQ&t=348s); standalone HTML prototypes and isolated visual/behavior reviewers at [9:51](https://www.youtube.com/watch?v=bBMp5tLxShQ&t=591s); a critic/fixer loop at [12:21](https://www.youtube.com/watch?v=bBMp5tLxShQ&t=741s); and feedback recorded for subsequent work at [13:37](https://www.youtube.com/watch?v=bBMp5tLxShQ&t=817s).

Two distinctions matter: AI LABS uses a critic plus fixer, whereas Shopify describes two independent reviewers. AI LABS describes human review after planning and at the end; Shopify describes checkpoint-level approval by default. The video's promotional claims are not validation results. The linked commercial skill bundle was not inspected.

## Helix: small checkpoints with enforceable review gates

Shopify's first-party article describes an internal migration tool. Work proceeds through small checkpoints. Each passes behavior tests, a visual comparison when applicable, two context-isolated adversarial reviews, and normally an engineer's approval. Review feedback enters memory; completed checkpoints become commits. An explicit autonomous mode can reduce human approvals without weakening the remaining gates. [Helix, September 21, 2026](https://shopify.engineering/helix)

Visual comparisons must use matching application states. A reviewer can reject mismatched screenshots as invalid rather than issue a quality verdict. Fixes require affected checks to run again. This is a useful distinction between invalid evidence, failed quality, and successful validation. The article describes the workflow, but does not expose its internal state store, scheduler, locking, crash recovery, or full source implementation. Those remain unverified. [Helix review gates](https://shopify.engineering/helix)

## Roast: explicit code and agent steps

Shopify describes Roast as a Ruby workflow tool using YAML and Markdown prompts, with command steps, custom Ruby steps, parallel work, conditional flow, and an embedded coding agent. Its example performs deterministic cleanup and type corrections before delegating remaining problems to an agent. Recorded sessions support replay/resuming from steps. This supports the user's central boundary: make ordinary execution explicit and delegate uncertain reasoning. These are first-party documented capabilities; this research did not run Roast or audit its current source. [Introducing Roast, June 18, 2025](https://shopify.engineering/introducing-roast)

## Harness design: verification survives model changes

Shopify's security-harness article argues for independently verifiable evidence, structured outputs, and deterministic ownership of credentials, Git, and storage. It describes using real application tests as an oracle and cross-model verification. The transferable principle is separation of proposal from acceptance: a model can propose a finding or fix, while the harness checks an explicit evidence contract. This is supporting design evidence, not a security guarantee for any proposed factory. [Building an agentic harness that outlasts the model, July 29, 2026](https://shopify.engineering/building-an-agentic-harness-that-outlasts-the-model)

## Design implications (our proposals)

Use code to validate structured checkpoint proposals, record transitions, execute checks, enforce attempt limits, and accept evidence tied to a code revision. Agents choose a decomposition, implement changes, identify problems, and propose lessons. A stop hook may remind or re-enter a workflow, but the authoritative state transition should live in the runtime. A failed gate cannot become passed through narration.

Treat UI reference state, accepted code revision, workflow version, and reviewer context as explicit artifacts. Invalidate an old verdict after relevant code changes. Keep human approval policy configurable per workflow; do not silently infer approval from agent confidence. Prototype walkthroughs should demonstrate failures, recovery, and exhausted retries, not just an idealized success path.

The three proposed architectures differ in where state and scheduling live. None should change this trust boundary. Their diagrams, sample events, and recovery policies are design proposals, not claims that Shopify already implements them.
