# Data

Datasets behind the figures in the perspective paper. Scope is deliberate: what the
three figures rest on, and nothing else. Survey responses, raw pull request caches, and
the organizers' bounty list stay outside this repository.

Last verified: 2026-10-20

License: CC BY 4.0 (see [../LICENSING.md](../LICENSING.md)). These files are often
downloaded one at a time, so the terms travel only through this page.

## When each file was measured

The files do not share one date, and none of them carries its own timestamp, so this is
the only record of it. "Measured" is when the script last ran against its source;
"covers" is the period the numbers describe, where that differs.

| File | Measured | Covers |
|---|---|---|
| `corpus_size.csv` | 2026-10-06 | GitHub code search and the preceding 30 days of PyPI installs, both as of that date |
| `api_survival.csv` | 2026-10-06 | release tags per year from each project's first to its latest 2026 release |
| `api_churn_summary.csv` | 2026-08-23 | release notes up to that date |
| `qubit_counts.csv`, `qubit_by_module.csv`, `circuit_kind.csv` | 2026-10-06 | the test suites as of that date |
| the four `ai_disclosure_*.csv` | 2026-10-06 | commits and pull requests through 2026-09-30, so that the last quarter is complete |
| `task_pipeline_by_year.csv`, `task_solution_size.csv` | 2026-10-06 | the 2022 to 2026 unitaryHACK events, re-resolved on that date for the bounties still open in August, which moved one more bounty into the usable set |
| `bounties_by_year.csv` | 2026-08-23 | the 2022 to 2026 events, all concluded |
| `ai_attitudes.csv` | 2026-08-23 | the 2026 post-event surveys, closed |
| the three `survey_*.csv` | 2026-10-20 | a 2026-10-20 snapshot of a survey still collecting responses |

Three files were not part of the October re-measurement. For `bounties_by_year.csv` and
`ai_attitudes.csv` that changes nothing, because both describe events that had already
concluded when they were measured. `api_churn_summary.csv` counts deprecations per year
from release notes that have grown since August, so its four numbers are an August
measurement.

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
| `task_solution_size.csv` | Distribution of lines changed across the 417 reference solutions |
| `bounties_by_year.csv` | Bounties offered per year, aggregated |
| `ai_attitudes.csv` | Topic counts from the free-text AI questions of the 2026 unitaryHACK surveys, 9 maintainers and 16 contributors |

### Community survey

| File | Contents |
|---|---|
| `survey_tasks.csv` | How respondents perform each task in their quantum workflow, manually or with AI assistance |
| `survey_verification.csv` | How respondents who use AI to write or debug code verify that the result is correct |
| `survey_agreement.csv` | Agreement with three statements about the accuracy and usefulness of AI assistants |

These are the three questions behind the figure panels and nothing else from that
survey. They come from the 2026 Quantum Open Source Software Survey run by the Unitary
Foundation, as a snapshot taken on 2026-10-20 while collection was still open. The
survey was announced to run through 29 October 2026 and the Foundation publishes its own
summary of the full results, so these counts are a mid-collection cut rather than the
final ones.

Denominators differ by question, because respondents drop out as the survey proceeds, so
each file carries its own answered count. `survey_tasks.csv` and
`survey_verification.csv` come from questions that allowed several answers, so their
shares overlap and do not sum to 100; in the first of them a respondent can report both
modes for one task. The verification question offered both "Automated tests" and
"Automation verification" without defining either, and 102 of the 133 respondents who
chose the second also chose the first, so the two are published as one row,
`Automated test/verification`. In `survey_agreement.csv` the `rated` column is the row
total minus the respondents who answered "not applicable", and it is the denominator
the paper uses.

The export this snapshot comes from carries one row per respondent, where the
2026-10-07 one was already aggregated. SurveyMonkey flags 90 of the 1,315 responses as
poor quality, mostly for speeding. Dropping them moves no share in these three files by
more than a point, so the published counts are over all respondents.

Survey respondents are the quantum software community at large. They are not the
contributors to the 19 repositories measured in the disclosure files above, so adoption
in one and recorded disclosure in the other describe different populations.

For the benchmark collection, we publish only the collection method and aggregate
statistics. The per-task list, issue text, reference patches, and tests are not released.
Any future release will require a review of the applicable licenses and permissions,
alongside privacy considerations. The aggregates above carry the numbers the figures
rest on.

The PR-template policy file contains counts and a yes/no classification. Text excerpts
from pull request bodies are excluded from the public export.

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

The three `survey_*.csv` files are counts over respondents to the community survey. They
carry no response text and no respondent attribute, so no answer can be traced to a
person. Free-text answers to that survey are not published here in any form.

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

## Re-measurement

The paper is a snapshot; these files are the part that can be brought forward. What we
intend to re-run, and what is missing, is recorded here rather than in the paper so that
it can be revised as it happens.

| Measurement | Cadence | What changes it |
|---|---|---|
| `corpus_size.csv` | Annual | New framework releases, and consolidation of the ecosystem onto fewer libraries |
| `api_survival.csv`, `api_churn_summary.csv` | Annual, on each project's latest stable release | Major releases; the 2021 baseline stays fixed so the series stays comparable |
| `qubit_counts.csv`, `qubit_by_module.csv`, `circuit_kind.csv` | Annual | Growth of the test suites; adoption of verification that does not need full simulation |
| `ai_disclosure_*.csv` | Quarterly | Projects adding or removing a disclosure field; tools changing what they write into a commit |
| `task_pipeline_by_year.csv`, `task_solution_size.csv` | After each unitaryHACK event | The next event's bounty list |
| `ai_attitudes.csv` | After each event that asks about AI | The survey instrument, which changed in 2026 when the AI questions were added |
| `survey_*.csv` | After each annual community survey closes | The next survey; the 2026 snapshot here predates that survey's own close |

Three things are absent and would have to be collected rather than recomputed.

Contributor retention. The surveys ask participants whether they intend to keep
contributing; whether they did is not recorded anywhere. It can be reconstructed from
each project's commit history without a survey, by checking whether a participant
appears again in the following year.

Fail-then-pass validation of the benchmark tasks. Until each reference test is shown to
fail at the parent commit and pass after the change, the automatically scorable count is
an upper bound. See [../benchmarks/](../benchmarks/).

Direct evidence on model staleness. The interface-survival numbers say what fraction of
an old API still imports, which bounds how wrong a model trained on that snapshot can
be. What a model actually emits for a given framework version is a separate measurement
that we have not made; published work covering Qiskit 0.43, 1.3, and 2.0 reports
pass@1 between 0.02 and 0.85 across 17 models
([arXiv:2607.04072](https://arxiv.org/abs/2607.04072)).

## Reproducing

The scripts that produce every file here are in [../analysis/](../analysis/), one
directory per measurement, each with a docstring stating its method, its denominators,
and the ways it can be wrong. That directory's README says which scripts a reader can run
from public sources, which need a GitHub token, and which depend on inputs we do not
publish.

`../analysis/figures/components.py` redraws every panel of the paper's three figures from
the CSVs in this directory alone, so the figures can be checked against the data without
anything else.
