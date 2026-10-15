#!/usr/bin/env python
# Copyright 2026 Unitary Foundation
# SPDX-License-Identifier: Apache-2.0
"""Audit everything staged for the public repository before it is committed.

Checks each published CSV for material that identifies a person: email addresses,
@handles, and the owner segment of any GitHub URL or `owner/repo` slug, since an owner
may be a personal account rather than an organization. Prints findings and never the
surrounding cell content beyond what is needed to locate the column.
"""
import csv
import re
import sys
from collections import Counter
from pathlib import Path

DEST = Path(__file__).resolve().parents[1] / "data" / "figures"

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
HANDLE = re.compile(r"(?<![\w/])@[A-Za-z0-9][A-Za-z0-9-]{2,}")
GH_URL = re.compile(r"github\.com/([\w.-]+)/([\w.-]+)")
SLUG = re.compile(r"^([\w.-]+)/([\w.-]+)$")

findings = 0
owners = Counter()

for path in sorted(DEST.glob("*.csv")):
    rows = list(csv.reader(open(path)))
    if not rows:
        continue
    header = rows[0]
    per_col = Counter()
    mail = handle = 0
    for r in rows[1:]:
        for i, v in enumerate(r):
            if not isinstance(v, str) or not v:
                continue
            if EMAIL.search(v):
                mail += 1
                per_col[header[i] if i < len(header) else i] += 1
            if HANDLE.search(v):
                handle += 1
            for m in GH_URL.finditer(v):
                owners[m.group(1)] += 1
                per_col[f"{header[i]} (github url)"] += 1
            m = SLUG.match(v)
            if m and "/" in v and not v.startswith("http"):
                owners[m.group(1)] += 1
                per_col[f"{header[i]} (owner/repo)"] += 1

    flags = []
    if mail:
        flags.append(f"{mail} email-shaped values")
    if handle:
        flags.append(f"{handle} @handles")
    url_cols = {k: v for k, v in per_col.items() if "github url" in k or "owner/repo" in k}
    if url_cols:
        flags.append("account names in " + ", ".join(sorted(url_cols)))
    status = "; ".join(flags) if flags else "no identifying material"
    print(f"{path.name:<44}{len(rows)-1:>5} rows   {status}")
    findings += len(flags)

if owners:
    print(f"\naccount names appearing in the published files: {len(owners)} distinct")
    print("these are GitHub owners, which may be personal accounts:")
    for name, n in owners.most_common(12):
        print(f"  {n:>5}  {name}")
    if len(owners) > 12:
        print(f"  ... and {len(owners) - 12} more")

print(f"\n{findings} file-level finding(s)" if findings
      else "\nclean: no identifying material in any published file")
sys.exit(0)
