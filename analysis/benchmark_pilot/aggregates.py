#!/usr/bin/env python
# Copyright 2026 Unitary Foundation
# SPDX-License-Identifier: Apache-2.0
"""Aggregate the per-task tables into the two files that are published.

The per-task lists (out/tasks.csv, out/task_scoring.csv) name contributors'
repositories and pull requests and are not published. What is published is the stage
count per year and the size distribution of the reference solutions.

Output: out/task_pipeline_by_year.csv, out/task_solution_size.csv
"""
import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out  # noqa: E402

# Repository names change, and GitHub keeps the old path working through a redirect, so
# the bounty sheets carry both spellings. Resolved against github.com on 2026-10-19,
# where a 301 gives the current name.
REPO_RENAMES = {
    'CQCL/guppylang': 'Quantinuum/guppylang',
    'CQCL/hugr': 'Quantinuum/hugr',
    'CQCL/lambeq': 'Quantinuum/lambeq',
    'MSRudolph/PauliPropagation.jl': 'SparqleSim/PauliPropagation.jl',
    'Qiskit-Partners/qiskit-ionq': 'qiskit-community/qiskit-ionq',
    'Qiskit/qiskit-terra': 'Qiskit/qiskit',
    'QuEraComputing/bloqade-python': 'QuEraComputing/bloqade-analog',
    'Quantomatic/zxlive': 'zxcalc/zxlive',
    'UCL-CCS/symmer': 'qmatter-labs/symmer',
    'aarontrowbridge/NamedTrajectories.jl': 'harmoniqs/NamedTrajectories.jl',
    'aarontrowbridge/QuantumCollocation.jl': 'harmoniqs/QuantumCollocation.jl',
    'goodchemistryco/Tangelo': 'sandbox-quantum/Tangelo',
    'harmoniqs/Stretto.jl': 'harmoniqs/Legato.jl',
    'ionq/ionq-core-python': 'ionq/ionq-core',
    'microsoft/qsharp': 'microsoft/qdk',
    'pasqal-io/PyQ': 'pasqal-io/pyqtorch',
    'qiskit-community/qiskit-braket-provider': 'amazon-braket/qiskit-braket-provider',
    'sg495/pauliopt': 'hashberg-io/pauliopt',
    'unitaryfund/metriq-app': 'unitaryfoundation/metriq-app',
    'unitaryfund/metriq-client': 'unitaryfoundation/metriq-client',
    'unitaryfund/mitiq': 'unitaryfoundation/mitiq',
    'unitaryfund/pyqrack': 'unitaryfoundation/pyqrack',
    'unitaryfund/qrack': 'unitaryfoundation/qrack',
    'vm6502q/pyqrack': 'unitaryfoundation/pyqrack',
    'zapatacomputing/orquestra-core': 'zapata-engineering/orquestra-core',
}


def canon_repo(name):
    return REPO_RENAMES.get(name, name).lower()


def distinct_issues(rows):
    """One row per issue, keyed on current repository name and issue number.

    The organizers list an issue twice in a year often enough to matter, and carry some
    into the next year, so the sheets hold repeated bounties on one issue. A task count
    has to collapse those; a bounty count must not. Each issue is attributed to the
    first year it was offered.
    """
    groups = {}
    for r in rows:
        if not r.get("repo"):
            continue
        groups.setdefault((canon_repo(r["repo"]), r["number"]), []).append(r)
    return [sorted(v, key=lambda x: x["year"])[0] for v in groups.values()]


OUT = out("benchmark_pilot")

tasks = list(csv.DictReader(open(OUT / "tasks.csv")))
scoring = list(csv.DictReader(open(OUT / "task_scoring.csv")))

years = sorted({t["year"] for t in tasks if t["year"]})

# bounties_listed counts bounties, because a twice-listed issue did carry two bounties.
# Every stage after it counts distinct issues.
closed = distinct_issues([t for t in tasks if t["state"] == "closed"])
merged = distinct_issues([t for t in tasks if t["merged_prs"] not in ("", "0")])
usable = distinct_issues([t for t in tasks if t["usable_as_task"] == "yes"])
scored = distinct_issues(scoring)

with open(OUT / "task_pipeline_by_year.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["year", "bounties_listed", "issue_closed", "closed_by_merged_pr",
                "usable_as_task", "solution_changes_tests", "solution_source_only",
                "solution_docs_only"])
    for y in years:
        kinds = Counter(r["solution_kind"] for r in scored if r["year"] == y)
        w.writerow([y, sum(1 for t in tasks if t["year"] == y),
                    sum(1 for t in closed if t["year"] == y),
                    sum(1 for t in merged if t["year"] == y),
                    sum(1 for t in usable if t["year"] == y),
                    kinds["changes tests"], kinds["source only, no test"],
                    kinds["documentation only"]])

sizes = sorted(int(t["lines_changed"]) for t in usable if t["lines_changed"])
with open(OUT / "task_solution_size.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["statistic", "lines_changed"])
    w.writerow(["n", len(sizes)])
    for name, q in (("p25", 0.25), ("median", 0.5), ("p75", 0.75), ("p90", 0.9)):
        w.writerow([name, sizes[int(q * len(sizes))]])

print(f"{len(tasks)} bounties over {len(distinct_issues(tasks))} distinct issues, "
      f"{len(sizes)} usable, median {sizes[len(sizes) // 2]} lines")
print(f"wrote {OUT}/task_pipeline_by_year.csv, task_solution_size.csv")
