# Harness recipes

A harness is the setup around an AI model that lets it complete a task: the tools it can
call, the environment it runs in, the check the loop relies on, and the guardrails.
Each recipe here is one card, in the format of [TEMPLATE.md](TEMPLATE.md).

The check is the most important part of every card: state what the loop uses to decide
whether an attempt succeeded, what that check costs, and where it can be fooled.

Last verified: 2026-07-30

## Design principles

General principles for harness builders, independent of quantum. The cards in this
directory are expected to follow them.

- **Deterministic parts stay deterministic.** If a step can be handled by a script, a
  rule, or an API call, handle it there. The model is reserved for the steps that need
  judgment.
- **Assume frequent errors.** Design the loop to converge even when a large fraction of
  model attempts are wrong. Reliability comes from the checks, retries, and fallbacks
  around the model.
- **Contain a misbehaving model.** The harness must remain safe even if the model
  actively works against it. Sandboxing and permission scoping are sized for that case;
  the guardrails section of each card states how.
- **Every component needs evidence.** Add a component only when a measurement shows it
  improves results, and remove complexity that cannot show a gain.
- **Measure before tuning.** Instrument the loop and locate the actual bottleneck
  before optimizing anything.
- **Prefer existing agents.** Off-the-shelf coding agents handle most software tasks
  well. A custom harness is worth building only for what they fail at; in quantum
  software that remainder usually involves the verification problems this repository
  documents.

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
