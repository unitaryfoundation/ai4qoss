# Characterizing the candidate maintenance tasks

How the 417 candidate tasks recovered from unitaryHACK records were classified, and
how the aggregate files in [../../data/benchmarks/](../../data/benchmarks/) were
produced. The per-task annotations are not published, because they name issues, pull
requests and, through them, contributors.

Last verified: 2026-10-25

## Unit of analysis

A task is a distinct issue: canonical repository name plus issue number, with renamed
repositories mapped to their current name and repeated bounty listings collapsed, as in
`aggregates.py`. An issue listed in several years is attributed to the first year it
was offered. The cohort is the 417 issues that have a merged reference pull request and
an issue description of at least 120 characters; no task was added or removed for this
analysis. Three pull requests each serve as the reference for two tasks, so shares are
over tasks, not pull requests.

The collection is a set of candidates. No historical environment has been rebuilt, no
reference solution has been executed, and no agent has been run on any task.

## What was read for each task

For every task we fetched, read-only, the issue title and body, up to 40 issue
comments, every pull request linked as closing the issue, and the selected reference
pull request's description, complete file list and diff. Annotators saw a compact
record of each task: the issue body up to 5,000 characters, up to six comments other
than bot messages, the pull request description up to 3,000 characters, the file list,
about 9,000 characters of diff, and, in the second pass, the text of added notebook
cells. Two reference pull requests
now return 404 on GitHub; for those, the file list cached in an earlier collection pass
was used. One reference pull request is merged with zero changed files.

## Labels

Each task received the following labels from its issue text and the actual change.
Repository names, issue labels and keywords were not used as the basis of a label.

| Field | Values | Cardinality |
|---|---|---|
| Maintenance task type | bug/correctness fix, feature/method extension, compatibility/migration/integration, performance, refactoring, testing/verification, build/packaging/CI, documentation/examples/UI, other/unclear | one primary, optional secondary |
| Software domain | circuits/IR/operators, compilation/optimization, simulation/numerics, algorithms/applications, error mitigation, QEC/fault tolerance, hardware control and execution, characterization/benchmarking, quantum information theory, visualization/UI, educational content, classical support code, cross-cutting infrastructure | one to three |
| Technologies | frameworks and libraries, quantum simulators, hardware providers, each split into directly involved and background mentions; physical platforms modeled or designed (execution status not established) | lists |
| Capabilities the task would exercise | fault localization, API understanding, cross-file integration, compatibility/migration, scientific/numerical reasoning, algorithm implementation, performance optimization, test design, documentation writing, build tooling, UI/front end | one to three |
| Proposed verification | reproducer plus regression, interface contract, circuit/state semantic comparison, analytic or independent reference value, invariant/differential/metamorphic, statistical, correctness plus performance, clean build, executable examples, browser/UI workflow, maintainer review | one to three |
| Knowledge required | general engineering, quantum API/workflow knowledge, quantum mathematical/physical semantics | one |
| Quality flags | reference match (full, partial, mismatch, unclear), material sufficiency, annotation confidence | one each |

Boundaries that mattered in practice:

- A task is labeled by what the issue asks, confirmed against the change. A change
  that also edits tests is not a testing task for that reason.
- A crash or wrong result on input within a function's intended scope is a bug fix; an
  input outside that scope by design makes it a feature.
- A new converter, importer, exporter or provider integration is compatibility and
  integration work; extending an existing converter to more constructs is a feature.
- A provider counts as directly involved only if the change calls, wraps, configures
  or parses that provider's interface or data. Hardware is never inferred from a
  project's dependencies, and involvement is not evidence of verified execution
  support. Classical solvers, such as electromagnetic field solvers, are not counted
  as quantum simulators.
- Where the record is not enough to tell, the label is `unclear`. "None involved" and
  "cannot tell" are recorded separately.
- The verification labels are proposals for how a task could be verified. None of them
  has been implemented or validated as a scoring criterion.

Programming languages are not annotated. They are inferred by `task_scope.py` from the
extensions of recognized implementation, markup and notebook files. This includes
docstring-only and test changes; it does not measure which languages were executed.

## How the labels were produced

The labels are LLM-assisted, and none of them has been verified by a person.

1. A codebook was drafted and calibrated on eight tasks from eight projects.
2. Twelve independent LLM annotators labeled the full cohort, each on a disjoint
   random batch of about 35 tasks, from the material described above.
3. Recurring disagreements on boundaries led to added rules (version 1.1 of the
   codebook), and a rule pass over the first-pass records applied them.
4. A second, blind LLM pass, without access to the first-pass labels, re-annotated
   every task with low confidence, insufficient material, or an unclear or mismatched
   reference, plus a random sample of the remaining tasks.
5. Disagreements between the two passes on primary type, knowledge level, reference
   match or domains were adjudicated by a further LLM pass that saw both records and the
   material. The coordinator inspected a sample of the adjudications against the
   material.

Agreement between the passes is published in `task_annotation_agreement.csv`, as historical consistency between the two LLM passes, before adjudication and
source-audit corrections. It does not measure correctness against human judgment.

## Completed source audit and corrections

A non-blind Codex AI source review covered a stratified sample of 40 tasks, with one
additional targeted provider-interface follow-up. It inspected issue/PR evidence and
selected complete diff/notebook material. The review task was accepted as completed;
no human labels or human agreement score were created. A persistent correction layer
runs after adjudication, while the original two-pass agreement remains unchanged.

Codebook v1.2 clarifies the following boundaries:

- Verification added to an existing benchmark pipeline is testing work, even if it
  introduces a helper function. Newly supported callable wrappers can remain features
  where the previous input shape was unsupported; error output alone is insufficient.
- General tensor batching/numerical linear algebra does not automatically require
  quantum semantics. Software domains follow the change, not the host project's use.
- Direct provider involvement includes mocked API/data contract tests. CI credentials
  forwarded to existing initialization paths are background access enablement.
- Partial reference coverage requires an identifiable unmet mandatory requirement.
  Multiple PRs, omitted optional content or branch/repository location alone do not
  establish partial resolution. Unresolved completion criteria are marked unclear.
- Material flags are updated after additional sources are read; otherwise limited
  material retains low confidence. This consistency rule was applied across the cohort.

These are targeted corrections, not a new full-cohort semantic annotation pass.
Reference-match labels describe selected-PR scope, not scientific correctness. The
1-3 proposed verification labels per task are not an exhaustive list of feasible tests.

## Reproducing the aggregates

`task_scope.py` computes the scripted features from the cohort list and the reference
pull request file lists. `characterize.py` joins them with the annotations and writes
the aggregate files. Both read unpublished inputs through `private()` in
[../paths.py](../paths.py) and exit with an explanation if those are absent.

```
python3 benchmark_pilot/task_scope.py --data-root PATH
python3 benchmark_pilot/characterize.py --data-root PATH
```

Running the scripts reproduces the aggregates from the annotations. It does not
re-examine the annotations, which would require reading the issues and pull requests
again.

## Limits

- The labels are semantic judgments by language models. Consistency between two
  passes is reported; correctness against expert judgment has not been measured.
- Lines changed are additions plus deletions in the reference pull request. They are
  not a measure of difficulty: generated files, notebooks and data inflate them.
- A test file is recognized by its path, so its presence does not show that a test
  exercises the change, nor that the task can be scored automatically.
- Coverage describes these 417 tasks from one community event series. It does not
  describe the quantum open-source ecosystem as a whole: the projects are those that
  chose to post bounties, and a few repositories contribute many tasks.
