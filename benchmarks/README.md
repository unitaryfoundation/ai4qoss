# Benchmarks

Benchmark tasks built from real QOSS work: resolved issues, version migrations, and
reviews, where the historical resolution provides the ground truth. To our knowledge,
no benchmark measures this today; existing quantum coding benchmarks test
snippet-level generation or question answering (see [reading/](../reading/)).

## Status

Planning. The pilot: 20 to 50 resolved issues from past unitaryHack editions, where
the merged PR is the reference solution, subject to the consent review described in
[data/](../data/).

## Task format (draft)

Each task is a directory containing:

- `task.md`: the issue text as the agent sees it (scrubbed of links to the actual fix).
- `environment/`: container spec pinning the repo at the pre-fix commit and its
  dependencies.
- `check/`: the programmatic check. Default: the regression test from the real fix,
  which must go from failing to passing. The original merged PR is the reference, and
  an information firewall keeps it out of the agent's context.
- `meta.yaml`: task type (bug, feature, migration, docs), difficulty notes, source
  links, license of the underlying code.

## Also worth doing

Contributing quantum tasks to existing science benchmarks (for example Terminal-Bench
Science), which reach the AI community directly.
