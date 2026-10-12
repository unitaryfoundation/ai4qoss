# Contributor pipeline (template)

Practices for projects and event organizers who recruit maintainers from their
contributors. The concern is narrow: introductory issues and hackathon bounties are how
most QOSS projects train the people who later maintain them, and they are also the
tasks coding agents handle best. A project that routes all of its small work to agents
keeps its issue tracker short and loses the path by which contributors become
maintainers.

This page pairs with the [AI contribution policy](ai-contribution-policy.md), which
governs what any single contribution must state. The practices here apply to the
sequence of contributions a person makes over time.

Last verified: 2026-10-12

## Why this is worth a policy

Maintenance in this ecosystem is thin. In a survey of public quantum repositories,
81.7 percent had maintenance resting on a single contributor (Lara-Martín and
Pérez-Castillo, IEEE QCE 2026,
[arXiv:2609.28349](https://arxiv.org/abs/2609.28349)). A project in that position
cannot treat contributor development as a side effect of resolving issues.

Completing a task is also not the same as learning from it. A randomized study of
developers learning an unfamiliar Python library found lower comprehension and debugging
scores afterward among those who had AI assistance
([arXiv:2601.20245](https://arxiv.org/abs/2601.20245)). For a newcomer, the pressure to
close an issue quickly runs against the time it takes to acquire the skill, and the
completed pull request looks the same either way.

## For projects

- **Reserve some introductory issues for people.** Label them, and say in the label's
  description that they are held for contributors who want to learn the codebase.
  A project that wants agents on its small issues can still keep a set aside.
- **Ask for an approach before the code.** For an introductory issue, ask the
  contributor to describe how they intend to fix it, in the issue, before opening a pull
  request. This is useful review practice regardless of AI, and it is the point where a
  contributor who does not understand the problem is easiest to help.
- **Say what AI assistance is for on introductory work.** The version that preserves
  learning is the contributor drafting an approach first and using generated code to
  revise their own work. State that as the expectation rather than banning tools, which
  is unenforceable.
- **Give credit for the parts that are not the diff.** Reviewing someone else's pull
  request, writing a reproducing example, and improving a test all develop maintainers.
  If the project's only recognized unit of contribution is a merged pull request, these
  go unrecorded.

## For event organizers

These come from running unitaryHACK from 2022 to 2026 and from the 2026 maintainer
meeting. Each one addresses a problem the organizers actually hit.

- **Cap open pull requests per participant.** unitaryHACK 2026 limited each participant
  to four at a time. Without a cap, a small number of participants open many
  low-confidence pull requests and the review queue becomes the bottleneck for everyone.
- **Hold a design conversation before the pull request** on anything beyond a small
  fix, so that competing submissions do not arrive against the same issue.
- **Freeze an issue once someone is working on it.** Issues that attract several
  simultaneous submissions waste both the contributors' and the maintainers' time.
- **Schedule maintainer time for mentoring separately from review time.** When the two
  come from the same budget, review wins, because review has a deadline. Organizers who
  reported more work than they expected after the 2026 event described the time going to
  explaining rejections and establishing how AI had been used.
- **Office hours before review** give contributors somewhere to take a question that is
  not a pull request comment.

## What to measure

Two measurements are cheap and answer whether any of the above works. Neither needs a
survey.

| Measurement | How | What it tells you |
|---|---|---|
| Return rate | For each participant in an event, whether they commit to any project in the ecosystem in the following twelve months | Whether the event produces contributors or only contributions |
| Progression | Whether any returning contributor later holds review or merge rights | Whether the pipeline reaches maintainership at all |

Both are recoverable from public commit history without asking anyone. We have not run
either for unitaryHACK; the records exist and the measurement does not.

A third measurement would be more useful and is harder. A follow-up task completed
without AI assistance would show whether a participant can apply what they learned, but
a project cannot verify that a contributor worked without assistance, so this only works
where a contributor opts in.

## What this page does not claim

No measurement here establishes that agents taking over introductory issues leaves
projects with fewer future maintainers. The mechanism is plausible and the two
conditions behind it are documented, which is single-maintainer projects and lower
comprehension after AI-assisted learning. The connection between them is not measured,
in this ecosystem or elsewhere. Corrections and data are welcome under the usual pull request rules.
