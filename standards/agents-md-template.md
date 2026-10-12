# AGENTS.md template for QOSS repositories

`AGENTS.md` is an open format for the instructions a coding agent reads when it works
inside a repository, stewarded by the Agentic AI Foundation under the Linux Foundation
since December 2025. It is read natively by OpenAI Codex, Cursor, GitHub Copilot's
agent features, and the other tools listed at [agents.md](https://agents.md/). Claude
Code reads it natively from v2.1.277, by default only when the working directory and
those above it hold no `CLAUDE.md` or `CLAUDE.local.md`; the
[`claude-md-and-agents-md`](https://code.claude.com/docs/en/memory) setting loads both,
and a one-line `CLAUDE.md` containing `@AGENTS.md` still works where native support is
unavailable.

The file is injected into the agent's context at every session, so length costs
tokens and dilutes adherence: Claude Code's documentation recommends staying under
200 lines, and Codex caps combined instruction files at 32 KiB by default. Exact
commands with flags work better than prose ("run `pytest tests/fast`" over "test your
changes"). Monorepos can nest `AGENTS.md` files; the file closest to the edited code
takes precedence.

Copy the template, fill in the brackets, and delete what does not apply. The
boundaries section pairs with the
[AI contribution policy](ai-contribution-policy.md) and the
[CI gates](ci-gates.md): what the policy asks of contributors, this file tells their
agents directly, and the gates enforce mechanically.

Last verified: 2026-10-12

```markdown
<!-- Read by coding agents at every session. Keep it terse: length costs
     context. Write direct instructions an agent can execute. -->

# AGENTS.md

## Environment and build

- Create the environment: [command, e.g. `pip install -e ".[dev]"`; pin the
  Python version]
- The virtual environment lives at [path]; file-listing tools often skip
  gitignored directories, so use this path directly.

## Test and lint

- Full test suite: [command]. Fast subset for iteration: [command].
- Run the tests relevant to the change; run the full suite only when asked.
- Lint / typecheck: [exact commands with flags]
- Docs build: [command, if applicable]

## Verification expectations

- Every behavior change comes with a test. For bug fixes, write the failing
  test first and confirm it fails before writing the fix.
- Probabilistic tests use fixed seeds and explicit tolerances. Do not loosen a
  tolerance, skip a test, or silence a linter warning to make a check pass;
  report the failure instead.
- [Project-specific verification: the circuit-equivalence suite and when to run it,
  conventions for statevector or unitary comparison, the qubit sizes above
  which exact verification stops being practical.]

## Boundaries

Always:

- Run the linter and the relevant tests before declaring a change done.
- Add an `AI use:` line to the PR description, per [CONTRIBUTING / your AI
  policy].

Ask first:

- Any change to dependencies, CI configuration, or release workflows.
- Test edits beyond what the change itself requires.

Never:

- Touch anything that uses credentials, paid services, or hardware backends.
- Commit, push, or open a PR unless explicitly asked.
- [Optional: work on issues labeled good-first-issue; those are reserved for
  new human contributors.]

If a task seems to require something in the ask-first or never lists, stop and
report that to the user instead of proceeding.

## Conventions

- [Code style, naming, docstring format, import aliases.]
- [Changelog: which file, which entry format.]
```

## Working examples

- [PennyLane's AGENTS.md](https://github.com/PennyLaneAI/pennylane/blob/master/AGENTS.md),
  the fullest example among the major quantum libraries: terse commands, an AI policy
  adapted from PyTorch's, changelog and architecture rules; its `CLAUDE.md` is the
  one-line import.
- [Qiskit IBM Runtime's AGENTS.md](https://github.com/Qiskit/qiskit-ibm-runtime/blob/main/AGENTS.md),
  added in September 2026: project goals, testing rules including a credentials gate on
  integration tests, and deprecation-policy constraints. Qiskit itself, Cirq, and QuTiP
  had none as of October 2026.
- [scikit-learn's AGENTS.md](https://github.com/scikit-learn/scikit-learn/blob/main/AGENTS.md),
  a minimal, policy-first example from scientific Python: a required AI-disclosure
  block and a small set of workflow rules.
