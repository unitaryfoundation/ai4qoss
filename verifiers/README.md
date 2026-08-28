# Verifier catalog

Tools that check a quantum artifact (a circuit, a detector error model, a code spec)
and report whether it is sound, ideally without full simulation and with a concrete
counterexample on failure. These are the checks that harnesses and CI gates rely on;
the catalog records what exists, what it costs, and where the gaps are.

Entries must state concrete scope limits, including the sizes at which the tool remains
practical.

Last verified: 2026-08-23

## Catalog

### Circuits

| Tool | What it checks | Cost | Maturity | Link |
|---|---|---|---|---|
| MQT QCEC | Equivalence of two circuits, for example before and after transpilation | Seconds for moderate sizes; worst case exponential | Mature, maintained | [github.com/cda-tum/mqt-qcec](https://github.com/cda-tum/mqt-qcec) · [IEEE TCAD 40, 1810 (2021)](https://doi.org/10.1109/TCAD.2020.3032630) |
| PyZX | ZX-calculus simplification and equivalence | Fast on Clifford+T structures | Mature, maintained | [github.com/zxcalc/pyzx](https://github.com/zxcalc/pyzx) · [EPTCS 318, 229 (2020)](https://doi.org/10.4204/EPTCS.318.14) |
| Exact unitary / statevector comparison | Exact equivalence of small circuits | Exponential; unitary comparison to roughly 15 qubits, statevector to roughly 30 | Standard practice | n/a |
| Randomized / sampled fidelity checks | Statistical closeness on sampled inputs, for mid-size circuits | Tunable | Standard practice | n/a |

### Error correction

| Tool | What it checks | Cost | Maturity | Link |
|---|---|---|---|---|
| Stim | Stabilizer circuits and detector error models: Clifford simulation, and logical-error search for distance upper bounds | Simulation fast at large qubit counts; error search exact only for graphlike errors | Mature, maintained | [github.com/quantumlib/Stim](https://github.com/quantumlib/Stim) · [Quantum 5, 497 (2021)](https://doi.org/10.22331/q-2021-07-06-497) |
| emlint | Structural problems in a Stim detector error model, and equivalence of two models | Quasilinear in the number of instructions; decides equivalence exactly for non-adaptive pipelines, soundly for partially adaptive ones such as lattice surgery | Early; v0.2 is preliminary and its APIs may change | [github.com/MathysRennela/emlint](https://github.com/MathysRennela/emlint) · [arXiv:2606.14677](https://arxiv.org/abs/2606.14677) |
| Lean-QEC | Distance lower bounds for stabilizer codes, through a reduction to Boolean satisfiability that is itself verified in Lean | Kernel-checked distance certificates at up to 90 physical qubits; the formulation scales to 144 qubits when run outside the kernel | Research prototype | [github.com/VerifiedQC/Lean-QEC](https://github.com/VerifiedQC/Lean-QEC) · [arXiv:2605.16523](https://arxiv.org/abs/2605.16523) |
| QECLean | Stabilizer-code theory in Lean 4: Pauli group, binary symplectic representation, CSS structure, and concrete codes, including the toric code proved to have distance exactly L for every lattice size L at least 2 | Kernel check; the bivariate bicycle proofs are memory-heavy and are excluded from the lightweight build | Active; sorry-free on main, no `native_decide` | [github.com/Stavan-Jain/QECLean](https://github.com/Stavan-Jain/QECLean) |

### Theorem-level claims

| Tool | What it checks | Cost | Maturity | Link |
|---|---|---|---|---|
| Lean 4 + Mathlib | Any claim stated as a theorem, with the proof accepted or rejected by the kernel | High effort to build, instant to re-check | Growing in quantum information (see [reading/](../reading/)) | [github.com/leanprover-community/mathlib4](https://github.com/leanprover-community/mathlib4) |

The largest quantum-information result checked this way is the generalized quantum
Stein's lemma, whose published proof was relied on for a decade before a gap was found
([Quantum 7, 1103 (2023)](https://doi.org/10.22331/q-2023-09-07-1103)) and which was
later re-proven and formalized ([arXiv:2510.08672](https://arxiv.org/abs/2510.08672)).
How well AI agents construct proofs of this kind has been measured on two Lean 4
benchmarks covering quantum algorithms and quantum information theory
([arXiv:2607.21533](https://arxiv.org/abs/2607.21533)).

Corrections to scope, cost, or maturity are welcome under the usual PR rules.

## Gaps (wanted)

- Distance verification for general large qLDPC codes. Machine-checked certificates now
  exist for the bivariate bicycle and generalized bicycle families
  ([arXiv:2605.16523](https://arxiv.org/abs/2605.16523)); the general case is open, and
  counterexample search for a claimed distance is not addressed by either entry above.
- Detector-error-model equivalence for fully adaptive pipelines, where the existing
  decision procedure is sound and not complete.
- Noise-model sanity checks: flagging physically inconsistent noise parameters.
- Equivalence checking above the exact-simulation ceiling for non-Clifford circuits,
  with stated soundness trade-offs.
- Proof-carrying transpilation: passes that emit a checkable equivalence certificate,
  which would take the transpiler out of the trusted set.
