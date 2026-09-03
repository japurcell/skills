# pytest best practices for converting the bash hook test suite to pytest

Research notes from the official pytest documentation (`docs.pytest.org/en/stable/`,
the 9.x line — doc examples render as `pytest-9.x.y`). Every non-obvious claim
cites the exact page it was taken from. Anything not traceable to the pytest docs
is labeled **general Python practice (not from pytest docs)**.

Test context: the suite exercises Python "hooks" — entry-point scripts that read
JSON from stdin, print JSON to stdout, and exit `0` (normal) or `2` (hard block,
reason on stderr). The current bash tests use `mktemp`, env overrides
(`HOME`, `GEMINI_PROJECT_DIR`), subprocess invocation with piped JSON stdin,
`jq` for stdout parsing, exit-code assertions, and file-state checks. Some tests
exercise an *installed* copy of the hooks inside a temporary `HOME`.

Note on sources: `https://docs.pytest.org/en/stable/faq.html` returns 404 and no
FAQ page appears in the stable docs navigation (checked 2026-09-01); there is no
dedicated "how to test CLI/subprocess programs" page either. What the docs do say
about subprocess output is covered in §5 and §11.

---

## 1. How to use this for the bash→pytest hook conversion (mapping)

| Bash idiom | pytest replacement | Section |
|---|---|---|
| `tmpdir=$(mktemp -d)` per test case | `tmp_path` fixture — unique `pathlib.Path` dir per test, no manual cleanup | §3 |
| One shared temp `HOME` set up once for the "installed copy" tests | session-scoped fixture using `tmp_path_factory.mktemp("home")` (§3) + `yield` teardown (§9) | §3, §9 |
| `HOME=$tmp GEMINI_PROJECT_DIR=$proj ./hook ...` | `monkeypatch.setenv(...)` / `delenv(...)` — auto-reverted after the test (§4) | §4 |
| `echo "$json" \| hook; status=$?` | `subprocess.run([...], input=json.dumps(payload), capture_output=True, text=True)` (§11) | §11 |
| `[ $status -eq 2 ]` + `grep reason` on stderr | `assert result.returncode == 2`; `assert "reason" in result.stderr` (§11) | §11 |
| `jq -e '.field == "x"'` on stdout | `json.loads(result.stdout)` + plain asserts (§11) | §11 |
| Repeated near-identical cases per payload | `@pytest.mark.parametrize` over `(payload, expected_exit, ...)` tuples (§5) | §5 |
| "only run the slow installed-copy tests" flag | registered marker (e.g. `installed`) + `pytest -m "not installed"` (§8) | §8 |
| File-state checks after the hook runs | plain `assert (tmp_path / "x").read_text() == ...` in the same test | §11 |
| Suite exit status drives CI | pytest exit codes: `0` all passed, `1` some failed, `5` no tests collected (§10) | §10 |
| Fail-fast while iterating locally | `pytest -x` or `--maxfail=2`; do not bake into CI config (§10) | §10 |

Highest-value practices for this conversion:

1. **One test function per behavior**; use `parametrize` for payload matrices
   (each case gets its own `[id]` in reports). §5.
2. **A single `run_hook` helper** (plain function or fixture in `conftest.py`)
   wrapping `subprocess.run` so JSON plumbing, timeout, and env handling live in
   one place. §11.
3. **`tmp_path` for per-test sandboxes**; a session-scoped
   `tmp_path_factory.mktemp(...)` fixture for the installed-copy `HOME` so the
   `pip install` happens once per run, not per test. §3, §9.
4. **`monkeypatch.setenv`/`delenv` for `HOME` / `GEMINI_PROJECT_DIR`** —
   automatically reverted, so no bash-style save/restore boilerplate. The hook
   subprocess sees the patched values because a child inherits the parent
   environment when `env=` is not passed (general Python practice, not from
   pytest docs). §4.
5. **Do not reach for `capsys`/`capfd` to read the hook's output.** With
   `capture_output=True` the child's stdout/stderr go to pipes owned by
   `subprocess`, not FD 1/2, so pytest capture never sees them — assert on
   `result.stdout`/`result.stderr`. §5.
6. **Register all custom markers in `pyproject.toml` and enable
   `--strict-markers`** via `addopts`, so typos fail loudly. §7, §8.
7. **Keep pytest's own exit code in mind**: the hook's exit code `2` (hard
   block) is data you assert on; pytest exiting `2` means "interrupted by the
   user" and is unrelated. §10.

---

## 2. Fixtures: scope, parameters, conftest

- A fixture is a function decorated with `@pytest.fixture`, requested by name as
  a test argument. Default scope is `function` (one instance per test). Possible
  values for `scope`: `function`, `class`, `module`, `package`, or `session`.
  A higher scope means the fixture is invoked once and shared across that unit.
  Source: <https://docs.pytest.org/en/stable/explanation/fixtures.html#scope-sharing-fixtures-across-classes-modules-packages-or-session>

- Fixtures are created when first requested and destroyed at the end of their
  scope (`function`: end of test; `module`: teardown of last test in module;
  `session`: end of run). Source: same page, "Fixture scopes".

- **Parametrized fixtures**: with a parametrized fixture, "pytest may invoke a
  fixture more than once in the given scope" because only one instance is cached
  at a time. Source: same page, "Fixture scopes".

- **Dynamic scope**: `scope` may also be a callable
  (`def determine_scope(fixture_name, config): ...`) evaluated once at fixture
  definition — useful for e.g. choosing container lifetime from a CLI option.
  Source: <https://docs.pytest.org/en/stable/explanation/fixtures.html#dynamic-scope>

- **Sharing via `conftest.py`**: putting a fixture in a directory's
  `conftest.py` makes it available to all tests in that directory and below.
  Source: <https://docs.pytest.org/en/stable/explanation/fixtures.html#scope-sharing-fixtures-across-classes-modules-packages-or-session>
  (the `smtp_connection` example moves the fixture into `conftest.py` "so that
  tests from multiple test modules in the directory can access it").

- **conftest discovery order**: at startup pytest determines the test paths
  (command line, else `testpaths`, else current dir) and for each test path loads
  its `conftest.py` — "Before a `conftest.py` file is loaded, load `conftest.py`
  files in all of its parent directories." Hooks defined in conftests closer to
  the filesystem root run first. Source:
  <https://docs.pytest.org/en/stable/how-to/writing_plugins.html#plugin-discovery-order-at-tool-startup>
  and <https://docs.pytest.org/en/stable/how-to/writing_plugins.html#conftest-py-local-per-directory-plugins>

- **Fixture override**: a fixture with the same name in a `conftest.py` closer
  to the test (or in the test module itself) overrides the outer definition.
  Source: <https://docs.pytest.org/en/stable/explanation/fixtures.html>
  (fixture override section).

- Doc note: don't import from non-package `conftest.py` files; either keep them
  under a package scope or never import from them. Source:
  <https://docs.pytest.org/en/stable/how-to/writing_plugins.html#conftest-py-local-per-directory-plugins>

**For the hook suite**: put `run_hook`, the per-test sandbox, and env fixtures in
`tests/conftest.py`; put the session-scoped installed-`HOME` fixture there too
(or in a dedicated module pulled in via the root conftest).

---

## 3. `tmp_path` and `tmp_path_factory`

- `tmp_path` provides "a temporary directory unique to each test function" and
  is a `pathlib.Path` object. Source:
  <https://docs.pytest.org/en/stable/how-to/tmp_path.html#the-tmp-path-fixture>

- Default location is
  `{temproot}/pytest-of-{user}/pytest-{num}/{testname}/` where `{num}` increments
  per run; "By default, the last 3 temporary directories are kept" — configurable
  via `tmp_path_retention_count` (default `"3"`) and
  `tmp_path_retention_policy` (`all` / `failed` / `none`, default `all`).
  Sources:
  <https://docs.pytest.org/en/stable/how-to/tmp_path.html#temporary-directory-location-and-retention>,
  <https://docs.pytest.org/en/stable/reference/reference.html#confval-tmp-path-retention-count>,
  <https://docs.pytest.org/en/stable/reference/reference.html#confval-tmp-path-retention-policy>

- `tmp_path_factory` is a **session-scoped** fixture for creating arbitrary temp
  dirs from other fixtures or tests. The docs' own example is exactly the
  "expensive resource shared across a session" shape:
  `tmp_path_factory.mktemp("data")` inside a `scope="session"` fixture.
  Source: <https://docs.pytest.org/en/stable/how-to/tmp_path.html#the-tmp-path-factory-fixture>

- `TempPathFactory.mktemp(basename, numbered=True)`: with `numbered=True`,
  `basename="foo-"` creates `foo-0`, `foo-1`, ... Source:
  <https://docs.pytest.org/en/stable/reference/reference.html#tmp-path-factory-factory-api>

- `--basetemp=DIR` overrides the base dir but "will be cleared blindly before
  each test run" and has no retention. Source:
  <https://docs.pytest.org/en/stable/reference/reference.html#cmdoption-basetemp>
  and the retention section above.

- The legacy `tmpdir`/`tmpdir_factory` (`py.path.local`) still exist; "these
  days, it is preferred to use `tmp_path`". Source:
  <https://docs.pytest.org/en/stable/how-to/tmp_path.html#the-tmpdir-and-tmpdir_factory-fixtures>

**For the hook suite**:
- Per-test scratch space (project dir, config files the hook should read/write)
  → `tmp_path`.
- Installed-copy tests → one session fixture:

  ```python
  @pytest.fixture(scope="session")
  def installed_home(tmp_path_factory):
      home = tmp_path_factory.mktemp("home")
      # pip install the hooks into an environment rooted at `home` once
      ...
      return home
  ```

  Every "installed" test requests `installed_home` (directly or through a
  wrapper), so the install happens once per run. Retention of the dir after the
  run is governed by `tmp_path_retention_*`.

---

## 4. `monkeypatch` (env vars, attributes, cwd)

- The `monkeypatch` fixture offers `setattr`, `delattr`, `setitem`, `delitem`,
  `setenv(name, value, prepend=None)`, `delenv(name, raising=True)`,
  `syspath_prepend`, `chdir(path)`, and `context()`. "All modifications will be
  undone after the requesting test function or fixture has finished."
  Source: <https://docs.pytest.org/en/stable/how-to/monkeypatch.html>

- Env-var usage (replaces bash `HOME=... GEMINI_PROJECT_DIR=...` prefixes):

  ```python
  def test_block_reason(monkeypatch, tmp_path):
      monkeypatch.setenv("HOME", str(tmp_path / "home"))
      monkeypatch.setenv("GEMINI_PROJECT_DIR", str(tmp_path / "proj"))
      proc = run_hook({"tool": "Bash", "command": "rm -rf /"})
      assert proc.returncode == 2
  ```

  `monkeypatch.delenv("GEMINI_PROJECT_DIR", raising=False)` simulates the
  variable being absent. Source:
  <https://docs.pytest.org/en/stable/how-to/monkeypatch.html#monkeypatching-environment-variables>

- `setenv("PATH", value, prepend=os.pathsep)` is the documented way to modify
  `$PATH`. Source: <https://docs.pytest.org/en/stable/how-to/monkeypatch.html>

- Subprocess relevance: `monkeypatch.setenv` mutates the pytest process's
  environment; a child started with `subprocess.run(...)` without an explicit
  `env=` inherits it, so the hook sees the patched `HOME` etc. (child-inherits-
  parent-env is general Python practice, not from pytest docs). Alternatively
  pass an explicit `env=` dict to `subprocess.run` and skip `monkeypatch` for
  that variable.

- `monkeypatch.context()` limits patches to a `with` block — useful inside one
  test that needs two different environments. Source:
  <https://docs.pytest.org/en/stable/how-to/monkeypatch.html>

- Docs warnings: don't patch builtins (`open`, `compile`, ...) — it can break
  pytest internals; prefer patching the reference your code uses over the stdlib
  original. Source: same page, notes under "Global patch example".

---

## 5. `capsys` vs `capfd` — and the subprocess limitation

- Default capturing is at file-descriptor level: "All writes going to the
  operating system file descriptors 1 and 2 will be captured." The docs state
  this "allows capturing output from simple print statements as well as output
  from a subprocess started by a test." Source:
  <https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html#default-stdout-stderr-stdin-capturing-behaviour>

- `capsys` captures only writes to Python's `sys.stdout`/`sys.stderr`; `capfd`
  captures at FD level and "allows to also capture output from libraries or
  subprocesses that directly write to operating system level output streams
  (FD1 and FD2)". `capsysbinary`/`capfdbinary` return `bytes`.
  `readouterr()` returns a namedtuple with `out`/`err`, snapshots so far, and
  capturing continues. Source:
  <https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html#accessing-captured-output-from-a-test-function>

- **The nuance that matters here** (general Python practice, not from pytest
  docs): `subprocess.run(capture_output=True)` connects the child's stdout and
  stderr to *pipes*, not to FD 1/2. pytest's fd-level capture — and therefore
  `capfd` — only sees what the child writes to inherited FD 1/2. So for
  subprocess-based hook tests, `capfd.readouterr().out` will be empty and the
  output to assert on is `result.stdout` / `result.stderr`. `capfd` would only
  help if the child were launched without `capture_output` (inheriting FD 1/2)
  or for in-process C-level writes.

- When the capture fixtures are used, they take precedence over global
  `--capture` settings; `capsys.disabled()` / `capfd.disabled()` are context
  managers to temporarily stop capturing. Source: same page.

- **In-process alternative**: if a hook is cheap to import, you can call its
  entry point in-process and use `capsys` for stdout; the exit code then arrives
  as `SystemExit`, which you assert with `pytest.raises(SystemExit)` (this
  in-process pattern is general Python practice, not from pytest docs). The
  subprocess pattern (§11) is the faithful translation of the bash suite and is
  recommended.

---

## 6. `parametrize`

- `@pytest.mark.parametrize("a,b", [(1, 2), (3, 4)])` runs the test once per
  tuple; each run is a separate test item with an auto-generated id
  (`test_eval[3+5-8]` style). Source:
  <https://docs.pytest.org/en/stable/how-to/parametrize.html#pytest-mark-parametrize-parametrizing-test-functions>

- Signature: `parametrize(argnames, argvalues, indirect=False, ids=None,
  scope=None)`. `ids` accepts a sequence of string/int/float/bool/None or a
  callable, for readable, unique test names. `indirect=True` routes the values
  through a *fixture* of the same name so expensive setup happens at test-setup
  time rather than collection time. Source:
  <https://docs.pytest.org/en/stable/reference/reference.html#pytest-mark-parametrize-ref>

- Per-case marks: wrap a case in `pytest.param(..., marks=pytest.mark.xfail)` /
  `skipif` to mark individual instances. Source:
  <https://docs.pytest.org/en/stable/how-to/parametrize.html#pytest-mark-parametrize-parametrizing-test-functions>
  and <https://docs.pytest.org/en/stable/how-to/skipping.html#skip-xfail-with-parametrize>

- Empty parameter list (e.g. dynamically generated): behavior is defined by the
  `empty_parameter_set_mark` option (default: skip with "got empty parameter
  set"). Source:
  <https://docs.pytest.org/en/stable/how-to/parametrize.html#pytest-mark-parametrize-parametrizing-test-functions>

- **Mutation hazard**: "Parameter values are passed as-is to tests (no copy
  whatsoever)" — a mutable payload dict edited by one case leaks into the next.
  Build fresh dicts per case or `copy.deepcopy` inside the test. Source: same page.

- Stacking multiple `parametrize` decorators yields the cartesian product.
  Source: same page.

- Module-wide parametrization via `pytestmark = pytest.mark.parametrize(...)`.
  Source: same page.

**For the hook suite**, the natural shape is:

```python
@pytest.mark.parametrize(
    ("payload", "expected_exit"),
    [
        ({"tool": "Bash", "command": "ls"}, 0),
        ({"tool": "Bash", "command": "rm -rf /"}, 2),
        ({"tool": "Edit", "path": "/etc/passwd"}, 2),
    ],
    ids=["harmless", "destructive", "protected-path"],
)
def test_pre_tool_use(payload, expected_exit):
    proc = run_hook(payload)
    assert proc.returncode == expected_exit
```

---

## 7. Configuration (`pyproject.toml`)

- Supported config files, in precedence order: `pytest.toml` / `.pytest.toml`
  (new in 9.0, match even when empty) → `pytest.ini` / `.pytest.ini` (match even
  when empty) → `pyproject.toml` (must contain a `[tool.pytest]` or
  `[tool.pytest.ini_options]` table) → `tox.ini` (with a `[pytest]` section) →
  `setup.cfg` (with a `[tool:pytest]` section). "Options from multiple
  configfiles candidates are never merged - the first match wins."
  Source: <https://docs.pytest.org/en/stable/reference/customize.html#configuration-file-formats>
  and <https://docs.pytest.org/en/stable/reference/customize.html#finding-the-rootdir>

- `pyproject.toml` support: `[tool.pytest.ini_options]` since 6.0; native-TOML
  `[tool.pytest]` since 9.0. Source:
  <https://docs.pytest.org/en/stable/reference/customize.html#pyproject-toml>

- `rootdir` is determined from the args + config-file search and is printed in
  the session header; it anchors nodeids and the `.pytest_cache` location. It is
  *not* used to modify `sys.path`. Source:
  <https://docs.pytest.org/en/stable/reference/customize.html#initialization-determining-rootdir-and-configfile>

- Options relevant to this suite (all from
  <https://docs.pytest.org/en/stable/reference/reference.html>):

  | Option | Anchor | Use here |
  |---|---|---|
  | `testpaths` | `#confval-testpaths` | e.g. `["tests"]` so bare `pytest` runs the hook suite |
  | `markers` | `#confval-markers` | register `installed`, `slow`, ... |
  | `addopts` | `#confval-addopts` | default CLI args, e.g. `["-ra", "--strict-markers"]`; "Add the specified OPTS to the set of command line arguments as if they had been specified by the user" |
  | `filterwarnings` | `#confval-filterwarnings` | promote/ignore specific warnings |
  | `norecursedirs` | `#confval-norecursedirs` | keep collection out of temp/venv dirs (setting it *replaces* the default) |
  | `python_files` | `#confval-python_files` | discovery globs, default `test_*.py` / `*_test.py` |
  | `-o name=value` | CLI | override any ini option per invocation |

- `--rootdir` cannot be set via `addopts` (rootdir is used to *find* the config
  file). Source:
  <https://docs.pytest.org/en/stable/reference/customize.html#initialization-determining-rootdir-and-configfile>

- **Strict mode** (new in 9.0): `strict = true` enables all strictness options
  at once (`strict_config`, `strict_markers`, `strict_parametrization_ids`,
  `strict_xfail`); the docs recommend enabling them "if you can", noting new
  strict options will be picked up automatically, so pair with a pinned pytest.
  Source: <https://docs.pytest.org/en/stable/explanation/goodpractices.html#using-pytest-s-strict-mode>

Suggested config for this repo's suite:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["-ra", "--strict-markers"]
markers = [
    "installed: tests that run against the installed copy in a temp HOME (slow)",
]
```

---

## 8. Test discovery and naming

- Default discovery (Source:
  <https://docs.pytest.org/en/stable/explanation/goodpractices.html#conventions-for-python-test-discovery>):
  - With no arguments, collection starts from `testpaths` (if configured) or the
    current directory; CLI args may be directories, file names, or node ids.
  - Recurses into directories unless they match `norecursedirs`.
  - Collects files matching `test_*.py` or `*_test.py`.
  - Within them: `test`-prefixed functions/methods outside classes, and
    `test`-prefixed methods inside `Test`-prefixed classes (no `__init__`);
    `unittest.TestCase` subclasses are also discovered.

- Layout guidance: tests in a top-level `tests/` directory outside application
  code is a recommended layout; for new projects the docs recommend
  `--import-mode=importlib` via `addopts`. Source:
  <https://docs.pytest.org/en/stable/explanation/goodpractices.html#choosing-a-test-layout>

- Customizing discovery: `python_files`, `python_classes`, `python_functions`
  ini options (example page:
  <https://docs.pytest.org/en/stable/example/pythoncollection.html>;
  `python_files` reference:
  <https://docs.pytest.org/en/stable/reference/reference.html#confval-python_files>).

**For the hook suite**: `tests/test_<hook_name>.py` per hook script (e.g.
`tests/test_pre_tool_use.py`), plain `test_*` functions, no classes needed.
Bare `pytest` then runs everything via `testpaths`.

---

## 9. Markers and selection

- Custom markers should be **registered** in the config file
  (`markers = ["slow: marks tests as slow (deselect with '-m \"not slow\"')", ...]`)
  or via `config.addinivalue_line("markers", ...)` in a `pytest_configure` hook.
  Registered marks "appear in pytest's help text and do not emit warnings".
  Source: <https://docs.pytest.org/en/stable/how-to/mark.html#registering-marks>

- Unregistered marks always emit a warning; with `strict_markers` (or
  `addopts = ["--strict-markers"]`) they become **errors**. Source:
  <https://docs.pytest.org/en/stable/how-to/mark.html#raising-errors-on-unknown-marks>

- Selection:
  - `pytest -m MARKEXPR` — "Only run tests matching given mark expression.
    Supports and, or, and not operators." Source:
    <https://docs.pytest.org/en/stable/reference/reference.html#cmdoption-m>
  - `pytest -k 'expr'` — case-insensitive string expression over file/class/
    function names. Source:
    <https://docs.pytest.org/en/stable/how-to/usage.html#specifying-which-tests-to-run>
  - Node ids: `pytest tests/test_mod.py::TestClass::test_method`, with
    parametrization in `[...]`: `test_func[x1,y2]`. Source: same page.
  - `--collect-only` / `--co`: "Only collect tests, don't execute them."
    Source: <https://docs.pytest.org/en/stable/reference/reference.html#cmdoption-collect-only>
  - Args from a file: `pytest @tests_to_run.txt` (since 8.2); the file can be
    generated with `pytest --collect-only -q`. Source:
    <https://docs.pytest.org/en/stable/how-to/usage.html#specifying-which-tests-to-run>

- Marks apply to tests only, "having no effect on fixtures". Source:
  <https://docs.pytest.org/en/stable/how-to/mark.html>

- Conditional skipping: `@pytest.mark.skipif(condition, reason=...)` (evaluated
  at collection; shareable as a module-level marker variable), imperative
  `pytest.skip(reason)` (also `allow_module_level=True` for whole modules), and
  `pytest.importorskip("mod", minversion=...)` for missing dependencies.
  Source: <https://docs.pytest.org/en/stable/how-to/skipping.html#skipping-test-functions>

**For the hook suite**: register `installed` (temp-HOME install tests) and
optionally `slow`; day-to-dev runs become `pytest -m "not installed"`.

---

## 10. `yield` fixtures (setup/teardown)

- "Yield" fixtures `yield` instead of `return`; "Any teardown code for that
  fixture is placed after the `yield`." Setup runs in fixture order; teardown
  runs "in the reverse order". Source:
  <https://docs.pytest.org/en/stable/explanation/fixtures.html#yield-fixtures-recommended>

- Error behavior: "If a yield fixture raises an exception before yielding,
  pytest won't try to run the teardown code after that yield fixture's `yield`
  statement. But, for every fixture that has already run successfully for that
  test, pytest will still attempt to tear them down." Source:
  <https://docs.pytest.org/en/stable/explanation/fixtures.html#handling-errors-for-yield-fixture>

- Alternative: `request.addfinalizer(fn)`; finalizers run first-in-last-out, and
  a finalizer runs even if the fixture later raises — so add it only after the
  state-changing step succeeded. Source:
  <https://docs.pytest.org/en/stable/explanation/fixtures.html> (finalizers
  section, "Safe teardowns").

- Docs' safety guidance: the safest structure is "limiting fixtures to only
  making one state-changing action each, and then bundling them together with
  their teardown code." Source:
  <https://docs.pytest.org/en/stable/explanation/fixtures.html#safe-teardowns>

**For the hook suite**: the installed-`HOME` fixture is a `yield` fixture only
if it needs teardown (e.g. killing a spawned server). For "pip install into temp
HOME, never clean up" the plain return style is fine — `tmp_path` retention
handles disk cleanup.

---

## 11. pytest exit codes and CLI flags

Exit codes (Source: <https://docs.pytest.org/en/stable/reference/exit-codes.html>):

| Code | Meaning |
|---|---|
| 0 | All tests were collected and passed successfully |
| 1 | Tests were collected and run but some of the tests failed |
| 2 | Test execution was interrupted by the user |
| 3 | Internal error happened while executing tests |
| 4 | pytest command line usage error |
| 5 | No tests were collected |
| 6 | Maximum number of warnings exceeded (`--max-warnings`) |

They are exposed as the `pytest.ExitCode` enum. Note for this project: the
*hook's* exit code `2` (hard block) is unrelated to pytest's own exit code `2`.
Exit code `5` is useful as a CI guard: an accidentally empty selection fails the
run instead of passing silently.

CLI flags (all from <https://docs.pytest.org/en/stable/reference/reference.html>):

| Flag | Anchor | Behavior (docs wording) |
|---|---|---|
| `-x, --exitfirst` | `#cmdoption-exitfirst` | "Exit instantly on first error or failed test." |
| `--maxfail=NUM` | `#cmdoption-maxfail` | "Exit after first num failures or errors. Useful for CI environments where you want to fail fast but see a few failures." |
| `-q, --quiet` | `#cmdoption-quiet` | "Decrease verbosity." |
| `--tb=STYLE` | `#cmdoption-tb` | `auto` (default), `long`, `short`, `line`, `native`, `no` |
| `-r CHARS` | `#cmdoption-r` | extra summary info: `f` failed, `E` error, `s` skipped, `x` xfailed, `X` xpassed, ... (e.g. `-ra`) |
| `--collect-only, --co` | `#cmdoption-collect-only` | "Only collect tests, don't execute them." |
| `--basetemp=DIR` | `#cmdoption-basetemp` | base temp dir for the run; "this directory is removed if it exists" |
| `-o name=value` | (config section) | override an ini option per invocation |
| `--deselect=NODEID_PREFIX` | `#cmdoption-deselect` | deselect by node id prefix (multi-allowed) |
| `-p no:name` | <https://docs.pytest.org/en/stable/how-to/usage.html#disabling-plugins> | disable a plugin (e.g. `-p no:legacypath` to force `tmp_path`) |

CI behavior (Source: <https://docs.pytest.org/en/stable/explanation/ci.html>):
pytest detects CI via non-empty `CI` or `BUILD_NUMBER` env vars; the effect is
that "the output of the short test summary info is no longer truncated to the
terminal size". No other behavior changes — do not rely on CI auto-detection for
anything else.

**For the hook suite**: local dev `pytest -x -q` (or `--maxfail=2`); CI plain
`pytest` with `-ra` from `addopts`; treat exit code `5` as a packaging bug.

---

## 12. Testing CLI/subprocess programs (the hook pattern)

There is no dedicated pytest how-to for testing subprocesses; the only official
statements are the capture ones in §5 (default fd capture; `capfd` captures
subprocess output that writes to FD1/FD2). The pytester fixture
(<https://docs.pytest.org/en/stable/how-to/writing_plugins.html#testing-plugins>)
is for testing *pytest plugins*, not external CLIs — not applicable here.

Recommended pattern (general Python practice, not from pytest docs):

```python
# tests/conftest.py
import json
import subprocess
import sys

HOOK = sys.executable  # + path to hook entry point, resolved once

def run_hook(payload: dict, *, env=None, timeout=30) -> subprocess.CompletedProcess:
    return subprocess.run(
        [HOOK, str(HOOK_PATH)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,          # None -> inherit (monkeypatched) environment
        timeout=timeout,
    )
```

- Expose it as a plain function imported by test modules, or wrap in a
  function-scoped fixture if you want per-test knobs.
- Assert on `proc.returncode` (0 vs 2), `json.loads(proc.stdout)` for the JSON
  contract (replaces `jq`), and substrings of `proc.stderr` for block reasons.
- For installed-copy tests, build `env` explicitly: a copy of `os.environ` with
  `HOME` pointed at the session temp home and `PATH` prefixed with its bin dir —
  or rely on `monkeypatch.setenv("HOME", ...)` and let the child inherit it (§4).
- `timeout=` prevents a hung hook from hanging the suite (general practice).
- File-state checks (`assert (tmp_path / "out.json").read_text() == ...`) stay
  in the same test, after `run_hook` returns.

---

## Sources consulted (all `docs.pytest.org/en/stable/`)

- explanation/fixtures.html — fixture scopes, conftest sharing, override, yield
  fixtures, finalizers, safe teardowns, dynamic scope
- how-to/writing_plugins.html — plugin/conftest discovery order, per-directory
  conftests, marker registration, pytester
- how-to/tmp_path.html — tmp_path, tmp_path_factory, location & retention
- how-to/monkeypatch.html — setenv/delenv/setattr/chdir/context, warnings
- how-to/capture-stdout-stderr.html — default fd capture, capsys vs capfd,
  readouterr, disabled()
- how-to/parametrize.html — parametrize, pytest.param marks, empty sets,
  no-copy note
- how-to/mark.html — registering marks, strict_markers
- how-to/skipping.html — skip/skipif/xfail/importorskip, per-case marks
- how-to/usage.html — selection (-k, node ids, -m, @file), plugin loading
- reference/customize.html — config file formats & precedence, rootdir
- reference/exit-codes.html — exit codes 0–6
- reference/reference.html — CLI flags (-x, --maxfail, -q, --tb, -r,
  --collect-only, --basetemp, -m), ini options (testpaths, markers, addopts,
  filterwarnings, norecursedirs, python_files, tmp_path_retention_*),
  parametrize signature, TempPathFactory.mktemp
- explanation/goodpractices.html — discovery conventions, layout/import mode,
  strict mode
- explanation/ci.html — CI detection and its (limited) effects

Not available in stable docs (verified 404 + nav check on 2026-09-01):
`faq.html` (no FAQ page in the stable docs), and any dedicated subprocess/CLI
testing guide.
