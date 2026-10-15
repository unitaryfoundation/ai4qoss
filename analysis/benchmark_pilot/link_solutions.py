#!/usr/bin/env python
# Copyright 2026 Unitary Foundation
# SPDX-License-Identifier: Apache-2.0
"""Second pass: find the change that closed each bounty issue.

The first pass only looked for `cross-referenced` and `connected` timeline events and
for a commit on the `closed` event, and found nothing across 671 closed issues. The
link is usually carried by a `referenced` event instead, and many issues are closed by
a commit rather than by a linked pull request. Both count as a reference solution: a
commit has a diff, which is what a benchmark task needs.

Timeline responses are cached in out/timelines.jsonl so the scoring can be revised
without refetching. Read-only: GET on the timeline endpoint.

Run:  zsh -i -c 'python3 benchmark_pilot/link_solutions.py'
Output: updates out/tasks.csv, writes out/timelines.jsonl
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out  # noqa: E402

OUT = out("benchmark_pilot")
RESOLVED = OUT / "resolved.jsonl"
TIMELINES = OUT / "timelines.jsonl"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

LINK_EVENTS = ("cross-referenced", "connected", "referenced", "closed", "merged")


def api(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai4qoss-analysis",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                time.sleep(int(e.headers.get("Retry-After", 60)))
                continue
            return {"_error": e.code}
        except (urllib.error.URLError, TimeoutError):
            time.sleep(3 * (attempt + 1))
    return {"_error": "unreachable"}


def extract(timeline):
    """Pull requests and commits that reference or close the issue."""
    prs, commits = set(), set()
    if not isinstance(timeline, list):
        return [], []
    for ev in timeline:
        name = ev.get("event")
        if name not in LINK_EVENTS:
            continue
        src = (ev.get("source") or {}).get("issue") or {}
        if src.get("pull_request"):
            prs.add(src.get("html_url"))
        if ev.get("commit_id"):
            commits.add(ev["commit_id"])
    return sorted(p for p in prs if p), sorted(commits)


def main():
    if not TOKEN:
        print("no GITHUB_TOKEN", file=sys.stderr)
        return 1

    cached = {}
    if TIMELINES.exists():
        for line in TIMELINES.open():
            d = json.loads(line)
            cached[d["key"]] = d["timeline"]
    print(f"{len(cached)} timelines cached")

    recs = [json.loads(l) for l in RESOLVED.open()]
    targets = [r for r in recs
               if r.get("status") == "closed" and not r.get("is_pr") and r.get("repo")]
    print(f"{len(targets)} closed issues to link")

    with TIMELINES.open("a") as tf:
        for i, r in enumerate(targets, 1):
            key = f"{r['repo']}#{r['number']}"
            if key not in cached:
                tl = api(f"https://api.github.com/repos/{r['repo']}/issues/"
                         f"{r['number']}/timeline?per_page=100")
                cached[key] = tl
                tf.write(json.dumps({"key": key, "timeline": tl}) + "\n")
                tf.flush()
                time.sleep(0.12)
                if i % 50 == 0:
                    print(f"  {i}/{len(targets)}", flush=True)
            prs, commits = extract(cached[key])
            r["closing_prs"], r["closing_commits"] = prs, commits

    with RESOLVED.open("w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")

    # ------------------------------------------------------------------ scoring
    rows, tally = [], Counter()
    for r in recs:
        prs = r.get("closing_prs") or []
        commits = r.get("closing_commits") or []
        state = r.get("status", "")
        has_solution = bool(state == "closed" and not r.get("is_pr")
                            and (prs or commits))
        # a task needs a prompt as well as a solution
        enough_text = (r.get("body_chars") or 0) >= 120
        usable = has_solution and enough_text
        tally[state] += 1
        if state == "closed" and not r.get("is_pr"):
            tally["closed issue"] += 1
            if prs:
                tally["  linked to a pull request"] += 1
            elif commits:
                tally["  closed by a commit only"] += 1
            else:
                tally["  no traceable change"] += 1
            if usable:
                tally["  usable as a task"] += 1
        rows.append([r.get("year"), r.get("repo", ""), r.get("number", ""), state,
                     r.get("closed_at", ""), r.get("body_chars", ""),
                     len(prs), len(commits), prs[0] if prs else "",
                     "yes" if usable else "no", r["url"]])

    with open(OUT / "tasks.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "repo", "number", "state", "closed_at", "body_chars",
                    "closing_prs", "closing_commits", "first_pr", "usable_as_task",
                    "url"])
        w.writerows(sorted(rows, key=lambda x: (str(x[0]), str(x[1]), str(x[2]))))

    print("\nresolution")
    for k, n in tally.most_common():
        print(f"  {n:>4}  {k}")

    print("\nusable tasks by year")
    for y in sorted({str(r[0]) for r in rows}):
        tot = sum(1 for r in rows if str(r[0]) == y)
        use = sum(1 for r in rows if str(r[0]) == y and r[9] == "yes")
        print(f"  {y}: {use:>3} of {tot:>3} bounties")
    print(f"\nwrote {OUT}/tasks.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
