# Harness recipes

A harness is the setup around an AI model that lets it complete a task: the tools it can
call, the environment it runs in, the check the loop relies on, and the guardrails.
Each recipe here is one card, in the format of [TEMPLATE.md](TEMPLATE.md).

The check is the most important part of every card: state what the loop uses to decide
whether an attempt succeeded, what that check costs, and where it can be fooled.

Last verified: 2026-07-29

## Cards

| Card | Task | Check |
|---|---|---|
| [version-migration](version-migration.md) | Migrate code across a breaking framework release | Test suite on the pinned target environment |
| [issue-to-pr](issue-to-pr.md) | Turn a repository issue into a reviewable PR | New regression test written first; old tests still pass |
| [bug-report](bug-report.md) | File a usable bug report | Minimal reproducing test, fails on HEAD |

## Gaps (wanted)

- Transpiler / compiler pass tuning (check: equivalence, exact for small circuits,
  stabilizer or sampled fidelity for large ones).
- Docs and retrieval against versioned API references (check: doctests execute).
- PR triage for maintainers (sandboxed checks plus a review checklist).
- Hardware calibration with spend caps and credential sandboxing (stretch; the
  guardrails are the hard part and belong on the card).
