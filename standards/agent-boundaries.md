# Agent boundaries (template)

Limits on what an automated contributor may do inside a repository, and where each
limit is enforced. A limit written only into the agent's instructions is advice, not a
boundary: it holds while the model follows instructions and fails exactly when it does
not. Every item below therefore names the place outside the agent's reach where it is
enforced.

This page pairs with the [AI contribution policy](ai-contribution-policy.md), which
states what a contributor must do, the [AGENTS.md template](agents-md-template.md),
which tells an agent the same rules directly, and the [CI gates](ci-gates.md), which
block a merge mechanically.

Last verified: 2026-10-07

## Where each limit lives

| Boundary | Enforced by | Inside the agent's control? |
|---|---|---|
| What the agent may read and write | Container image and working directory | No |
| Repository write access | `permissions:` block on the workflow, branch protection | No |
| New or changed dependencies | Maintainer approval, plus the freeze gate in [ci-gates.md](ci-gates.md) | No |
| Changes to verification workflows | Same as dependencies; treat `.github/workflows/` as a protected path | No |
| Credentials for hardware or paid services | Environment secret behind a required reviewer | No |
| Money and device time | Allocation on the provider account | No |
| Iterations and wall-clock per task | Runner script counter and `timeout-minutes` | No |
| Everything in AGENTS.md | The model following instructions | Yes |

The last row is the reason for the other eight.

## Environment and permissions

Run the agent in a container that holds the repository, its pinned dependencies, and
nothing else. Keep credentials out of the image. Give the workflow the least token
scope the task needs, which for a read-and-propose loop is:

```yaml
permissions:
  contents: read
  pull-requests: read
```

A job that opens a pull request needs `pull-requests: write`; grant it on that job
alone, not at the workflow level. Where the runner supports an egress allowlist,
restrict network access to the package index and the APIs the task actually uses.

## Approval before dependency and workflow changes

Agent-opened pull requests that add or update a dependency, or that touch CI
configuration, release workflows, or the verification workflows themselves, need
maintainer approval before the work starts. Gate 4 in [ci-gates.md](ci-gates.md)
enforces the same restriction for first-time contributors; for automated contributors
it applies regardless of history, because an agent has no history to judge.

Treat the files that define verification as protected paths. An agent that can edit the
workflow that checks its own output can satisfy the check by weakening it.

## Hardware and paid services

- Keep provider credentials in a GitHub environment secret rather than a repository
  secret. Protect that environment with a required reviewer, so any job referencing it
  pauses until a maintainer approves the run. Jobs that do not reference the
  environment cannot read the secret at all.
- Set the budget on the provider account, not in the prompt and not in the agent's
  configuration. Cloud quantum providers allocate runtime per account or per instance;
  set that allocation to the task budget so that exhausting it ends the run whatever
  the agent does. Confirm with your provider which unit the allocation is measured in
  before relying on it.
- Default every task to a simulator backend. Moving to hardware is an explicit,
  separately approved step, not something a retry can reach.

## Iteration and time limits

- Count iterations in the script that drives the loop and stop at the cap. An
  instruction to stop after N attempts is not a cap.
- Set `timeout-minutes` on the job. The GitHub default is 360 minutes, long enough for
  a failing loop to run all day.
- Use a `concurrency` group with `cancel-in-progress: true` so repeated pushes do not
  queue parallel copies of the same expensive job.

```yaml
concurrency:
  group: agent-${{ github.head_ref }}
  cancel-in-progress: true
jobs:
  agent:
    timeout-minutes: 30
```

## Where this can be fooled

An agent that cannot change a limit can still work around its purpose. A spend cap set
per run does not stop many runs. A timeout bounds one job, not a loop that reopens the
pull request. Caps belong at the account and repository level, where the sum is
bounded, and a maintainer should look at totals rather than at individual runs.

None of this addresses a contribution that is cheap to produce and expensive to read.
That cost is what the contribution requirements in
[ai-contribution-policy.md](ai-contribution-policy.md) and the gates in
[ci-gates.md](ci-gates.md) are for.
