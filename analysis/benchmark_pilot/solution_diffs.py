#!/usr/bin/env python
# Copyright 2026 Unitary Foundation
# SPDX-License-Identifier: Apache-2.0
"""Do the reference solutions touch tests?

For a task to be scored automatically, the merged change needs a test the harness can
run. This records the file list of each solution pull request and classifies it: does it
add or change test files, only source, or only documentation.

Batched GraphQL `query` operations, about 20 pull requests per request. Read-only, no
mutation. Cached in out/pr_files.jsonl.

Run:  zsh -i -c 'python3 benchmark_pilot/solution_diffs.py'
Output: out/task_scoring.csv
"""
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out  # noqa: E402

OUT = out("benchmark_pilot")
CACHE = OUT / "pr_files.jsonl"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
BATCH = 20

TEST = re.compile(r"(^|/)tests?/|(^|/)test_[^/]+$|_test\.[a-z]+$|"
                  r"(^|/)spec/|\.test\.[a-z]+$|conftest\.py$", re.I)
DOC = re.compile(r"\.(md|rst|txt|ipynb)$|(^|/)docs?/|(^|/)examples?/", re.I)
PRURL = re.compile(r"github\.com/([\w.-]+)/([\w.-]+)/pull/(\d+)")


def graphql(query):
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body, method="POST",
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Content-Type": "application/json",
                 "User-Agent": "ai4qoss-analysis"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                time.sleep(int(e.headers.get("Retry-After", 60)))
                continue
            return {"errors": [{"message": f"http {e.code}"}]}
        except (urllib.error.URLError, TimeoutError):
            time.sleep(3 * (attempt + 1))
    return {"errors": [{"message": "unreachable"}]}


def classify(paths):
    if not paths:
        return "no file list"
    has_test = any(TEST.search(p) for p in paths)
    non_doc = [p for p in paths if not DOC.search(p)]
    if has_test:
        return "changes tests"
    if not non_doc:
        return "documentation only"
    return "source only, no test"


def main():
    if not TOKEN:
        print("no GITHUB_TOKEN", file=sys.stderr)
        return 1

    cached = {}
    if CACHE.exists():
        for line in CACHE.open():
            d = json.loads(line)
            cached[d["url"]] = d["files"]
    print(f"{len(cached)} pull requests cached")

    with open(OUT / "tasks.csv") as f:
        tasks = [r for r in csv.DictReader(f) if r["usable_as_task"] == "yes"]
    todo = [t for t in tasks if t["solution_pr"] and t["solution_pr"] not in cached]
    print(f"{len(tasks)} usable tasks, {len(todo)} pull requests to fetch")

    with CACHE.open("a") as cf:
        for start in range(0, len(todo), BATCH):
            chunk = todo[start:start + BATCH]
            parts = []
            for i, t in enumerate(chunk):
                m = PRURL.search(t["solution_pr"])
                if not m:
                    continue
                owner, name, number = m.groups()
                parts.append(
                    f'p{i}: repository(owner: "{owner}", name: "{name}") '
                    f'{{ pullRequest(number: {number}) {{ '
                    f'files(first: 100) {{ nodes {{ path additions deletions }} }} }} }}')
            if not parts:
                continue
            data = graphql("query {\n" + "\n".join(parts) + "\n}")
            for i, t in enumerate(chunk):
                node = ((data.get("data") or {}).get(f"p{i}") or {}).get("pullRequest")
                files = [n["path"] for n in
                         (((node or {}).get("files") or {}).get("nodes") or [])]
                cached[t["solution_pr"]] = files
                cf.write(json.dumps({"url": t["solution_pr"], "files": files}) + "\n")
            cf.flush()
            print(f"  {min(start + BATCH, len(todo))}/{len(todo)}", flush=True)
            time.sleep(0.6)

    rows, tally, per_year = [], Counter(), {}
    for t in tasks:
        files = cached.get(t["solution_pr"], [])
        kind = classify(files)
        tally[kind] += 1
        y = t["year"]
        per_year.setdefault(y, Counter())[kind] += 1
        rows.append([t["year"], t["repo"], t["number"], t["issue_body_chars"],
                     t["files_changed"], t["lines_changed"], len(files), kind,
                     t["solution_pr"], t["issue_url"]])

    with open(OUT / "task_scoring.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "repo", "number", "issue_body_chars", "files_changed",
                    "lines_changed", "files_seen", "solution_kind", "solution_pr",
                    "issue_url"])
        w.writerows(rows)

    print(f"\nreference solutions, {len(tasks)} tasks")
    for k, n in tally.most_common():
        print(f"  {n:>4}  {k}  ({100 * n / len(tasks):.0f}%)")
    print("\nchanges tests, by year")
    for y in sorted(per_year):
        c = per_year[y]
        tot = sum(c.values())
        print(f"  {y}: {c['changes tests']:>3} of {tot:>3} "
              f"({100 * c['changes tests'] / tot:.0f}%)")
    print(f"\nwrote {OUT}/task_scoring.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
