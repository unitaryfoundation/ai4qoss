# AGENTS.md template for QOSS repositories

A starting point for an `AGENTS.md` file: the instructions a coding agent reads when it
works inside your repository. Copy, fill in, and delete what does not apply.

Last verified: 2026-07-29

```markdown
# AGENTS.md

## Build and test

- Environment: [how to create it, e.g. `pip install -e ".[dev]"`; pin the Python version]
- Run tests: [command, e.g. `pytest`; note the fast subset if the full suite is slow]
- Lint / typecheck: [commands]
- Docs build: [command, if applicable]

## Verification expectations

- Every behavior change comes with a test. For bug fixes, write the failing test first.
- [Project-specific checks: e.g. circuit-equivalence tests, tolerance conventions for
  probabilistic tests, fixed seeds, maximum qubit counts in tests.]
- Probabilistic tests: [state the project's convention, e.g. fixed seeds and explicit
  tolerances; do not loosen tolerances to make a test pass.]

## Boundaries

- Do not add or update dependencies.
- Do not modify CI configuration or release workflows.
- Do not touch anything that uses credentials, paid services, or hardware backends.
- If a task seems to require any of the above, stop and ask in the issue instead.

## Conventions

- [Code style, naming, docstring format, changelog practice.]
- Disclose AI involvement in the PR description, per CONTRIBUTING.
```
