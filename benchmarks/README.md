# Benchmarks

Benchmark tasks built from real quantum open-source work: resolved issues where the
merged pull request is the reference solution. Existing quantum coding benchmarks test
snippet-level generation or question answering (see [reading/](../reading/)); these tasks
are drawn from changes that maintainers accepted into their projects.

Last verified: 2026-08-23

## Status

A pilot set of 430 candidate tasks has been assembled from five unitaryHACK events
(2022 to 2026). Stage counts per year are in
[../data/figures/task_pipeline_by_year.csv](../data/figures/task_pipeline_by_year.csv).

The per-task list is not published here. It names the repositories and pull requests of
individual contributors, several of them under personal accounts, so releasing it is a
question of consent rather than of licensing. Anyone wanting to rebuild the set can do so
from the method below against an event's own bounty list.

| | count |
|---|---|
| bounties listed by the organizers | 812 |
| issue closed | 671 |
| closed by a merged pull request | 438 |
| issue body long enough to serve as a prompt, with a merged solution | 430 |
| solution changes a test file | 280 |

Reference solutions have a median of 307 changed lines. The share of bounties reaching a
usable task rises from 48 percent for 2022 to 66 percent for 2026, as older records lose
traceability through repository renames and deleted issues.

## What is not done yet

The tasks are candidates, not a validated benchmark. Before they can score an agent,
each reference test has to be shown to fail at the parent commit and pass after the
change. That requires building each project at its historical commit, which is the
substantial remaining work and is not started. Until it is done, the 280 figure is an
upper bound on how many tasks are automatically scorable.

A file is currently counted as a test by its path (`test_*`, `tests/`, `spec/`,
`conftest.py`) without inspecting it, so some of those 280 may carry a test that does not
exercise the change.

## Task format (draft)

Each task is a directory containing:

- `task.md`: the issue text as the agent sees it, scrubbed of links to the actual fix.
- `environment/`: container spec pinning the repo at the pre-fix commit and its
  dependencies.
- `check/`: the programmatic check. Default: the regression test from the real fix,
  which must go from failing to passing. The original merged pull request is the
  reference, and an information firewall keeps it out of the agent's context.
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
