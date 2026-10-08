# Harness recipes

A harness is the setup around an AI model that lets it complete a task: the tools it can
call, the environment it runs in, the verification the loop relies on, and the
guardrails.

Each card here is a design for a harness a project could build, in the format of
[TEMPLATE.md](TEMPLATE.md). The cards are not harnesses themselves and ship no code;
they describe the task, the loop, the verification, and the guardrails closely enough
that a
maintainer can implement one, and they state what is known about how well the task
goes. Anything mechanically enforceable in the receiving repository belongs in
[standards/ci-gates.md](../standards/ci-gates.md), which does ship configuration.

Verification is the most important part of every card: state what the loop uses to
decide whether an attempt succeeded, what it costs, and where it can be fooled.

Last verified: 2026-10-07

## Design principles

General principles for harness builders, independent of quantum. The cards in this
directory are expected to follow them.

- **Deterministic parts stay deterministic.** If a step can be handled by a script, a
  rule, or an API call, handle it there. The model is reserved for the steps that need
  judgment.
- **Assume frequent errors.** Design the loop to converge even when a large fraction of
  model attempts are wrong. Reliability comes from the verification, retries, and
  fallbacks around the model.
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

| Card | Task | Verification |
|---|---|---|
| [version-migration](version-migration.md) | Migrate code across a breaking framework release | Test suite on the pinned target environment |
| [issue-to-pr](issue-to-pr.md) | Turn a repository issue into a reviewable PR | New regression test written first; old tests still pass |
| [bug-report](bug-report.md) | File a usable bug report | Minimal reproducing test, fails on HEAD |
| [transpiler-tuning](transpiler-tuning.md) | Improve a compiler pass against a cost metric | Circuit equivalence on every benchmark circuit, then the test suite |
| [docs-and-retrieval](docs-and-retrieval.md) | Write documentation correct for a pinned version | Every code example executes on that version |
| [pr-triage](pr-triage.md) | Reduce what a maintainer reads before deciding | CI gates; the summary itself is not verified |

None of these cards has been run by us. Each states what is published about its task
and what is not, and several tasks have no measurement at all. Treat the numbers in
them as expectations from adjacent work, and send corrections or results from a real
run as pull requests.

## Gaps (wanted)

- Hardware calibration with spend caps and credential sandboxing. The configurations
  that enforce those limits are now in
  [standards/agent-boundaries.md](../standards/agent-boundaries.md); what is still
  missing is the card itself, where the loop and its verification have to be worked out
  against a real calibration routine.
- Measured cost and results from a real run of any card above: iterations, wall-clock,
  and money on a real repository.
- A card whose verification is a proof rather than a test, for the tasks in
  [verifiers/](../verifiers/) where a certificate is available.
- A card whose verification is a statistical comparison rather than a pass or fail,
  which is what error mitigation and noise modeling would need. Every verification above
  is a test suite, an equivalence result, or an execution.
- A CI gate for executable documentation, which
  [docs-and-retrieval](docs-and-retrieval.md) depends on and
  [standards/ci-gates.md](../standards/ci-gates.md) does not yet cover.
