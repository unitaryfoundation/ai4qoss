# ai4qoss

AI for quantum open-source software (QOSS): community standards, harness recipes,
verification tools, and benchmarks.

This repository accompanies a perspective paper by Unitary Foundation and collaborators,
[arXiv:2610.38049](https://arxiv.org/abs/2610.38049). The paper is a fixed snapshot.
This repository holds the parts that change: policies, tool catalogs, harness recipes,
and data.

## Layout

| Directory | Contents |
|---|---|
| [`standards/`](standards/) | Policy templates repos can copy: what a contribution must state, AI disclosure and review, agent boundaries, an AGENTS.md template, CI gate examples, contributor pipeline practices |
| [`harnesses/`](harnesses/) | Designs for agent harnesses a project could build: the task, the loop, the check the loop relies on, and the guardrails. Cards, not code |
| [`verifiers/`](verifiers/) | Catalog of verification tools for quantum artifacts, with scope, cost, maturity, and open gaps |
| [`benchmarks/`](benchmarks/) | Task format, collection method, and stage counts for tasks built from real QOSS work; the task list itself is not published |
| [`data/`](data/) | Datasets behind the paper's figures, with the re-measurement schedule |
| [`analysis/`](analysis/) | The code that produced those datasets and the figure panels, one directory per measurement |
| [`reading/`](reading/) | Reading list, one line per entry |

## Conventions

- Every content page carries a `Last verified:` date, so stale content is visible.
- Contributions arrive as pull requests and follow the repository's own
  [AI contribution policy](standards/ai-contribution-policy.md). That policy applies to
  this repository too, and
  [AI_use_this_repository.md](AI_use_this_repository.md) states how AI tools were used
  to produce it.
- Releases are tagged and dated; the default branch carries the latest content.
  Release v1.0.0 matches the data in the paper.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Gaps are listed in the harnesses and verifiers
READMEs; picking one up is the most useful contribution.

## Maintainers

This repository is maintained by the [Unitary Foundation](https://unitary.foundation).
Per-directory maintainers may be listed here as the project grows.

## Citing

Cite the paper:

```bibtex
@misc{Li2026Perspective,
  title         = {Perspective on {AI} and quantum open-source software},
  author        = {Li, Changhao and Chase, Bradley A. and Vijayakumar, Veena and
                   Rennela, Mathys and Cosentino, Alessandro and Guo, Naixu and
                   Hassinger, Sebastian and Labib, Farrokh and Omonije, Seun and
                   Rebentrost, Patrick and Russo, Vincent and Shammah, Nathan and
                   Zeng, William J. and Castanon, Ben},
  year          = {2026},
  eprint        = {2610.38049},
  archivePrefix = {arXiv},
  primaryClass  = {quant-ph}
}
```

To cite the repository itself, use the Attribution in [LICENSING.md](LICENSING.md).

## License

Copyright 2026 Unitary Foundation. Documents and data are under
[CC BY 4.0](LICENSE), the policy templates in [`standards/`](standards/) are under
CC0 1.0 so they can be copied without attribution, and the code in
[`analysis/`](analysis/) is under Apache-2.0. [LICENSING.md](LICENSING.md) gives
the breakdown and what these licenses do not cover.
