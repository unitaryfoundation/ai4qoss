#!/usr/bin/env python
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

OUT = out("benchmark_pilot")

tasks = list(csv.DictReader(open(OUT / "tasks.csv")))
scoring = list(csv.DictReader(open(OUT / "task_scoring.csv")))

years = sorted({t["year"] for t in tasks if t["year"]})
with open(OUT / "task_pipeline_by_year.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["year", "bounties_listed", "issue_closed", "closed_by_merged_pr",
                "usable_as_task", "solution_changes_tests", "solution_source_only",
                "solution_docs_only"])
    for y in years:
        rows = [t for t in tasks if t["year"] == y]
        kinds = Counter(r["solution_kind"] for r in scoring if r["year"] == y)
        w.writerow([y, len(rows),
                    sum(1 for t in rows if t["state"] == "closed"),
                    sum(1 for t in rows if t["merged_prs"] not in ("", "0")),
                    sum(1 for t in rows if t["usable_as_task"] == "yes"),
                    kinds["changes tests"], kinds["source only, no test"],
                    kinds["documentation only"]])

sizes = sorted(int(t["lines_changed"]) for t in tasks
               if t["usable_as_task"] == "yes" and t["lines_changed"])
with open(OUT / "task_solution_size.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["statistic", "lines_changed"])
    w.writerow(["n", len(sizes)])
    for name, q in (("p25", 0.25), ("median", 0.5), ("p75", 0.75), ("p90", 0.9)):
        w.writerow([name, sizes[int(q * len(sizes))]])

print(f"{len(tasks)} bounties, {len(sizes)} usable, median {sizes[len(sizes) // 2]} lines")
print(f"wrote {OUT}/task_pipeline_by_year.csv, task_solution_size.csv")
