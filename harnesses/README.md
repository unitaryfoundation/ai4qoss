# Harness recipes

A harness is the setup around an AI model that lets it complete a task: the tools it can
call, the environment it runs in, the check the loop relies on, and the guardrails.

Each card here is a design for a harness a project could build, in the format of
[TEMPLATE.md](TEMPLATE.md). The cards are not harnesses themselves and ship no code;
they describe the task, the loop, the check, and the guardrails closely enough that a
maintainer can implement one, and they state what is known about how well the task
goes. Anything mechanically enforceable in the receiving repository belongs in
[standards/ci-gates.md](../standards/ci-gates.md), which does ship configuration.

The check is the most important part of every card: state what the loop uses to decide
whether an attempt succeeded, what that check costs, and where it can be fooled.

Last verified: 2026-08-28

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
| [transpiler-tuning](transpiler-tuning.md) | Improve a compiler pass against a cost metric | Circuit equivalence on every benchmark circuit, then the test suite |
| [docs-and-retrieval](docs-and-retrieval.md) | Write documentation correct for a pinned version | Every code example executes on that version |
| [pr-triage](pr-triage.md) | Reduce what a maintainer reads before deciding | CI gates; the summary itself is unchecked |

None of these cards has been run by us. Each states what is published about its task
and what is not, and several tasks have no measurement at all. Treat the numbers in
them as expectations from adjacent work, and send corrections or first-hand results as
pull requests.

## Gaps (wanted)

- Hardware calibration with spend caps and credential sandboxing. The guardrails are
  the hard part and belong on the card, which is why there is no draft here yet.
- First-hand cost and results for any card above: iterations, wall-clock, and money
  for a real run on a real repository.
- A card whose check is a proof rather than a test, for the tasks in
  [verifiers/](../verifiers/) where a certificate is available.
- A card whose check is a statistical comparison rather than a pass or fail, which is
  what error mitigation and noise modeling would need. Every check above is a test
  suite, an equivalence result, or an execution.
- A CI gate for executable documentation, which
  [docs-and-retrieval](docs-and-retrieval.md) depends on and
  [standards/ci-gates.md](../standards/ci-gates.md) does not yet cover.
