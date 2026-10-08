# Benchmarks

Benchmark tasks built from real quantum open-source work: resolved issues where the
merged pull request is the reference solution. Existing quantum coding benchmarks test
snippet-level generation or question answering (see [reading/](../reading/)); these tasks
are drawn from changes that maintainers accepted into their projects.

Last verified: 2026-10-07

## Status

A pilot collection of 431 candidate tasks has been assembled from five unitaryHACK
events (2022 to 2026). Stage counts per year are in
[../data/figures/task_pipeline_by_year.csv](../data/figures/task_pipeline_by_year.csv).

The per-task list is not published here. It names the repositories and pull requests of
individual contributors, several of them under personal accounts, so releasing it is a
question of consent rather than of licensing. Anyone wanting to rebuild the set can do so
from the method below against an event's own bounty list.

| | count |
|---|---|
| bounties listed by the organizers | 812 |
| issue closed | 677 |
| closed by a merged pull request | 439 |
| issue body long enough to serve as a prompt, with a merged solution | 431 |
| solution changes a test file | 281 |

Counts are as of 2026-10-06. Reference solutions have a median of 307 changed lines, and
a quarter of them change more than 658. The share of bounties reaching a usable task
rises from 48 percent for 2022 to 66 percent for 2026, as older records lose
traceability through repository renames and deleted issues.

## What is not done yet

The tasks are candidates, not a validated benchmark, and two things stand between the
collection and a set that can score an agent.

The first is the historical environment. Each project has to build at the commit
preceding its fix, with the dependencies of that time, before anything can be run
against it. This is the substantial remaining work and is not started.

The second is the acceptance criterion for each task. Where the reference solution
carries a regression test, fail-then-pass against that test is the criterion: it has to
be shown to fail at the parent commit and pass after the change. That rule does not
cover the rest of the collection, where a task is a new feature, a method, or a
migration, and what counts as a solution has to be stated per task from the issue's own
requirements. Until both are done, the 281 figure is an upper bound on how many tasks
are automatically scorable.

A file is currently counted as a test by its path (`test_*`, `tests/`, `spec/`,
`conftest.py`) without inspecting it, so some of those 281 may carry a test that does not
exercise the change.

## What the collection is for

Beyond scoring one agent against another, these tasks can measure what verification
itself contributes. The circuit-transformation tasks in the collection admit an
equivalence verifier alongside the repository's own tests, so the same agent can be run
twice, once with the test suite alone and once with equivalence verification available
during development, with the agent configuration and the final acceptance criterion held
fixed. The difference between the two runs is a direct measurement of what a stronger
verifier buys, on real repository work rather than on constructed examples.

## Task format (draft)

Each task is a directory containing:

- `task.md`: the issue text as the agent sees it, scrubbed of links to the actual fix.
- `environment/`: container spec pinning the repo at the pre-fix commit and its
  dependencies.
- `verification/`: the programmatic acceptance criterion. Default: the regression test
  from the real fix, which must go from failing to passing. Tasks without such a test
  state their criterion from the issue's own requirements. The original merged pull
  request is the reference and is withheld from the agent's context.
- `meta.yaml`: task type (bug, feature, migration, docs), difficulty notes, source
  links, license of the underlying code.

## Method note for anyone rebuilding this

The link from an issue to the pull request that closed it is exposed only through
GitHub's GraphQL API, through `ClosedEvent.closer` and
`closedByPullRequestsReferences`. The REST timeline endpoint returns no
`cross-referenced` events, and its `connected` events carry no reference to the pull
request they connect to; a pass built on REST reports zero linked pull requests for this
entire set.

Searching GitHub labels instead of using an organizer's list recovers about half of the
bounties for 2026, because projects tag them under four different spellings and some do
not tag them at all.

## Also worth doing

Contributing quantum tasks to existing science benchmarks (for example Terminal-Bench
Science), which reach the AI community directly.
