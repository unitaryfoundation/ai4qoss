# [Harness name]

Last verified: YYYY-MM-DD
Status: [draft | tested on one repo | in regular use]

## Task

One paragraph: what the agent is asked to do, and what "done" means.

## Loop

The steps the agent iterates through, including what feedback it gets between attempts.

## Check

What the loop relies on to decide whether an attempt succeeded.

- What it is (test suite, equivalence checker, simulator comparison, doctest run, ...)
- What it costs per iteration (time, compute, money)
- Where it can be fooled, and what limits that

## Guardrails

What the agent is prevented from doing, and how (sandboxing, allowlists, spend caps,
human approval points).

## Cost and results

Rough numbers from actual runs: iterations to success, wall time, spend. Link to logs
or examples if public.
