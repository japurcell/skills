# Large report input

Use the supplied report project as the starting point. The command currently summarizes the fixed rows `[7, 11, 13]` and prints `count=3 total=31`. No feature work has started.

We want `--input PATH` to read a UTF-8 file containing one signed integer per line. An empty file is valid and summarizes to count 0 and total 0. Reject a blank or malformed line with exit code 2, a stderr diagnostic naming the one-based line number, and no summary on stdout. Omitting `--input` must preserve the existing fixed-row output exactly.

The current `summarize(rows)` function needs a list. We are considering a streaming implementation because production files may contain ten million rows. Parsing input one line at a time and accumulating totals without a list are separate unknowns for this project. We have not measured their behavior or memory use. Use only the Python standard library.

During adoption, expose `--engine list` and `--engine stream` for file input. Keep `list` as the default until the replacement has sufficient evidence. The stream path must stay below 64 MiB peak process RSS for ten million short integer rows on the target Linux Python 3 environment. The data-generation step is outside that memory measurement. The report output and error behavior must agree across both engines. Once the replacement is proven, switch the default and describe how the legacy path could be retired safely.

Write an implementation-ready ExecPlan for another contributor. Make reasonable technical choices and explain them. This request is for the plan only; do not implement the feature or claim unperformed measurements.
