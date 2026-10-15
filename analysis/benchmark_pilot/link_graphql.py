#!/usr/bin/env python
# Copyright 2026 Unitary Foundation
# SPDX-License-Identifier: Apache-2.0
"""Third pass: ask GraphQL what actually closed each bounty issue.

The REST timeline cannot answer this. It never returns `cross-referenced` events, and
its `connected` events carry no reference to the pull request they connect to, so a
REST-only pass reported 448 of 671 closed issues as having no traceable change. GitHub
exposes the real relation only in GraphQL, as `ClosedEvent.closer` and
`closedByPullRequestsReferences`.

Read-only. GraphQL uses POST as its transport, but every operation here is a `query`;
there is no mutation anywhere in this file, and the token is a public-repositories
read-only credential that cannot write in any case.

Issues are batched by alias, about 25 per request, so the whole set costs roughly 27
requests instead of 671. Responses are cached in out/graphql.jsonl.

Run:  zsh -i -c 'python3 benchmark_pilot/link_graphql.py'
Output: updates out/tasks.csv
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
GQL_CACHE = OUT / "graphql.jsonl"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
BATCH = 25

FRAGMENT = """
fragment F on Issue {
  number
  url
  closedByPullRequestsReferences(first: 5, includeClosedPrs: true) {
    nodes { url merged mergedAt additions deletions changedFiles }
  }
  timelineItems(last: 40, itemTypes: [CLOSED_EVENT, CROSS_REFERENCED_EVENT]) {
    nodes {
      __typename
      ... on ClosedEvent {
        closer {
          __typename
          ... on PullRequest { url merged mergedAt additions deletions changedFiles }
          ... on Commit { oid }
        }
      }
      ... on CrossReferencedEvent {
        willCloseTarget
        source { __typename ... on PullRequest { url merged additions deletions changedFiles } }
      }
    }
  }
}
"""


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


def solutions(node):
    """Merged pull requests, then commits, that closed this issue."""
    prs, commits = {}, set()
    for pr in ((node.get("closedByPullRequestsReferences") or {}).get("nodes") or []):
        if pr and pr.get("url"):
            prs[pr["url"]] = pr
    for item in ((node.get("timelineItems") or {}).get("nodes") or []):
        if item.get("__typename") == "ClosedEvent":
            closer = item.get("closer") or {}
            if closer.get("__typename") == "PullRequest" and closer.get("url"):
                prs[closer["url"]] = closer
            elif closer.get("__typename") == "Commit" and closer.get("oid"):
                commits.add(closer["oid"])
        elif item.get("__typename") == "CrossReferencedEvent":
            src = item.get("source") or {}
            if src.get("__typename") == "PullRequest" and src.get("url") \
                    and item.get("willCloseTarget"):
                prs[src["url"]] = src
    return prs, sorted(commits)


def main():
    if not TOKEN:
        print("no GITHUB_TOKEN", file=sys.stderr)
        return 1

    cached = {}
    if GQL_CACHE.exists():
        for line in GQL_CACHE.open():
            d = json.loads(line)
            cached[d["key"]] = d["node"]
    print(f"{len(cached)} issues cached from GraphQL")

    recs = [json.loads(l) for l in RESOLVED.open()]
    targets, seen_keys = [], set()
    for r in recs:
        if r.get("status") != "closed" or r.get("is_pr") or not r.get("repo"):
            continue
        key = f"{r['repo']}#{r['number']}"
        if key in seen_keys or key in cached:
            continue
        seen_keys.add(key)
        targets.append((key, r["repo"], r["number"]))
    print(f"{len(targets)} to query, {len(targets) // BATCH + 1} requests")

    with GQL_CACHE.open("a") as cf:
        for start in range(0, len(targets), BATCH):
            chunk = targets[start:start + BATCH]
            parts = []
            for i, (key, repo, number) in enumerate(chunk):
                owner, name = repo.split("/", 1)
                parts.append(f'a{i}: repository(owner: "{owner}", name: "{name}") '
                             f'{{ issue(number: {number}) {{ ...F }} }}')
            data = graphql("query {\n" + "\n".join(parts) + "\n}\n" + FRAGMENT)
            if data.get("errors") and not data.get("data"):
                print(f"  batch {start // BATCH}: "
                      f"{data['errors'][0].get('message')}", file=sys.stderr)
            for i, (key, repo, number) in enumerate(chunk):
                node = ((data.get("data") or {}).get(f"a{i}") or {}).get("issue")
                cached[key] = node
                cf.write(json.dumps({"key": key, "node": node}) + "\n")
            cf.flush()
            print(f"  {min(start + BATCH, len(targets))}/{len(targets)}", flush=True)
            time.sleep(0.6)

    # ------------------------------------------------------------------ scoring
    rows, tally = [], Counter()
    for r in recs:
        key = f"{r.get('repo')}#{r.get('number')}"
        node = cached.get(key)
        prs, commits = solutions(node) if node else ({}, [])
        merged = [p for p in prs.values() if p.get("merged")]
        state = r.get("status", "")
        enough_text = (r.get("body_chars") or 0) >= 120
        usable = bool(state == "closed" and not r.get("is_pr") and merged and enough_text)
        tally[state] += 1
        if state == "closed" and not r.get("is_pr"):
            tally["closed issue"] += 1
            if merged:
                tally["  closed by a merged PR"] += 1
            elif prs:
                tally["  linked PR, not merged"] += 1
            elif commits:
                tally["  closed by a commit only"] += 1
            else:
                tally["  no traceable change"] += 1
            if usable:
                tally["  usable as a task"] += 1
        best = merged[0] if merged else None
        rows.append([r.get("year"), r.get("repo", ""), r.get("number", ""), state,
                     r.get("closed_at", ""), r.get("body_chars", ""),
                     len(merged), len(commits),
                     best["url"] if best else "",
                     best.get("changedFiles", "") if best else "",
                     (best.get("additions", 0) + best.get("deletions", 0)) if best else "",
                     "yes" if usable else "no", r["url"]])

    with open(OUT / "tasks.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "repo", "number", "state", "closed_at", "issue_body_chars",
                    "merged_prs", "closing_commits", "solution_pr", "files_changed",
                    "lines_changed", "usable_as_task", "issue_url"])
        w.writerows(sorted(rows, key=lambda x: (str(x[0]), str(x[1]), str(x[2]))))

    print("\nresolution")
    for k, n in tally.most_common():
        print(f"  {n:>4}  {k}")
    print("\nusable tasks by year")
    for y in sorted({str(r[0]) for r in rows}):
        tot = sum(1 for r in rows if str(r[0]) == y)
        use = sum(1 for r in rows if str(r[0]) == y and r[11] == "yes")
        print(f"  {y}: {use:>3} of {tot:>3} bounties  ({100 * use / tot:.0f}%)")
    sizes = sorted(r[10] for r in rows if r[11] == "yes" and r[10] != "")
    if sizes:
        print(f"\nreference solution size, lines changed: median "
              f"{sizes[len(sizes) // 2]}, quartiles {sizes[len(sizes) // 4]} to "
              f"{sizes[3 * len(sizes) // 4]}")
    print(f"\nwrote {OUT}/tasks.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
