# Pull request triage

Last verified: 2026-08-28
Status: draft

## Task

Reduce what a maintainer has to read before deciding on an incoming pull request. Done
means: every PR arrives with the mechanical checks already run and their results
stated, and the maintainer's first look is at the substance of the change.

This harness assists a maintainer. It does not decide, and it does not post on the
project's behalf.

## Loop

1. Mechanical gates run first, in CI, without a model: tests, linters, the
   fail-then-pass reproduction check for bug fixes, and the disclosure and
   sensitive-path checks in [standards/ci-gates.md](../standards/ci-gates.md). Two of
   those gates are keyed on labels a maintainer applies, so triage begins with a
   glance rather than with nothing.
2. For PRs that pass the gates, an agent produces a summary for the reviewer: what the
   change does, which parts of the diff carry the behavior change against which are
   mechanical, whether the tests exercise the change, and which project conventions
   the change touches.
3. The agent lists open questions for the maintainer rather than verdicts.
4. The maintainer reviews and decides.

## Check

There is no automatic check on the output of step 2, which is what separates this card
from the others in this directory. A triage summary is prose, and its errors are
omissions.

What can be checked is the gate layer in step 1, and the useful discipline is to keep
the two apart: anything mechanically decidable belongs in CI, where it is
deterministic and auditable, and the model handles only what needs reading.

- Cost per PR: the CI run, plus one model pass over the diff.
- Where it can be fooled: a summary that reads well and misses the thing that matters.
  A reviewer who stops reading because the summary looked complete is worse off than
  with no summary. The mitigation that works is structural: the maintainer's decision
  is recorded against the diff rather than against the summary, and every claim in the
  summary cites the lines it came from, so a spot check is cheap. Asking the model to
  declare what it did not examine is a useful convention and not a check, since it
  relies on the same judgment that failed.

## Guardrails

- The agent does not post comments, apply labels, close pull requests, or request
  changes. Output goes to the maintainer.
- No rejection is attributed to suspected AI authorship. Detection is unreliable, and
  the projects that have written policies (below) judge contributions on review cost
  and on whether a human understands the change.
- Contributor-facing tone stays a maintainer's decision. A triage summary is an
  internal artifact.
- Repository policy governs. Several quantum projects forbid agents from acting in
  their repositories at all, which this card's design already respects.

## Cost and results

We have not run this harness, and there is no published measurement of AI-assisted PR
triage in quantum software: no time saved, no error rate, no maintainer assessment.
PennyLane and mitiq both state in their policies that their labeling exists to help
reviewers and deliberately does not track which parts of the codebase are
AI-generated, so the denominator for such a measurement does not exist either.

What is documented is what maintainers decided to do about the problem. Seven quantum
projects adopted written policies between February 2025 and August 2026: Cirq and Stim
(February 2025), Qiskit (October 2025, substantially rewritten August 2026), PennyLane
(February 2026), mitiq (March 2026), QuTiP (April 2026), and bloqade (May 2026). Their
content converges on review cost rather than on authorship. Qiskit's states that
maintainers may close any pull request when the review effort is expected to outweigh
the benefit, with no proof of AI use required, and that development is not bottlenecked
by the speed of writing code. PennyLane's, adapted from the LLVM policy, puts the same
principle as a contribution being worth more than the time it takes to review.
Both forbid agents from acting autonomously in the repository. QuTiP requires a
disclosure in every pull request, bars fully autonomous agents from submitting, and
asks that AI assistance be recorded as `Assisted-by:` rather than as a
`Co-authored-by:` trailer. Bloqade asks first-time contributors not to submit
AI-generated pull requests, so that the project can get to know a contributor before
AI-assisted work enters the mix.

For the general case, one study of 9,799 agentic pull requests across open-source
projects reports 63.1 percent merged
([arXiv:2605.22534](https://arxiv.org/abs/2605.22534)); a second reports agentic
acceptance at 83.8 percent against 91.0 percent for human-authored pull requests
([arXiv:2509.14745](https://arxiv.org/abs/2509.14745)), which we have verified less
firmly than the first. Neither covers quantum projects. Where disclosure is requested,
compliance is partial: our own measurements of disclosure markers across quantum and
mainstream projects are in [../data/](../data/), and they are lower bounds, since a
contributor who uses an assistant and writes nothing leaves no trace. Together these
point the same way: triage effort is not reducible to detecting AI involvement, and a
harness built to do that would be solving the wrong problem.

The honest summary is that this card describes a plausible division of labor, the
mechanical part of which is implemented and testable today, and the model part of
which is unevaluated.