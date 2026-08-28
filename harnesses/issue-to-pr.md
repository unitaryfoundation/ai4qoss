# Issue to PR

Last verified: 2026-08-28
Status: draft

## Task

Take a repository issue (bug or small feature) and produce a reviewable pull request.
Done means: a new test that captures the issue, a change that makes it pass, all old
tests still passing, and a PR description a reviewer can follow.

## Loop

1. Reproduce: agent writes a test that fails on the current head and matches the issue.
   If it cannot, it reports that instead of proceeding (that report is itself useful).
2. Fix: agent edits the code until the new test passes and the old suite stays green.
3. Explain: agent drafts the PR description: what failed, why, what changed, and the
   disclosure footer.

## Check

Test-first gating: the new regression test must fail before the change and pass after
it; the existing suite must stay green. This is gate 2 in
[standards/ci-gates.md](../standards/ci-gates.md), which gives a workflow that
enforces it.

- Cost per iteration: one test run (use the project's fast subset where defined).
- Where it can be fooled: a test written to match the fix rather than the issue, which
  is why reviewers should read the test against the issue text before anything else.
  The gate also passes when the new test fails on the base branch for an unrelated
  reason, an import error rather than the reported bug being the common case, and a
  change touching only test helpers can leave the collector with nothing to run, which
  reads as failure. Projects with compiled extensions need a rebuild between the two
  runs or both results are meaningless.

## Guardrails

- No dependency or CI changes without prior maintainer approval (see
  [standards/ai-contribution-policy.md](../standards/ai-contribution-policy.md)).
- Diff size cap; larger changes need a human-approved plan in the issue first.
- One issue, one PR.
- Check the receiving project's policy first. Qiskit's contributing guide forbids an
  agent from posting content autonomously and bars generative AI on issues labeled
  `good first issue`, which excludes much of what this harness would otherwise be
  pointed at; PennyLane's policy likewise requires human approval for any action in
  the repository. Under those rules a human opens the pull request.

## Cost and results

We have not run this harness ourselves. The numbers below come from published
benchmarks whose task form matches the check above, a real issue plus the repository's
own tests, and they set expectations rather than measure this card.

The only repository-level results on quantum software come from AInsteinBench
([arXiv:2512.21373](https://arxiv.org/abs/2512.21373)), which scores agents on merged
pull requests from six scientific codebases. Its released dataset holds 38 Qiskit and
47 PySCF tasks, though the reported percentages imply 37 scored Qiskit instances. Each
task carries the linked upstream issue, the maintainers' own test patch, and a gold
fix; scoring is binary on the full test suite in a per-instance container. Qiskit is
the highest-scoring domain in the results we checked: Claude 4.5 Opus resolves 67.6
percent of the Qiskit tasks and 38.3 percent of the PySCF tasks, against 44.0 percent
overall; GPT-4o, the weakest model reported, resolves 16.2 and 2.1 percent.

Four limits apply before those numbers are read as the rate to expect. They appear as
one column of a general scientific-computing benchmark, which no purpose-built quantum
software benchmark currently provides. Coverage stops at Qiskit and PySCF, with no
repository-level numbers for
Cirq, PennyLane, QuTiP, Stim, tket, or mitiq. The tasks are public merged pull
requests that predate the models' training data, and the paper reports no
contamination analysis. And each task is scored on a single attempt.

For repairs to user-level quantum programs rather than library source, a study of 67
real Qiskit defects from Bugs4Q reports pass@10 of 48.8 percent for the strongest
model tested, with the model given the buggy program and the issue text and nothing
else ([arXiv:2607.09007](https://arxiv.org/abs/2607.09007)). The same study found that
64 percent of the passes it observed fall on case and version pairs that fail
validation: 36 of the 67 cases validate even at Qiskit 0.25.0, and 7 at 2.3.1. That is
the failure mode fail-then-pass validation catches, which is also why our own task set
in [../benchmarks/](../benchmarks/) reports an upper bound until that validation is
done.

Cost per task is unreported in both studies. The scale to plan for is one container
build and one full test-suite run per attempt, plus the agent's own iterations inside
that container.
