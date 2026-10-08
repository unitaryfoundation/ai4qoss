# Version migration

Last verified: 2026-08-28
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

## Verification

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

We have not run this harness ourselves, and no published study measures a quantum
migration the way this card verifies one, by running the target project's test suite on
the pinned version.

The published work on Qiskit migration with language models detects migration
scenarios in synthetic snippets and proposes refactorings, which three human judges
then grade; no code is executed and no test suite is involved
([arXiv:2606.20173](https://arxiv.org/abs/2606.20173), and its predecessor
[arXiv:2506.14535](https://arxiv.org/abs/2506.14535) on 25 snippets targeting Qiskit
0.46). The stronger of the two models graded correct on roughly three quarters of the
scenarios it detected, and returned empty or invalid code on 15 percent of scenarios
against 61 percent for the weaker model. Those figures describe the quality of
suggestions as human judges rated them. Neither paper reports tokens, wall-clock time,
or iteration counts, and neither states which Qiskit version it targets, so
quantum-specific cost figures do not exist and the scope of the results is
unspecified.

What has been measured with an execution-based criterion on quantum software is the
underlying difficulty rather than the migration itself. Across Qiskit 0.43, 1.3, and
2.0, with 50 tasks and 17 models at 1,350 executions each, pass@1 ranges from 0.02 to
0.85 depending on the model and the target version, and giving the model the relevant
documentation repairs only 0.19 to 0.59 of its failures
([arXiv:2607.04072](https://arxiv.org/abs/2607.04072)). A migration loop inherits that
spread: the model's grasp of the target version bounds what any number of iterations
can reach.

Migration studies outside quantum software do use an execution-based criterion and
give the closest available expectation. Repository-level Java migration resolves
roughly half of projects: 53.3 percent on the harder setting with the strongest model
tested, at 34 to 59 model calls per repository (MigrationBench,
[arXiv:2505.09569](https://arxiv.org/abs/2505.09569)), and 52.3 percent of 228
repositories for the best model in FreshBrew
([arXiv:2510.04852](https://arxiv.org/abs/2510.04852)). Python library-to-library
migration produces individually correct changes far more often than it produces a
passing test suite: with the strongest model, 94 percent of 1,996 code changes were
correct while 16 of the 25 migrations that had usable coverage passed their tests, at
0.16 US dollars per thousand lines
([arXiv:2504.13272](https://arxiv.org/html/2504.13272v2)). The gap between a correct
edit and a passing suite is the reason this card's verification is the test suite.

A rule-based comparison exists for Qiskit specifically:
[flake8-qiskit-migration](https://github.com/frankharkins/flake8-qiskit-migration)
flags deprecated usage for the 1.0 and 2.0 transitions. It publishes no accuracy
numbers and its documentation states that several of its checks are heuristic and
produce false positives. Running it first is cheap and narrows what the loop above has
to handle.
