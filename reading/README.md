# Reading

A reading list. One line per entry, saying what the work is and why it belongs
here; additions welcome on the same terms.

Last verified: 2026-08-27

## Community and research software

- ReSA, "Research Software Engineering in the Age of Generative AI: Building a
  Community Vision" (2026), DOI 10.5281/zenodo.20320884. The community-vision
  precedent; covers what is shared across all research software.
- curl's bug-bounty shutdown (January 2026;
  [Stenberg's announcement](https://daniel.haxx.se/blog/2026/01/26/the-end-of-the-curl-bug-bounty/)).
  The documented case of AI-generated junk reports overwhelming a maintainer team.
- Seth Larson, "New era of slop security reports for open source"
  ([2024](https://sethmlarson.dev/slop-security-reports)). The PSF's security
  developer-in-residence documenting AI-generated junk vulnerability reports a year
  before curl's shutdown.
- METR developer study, arXiv:2507.09089. Randomized trial on experienced developers
  in large open-source repositories: early-2025 AI tools slowed them by 19% while
  they estimated a 20% speedup.
- AI-contribution policies in large open-source projects:
  [Gentoo's ban](https://wiki.gentoo.org/wiki/Project:Council/AI_policy) (2024),
  [QEMU's provenance-based decline](https://www.qemu.org/docs/master/devel/code-provenance.html)
  (relaxation under discussion since May 2026), and
  [Fedora's allow-with-disclosure](https://docs.fedoraproject.org/en-US/council/policy/ai-policy/)
  (2025). The range of positions a QOSS project can adopt.

## Benchmarks and evaluation

- SWE-bench, arXiv:2310.06770. The template for issue-based software benchmarks.
- SWE-Bench Illusion, arXiv:2506.12286. Models identify the buggy file path from the
  issue text alone at 76% on SWE-bench repositories versus 53% on held-out ones; a
  memorization caveat for any static coding benchmark.
- Terminal-Bench / TB-Science (tbench.ai). Agent benchmarks with programmatic
  verification; the science edition accepts community task contributions.
- SciCode, arXiv:2407.13168. Scientist-curated research-coding problems with
  executable tests; the best model at release solved 4.6% of the main problems.
- CORE-Bench, arXiv:2409.11363. Agents reproduce the computational results of 90
  published papers from the papers' own code and data; reproduction as a
  programmatically checkable target.
- NatureBench, arXiv:2606.24530. Discovery vs reproduction on real papers; useful
  framing for what "solving" means.
- CritPt, arXiv:2509.26574. Unpublished research-level physics problems with
  automated grading, built to resist training-data leakage.
- QuantumBench, arXiv:2511.00092; Qiskit HumanEval, arXiv:2406.14712; QuanBench+,
  arXiv:2604.08570. Current quantum benchmarks test snippet-level code generation or
  multiple-choice knowledge.
- AInsteinBench, arXiv:2512.21373. Repository-level agent tasks built from maintainer
  pull requests in six production scientific codebases, quantum computing and quantum
  chemistry included.

## AI in the quantum stack

- Qiskit Code Assistant, arXiv:2405.19495; LLM Qiskit migration, arXiv:2606.20173.
  Code generation and maintenance for the Qiskit ecosystem.
- RL transpiler passes, arXiv:2405.13196. AI shipping inside a QOSS package.
- AlphaTensor-Quantum, arXiv:2402.14396; Nat. Mach. Intell. 7, 374 (2025). Deep
  reinforcement learning for T-count optimization that matches or beats the best
  human-designed constructions, with code released.
- AlphaQubit, Bausch et al., Nature 635, 834 (2024). Learned decoding.
- VF-QCTRL, arXiv:2605.26021. LLM-proposed control with an optimizer in the loop.
- k-agents, arXiv:2412.07978; Patterns 6, 101372 (2025). LLM agents plan, execute,
  and analyze superconducting-qubit calibration in closed loop.
- PyTheus, arXiv:2210.09980; Quantum 7, 1204 (2023). Open-source framework
  discovering interpretable photonic quantum-experiment designs; AI discovery shipped
  as software.

## Formalization in QI

- Klowden and Tao, "Mathematical methods and human thought in the age of AI",
  arXiv:2603.26524. How AI is changing mathematical practice; a reference point for
  writing a field-level perspective.
- AlphaProof, Nature 651, 607 (2025). Reinforcement learning over Lean proofs at IMO
  silver-medal level (with AlphaGeometry 2); the capability argument for AI-assisted
  formalization.
- Verified quantum software: VOQC, arXiv:1912.02250 (POPL 2021); CoqQ,
  arXiv:2207.11350 (POPL 2023). A verified circuit optimizer and a machine-checked
  quantum program logic; the reference points for what "verified" means in practice.
- Lean formalizations in QI: arXiv:2607.05492, arXiv:2607.09632, arXiv:2607.14082;
  machine-verified QAOA conjecture, arXiv:2606.29687.
- Tensor-network autoformalization, arXiv:2607.07857. LLM agents formalize the
  fundamental theorem of matrix-product states in Lean, extending AI-assisted
  formalization to many-body theory.
- The generalized quantum Stein's lemma episode: the proof was relied on for a decade,
  a gap was found (Berta et al., Quantum 7, 1103 (2023)), and the theorem was later
  re-proven (Lami 2025; Hayashi and Yamasaki 2025), with a Lean formalization
  following. The case for formalization as risk reduction.
- Physlib ([github.com/leanprover-community/physlib](https://github.com/leanprover-community/physlib)).
  The 2026 merger of PhysLean and Lean-QuantumInfo under leanprover-community; the
  Stein's lemma formalization now lives here.
