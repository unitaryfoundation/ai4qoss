# Reading

A reading list. One line per entry, saying what the work is and why it belongs
here; additions welcome on the same terms.

Last verified: 2026-10-19

## Community and research software

- ReSA, "Research Software Engineering in the Age of Generative AI: Building a
  Community Vision" (2026), [DOI
  10.5281/zenodo.20320884](https://doi.org/10.5281/zenodo.20320884). The
  community-vision precedent; covers what is shared across all research software.
- curl's bug-bounty shutdown (January 2026; [Stenberg's
  announcement](https://daniel.haxx.se/blog/2026/01/26/the-end-of-the-curl-bug-bounty/)).
  The documented case of AI-generated junk reports overwhelming a maintainer team.
- Seth Larson, "New era of slop security reports for open source"
  ([2024](https://sethmlarson.dev/slop-security-reports)). The PSF's security
  developer-in-residence documenting AI-generated junk vulnerability reports a year
  before curl's shutdown.
- METR developer study, [arXiv:2507.09089](https://arxiv.org/abs/2507.09089).
  Randomized trial on experienced developers in large open-source repositories:
  early-2025 AI tools slowed them by 19% while they estimated a 20% speedup.
- Agentic coding pull requests, Watanabe et al., [ACM Trans. Softw. Eng. Methodol. 35,
  1 (2026)](https://doi.org/10.1145/3798166);
  [arXiv:2509.14745](https://arxiv.org/abs/2509.14745). 567 pull requests made with an
  agentic coding tool across 157 open-source projects: 83.8% were eventually merged,
  but only 54.9% of those went in unmodified. Agents were used mostly for refactoring,
  documentation, and testing.
- Baltes, Cheong and Treude, "An Endless Stream of AI Slop", [IEEE Softw.
  (2026)](https://doi.org/10.1109/MS.2026.3730626);
  [arXiv:2603.27249](https://arxiv.org/abs/2603.27249). Qualitative study of 1,154
  Reddit and Hacker News posts, coded into review friction, quality degradation, and
  systemic forces. Frames AI slop as a tragedy of the commons: the productivity gain
  is private and the review cost is not.
- Afroz et al., "AI Slop is DDoSing Open Source",
  [arXiv:2607.04003](https://arxiv.org/abs/2607.04003). Bayesian structural time
  series over 294 repositories and more than two million pull requests and issues.
  Volume rose through 2025 while merge rates fell, with an 18.18% drop for one-time
  contributors against the counterfactual; 11 remediation strategies validated by 229
  practitioners.
- Lara-Martín and Pérez-Castillo, "Entangle: Uncovering Collaboration in the GitHub
  Quantum Software Ecosystem", IEEE QCE 2026;
  [arXiv:2609.28349](https://arxiv.org/abs/2609.28349). Maps more than 1,500 quantum
  repositories, 27,000 contributors and 400 organizations, and finds that 81.7% of
  repositories have a bus factor of 1, meaning maintenance activity concentrated in
  one key contributor. The only quantitative picture of who maintains this ecosystem.
- AI-contribution policies in large open-source projects: [Gentoo's
  ban](https://wiki.gentoo.org/wiki/Project:Council/AI_policy) (2024), [QEMU's
  provenance-based
  decline](https://www.qemu.org/docs/master/devel/code-provenance.html) (relaxation
  under discussion since May 2026), and [Fedora's
  allow-with-disclosure](https://docs.fedoraproject.org/en-US/council/policy/ai-contribution-policy/)
  (2025). The range of positions a QOSS project can adopt.

## Benchmarks and evaluation

- SWE-bench, [arXiv:2310.06770](https://arxiv.org/abs/2310.06770). The template for
  issue-based software benchmarks.
- SWE-Bench Illusion, [arXiv:2506.12286](https://arxiv.org/abs/2506.12286). Models
  identify the buggy file path from the issue text alone at 76% on SWE-bench
  repositories versus 53% on held-out ones; a memorization caveat for any static
  coding benchmark.
- Terminal-Bench / TB-Science ([tbench.ai](https://tbench.ai)). Agent benchmarks with
  programmatic verification; the science edition accepts community task contributions.
- SciCode, [arXiv:2407.13168](https://arxiv.org/abs/2407.13168) (NeurIPS 2024 Datasets
  and Benchmarks). Scientist-curated research-coding problems with executable tests;
  338 subproblems from 80 main problems. In the published version the best model
  tested, o1-preview, solved 7.7% of the main problems in the most realistic setting.
  The arXiv abstract still reports the 4.6% that Claude 3.5 Sonnet reached at
  submission.
- CORE-Bench, [arXiv:2409.11363](https://arxiv.org/abs/2409.11363). Agents reproduce
  the computational results of 90 published papers from the papers' own code and data;
  reproduction as a programmatically checkable target.
- NatureBench, [arXiv:2606.24530](https://arxiv.org/abs/2606.24530). Discovery vs
  reproduction on real papers; useful framing for what "solving" means.
- CritPt, [arXiv:2509.26574](https://arxiv.org/abs/2509.26574). Unpublished
  research-level physics problems with automated grading, built to resist
  training-data leakage.
- QuantumBench, [arXiv:2511.00092](https://arxiv.org/abs/2511.00092); Qiskit
  HumanEval, [arXiv:2406.14712](https://arxiv.org/abs/2406.14712); QuanBench+,
  [arXiv:2604.08570](https://arxiv.org/abs/2604.08570). Current quantum benchmarks
  test snippet-level code generation or multiple-choice knowledge.
- AInsteinBench, [arXiv:2512.21373](https://arxiv.org/abs/2512.21373).
  Repository-level agent tasks built from maintainer pull requests in six production
  scientific codebases, quantum computing and quantum chemistry included.
- [Agentic leaderboards](https://unitary.foundation/posts/2026_agentic_leaderboards/)
  (Unitary Foundation, October 2026). Challenge harnesses for problems whose answer a
  program can check, with a public board so the current best becomes everyone else's
  starting line. The index covers ECDSA.fail, built in May 2026 on Google's
  zero-knowledge proof checker, where the community reached a Pareto front reported as
  68% better than Google's; stabilizer rank decompositions; Clifft's circuit
  optimizer; and hardware benchmarks on Metriq. The QEC Challenge is the
  error-correction board.
- Metriq, [arXiv:2603.08680](https://arxiv.org/abs/2603.08680). Open cross-vendor
  platform for benchmarking quantum computers: definition, execution, collection, and
  public presentation in one workflow, with released results from more than ten
  machines and a composite Metriq Score.
- Quantum-Harbor and QIQCBench, [arXiv:2609.17439](https://arxiv.org/abs/2609.17439).
  A virtual lab plus 49 expert-authored tasks across calibration and control, error
  correction and compilation, and sensing and networking. Outputs that cannot be
  verified from recorded data, such as calibrations or designs, are tested under fresh
  hidden conditions, and failures are split into no submission, science failure where
  the hidden grader rejects the physics, and contract failure where the answer breaks
  the submission protocol. The scoring design a repository benchmark has to copy.

## AI in the quantum stack

- Qiskit Code Assistant, [arXiv:2405.19495](https://arxiv.org/abs/2405.19495); LLM
  Qiskit migration, [arXiv:2606.20173](https://arxiv.org/abs/2606.20173). Code
  generation and maintenance for the Qiskit ecosystem.
- RL transpiler passes, [arXiv:2405.13196](https://arxiv.org/abs/2405.13196). AI
  shipping inside a QOSS package.
- AlphaTensor-Quantum, [arXiv:2402.14396](https://arxiv.org/abs/2402.14396); Nat.
  Mach. Intell. 7, 374 (2025). Deep reinforcement learning for T-count optimization
  that matches or beats the best human-designed constructions, with code released.
- AlphaQubit, Bausch et al., [Nature 635, 834
  (2024)](https://doi.org/10.1038/s41586-024-08148-8). Learned decoding.
- VF-QCTRL, [arXiv:2605.26021](https://arxiv.org/abs/2605.26021). LLM-proposed control
  with an optimizer in the loop.
- k-agents, [arXiv:2412.07978](https://arxiv.org/abs/2412.07978); Patterns 6, 101372
  (2025). LLM agents plan, execute, and analyze superconducting-qubit calibration in
  closed loop.
- PyTheus, [arXiv:2210.09980](https://arxiv.org/abs/2210.09980); Quantum 7, 1204
  (2023). Open-source framework discovering interpretable photonic quantum-experiment
  designs; AI discovery shipped as software.
- Verifiable structure for agentic compilation,
  [arXiv:2610.23832](https://arxiv.org/abs/2610.23832). Khattar, Rubin, Gidney,
  Broughton, Low and Babbush (Google) constrain bottleneck subroutines to reversible
  classical logic, phasing, and measurement-based uncomputation, so that approximate
  synthesis can be certified by fuzz testing. Applied to 1/sqrt(x) in the Coulomb
  operator, Reed-Solomon decoding, and look-up tables for chemistry. The verifier is
  what makes the agentic search usable, which is this repository's premise.
- LLM circuit discovery, [arXiv:2610.22367](https://arxiv.org/abs/2610.22367). Gu,
  Kemeny, Yelin and Lukin (Harvard) run an evolutionary loop in which the model
  proposes circuits and an evaluator independent of the model verifies and scores each
  one. Seven of eight tasks lower both Toffoli and qubit counts against the state of
  the art; the eighth finds a new reversible architecture for prime-field modular
  inversion.
 - Validated verifiers for agentic circuit optimization,
  [arXiv:2610.31352](https://arxiv.org/abs/2610.31352). Crichigno and Flammia
  (Phasecraft and Virginia Tech) have an agent build each problem's exact verifier
  with a researcher and validate it against an analytically solved case, deliberately
  broken solutions and published results before it is frozen and opened to competing
  agents. Applied to fermion-to-qubit encoding, Hamiltonian layout and unitary
  synthesis; the fermionic encodings outperform a state-of-the-art optimizer. Every
  accepted result is a program with the agent's notes.
- Meta-designing quantum experiments, Arlt et al., [Nat. Mach. Intell. 8, 148
  (2026)](https://doi.org/10.1038/s42256-025-01153-0). A transformer trained on
  millions of synthetic states and their blueprints writes human-readable Python that
  generates whole families of experiments, rather than one solution at a time,
  recovering known design principles and generalizing past them.
- Alexeev et al., "Artificial intelligence for quantum computing", [Nat. Commun. 16,
  10829 (2025)](https://doi.org/10.1038/s41467-025-65836-3);
  [arXiv:2411.09131](https://arxiv.org/abs/2411.09131). Twenty-eight authors reviewing
  AI across the quantum computing stack, from device design to applications. The
  field-level review this Perspective sits beside.
- [NVQLink](https://nvidianews.nvidia.com/news/nvidia-nvqlink-quantum-gpu-computing)
  (NVIDIA, 2025). GPU interconnect for running a learned decoder inside the
  error-correction cycle. AlphaQubit above is the accuracy side of decoding; this is
  the latency side, which is what kept learned decoders off real machines.

## Formalization in QI

- Klowden and Tao, "Mathematical methods and human thought in the age of AI",
  [arXiv:2603.26524](https://arxiv.org/abs/2603.26524). How AI is changing
  mathematical practice; a reference point for writing a field-level perspective.
- AlphaProof, [Nature 651, 607 (2025)](https://doi.org/10.1038/s41586-025-09833-y).
  Reinforcement learning over Lean proofs at IMO silver-medal level (with
  AlphaGeometry 2); the capability argument for AI-assisted formalization.
- Verified quantum software: VOQC,
  [arXiv:1912.02250](https://arxiv.org/abs/1912.02250) (POPL 2021); CoqQ,
  [arXiv:2207.11350](https://arxiv.org/abs/2207.11350) (POPL 2023). A verified circuit
  optimizer and a machine-checked quantum program logic; the reference points for what
  "verified" means in practice.
- Lean formalizations in QI: [arXiv:2607.05492](https://arxiv.org/abs/2607.05492),
  [arXiv:2607.09632](https://arxiv.org/abs/2607.09632),
  [arXiv:2607.14082](https://arxiv.org/abs/2607.14082); machine-verified QAOA
  conjecture, [arXiv:2606.29687](https://arxiv.org/abs/2606.29687).
- Tensor-network autoformalization,
  [arXiv:2607.07857](https://arxiv.org/abs/2607.07857). LLM agents formalize the
  fundamental theorem of matrix-product states in Lean, extending AI-assisted
  formalization to many-body theory.
- The generalized quantum Stein's lemma episode: the proof was relied on for a decade,
  a gap was found (Berta et al., [Quantum 7, 1103
  (2023)](https://doi.org/10.22331/q-2023-09-07-1103)), and the theorem was later
  re-proven (Lami 2025; Hayashi and Yamasaki 2025), with a Lean formalization
  following. The case for formalization as risk reduction.
- Physlib
  ([github.com/leanprover-community/physlib](https://github.com/leanprover-community/physlib)).
  The 2026 merger of PhysLean and Lean-QuantumInfo under leanprover-community; the
  Stein's lemma formalization now lives here.
