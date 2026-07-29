# AI contribution policy (template)

A template that QOSS projects can copy into their own repository and adapt. Replace
bracketed items.

Last verified: 2026-07-29

## Disclosure

- State in the pull request description whether AI tools were used, and roughly how:
  code generation, test generation, review assistance, or fully agentic (the tool ran
  commands or edited files itself).
- A one-line footer is enough, for example: `AI use: code drafted with [tool], tests and
  final review by the author.`
- Disclosure carries no penalty. Undisclosed AI use, when discovered, is treated the
  same way as any other misrepresentation in a contribution.

## Review

- AI-assisted pull requests get the same review as any other. The submitting human is
  the author of record and is responsible for the contribution.
- Reviewers may ask the author to explain any part of the change. A change the author
  cannot explain themselves is not ready for review.
- For bug reports: a minimal reproducing test is required before review. Reports
  without one are closed with a pointer to this policy.

## Blocked without prior approval

Agent-driven changes that do any of the following need explicit maintainer approval
before the PR is opened:

- adding or updating dependencies;
- modifying CI configuration or release workflows;
- anything that uses credentials, paid services, or hardware backends.

## Rate limits

[Optional: maximum number of open AI-assisted PRs per contributor, cool-down after
closed-as-invalid submissions, etc. Set thresholds that fit the project's review
capacity.]
