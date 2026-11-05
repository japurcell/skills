# Collapse Lines

This feature ships as a line filter. Its public interface accepts newline-terminated text on standard input and returns text on standard output. Empty input is valid. Only ASCII input, the default mode, and newline-terminated lines are in scope.

To exercise the shipping behavior locally, pipe input into `LC_ALL=C uniq`. Consumers depend on which lines come out. They do not depend on the executable used to produce them.
