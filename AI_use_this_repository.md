# How this repository was produced

`CONTRIBUTING.md` asks every contribution to state whether and how AI tools were used.
This page does that for the repository itself.

Last verified: 2026-10-12

## What AI assisted

The prose pages (`standards/`, `harnesses/`, `verifiers/`, `reading/`, and the directory
READMEs) were drafted with Claude Code and Codex in working sessions directed and reviewed by
Unitary Foundation staff. The `analysis/` scripts were written the same way. Every
factual claim, number, and citation was verified against its primary source before it
landed, and the `Last verified:` line on each page records when that check last ran.

The CSVs in `data/figures/` are script output. No model produced or edited a number in
them. The scripts behind them are in `analysis/`, one directory per dataset.

## What the verification covers

Pages separate our own results from work we quote from others. Where we have not run
something, the page says so: none of the six harness cards has been run by us, and their
cost and results sections carry figures from published work rather than ours. The gaps
lists in `harnesses/` and `verifiers/` record what we looked for and did not find.

Verification here means a person read the source and confirmed the claim. It does not
mean a page is free of error. Corrections are welcome as pull requests, and a correction
to a dated claim should move that page's date.
