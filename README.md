# ai4qoss

AI for quantum open-source software: community standards, harness recipes, verification
tools, and benchmarks.

This repository accompanies a perspective paper in preparation by the quantum open-source
software (QOSS) community; a link will be added when the preprint is posted. The paper is
a fixed snapshot. This repository holds the parts that change: policies, tool catalogs,
harness recipes, benchmark tasks, and data. The paper will cite a tagged release, so the
citation stays stable while the content moves on.

## Layout

| Directory | Contents |
|---|---|
| [`standards/`](standards/) | Policy templates repos can copy: what a contribution must state, AI disclosure and review, agent boundaries, an AGENTS.md template, CI gate examples |
| [`harnesses/`](harnesses/) | Designs for agent harnesses a project could build: the task, the loop, the check the loop relies on, and the guardrails. Cards, not code |
| [`verifiers/`](verifiers/) | Catalog of verification tools for quantum artifacts, with scope, cost, maturity, and open gaps |
| [`benchmarks/`](benchmarks/) | Task format, collection method, and stage counts for tasks built from real QOSS work; the task list itself is not published |
| [`data/`](data/) | Datasets behind the paper's figures, with the re-measurement schedule |
| [`reading/`](reading/) | Reading list, one line per entry |

## Conventions

- Every content page carries a `Last verified:` date, so stale content is visible.
- Contributions arrive as pull requests and follow the repository's own
  [AI contribution policy](standards/ai-contribution-policy.md).
- Releases are tagged and dated. Cite a specific release; the default branch carries the
  latest content.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Gaps are listed in the harnesses and verifiers
READMEs; picking one up is the most useful contribution.

## Maintainers

This repository is maintained by the [Unitary Foundation](https://unitary.foundation).
Per-directory maintainers may be listed here as the project grows.

## Citing

A `CITATION.cff` will be added with the first tagged release.

## License

Under discussion (suggested: CC BY 4.0 for documents, Apache 2.0 for code).
