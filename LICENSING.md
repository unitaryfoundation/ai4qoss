# Licensing

Copyright 2026 Unitary Foundation.

Three licenses, chosen by what the material is. Each directory that differs from
the repository default carries its own `LICENSE` file.

| Material | License | Why |
|---|---|---|
| `README.md`, `CONTRIBUTING.md`, `AI_use_this_repository.md` | CC BY 4.0 | Original prose |
| `reading/`, `verifiers/`, `harnesses/`, `benchmarks/` | CC BY 4.0 | Original prose |
| `data/` | CC BY 4.0 | Cite the repository when reusing the figure data |
| `standards/` | CC0 1.0 | Templates meant to be copied into other projects |
| `analysis/` | Apache-2.0 | Code |

`standards/` is CC0 because the point of a policy template is that a project
copies it into its own `CONTRIBUTING` and adapts it. Under CC BY an adopting
project would have to carry our attribution inside its own policy, which works
against being adopted. Copying a template and dropping the credit is what we want
to happen.

The `analysis/` scripts carry an SPDX header naming the license and the
copyright holder, so a script stays identifiable after it is copied out of the
repository, and that header is the attribution Apache-2.0 asks redistributors to
retain. We ship no `NOTICE` file, because one is optional under the license and
would put a further obligation on anyone reusing the code.

## Attribution

For the CC BY 4.0 material, this is enough:

> Unitary Foundation, ai4qoss, https://github.com/unitaryfoundation/ai4qoss,
> licensed under CC BY 4.0.

That covers what Section 3(a)(1) of the license asks for: the creator, a link to
the material, and a notice naming the license.

## What these licenses do not cover

External work quoted or linked from these pages stays under its own terms. The
catalog entries, reading list, and harness cards describe and cite other
people's tools and papers; our license covers our description of them and
nothing else.

Some pages reproduce short excerpts of third-party policy and documentation text
for comparison, which we take as fair use and which remains the property of the
projects named at the point of use.

The benchmark task list is not published here. Its issue text and patches belong
to the contributors and projects that wrote them, and any future release needs a
license review across the repositories involved rather than a blanket grant from
us.

Last verified: 2026-10-15
