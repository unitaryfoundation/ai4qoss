# CI gates for AI-era contributions

Checks a QOSS repository can enforce mechanically, so review capacity is spent on
substance. Examples, to adapt.

Last verified: 2026-07-29

## Gates worth enforcing

- **Tests required.** A PR that changes behavior without touching tests fails a check
  (label-based exemptions for docs and refactors).
- **Reproduction required for bug fixes.** The PR must contain a test that fails on the
  base branch and passes on the head. This one gate filters most low-effort AI
  submissions.
- **Disclosure footer present.** A lightweight check that the PR description contains an
  `AI use:` line (any value, including "none").
- **Dependency and CI freeze for first-time contributors.** Changes to dependency files,
  CI configuration, or release workflows from first-time contributors require a
  maintainer to remove a blocking label.
- **Equivalence checks where they exist.** For compiler or transpiler changes: run the
  project's circuit-equivalence suite (exact for small circuits, stabilizer or sampled
  checks for larger ones) in addition to the unit tests.

## Notes

- Gates filter mechanically what does not need human judgment, so review time goes to
  the parts that do.
- Publish the gates in CONTRIBUTING so contributors, human or agent, can run them
  locally before opening the PR.
