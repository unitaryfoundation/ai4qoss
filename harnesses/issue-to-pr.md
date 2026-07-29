# Issue to PR

Last verified: 2026-07-29
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
it; the existing suite must stay green.

- Cost per iteration: one test run (use the project's fast subset where defined).
- Where it can be fooled: a test written to match the fix rather than the issue.
  Reviewers should check the test against the issue text before anything else.

## Guardrails

- No dependency or CI changes without prior maintainer approval (see
  [standards/ai-contribution-policy.md](../standards/ai-contribution-policy.md)).
- Diff size cap; larger changes need a human-approved plan in the issue first.
- One issue, one PR.

## Cost and results

To be filled from the first real runs, including solve rates by issue type.
