# Version migration

Last verified: 2026-07-29
Status: draft

## Task

Migrate a codebase (or a downstream project) across a breaking release of a quantum
framework, for example a Qiskit major version. Done means: the test suite passes on the
pinned target version, with no use of APIs deprecated in that version.

## Loop

1. Pin the target environment (framework version, Python version) in a container.
2. Run the test suite and collect failures and deprecation warnings.
3. Agent proposes changes for one failure cluster at a time, using the framework's
   migration guide and changelog as context.
4. Re-run; repeat until the suite is green and the deprecation log is empty.

## Check

The project's own test suite on the pinned target environment, plus the deprecation
warning log.

- Cost per iteration: one test-suite run.
- Where it can be fooled: weak test coverage passes broken code; the agent can be
  tempted to weaken or skip failing tests. Guardrails below address the second; the
  first is a property of the target repo worth stating in the PR.

## Guardrails

- Tests are read-only for the agent, except for updating imports and API names that the
  migration itself renames; any other test edit needs human approval.
- No dependency changes beyond the target framework version.
- Migration lands as a series of small PRs (one failure cluster each), not one large one.

## Cost and results

To be filled from the first real runs. Reference: the LLM Qiskit migration study,
arXiv:2606.20173.
