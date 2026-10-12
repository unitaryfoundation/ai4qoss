#!/usr/bin/env python
"""Resolve each unitaryHACK bounty to its issue state and the work that closed it.

Input is the organizers' own bounty list (812 URLs over 2022 to 2026, normalized by
unitaryhack/bounties.py), which is more complete than searching GitHub labels: labels
found 87 of the 165 bounties the site reports closed for 2026, because projects tag
them inconsistently.

For each bounty this records whether the issue is closed, and what closed it: a linked
pull request, or a commit. That pairing is what a benchmark task needs, the issue text
as the prompt and the merged change as the reference solution.

Read-only. Every call is a GET against the issues, pulls and timeline endpoints; the
token is a fine-grained public-repositories read-only credential and cannot write.

Responses are cached in out/resolved.jsonl, so re-running costs nothing for bounties
already seen and the scoring can be revised without refetching.

Run:  zsh -i -c 'python3 benchmark_pilot/resolve_bounties.py'
Output: out/resolved.jsonl, out/tasks.csv
"""
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out  # noqa: E402

OUT = out("benchmark_pilot")
BOUNTIES = out("unitaryhack") / "bounties_long.csv"
CACHE = OUT / "resolved.jsonl"

TOKEN = os.environ.get("GITHUB_TOKEN", "")
URLPAT = re.compile(r"github\.com/([\w.-]+)/([\w.-]+)/(issues|pull)/(\d+)")


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
                wait = int(e.headers.get("Retry-After", 60))
                print(f"    rate limited, waiting {wait}s", file=sys.stderr, flush=True)
                time.sleep(wait)
                continue
            if e.code in (404, 410):
                return None          # deleted, moved, or private now
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(3 * (attempt + 1))
    return None


def closers(owner, repo, number):
    """Pull requests and commits that closed this issue, from its timeline."""
    prs, commits = [], []
    tl = api(f"https://api.github.com/repos/{owner}/{repo}/issues/{number}"
             f"/timeline?per_page=100")
    for ev in (tl or []):
        name = ev.get("event")
        src = (ev.get("source") or {}).get("issue") or {}
        if name in ("cross-referenced", "connected") and src.get("pull_request"):
            prs.append(src.get("html_url"))
        if name == "closed":
            if ev.get("commit_id"):
                commits.append(ev["commit_id"])
            # a PR that closes an issue shows up as a closed event with a source
            if src.get("pull_request"):
                prs.append(src.get("html_url"))
    return sorted(set(p for p in prs if p)), sorted(set(commits))


def main():
    if not TOKEN:
        print("no GITHUB_TOKEN in environment", file=sys.stderr)
        return 1

    seen = {}
    if CACHE.exists():
        for line in CACHE.open():
            d = json.loads(line)
            seen[d["url"]] = d
    print(f"{len(seen)} bounties already cached")

    with open(BOUNTIES) as f:
        bounties = [r for r in csv.DictReader(f) if r["url"].strip()]

    todo = [b for b in bounties if b["url"] not in seen]
    print(f"{len(bounties)} bounties total, {len(todo)} to fetch")

    with CACHE.open("a") as cache:
        for i, b in enumerate(todo, 1):
            m = URLPAT.search(b["url"])
            rec = {"url": b["url"], "year": b["year"], "project": b["project"],
                   "amount": b["amount_usd"]}
            if not m:
                rec["status"] = "unparseable url"
            else:
                owner, repo, kind, number = m.groups()
                rec.update(repo=f"{owner}/{repo}", number=int(number), kind=kind)
                d = api(f"https://api.github.com/repos/{owner}/{repo}/issues/{number}")
                if d is None:
                    rec["status"] = "not retrievable"
                else:
                    rec.update(status=d.get("state"),
                               closed_at=(d.get("closed_at") or "")[:10],
                               created_at=(d.get("created_at") or "")[:10],
                               title_chars=len(d.get("title") or ""),
                               body_chars=len(d.get("body") or ""),
                               labels=[l["name"] for l in d.get("labels", [])],
                               is_pr=bool(d.get("pull_request")))
                    if d.get("state") == "closed" and not d.get("pull_request"):
                        prs, commits = closers(owner, repo, number)
                        rec["closing_prs"] = prs
                        rec["closing_commits"] = commits
            cache.write(json.dumps(rec) + "\n")
            cache.flush()
            seen[rec["url"]] = rec
            if i % 25 == 0:
                print(f"  {i}/{len(todo)}", flush=True)
            time.sleep(0.12)

    # ------------------------------------------------------------------ scoring
    rows, tally = [], Counter()
    for b in bounties:
        r = seen.get(b["url"], {})
        prs = r.get("closing_prs") or []
        state = r.get("status", "")
        usable = bool(state == "closed" and prs and not r.get("is_pr"))
        tally[state] += 1
        if usable:
            tally["usable as a task"] += 1
        rows.append([r.get("year", b["year"]), r.get("repo", ""), r.get("number", ""),
                     state, r.get("closed_at", ""), r.get("body_chars", ""),
                     len(prs), prs[0] if prs else "",
                     "yes" if usable else "no", b["url"]])

    with open(OUT / "tasks.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "repo", "number", "state", "closed_at", "body_chars",
                    "closing_prs", "first_pr", "usable_as_task", "url"])
        w.writerows(sorted(rows, key=lambda r: (str(r[0]), str(r[1]), str(r[2]))))

    print("\nbounty resolution")
    for k, n in tally.most_common():
        print(f"  {n:>4}  {k}")
    per_year = Counter(r[0] for r in rows if r[8] == "yes")
    print("\nusable tasks by year")
    for y in sorted(per_year):
        total = sum(1 for r in rows if str(r[0]) == str(y))
        print(f"  {y}: {per_year[y]:>3} of {total}")
    print(f"\nwrote {OUT}/tasks.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
