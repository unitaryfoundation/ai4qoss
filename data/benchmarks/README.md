# Candidate maintenance tasks: composition

Aggregate description of the 417 candidate maintenance tasks recovered from five
unitaryHACK events (2022 to 2026): what kind of work they are, which parts of quantum
software they touch, which technologies they involve, how large the reference changes
are, how each task could be verified, and where the records are weak. The task list
itself, issue text, patches and tests are not released (see
[../../benchmarks/](../../benchmarks/)).

Last verified: 2026-10-25

License: CC BY 4.0 (see [../../LICENSING.md](../../LICENSING.md)).

## Status of these numbers

The tasks are candidates. No historical environment has been rebuilt, no reference
solution has been executed, and no agent has been run on any task. Each task was
classified from its issue and reference pull request with LLM assistance and a second,
blind LLM pass on 122 tasks. A subsequent non-blind Codex AI source audit of 40
tasks and targeted follow-up is complete, with corrections applied; no label has
been verified by a person. The method and the
codebook are in
[../../analysis/benchmark_pilot/CHARACTERIZATION.md](../../analysis/benchmark_pilot/CHARACTERIZATION.md).

Measured 2026-10-25: issues, comments and pull requests were fetched on that date. The
cohort itself is the one in [../figures/task_pipeline_by_year.csv](../figures/task_pipeline_by_year.csv)
(bounty records resolved on 2026-10-06, repository names on 2026-10-19).

## Denominators

Every share is over the 417 tasks unless a file says otherwise. A task is a distinct
issue; three reference pull requests each serve two tasks. Years are the first year an
issue was offered. Primary type is single-label. Domains, technologies, capabilities and
verification methods are multi-label, so their shares sum to more than 100 percent.

## Files

| File | Contents |
|---|---|
| `task_types.csv` | Primary maintenance task type, and primary-or-secondary counts |
| `task_type_by_year.csv` | Primary type per first-offered year |
| `task_domains.csv` | Software domains touched by the task (one to three per task) |
| `task_type_by_domain.csv` | Primary type against domain; a task appears once in each of its domains |
| `task_knowledge.csv` | Highest knowledge level the task requires: general engineering, quantum API and workflow knowledge, or quantum mathematical and physical semantics |
| `task_technologies.csv` | Frameworks and libraries, quantum simulators and hardware providers directly involved or only mentioned, with the number of host repositories; physical platforms modeled or designed; execution not established |
| `task_languages.csv` | Language/format categories of changed implementation, markup and notebook files, from extensions |
| `task_repository_concentration.csv` | How tasks are distributed over the 110 repositories |
| `task_scope_by_type.csv` | Files and lines changed by the reference pull request (quartiles) and the share changing a test file, per primary type |
| `task_capabilities.csv` | Capabilities a task would exercise |
| `task_verification_methods.csv` | Proposed verification methods, with two groupings |
| `task_capability_verification.csv` | Per primary type: most frequent capabilities, proposed verification methods and knowledge levels |
| `task_quality.csv` | Material sufficiency, annotation confidence, match between issue and reference pull request, reference availability, repository/branch provenance, original review status and subsequent source-audit status |
| `task_annotation_agreement.csv` | Agreement between the first and the blind second annotation pass, before adjudication |
| `benchmark_comparison.csv` | Comparison with published quantum and repository-level coding benchmarks, with sources |

## Column notes

`task_technologies.csv`. `n_tasks_direct` counts tasks whose change must use, modify or
interoperate with the named technology; the host project counts as directly involved
in its own tasks. `n_host_repositories_direct` is the number of distinct repositories
among those tasks, which separates a library used across projects from one that
appears only in its own repository. `n_tasks_background_only` counts tasks that mention
it only as context. Names under three tasks are pooled into one row per category. Rows
in parentheses count tasks: with any named technology, with none involved, or where
the material was not enough to tell. A hardware provider counts as directly involved
only if the change calls, wraps, configures or parses its interface or data; this is
not evidence that the task can be executed on that hardware. Mocked provider
API/data tests count as direct involvement; simply forwarding CI credentials into
an existing initialization path does not. The
`platform_modeled_not_executed` rows count physical modalities simulated or designed in
the task. This label does not establish whether upstream authors executed hardware;
this characterization performed no target-task execution.

`task_scope_by_type.csv`. Lines changed are additions plus deletions. They are not a
measure of difficulty: notebooks, generated files and data inflate them. The one
reference pull request merged with no changed file is excluded from the size columns,
so `n_with_size` is 416 overall. File and line counts use complete file lists. A test
file is recognized by its path within the first 100 files of each pull request, the
convention of `task_pipeline_by_year.csv`, so both give 275; one 223-file pull request
changes test files only beyond its first 100. A changed test file does not show that the
test exercises the change or that the task can be scored automatically.

`task_verification_methods.csv`. These are proposals for how each task could be
verified, from the issue's own requirements. None has been implemented. The two
grouping rows count tasks with at least one method that compares results against an
expected quantity, and tasks whose 1-3 assigned labels contain only build, example,
browser or review categories. The latter is not a claim that other methods are
impossible or that those tasks cannot be automatically scored.

`task_quality.csv`. `reference_match` records whether the selected pull request
covers mandatory requirements in the reviewed issue. `partial` requires an identified
unmet requirement in that selected PR. Multiple closing PRs or missing optional items
alone do not imply partial resolution; unclear requirements are labeled `unclear`.
A full scope match does not establish implementation correctness. Repository/branch
flags are provenance, not failure indicators; a template repository can be the intended
submission destination. `reference_pr_base_branch` compares
the pull request's base branch with the repository's current default branch;
"renamed since" means the base was `master` and the default is now `main`. Whether a
pull request merged into a feature or development branch later reached the default
branch was not checked.

`task_annotation_agreement.csv`. The "targeted" subset is every task with low
confidence, insufficient material or an unclear or mismatched reference (72 tasks); the
"random" subset is 50 tasks drawn from the rest. These sets and agreement values
are historical, from before subsequent source-audit corrections. Both passes used language models from
the same family, so agreement measures consistency, not correctness, and shared biases
would not show up as disagreement.

`benchmark_comparison.csv`. One row per dataset, with Quantum Arena as a leaderboard
platform hosting several of them. Values come from each project's paper, repository or
data files as of 2026-10-25; task counts marked as our own count in the notes were
computed from released data files. The last row describes this collection, which is not
a validated benchmark. The source URLs are citations of published work.

Changed-file language categories include docstring-only changes, notebooks and markup.
They are not counts of execution languages. The broad technology inventory includes
host projects, third-party libraries and formats; its long tail is not a count of
quantum frameworks alone.

`task_quality.csv` separates `initial_review_status`, `codex_source_audit` and
`post_audit_correction`. The 40-task audit is complete as an AI review; it supplies no
human accuracy estimate.

## What these numbers do not support

- Coverage of the quantum open-source ecosystem. The tasks come from projects that chose
  to post bounties at one event series, and ten repositories hold 28 percent of them.
- Difficulty. Neither lines changed nor the knowledge label has been compared with
  solve rates.
- Scorability. No acceptance criterion has been implemented or run.
- Freedom from training contamination. All reference solutions are public.

## Reproducing

[../../analysis/benchmark_pilot/task_scope.py](../../analysis/benchmark_pilot/task_scope.py)
computes the scripted features and
[../../analysis/benchmark_pilot/characterize.py](../../analysis/benchmark_pilot/characterize.py)
writes every file here except `benchmark_comparison.csv`. Both need the unpublished
per-task inputs. Running them reproduces these aggregates from the annotations; checking
the annotations themselves requires reading the issues and pull requests again.
