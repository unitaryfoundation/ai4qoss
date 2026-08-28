# Transpiler pass tuning

Last verified: 2026-08-28
Status: draft

## Task

Improve a compiler or transpiler pass against a cost metric, typically two-qubit gate
count, circuit depth, or T count, without changing what the circuit computes. Done
means: the metric improves on a benchmark set, every compiled circuit is checked
equivalent to its input, and the project's own test suite still passes.

This is the task where an unchecked loop is most dangerous. The metric rewards
removing gates, and the cheapest way to remove gates is to compile something other
than the requested circuit.

## Loop

1. Fix the benchmark set and the target device model (basis gates, connectivity), and
   record the baseline metric for each circuit.
2. Agent proposes a change to a pass or its heuristics.
3. Compile the benchmark set. Every circuit goes through the equivalence check below.
   Any circuit that fails, or that the checker cannot decide, rejects the change.
4. Compare the metric against the baseline; keep the change only if it improves the
   aggregate without regressing individual circuits beyond a stated tolerance.
5. Run the project's test suite before opening a pull request.

## Check

Equivalence of each compiled circuit against its input, then the project's test
suite. MQT QCEC provides this as a single call, `verify_compilation()`, which is built
for exactly this comparison and accounts for the layout permutation, ancillas, and
measurements that compilation introduces:

```python
from mqt import qcec
result = qcec.verify_compilation(original, compiled)
print(result.equivalence)
```

It coordinates several engines (decision-diagram construction, alternating
decision diagrams, simulation-based falsification, and ZX-calculus rewriting), handles
parameterized circuits symbolically, and can compare measured output distributions
when only partial equivalence is expected. See the
[verifier catalog](../verifiers/) for its cost profile and the alternatives when it
does not apply.

- Cost per iteration: one compile plus one equivalence check per benchmark circuit,
  plus one test-suite run per candidate change. Equivalence checking is worst-case
  exponential, and the size at which it stays practical is the constraint that decides
  whether this harness is usable at all. Structurally close pairs, which is what
  compilation produces, are the favorable case; unstructured pairs are not, and the
  measurements below show where the ceiling sat for one project. Falsification is
  cheaper than proof, so a broken change is often rejected quickly even when proving
  equivalence would be infeasible.
- Where it can be fooled: three ways, in increasing order of how easily they slip
  through. The checker can return that it could not decide, and a loop that treats
  that as success has no check at all; treat undecided as failure. The checker is
  itself a tested but unverified program, so a pass and the checker can share a
  blind spot. And equivalence says nothing about the metric being meaningful:
  optimizing two-qubit gate count on circuits unlike the ones users run produces a
  pass that is correct and useless, which is why the benchmark set is fixed in step 1
  rather than chosen by the agent.

## Guardrails

- The equivalence check runs on every benchmark circuit, not a sample, and the agent
  cannot edit the checker, the benchmark set, or the device model.
- Metric regressions on individual circuits need a human decision even when the
  aggregate improves.
- No changes to pass ordering defaults or to public APIs without maintainer sign-off;
  those affect every downstream user rather than one metric.
- Standard boundaries apply: no dependency or CI changes, and the project's own AI
  contribution policy governs what may be submitted. Several quantum projects forbid
  agents from opening pull requests without a human in the loop.

## Cost and results

We have not run this harness. What follows is what is known about the pieces, and the
check is the piece with the hardest constraint.

One project has published its attempt to raise that constraint. ucc, the Unitary
Foundation's compiler collection, verifies compilation in its own test suite by
comparing state vectors, which holds those tests to small circuits. In November 2024
it opened an issue asking how to check large compiled circuits and offered a bounty
([ucc#62](https://github.com/unitaryfoundation/ucc/issues/62)). Over 26 comments a
contributor tried QCEC, PyZX, and Giallar. QCEC verified 100-qubit random Clifford
circuits from ucc's tests in more than 24 hours on a 96-core machine, handled about 20
qubits within an hour, and scaled worse than linearly above that; Giallar exhausted 64
GB above 20 qubits; none of the three reached 50 qubits. The maintainers closed the
issue in June 2025 by paying the bounty for the search, writing that they had not been
sure it would be possible. As of this writing ucc's tests still compare state vectors.

Read that against the favorable case rather than as a verdict on QCEC. Random Clifford
circuits are close to the adversarial input for an equivalence checker, while a
transpiled circuit and its input share almost all of their structure, which is what
QCEC's compilation flow is built for. The honest statement is that the ceiling depends
on the circuits, that it was near 20 qubits for the unstructured case one project
measured, and that a maintainer adopting this harness should measure it on their own
benchmark set before trusting the loop.

Learned optimization of passes is established, though the published work uses
reinforcement learning trained for the task rather than a general coding agent. RL
synthesis and routing reaches near-optimal synthesis for linear function, Clifford,
and permutation circuits at 9, 11, and 65 qubits, orders of magnitude faster than
SAT-based optimization, and reduces two-qubit gate depth and count against the SABRE
routing heuristic at up to 133 qubits
([arXiv:2405.13196](https://arxiv.org/abs/2405.13196)). Those passes ship in the
separate `qiskit-ibm-transpiler` package rather than in Qiskit itself, and the
released versions carry lower limits than the paper reports, with the block sizes
they accept stated in that package's documentation. For T count, AlphaTensor-Quantum
improves on prior optimization methods across arithmetic benchmarks by casting the
problem as tensor decomposition
([arXiv:2402.14396](https://arxiv.org/abs/2402.14396);
[Nat. Mach. Intell. 7, 374 (2025)](https://doi.org/10.1038/s42256-025-01001-1)).

What is unmeasured is this card's own subject: a general-purpose coding agent
proposing pass changes, gated on equivalence, with a merged result. We found no
published account of one and no cost figures for the loop.