# AI contribution policy (template)

A template that QOSS projects can copy into their own repository and adapt. Replace
bracketed items.

Last verified: 2026-10-07

## What every contribution states

These requirements apply to all contributions, however they were produced. They ask for
the purpose of a change and the evidence behind it, which is what review actually turns
on.

- **The intended outcome.** One or two sentences on what the change is meant to achieve,
  written before the diff is read. "Fixes #123" is a reference, not an outcome.
- **Reproducible verification evidence.** Whatever establishes that the change does what
  it claims, in a form a reviewer can re-run: the test that covers it, the command that
  exercises it, the benchmark and the numbers it produced.
- **For bug reports and fixes:** a minimal reproducing example. Reports without one are
  closed with a pointer to this policy.
- **For new features and methods:** the functional or performance requirement the change
  is held to, and verification against that stated requirement. A feature with no stated
  requirement has nothing to verify.

Run the required verification in the project's own workflows before the change reaches a
maintainer, so that review starts from results rather than from running them.
[ci-gates.md](ci-gates.md) gives workflows for the mechanical parts.

## Disclosure

- State in the pull request description whether AI tools were used, and roughly how:
  code generation, test generation, review assistance, or fully agentic (the tool ran
  commands or edited files itself).
- A one-line footer is enough, for example: `AI use: code drafted with [tool], tests and
  final review by the author.`
- Record the tool name and version where the tool writes them itself, so that a class of
  defects traced to a particular tool or version can be found later. Several coding
  agents add an attribution line to the commit message without being asked; keep it
  rather than squashing it away.
- Disclosure carries no penalty. Undisclosed AI use, when discovered, is treated the
  same way as any other misrepresentation in a contribution.

## Review

- AI-assisted pull requests get the same review as any other. The submitting human is
  the author of record and is responsible for the contribution.
- Acceptance follows from the quality of the change and the verification evidence behind
  it, not from how it was produced.
- Reviewers may ask the author to explain any part of the change. A change the author
  cannot explain themselves is not ready for review, and the author remains responsible
  for answering what review raises.

## Blocked without prior approval

Agent-driven changes that do any of the following need explicit maintainer approval
before the PR is opened:

- adding or updating dependencies;
- modifying CI configuration, release workflows, or the workflows that run verification;
- anything that uses credentials, paid services, or hardware backends.

[agent-boundaries.md](agent-boundaries.md) gives the configurations that enforce these
outside the agent's own control.

## Rate limits

[Optional: maximum number of open AI-assisted PRs per contributor, cool-down after
closed-as-invalid submissions, etc. Set thresholds that fit the project's review
capacity.]
