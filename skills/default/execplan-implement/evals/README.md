# ExecPlan implementation authoring review

Load when changing this skill's instructions or authoring scenarios. The cases in `evals.json` are scoped to document review. A read-only interpretation can establish instruction coverage and identify contradictory gates; it does not establish sandbox execution, successful integration, real test results or runtime behavior. Preserve that evidence boundary when reporting results.

Cases 10-12 exercise parent decisions at runtime deadlines using supplied timelines, including the coordinator, checkpoints, replacement ownership and cleanup. Grade the decisions and any stated instruction conflict against the supplied skill snapshot. These scenarios do not run or measure a host timer, cancellation, worker quiescence or actual writes.
