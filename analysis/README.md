# analysis

The code behind every number in the perspective paper and every file in
[`../data/figures/`](../data/figures/) and [`../data/benchmarks/`](../data/benchmarks/).
Scripts only, no data. Each script's docstring states its method, its denominators,
and how it can be wrong.

Last verified: 2026-10-26

License: Apache-2.0 ([LICENSE](LICENSE)). Each script carries an SPDX header with
the copyright, so it stays identifiable after being copied out.

## Scripts you can run

These read public sources: clones of the projects under study, or the GitHub and PyPI
APIs.

| Script | What it measures | Output |
|---|---|---|
| `api_churn/run.py` | Deprecations each project announces per year | `api_churn_summary.csv` |
| `api_survival/run.py` | How much of a year's public API still imports today | `api_survival.csv` |
| `test_suite_audit/run.py` | Qubit counts written into test code | `qubit_counts.csv` |
| `test_suite_audit/by_module.py` | The same counts by area of the code under test | `qubit_by_module.csv` |
| `test_suite_audit/circuit_kind.py` | Random against structured test circuits | `circuit_kind.csv` |
| `corpus_size/run.py` | Public code importing each library, two proxies | `corpus_size.csv` |
| `ai_disclosure/commits.py` | Commits carrying an AI marker | `ai_disclosure_commits.csv`, `ai_disclosure_concentration.csv` |
| `ai_disclosure/pulls.py` | Pull requests carrying a disclosure, and whether the template asks | `ai_disclosure_pulls.csv`, `ai_disclosure_pr_template_policy.csv` |
| `benchmark_pilot/fetch_issues.py` | What a label search alone recovers, kept as a control | console |
| `figures/components.py` | Redraws every panel of the paper's figures | SVG and PDF panels |
| `audit_public_data.py` | Scans `../data/figures` for anything identifying a person | console |

`corpus_size`, `pulls.py` and `fetch_issues.py` need a GitHub token.

## Scripts whose input we do not publish

These produced published numbers from records we hold: the unitaryHACK organizers' bounty
sheets and post-event surveys, the community survey export, and the per-task benchmark
list. The first two carry answers from identifiable people. The third names individual
contributors and their pull requests.

They are here so the method can be read: which rows were counted, what the denominator
was, how free text was classified.

| Script | What it measures | Output |
|---|---|---|
| `unitaryhack/scrub.py` | Makes de-identified copies before anything else runs | working copies |
| `unitaryhack/audit_pii.py` | Re-checks the records for identifying material | console |
| `unitaryhack/bounties.py` | Bounties offered per year | `bounties_by_year.csv` |
| `unitaryhack/surveys.py` | Survey questions comparable across years | survey tables |
| `unitaryhack/ai_attitudes.py` | Topics raised in free-text answers about AI | `ai_attitudes.csv` |
| `qoss_survey/run.py` | The community survey questions the paper uses | the four `survey_*.csv` |
| `benchmark_pilot/resolve_bounties.py` | Each bounty's issue state and what closed it | task list |
| `benchmark_pilot/link_solutions.py` | Second pass over issue timelines | task list |
| `benchmark_pilot/link_graphql.py` | The issue-to-pull-request link, which only GraphQL gives | task list |
| `benchmark_pilot/solution_diffs.py` | Whether each reference solution carries a test | task list |
| `benchmark_pilot/reresolve_open.py` | Refetches only the bounties still open | task list |
| `benchmark_pilot/aggregates.py` | The per-year counts that are published | `task_pipeline_by_year.csv`, `task_solution_size.csv` |
| `benchmark_pilot/task_scope.py` | Files, lines, test files and languages of each reference solution, from complete file lists | task scope table |
| `benchmark_pilot/characterize.py` | Composition of the candidate tasks from their annotations; method in `benchmark_pilot/CHARACTERIZATION.md` | the CSVs in `../data/benchmarks/` |

## Running them

Python 3.9 or later. The collection scripts need only the standard library and `git`.
`requirements.txt` covers the rest.

Scripts write into a working directory, never beside the code. Set it with
`--data-root PATH` or `AI4QOSS_DATA_ROOT`. The default is `./_workspace`. Clone the
projects under study into `_repos/` inside it. Each script's docstring gives the clone
commands, and `api_survival` needs full history and tags.

```
export AI4QOSS_DATA_ROOT=~/qoss-work
mkdir -p $AI4QOSS_DATA_ROOT/_repos && cd $AI4QOSS_DATA_ROOT/_repos
git clone https://github.com/Qiskit/qiskit
git clone https://github.com/PennyLaneAI/pennylane
git clone https://github.com/quantumlib/Cirq
git clone https://github.com/numpy/numpy
git clone https://github.com/scipy/scipy
```

The scripts that call GitHub read `GITHUB_TOKEN` from the environment. A fine-grained
token with public repositories, read-only, is enough. Never put a token in a file here.
If your token lives in your shell profile, run through an interactive shell, since a
non-interactive `zsh` reads only `~/.zshenv`:

```
zsh -i -c 'python3 ai_disclosure/pulls.py --update'
```

`pulls.py` caches what it scores, so rescoring is free, and `--update` extends the cache
to the present instead of refetching it.

For a full refresh the order is: `api_churn`, the three `test_suite_audit` scripts,
`api_survival`, `ai_disclosure/commits.py`, `ai_disclosure/pulls.py --update`,
`corpus_size`. Disclosure is cut at the end of the last complete quarter, set as `UNTIL`
in both disclosure scripts, so a partial quarter never shows up as a data point.

## Personal data

Three scripts exist to keep it out of what we publish, and are included so the handling
can be checked.

- `unitaryhack/scrub.py` writes de-identified copies and leaves the sources untouched. It
  drops columns that name a person and masks email addresses and handles in free text.
- `unitaryhack/audit_pii.py` re-checks the sources and the copies.
- `audit_public_data.py` scans anything staged for publication. Run it before adding a
  file to `../data/figures/`.

Free-text answers are never reproduced. They are scored for topic and only counts are
published.

## Redrawing the figures

`figures/components.py` reads only the published CSVs and redraws every panel of the
paper's three figures into `figures/components/`.

```
python3 figures/components.py
```

Assembling the panels into the final figures is a separate step that is not included
here, because it depends on a helper we cannot redistribute.
