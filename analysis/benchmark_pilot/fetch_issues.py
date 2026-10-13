#!/usr/bin/env python
"""Collect the unitaryHACK 2026 issues from GitHub, for the benchmark pilot.

unitaryhack.dev publishes the rules, the 46 participating projects and aggregate
totals (85 participants closing 165 bounties for $17,870 in 2026), but no
machine-readable list of the bountied issues themselves. The issues are instead
discoverable through the labels the participating projects apply. There is no single
label: projects use `unitaryhack`, `unitaryhack-bounty`, `unitaryhack2026`, and
`unitary-hack` interchangeably, so all of them are queried and the results are
deduplicated by URL.

Coverage is reported rather than assumed. The site's own count of closed bounties is
the reference, and the gap between it and what the labels return is printed, since a
project that tagged its issues some other way is invisible here.

Reads GITHUB_TOKEN from the environment (search allows 30 requests per minute
authenticated). Run through an interactive shell if the token lives in ~/.zshrc:
  zsh -i -c 'python3 benchmark_pilot/fetch_issues.py'

Output: out/issues.jsonl (raw, one issue per line), out/issues.csv (summary)
"""
import csv
import json
import os
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
OUT.mkdir(parents=True, exist_ok=True)

LABELS = ["unitaryhack", "unitaryhack-bounty", "unitaryhack2026", "unitary-hack"]
YEAR = "2026"
EVENT_START, EVENT_END = "2026-06-03", "2026-06-17"   # from unitaryhack.dev/rules
SITE_CLOSED_BOUNTIES = 165                            # from unitaryhack.dev/leaderboard

TOKEN = os.environ.get("GITHUB_TOKEN", "")
PAUSE = 2.5      # search API: 30 requests per minute when authenticated


def api(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai4qoss-analysis",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                wait = int(e.headers.get("Retry-After", 60))
                print(f"    rate limited, waiting {wait}s", file=sys.stderr, flush=True)
                time.sleep(wait)
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"giving up on {url}")


def search_issues(query):
    """Every issue matching a search query, paged. The API caps a query at 1000."""
    page, seen = 1, []
    while True:
        q = urllib.parse.quote(query)
        d = api(f"https://api.github.com/search/issues?q={q}&per_page=100&page={page}")
        items = d.get("items", [])
        seen.extend(items)
        time.sleep(PAUSE)
        if len(items) < 100 or len(seen) >= min(d.get("total_count", 0), 1000):
            return seen, d.get("total_count", 0)
        page += 1


def main():
    if not TOKEN:
        print("no GITHUB_TOKEN in environment", file=sys.stderr)
        return 1

    issues = {}
    for label in LABELS:
        # Both windows: an issue can be tagged long before the event and closed during
        # it, or created for the event itself.
        for clause in (f"created:{YEAR}-01-01..{YEAR}-12-31",
                       f"closed:{YEAR}-01-01..{YEAR}-12-31"):
            items, total = search_issues(f'label:"{label}" is:issue {clause}')
            new = sum(1 for it in items if it["html_url"] not in issues)
            for it in items:
                issues[it["html_url"]] = it
            print(f"  label:{label:<20} {clause[:8]:<8} {total:>4} found, {new:>4} new")

    print(f"\n{len(issues)} distinct issues after deduplication")

    with open(OUT / "issues.jsonl", "w") as f:
        for it in issues.values():
            f.write(json.dumps(it) + "\n")

    rows = []
    for it in issues.values():
        repo = "/".join(it["repository_url"].split("/")[-2:])
        closed = (it.get("closed_at") or "")[:10]
        rows.append([repo, it["number"], it["title"], it["state"], closed,
                     it["created_at"][:10],
                     "yes" if EVENT_START <= closed <= "2026-07-15" else "no",
                     ";".join(l["name"] for l in it["labels"]),
                     len(it.get("body") or ""), it["html_url"]])
    rows.sort(key=lambda r: (r[0], r[1]))

    with open(OUT / "issues.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["repo", "number", "title", "state", "closed_at", "created_at",
                    "closed_in_event_window", "labels", "body_chars", "url"])
        w.writerows(rows)

    # ------------------------------------------------------------------ coverage
    closed_window = sum(1 for r in rows if r[6] == "yes")
    # GitHub owner and repository names are case-insensitive, so the same
    # repository can arrive under two spellings and inflate the count.
    repos = Counter(r[0].lower() for r in rows)
    print(f"\nclosed during the event window ({EVENT_START} to 2026-07-15): "
          f"{closed_window}")
    print(f"the site reports {SITE_CLOSED_BOUNTIES} closed bounties for 2026, so the "
          f"labels account for {100 * closed_window / SITE_CLOSED_BOUNTIES:.0f}% of them")
    print(f"{len(repos)} repositories, against 46 participating projects listed on the "
          f"site")
    print("\ntop repositories by issue count")
    for repo, n in repos.most_common(12):
        print(f"  {n:>3}  {repo}")
    print(f"\nwrote {OUT}/issues.jsonl, issues.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
