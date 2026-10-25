#!/usr/bin/env python
# Copyright 2026 Unitary Foundation
# SPDX-License-Identifier: Apache-2.0
"""Scripted change-scope features of each candidate task's reference pull request.

For every task of the 417-task cohort this records the number of changed files, lines
added and deleted, whether a test file is among them, and the programming languages of
the changed files, read from the complete file list of the reference pull request.
These features involve no judgment; the semantic labels are in characterize.py's input.

File and line counts and languages use the complete file list. Whether a solution
changes a test file follows the convention of solution_diffs.py, which looked at the
first 100 files of each pull request, so that the count agrees with the published
275. One 223-file solution changes test files only beyond its first 100; counted over
complete lists the figure would be 276.

Test files are recognized by path with the same expression as solution_diffs.py,
without opening the file, so a listed test need not exercise the change. Languages are
inferred from file extensions; prose, configuration and data files are not counted as
languages.

Inputs, unpublished (they name issues and pull requests), under the working directory:
  benchmark_characterization/cohort.csv     task_id, year, solution_pr, pr_shared_by_tasks,
                                             n_closing_prs, n_merged_closing_prs,
                                             reference_pr_repository (host, same owner, other owner),
                                             reference_pr_base_branch (default, renamed default,
                                             development/release, feature/event, unknown)
  benchmark_characterization/pr_files.jsonl one record per reference pull request:
                                             url, status (ok, pr_404_now, pr_empty),
                                             changedFiles, additions, deletions, paths
Output: benchmark_characterization/task_scope.csv beside the inputs, which
characterize.py reads.
"""
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import private  # noqa: E402

# Same expressions as benchmark_pilot/solution_diffs.py.
TEST = re.compile(r"(^|/)tests?/|(^|/)test_[^/]+$|_test\.[a-z]+$|"
                  r"(^|/)spec/|\.test\.[a-z]+$|conftest\.py$", re.I)
DOC = re.compile(r"\.(md|rst|txt|ipynb)$|(^|/)docs?/|(^|/)examples?/", re.I)

LANG = {".py": "Python", ".pyi": "Python", ".pyx": "Python", ".ipynb": "Jupyter notebook",
        ".rs": "Rust", ".jl": "Julia", ".cpp": "C++", ".cc": "C++", ".cxx": "C++", ".hpp": "C++",
        ".h": "C/C++ header", ".c": "C", ".cu": "CUDA", ".js": "JavaScript", ".jsx": "JavaScript",
        ".ts": "TypeScript", ".tsx": "TypeScript", ".mjs": "JavaScript", ".vue": "Vue",
        ".html": "HTML", ".css": "CSS", ".scss": "CSS", ".qs": "Q#", ".qasm": "OpenQASM",
        ".mlir": "MLIR", ".td": "MLIR", ".go": "Go", ".java": "Java", ".kt": "Kotlin",
        ".hs": "Haskell", ".ml": "OCaml", ".lean": "Lean", ".m": "MATLAB/Mathematica", ".wl": "Mathematica",
        ".r": "R", ".sh": "Shell", ".cmake": "CMake", ".tex": "TeX", ".hat": "H-hat",
        ".md": "Markdown", ".rst": "reStructuredText", ".toml": "config", ".yml": "config",
        ".yaml": "config", ".cfg": "config", ".ini": "config", ".json": "data/config", ".txt": "text",
        ".lym": "KLayout macro"}
PROSE_CFG = {"Markdown", "reStructuredText", "config", "data/config", "text"}


def lang_of(path):
    name = path.rsplit("/", 1)[-1]
    if name in ("CMakeLists.txt",):
        return "CMake"
    if name in ("Dockerfile",):
        return "config"
    ext = ("." + name.rsplit(".", 1)[-1].lower()) if "." in name else ""
    return LANG.get(ext, "other")



# solution_diffs.py requested files(first: 100); the test flag keeps that convention.
FIRST_N = 100


def main():
    src = private("benchmark_characterization",
                  "The cohort list and reference pull request file lists of the unitaryHACK "
                  "candidate tasks, which name issues and pull requests.")
    cohort = list(csv.DictReader(open(src / "cohort.csv")))
    prs = {}
    for line in open(src / "pr_files.jsonl"):
        d = json.loads(line)
        prs[d["url"]] = d
    rows = []
    for t in cohort:
        pr = prs[t["solution_pr"]]
        paths = pr["paths"]
        langs = Counter(lang_of(p) for p in paths)
        rows.append({
            "task_id": t["task_id"], "year": t["year"], "pr_status": pr["status"],
            "files_changed": pr["changedFiles"], "additions": pr["additions"],
            "deletions": pr["deletions"],
            "lines_changed": (pr["additions"] + pr["deletions"]
                              if pr["additions"] is not None else pr.get("lines_changed")),
            "changes_test_files": int(any(TEST.search(p) for p in paths[:FIRST_N])),
            "documentation_only": int(bool(paths) and all(DOC.search(p) for p in paths)),
            "code_languages": ";".join(sorted(l for l in langs
                                              if l not in PROSE_CFG and l != "other")),
            "n_test_files": sum(1 for p in paths if TEST.search(p)),
            "pr_shared_by_tasks": t["pr_shared_by_tasks"],
            "n_closing_prs": t["n_closing_prs"],
            "n_merged_closing_prs": t["n_merged_closing_prs"],
            "reference_pr_repository": t["reference_pr_repository"],
            "reference_pr_base_branch": t["reference_pr_base_branch"],
        })
    with open(src / "task_scope.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} tasks, {sum(r['changes_test_files'] for r in rows)} change a test file")


if __name__ == "__main__":
    main()
