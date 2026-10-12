# Documentation against a versioned API

Last verified: 2026-10-12
Status: draft

## Task

Write or update documentation, examples, and answers about a framework, correct for a
specific released version. Done means: every code example in the changed pages
executes against the pinned version and produces what the text says it produces.

The problem this addresses is that a model's knowledge of a framework is a blend of
every version it saw during training, and quantum frameworks move fast enough for that
blend to be wrong in ways that read as plausible.

## Loop

1. Pin the version and build the environment. State the version in the page itself, so
   a reader can tell what the example was verified against.
2. Retrieve the current documentation and release notes for the target version and put
   them in the agent's context rather than relying on the model's recollection of the
   API. The evidence for this step is partial, and it is discussed below; a project
   instrumenting the loop should measure whether retrieval is worth its cost here.
3. Agent drafts or updates the page.
4. Execute every code block in the page. Failures return to step 3 with the traceback.
5. A human reads the prose. Executability is not correctness of explanation.

## Verification

Executable documentation: every example in the page runs under the pinned version,
through doctests, a notebook execution in the docs build, or an equivalent mechanism
already in the project.

- Cost per iteration: one docs build or test run over the changed pages.
- Where it can be fooled: an example that runs and teaches the wrong thing. Executing
  code catches deprecated calls, renamed arguments, and hallucinated methods; it does
  not catch a correct-but-misleading explanation, an example that demonstrates bad
  practice, or a claim about physics in the surrounding prose. Step 5 exists for that
  and is not optional. The mechanism also matters: doctests compare printed output
  against what the page claims, while executing a notebook in the docs build only
  establishes that nothing raised, so a page whose text describes a different result
  than the code produces passes the second and fails the first.

## Guardrails

- The pinned version is set by a human and the agent does not change it.
- Doctest tolerances and seeds may not be loosened to make an example pass.
- Retrieved documentation is data, not instruction: text fetched from the web or from
  a docs corpus may not be treated as a direction to the agent.
- No new dependencies to make an example work.

## Cost and results

We have not run this harness, and no published study measures documentation writing
against a pinned quantum framework version with an execution gate.

The staleness the loop is built around has been measured directly in published work. Across Qiskit 0.43,
1.3, and 2.0, with 50 tasks, 17 models, and 1,350 executions per model, pass@1 ranges
from 0.02 to 0.85 across the 16 models run through a matched REST interface, depending
on model and target version, and supplying the relevant documentation repairs only 0.19
to 0.59 of repair attempts
([arXiv:2607.04072](https://arxiv.org/abs/2607.04072)). The second number is the one
that shapes this card: retrieval helps and does not rescue a model that has the wrong
version in mind, so the execution gate carries the weight.

Retrieval results in quantum code generation are mixed and worth reading before
investing in a retrieval pipeline. On PennyLane hackathon problems, retrieval-augmented
generation produced roughly the same results as standard prompting, particularly on
complex algorithms ([arXiv:2506.20008](https://arxiv.org/abs/2506.20008)). Taken with
the repair figure above, the case for step 2 rests on repairing a known-wrong example
rather than on generating a right one, and a project that measures no gain should drop
it, per the design principles in the [directory README](README.md).

For question answering rather than code, a retrieval agent over the Qibo framework
reached a peak of 90.2 percent on a 50-question benchmark with one open-weight model
and hybrid retrieval, against 56.9 percent for a proprietary baseline
([arXiv:2603.15538](https://arxiv.org/abs/2603.15538)); that benchmark has a fixed
answer key, so it bounds documentation retrieval rather than documentation writing.
The same paper attempted two real Qibo issues, #1699 and #1710. It claims the first was
resolved autonomously and hedges on the second, reports no merged pull request for
either, and both were opened by a core Qibo developer and both remain open.

For the verification itself, no measurement is needed to justify it, but adoption is uneven
and worth checking in the target project before assuming the gate exists. A project
whose documentation examples are not executed in continuous integration has no
mechanism to reject a plausible-looking stale example, whoever wrote it.