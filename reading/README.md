# Reading

A short annotated list. One line each; additions welcome if they carry their own
annotation.

Last verified: 2026-07-29

## Community and research software

- ReSA, "Research Software Engineering in the Age of Generative AI: Building a
  Community Vision" (2026), DOI 10.5281/zenodo.20320884. The community-vision
  precedent; covers what is shared across all research software.
- curl's bug-bounty shutdown (January 2026;
  [Stenberg's announcement](https://daniel.haxx.se/blog/2026/01/26/the-end-of-the-curl-bug-bounty/)).
  The documented case of AI-generated junk reports overwhelming a maintainer team.

## Benchmarks and evaluation

- SWE-bench, arXiv:2310.06770. The template for issue-based software benchmarks.
- Terminal-Bench / TB-Science (tbench.ai). Agent benchmarks with programmatic
  verification; the science edition accepts community task contributions.
- NatureBench, arXiv:2606.24530. Discovery vs reproduction on real papers; useful
  framing for what "solving" means.
- QuantumBench, arXiv:2511.00092; Qiskit HumanEval, arXiv:2406.14712; QuanBench+,
  arXiv:2604.08570. Current quantum benchmarks test snippet-level code generation or
  multiple-choice knowledge; repository-level work is unmeasured.

## AI in the quantum stack

- Qiskit Code Assistant, arXiv:2405.19495; LLM Qiskit migration, arXiv:2606.20173.
  Code generation and maintenance for the Qiskit ecosystem.
- RL transpiler passes, arXiv:2405.13196. AI shipping inside a QOSS package.
- AlphaQubit, Bausch et al., Nature 635, 834 (2024). Learned decoding.
- VF-QCTRL, arXiv:2605.26021. LLM-proposed control with an optimizer in the loop.

## Formalization in QI

- Klowden and Tao, "Mathematical methods and human thought in the age of AI",
  arXiv:2603.26524. How AI is changing mathematical practice; a reference point for
  writing a field-level perspective.
- Lean formalizations in QI: arXiv:2607.05492, arXiv:2607.09632, arXiv:2607.14082;
  machine-verified QAOA conjecture, arXiv:2606.29687.
- The generalized quantum Stein's lemma episode: the proof was relied on for a decade,
  a gap was found (Berta et al., Quantum 7, 1103 (2023)), and the theorem was later
  re-proven (Lami 2025; Hayashi and Yamasaki 2025), with a Lean formalization
  following. The case for formalization as risk reduction.
