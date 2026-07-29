# Verifier catalog

Tools that check a quantum artifact (a circuit, a detector error model, a code spec)
and report whether it is sound, ideally without full simulation and with a concrete
counterexample on failure. These are the checks that harnesses and CI gates rely on;
the catalog records what exists, what it costs, and where the gaps are.

Entries must state concrete scope limits, including the sizes at which the tool remains
practical.

Last verified: 2026-07-29

## Catalog

| Tool | Artifact | What it checks | Cost | Maturity | Link |
|---|---|---|---|---|---|
| MQT QCEC | Circuits | Equivalence of two circuits (e.g. before/after transpilation) | Seconds for moderate sizes; worst case exponential | Mature, maintained | [github.com/cda-tum/mqt-qcec](https://github.com/cda-tum/mqt-qcec) |
| PyZX | Circuits | ZX-calculus based simplification and equivalence | Fast on Clifford+T structures | Mature, maintained | [github.com/zxcalc/pyzx](https://github.com/zxcalc/pyzx) |
| Stim | Stabilizer circuits, DEMs | Fast Clifford simulation; logical-error search for distance upper bounds | Simulation fast at large qubit counts; error search exact only for graphlike errors | Mature, maintained | [github.com/quantumlib/stim](https://github.com/quantumlib/stim) |
| Exact unitary / statevector comparison | Small circuits | Exact equivalence | Exponential; unitary comparison to roughly 15 qubits, statevector to roughly 30 | Standard practice | n/a |
| Randomized / sampled fidelity checks | Mid-size circuits | Statistical closeness on sampled inputs | Tunable | Standard practice | n/a |
| QECLean, emlint | QEC pipelines, DEMs | Static analysis of QEC artifacts | Static | Early prototypes | [QECLean](https://github.com/Stavan-Jain/QECLean) · [arXiv:2606.14677](https://arxiv.org/abs/2606.14677) |
| Machine-checked proofs (Lean 4 + Mathlib) | Theorem-level claims | Full formal verification | High effort to build, instant to re-check | Growing in QI (see reading/) | [github.com/leanprover-community/mathlib4](https://github.com/leanprover-community/mathlib4) |

Corrections to scope, cost, or maturity are welcome under the usual PR rules.

## Gaps (wanted)

- Distance verification for general large qLDPC codes; machine-checked certificates
  exist for specific families (arXiv:2605.16523), and counterexample search in the
  general case remains open.
- Detector-error-model linting beyond early prototypes.
- Noise-model sanity checks: flagging physically inconsistent noise parameters.
- Equivalence checking above the exact-simulation ceiling for non-Clifford circuits,
  with stated soundness trade-offs.
- Proof-carrying transpilation: passes that emit a checkable equivalence certificate.
