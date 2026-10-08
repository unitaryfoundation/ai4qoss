# Verifier catalog

Tools that verify a quantum artifact (a circuit, a detector error model, a code spec)
and report whether it is sound, ideally without full simulation and with a concrete
counterexample on failure. These are the verifiers that harnesses and CI gates rely on;
the catalog records what exists, what it costs, and where the gaps are.

Entries must state concrete scope limits, including the sizes at which the tool remains
practical.

Last verified: 2026-08-28

## Catalog

### Circuits

| Tool | What it verifies | Cost | Maturity | Link |
|---|---|---|---|---|
| MQT QCEC | Equivalence of two circuits, for example before and after transpilation, through decision diagrams, simulation-based falsification, and ZX-calculus rewriting; `verify_compilation()` handles the layout permutation and ancillas that compilation introduces | Seconds for moderate sizes and worst case exponential; fast when the two circuits are structurally close, which is the compilation case. One project reported about 20 qubits within an hour on random Clifford pairs, the adversarial case, and over 24 hours at 100 qubits ([ucc#62](https://github.com/unitaryfoundation/ucc/issues/62)) | Mature, maintained | [github.com/munich-quantum-toolkit/qcec](https://github.com/munich-quantum-toolkit/qcec) · [IEEE TCAD 40, 1810 (2021)](https://doi.org/10.1109/TCAD.2020.3032630) |
| PyZX | ZX-calculus simplification and equivalence | Fast on Clifford+T structures | Mature, maintained | [github.com/zxcalc/pyzx](https://github.com/zxcalc/pyzx) · [EPTCS 318, 229 (2020)](https://doi.org/10.4204/EPTCS.318.14) |
| Exact unitary / statevector comparison | Exact equivalence of small circuits | Exponential; unitary comparison to roughly 15 qubits, statevector to roughly 30 | Standard practice | n/a |
| Randomized / sampled fidelity checks | Statistical closeness on sampled inputs, for mid-size circuits | Tunable | Standard practice | n/a |
| Clifft | Exact simulation of near-Clifford circuits, extending the exact-comparison and sampled-fidelity checks above to large circuits with few non-Clifford gates | Exponential in the peak active dimension; the Clifford part is cheap at any qubit count | New (2026), actively maintained (Unitary Foundation) | [github.com/unitaryfoundation/clifft](https://github.com/unitaryfoundation/clifft) · [arXiv:2604.27058](https://arxiv.org/abs/2604.27058) |

### Error correction

| Tool | What it verifies | Cost | Maturity | Link |
|---|---|---|---|---|
| Stim | Stabilizer circuits and detector error models: Clifford simulation, and logical-error search for distance upper bounds | Simulation fast at large qubit counts; error search exact only for graphlike errors | Mature, maintained | [github.com/quantumlib/Stim](https://github.com/quantumlib/Stim) · [Quantum 5, 497 (2021)](https://doi.org/10.22331/q-2021-07-06-497) |
| emlint | Structural problems in a Stim detector error model, and equivalence of two models | Quasilinear in the number of instructions; decides equivalence exactly for non-adaptive pipelines, soundly for partially adaptive ones such as lattice surgery | Early; v0.2 is preliminary and its APIs may change | [github.com/MathysRennela/emlint](https://github.com/MathysRennela/emlint) · [arXiv:2606.14677](https://arxiv.org/abs/2606.14677) |
| Lean-QEC | Distance lower bounds for stabilizer codes, through a reduction to Boolean satisfiability that is itself verified in Lean | Kernel-checked distance certificates at up to 90 physical qubits; the formulation scales to 144 qubits when run outside the kernel | Research prototype | [github.com/VerifiedQC/Lean-QEC](https://github.com/VerifiedQC/Lean-QEC) · [arXiv:2605.16523](https://arxiv.org/abs/2605.16523) |
| QECLean | Stabilizer-code theory in Lean 4: Pauli group, binary symplectic representation, CSS structure, and concrete codes, including the toric code proved to have distance exactly L for every lattice size L at least 2 | Kernel check; the bivariate bicycle proofs are memory-heavy and are excluded from the lightweight build | Active; sorry-free on main, no `native_decide` | [github.com/Stavan-Jain/QECLean](https://github.com/Stavan-Jain/QECLean) |
| Veri-QEC | Correctness of error-correction programs against assertions in a dedicated program logic, with verification conditions discharged by SMT; exact for Pauli errors, heuristic beyond them; the logic itself is proved sound in Coq | SMT solver time, growing with code size | Research prototype; evaluated on 14 stabilizer codes | [github.com/Chesterhuang1999/Veri-qec](https://github.com/Chesterhuang1999/Veri-qec) · [PLDI 2025](https://doi.org/10.1145/3729293) · [arXiv:2504.07732](https://arxiv.org/abs/2504.07732) |

### Program and platform testing

Tools here target either a user's quantum program or the platform underneath it, the
compiler, transpiler, and simulator stack. Recent maintenance and documented bug
counts concentrate in the platform-testing line. Among user-program tools, QuCheck is
the one with current activity; the mutation and coverage tools from the 2021 to 2023
research wave are frozen and predate Qiskit 1.0.

| Tool | What it tests | Cost | Maturity | Link |
|---|---|---|---|---|
| QITE (IterTestQ) | Round-trips OpenQASM through the importers, optimizers, and exporters of Qiskit, PennyLane, Pytket, BQSKit, and more recently Cirq, cross-checking crashes and circuit equivalence with QCEC | Formal equivalence check per round trip; the published evaluation used 11-qubit, 15-gate programs | Actively developed in 2026; 23 platform bugs reported and 17 confirmed or fixed per the project README, against 17 and 14 in the paper | [github.com/sola-st/qite-quantum-platform-testing](https://github.com/sola-st/qite-quantum-platform-testing) · [arXiv:2503.17322](https://arxiv.org/abs/2503.17322) |
| MorphQ | Metamorphic testing of Qiskit: generates valid programs, applies semantics-preserving transformations, flags crashes and output divergence between related pairs | Roughly 8,000 program pairs in two days on commodity hardware, simulation only | Research artifact, last activity March 2025; 13 Qiskit bugs, 9 confirmed (ICSE 2023) | [github.com/sola-st/MorphQ-Quantum-Qiskit-Testing-ICSE-23](https://github.com/sola-st/MorphQ-Quantum-Qiskit-Testing-ICSE-23) · [arXiv:2206.01111](https://arxiv.org/abs/2206.01111) |
| QuteFuzz | Fuzzing of Pytket, Qiskit, and Cirq compilers and simulators with random circuits including control flow, under a differential oracle | Simulation per generated circuit | Prototype, last activity mid-2025; 17 bugs across the three platforms, self-reported in the project README; workshop report only (PLanQC 2025), no archival paper | [github.com/QuteFuzz/QuteFuzz](https://github.com/QuteFuzz/QuteFuzz) |
| FuzzQ | Constraint-guided fuzzing of Qiskit and Cirq simulators from a formal Alloy model of OpenQASM 3.0, with invariant, statistical, and cross-simulator oracles | Over 800,000 circuits in the published evaluation | Research artifact (OOPSLA 2025, ACM artifact badges); 8 simulator bugs, 6 previously undocumented | [DOI 10.1145/3763100](https://doi.org/10.1145/3763100) · [Zenodo artifact](https://zenodo.org/records/16918102) |
| QuCheck | Property-based testing of Qiskit programs: user-declared properties, preconditions, and statistical assertions, QuickCheck style | Repeated simulator executions per property; evaluated on 2 to 10 qubit programs | Single-author tool on PyPI, active in 2026; evaluated on seeded faults, no platform bugs claimed | [github.com/GabrielPontolillo/qucheck](https://github.com/GabrielPontolillo/qucheck) · [ACM TQC](https://doi.org/10.1145/3815169) · [arXiv:2503.22641](https://arxiv.org/abs/2503.22641) |
| QMutPy, Muskit | Mutation testing for Qiskit: gate- and measurement-level mutants scored against the project's test suite or an output specification; measures test-suite strength. Muskit additionally requires sequential code, a single qubit register, and a full output specification | One test-suite or specification run per mutant, on a simulator | Frozen research artifacts since 2021; predate Qiskit 1.0 | [QMutPy (MutPy fork)](https://github.com/danielfobooss/mutpy) · [Muskit](https://github.com/Simula-COMPLEX/muskit) |
| Quito, QuSBT, QuCAT | Coverage-guided, search-based, and combinatorial input generation for Qiskit programs, against a full expected-output specification | Simulation per generated input; the specification requirement limits use to small programs | Frozen research artifacts (2021 to 2023) | [Quito](https://github.com/Simula-COMPLEX/quito) · [QuSBT](https://github.com/Simula-COMPLEX/qusbt-tool) · [QuCAT](https://github.com/Simula-COMPLEX/qucat-tool) |

### Verified quantum software

Frameworks that prove programs correct once and for all, in a proof assistant or a
deductive verifier. Each verifies programs written in its own language; applying one
to an existing codebase means porting the program and supplying proofs, which is
formal-methods work with a timescale of months.

| Tool | What it verifies | Cost | Maturity | Link |
|---|---|---|---|---|
| VOQC (on SQIR) | A circuit optimizer whose passes are proven semantics-preserving in Coq; SQIR, the underlying circuit language, supports proving programs correct up to a certified end-to-end Shor implementation ([PNAS 120, e2218775120 (2023)](https://doi.org/10.1073/pnas.2218775120)) | Verified once and for all; running the extracted optimizer is push-button | Framework maintained at low intensity; the extracted binaries (mlvoqc, pyvoqc) have had no release since 2022 and their Qiskit interop predates Qiskit 1.0 | [github.com/inQWIRE/SQIR](https://github.com/inQWIRE/SQIR) · [POPL 2021](https://doi.org/10.1145/3434318) · [arXiv:1912.02250](https://arxiv.org/abs/1912.02250) |
| Qbricks | Deductive verification (Why3 with SMT solvers) of parametrized circuit-building programs against input-output specifications; verified parametric Shor order finding, QPE, and Grover | Specification and proof effort per program; SMT discharges most obligations, the remaining lemmas are manual | Research artifact, minor activity in 2026 | [github.com/Qbricks/qbricks.github.io](https://github.com/Qbricks/qbricks.github.io) · [ESOP 2021](https://doi.org/10.1007/978-3-030-72019-3_6) · [arXiv:2003.05841](https://arxiv.org/abs/2003.05841) |
| CoqQ | A quantum Hoare-style program logic in Coq, sound against a denotational semantics; case studies are textbook algorithms (HHL, Grover, QPE) at parametric size | Interactive Coq proof per property; no extraction to executables | Research artifact, no activity since December 2024 | [github.com/coq-quantum/CoqQ](https://github.com/coq-quantum/CoqQ) · [POPL 2023](https://doi.org/10.1145/3571222) · [arXiv:2207.11350](https://arxiv.org/abs/2207.11350) |

### Theorem-level claims

| Tool | What it verifies | Cost | Maturity | Link |
|---|---|---|---|---|
| Lean 4 + Mathlib | Any claim stated as a theorem, with the proof accepted or rejected by the kernel | High effort to build, instant to re-check | Growing in quantum information (see [reading/](../reading/)) | [github.com/leanprover-community/mathlib4](https://github.com/leanprover-community/mathlib4) |

The largest quantum-information result verified this way is the generalized quantum
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
- Noise-model verification: flagging parameters that violate physical constraints.
  Gate set tomography (pyGSTi) reports whether a model is consistent with data;
  verifying a supplied model's internal consistency without data is unaddressed.
- Soundness verification for error mitigation. No tool verifies that a mitigation
  estimator's bias claims hold for a given noise model, or that a composed pipeline
  keeps its stated guarantees; mitiq's calibration module compares strategies
  empirically, with no guarantee attached.
- Maintained testing tools for user-level quantum programs beyond property-based
  testing. QuCheck is the one entry above with current activity; the mutation and
  coverage tools are frozen at 2021 to 2023 and predate Qiskit 1.0.
- Equivalence checking above the exact-simulation ceiling for non-Clifford circuits,
  with stated soundness trade-offs.
- Proof-carrying transpilation: passes that emit a verifiable equivalence certificate,
  which would take the transpiler out of the trusted set. QCEC validates each
  compiled circuit, and the verifier itself then sits in the trusted set.
