#!/usr/bin/env python
"""Bring the bounty resolution forward without refetching everything.

Drops from out/resolved.jsonl the bounties that were still open, or not retrievable, at
the last run, so that resolve_bounties.py fetches only those again. Issues that were
already closed keep their cached record. Run the pipeline afterwards in order:

  zsh -i -c 'python3 benchmark_pilot/reresolve_open.py'
  zsh -i -c 'python3 benchmark_pilot/resolve_bounties.py'
  zsh -i -c 'python3 benchmark_pilot/link_graphql.py'      # needs a valid token: GraphQL
  zsh -i -c 'python3 benchmark_pilot/solution_diffs.py'    # has no unauthenticated form

A copy of the cache as it stood is written beside it with the date, in case the refetch
has to be undone.
"""
import json
import shutil
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out  # noqa: E402

OUT = out("benchmark_pilot")
CACHE = OUT / "resolved.jsonl"

recs = [json.loads(l) for l in CACHE.open() if l.strip()]
keep = [r for r in recs if r.get("status") not in ("open", "not retrievable")]
shutil.copy(CACHE, OUT / f"resolved_{date.today().isoformat()}.bak.jsonl")
CACHE.write_text("".join(json.dumps(r) + "\n" for r in keep))
print(f"{len(recs)} cached, {len(recs) - len(keep)} open or unretrievable dropped for "
      f"re-resolution, {len(keep)} kept")
