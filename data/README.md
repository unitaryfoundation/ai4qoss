# Data

Datasets behind the figures in the perspective paper. Scope is deliberate: what the
three figures rest on, and nothing else. Survey responses, raw pull request caches, and
the organizers' bounty list stay outside this repository.

Last verified: 2026-08-23

## Contents

Files are in [figures/](figures/), grouped by the figure they support.

### Corpus and interface stability

| File | Contents |
|---|---|
| `corpus_size.csv` | Files in public repositories importing each library, and PyPI installs over 30 days, for 9 quantum and 8 mainstream libraries |
| `api_survival.csv` | Share of a project's public API of each year still importable in its latest release, per project and year |
| `api_churn_summary.csv` | Deprecations announced per year and per release, counted from each project's own release notes |

### Verification scale and AI disclosure

| File | Contents |
|---|---|
| `qubit_counts.csv` | Literal qubit counts in test constructors, per project |
| `qubit_by_module.csv` | Those counts split by the area of the code under test |
| `circuit_kind.csv` | Random against structured circuit construction in test files |
| `ai_disclosure_commits.csv` | Commits carrying an AI marker, per project and quarter |
| `ai_disclosure_pulls.csv` | Pull requests carrying an AI disclosure, per project and quarter |
| `ai_disclosure_pr_template_policy.csv` | Whether each project's pull request template asks about AI use |
| `ai_disclosure_concentration.csv` | How concentrated disclosure is within each project |

### Tasks recovered from community records

| File | Contents |
|---|---|
| `task_pipeline_by_year.csv` | Counts at each stage from bounty to usable task, per year, and what the reference solutions change |
| `task_solution_size.csv` | Distribution of lines changed across the 430 reference solutions |
| `bounties_by_year.csv` | Bounties offered per year, aggregated |
| `ai_attitudes.csv` | Topic counts from the free-text AI questions of the 2026 surveys |

The per-task list is not published. It names the repositories and pull requests of
individual contributors, and several of those repositories sit under personal accounts,
so releasing it is a question of consent rather than of licensing. The aggregates above
carry the numbers the figures rest on.

## Privacy

Nothing here identifies an individual. The files hold library and project names, dates,
and counts. No account name, email address, issue URL, or pull request URL appears in any
of them, which is checked before publication rather than assumed.

Two things were removed on the way out. The account name of each project's largest
discloser in `ai_disclosure_concentration.csv`, where the count is published and the name
is not. And the per-task list behind the task figure, which named contributors'
repositories and pull requests; it is replaced by the two aggregate files above.

`ai_attitudes.csv` is derived from participant surveys. It carries topic counts over 9
maintainers and 16 contributors and no response text; free-text answers are not published
in any form. The underlying responses stay with the organizers.

## Reading these numbers

Three limits apply across the set and are stated in the paper's figure captions.

GitHub's code search returns an estimate rather than a count for large result sets, so
`corpus_size.csv` supports an order of magnitude and not a ratio. PyPI counts installs
rather than code and is inflated by continuous integration for packages deep in
dependency trees.

Disclosure counts are lower bounds. A contributor who uses an assistant and records
nothing leaves no trace in any of these files.

Counts drawn from surveys rest on single digits. They describe the respondents and not
the wider community.

## Reproducing

The scripts that produce these files, together with the full method and caveats for each
measurement, are described in the paper. Figure sources are in the paper's repository
under `perspective_paper/figures/`.
