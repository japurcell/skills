# Learn

The intended command accepts UTF-8 JSON input using `--input PATH` or `--input -`, along with an integration-issued `--invocation-file`. A path or provider-named environment variable does not establish identity or authority.

In the current standalone source CLI, no integration can register active context. `learn` therefore exits with code 2 before opening the input or invocation file and before creating state or changing knowledge. Report the operation as unavailable; do not claim a lesson was recorded. The active foreground agent performs semantic work only when a registered integration later supplies an eligible context. The CLI itself never launches a model.
