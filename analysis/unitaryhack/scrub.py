#!/usr/bin/env python
# Copyright 2026 Unitary Foundation
# SPDX-License-Identifier: Apache-2.0
"""Make a de-identified working copy of the unitaryHACK records.

The source files under ../unitaryHackData are the organizers' own exports and are
left untouched. This writes CSV copies into ./clean with identifying material
removed, and every later script in this directory reads only those copies, so no
analysis can reach the personal data even by accident.

What is dropped or masked, and why it was present: the surveys were already
de-identified by hand, but the 2022 bounty sheet still carries a submitter name on
every row and 17 email addresses, the 2022 exit survey carries pronouns and country
for 3 respondents, and free-text cells across years mention contributors by GitHub
handle. Column names that denote a person are dropped whole; email addresses and
@handles are masked inside surviving free text.

Run:  python3 unitaryhack/scrub.py
"""
import csv
import glob
import os
import re
import sys
from pathlib import Path

from numbers_parser import Document

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out, private  # noqa: E402

SRC = private(
    "unitaryHackData",
    "It is the unitaryHACK organizers' own bounty sheets and post-event "
    "surveys, which are not public.",
)
OUT = out("unitaryhack/clean")

# Whole columns that identify a person or describe them demographically.
DROP_COLS = re.compile(
    r"^(submitter|submitter email|pronouns|other pronouns|country|"
    r"send email\?.*|name \(from participating projects\))$", re.I)

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
HANDLE = re.compile(r"(?<![\w/])@[A-Za-z0-9][A-Za-z0-9-]{2,}")


def mask(value):
    if not isinstance(value, str):
        return value
    value = EMAIL.sub("[email]", value)
    value = HANDLE.sub("[handle]", value)
    return value


def load(path):
    if path.endswith(".csv"):
        with open(path, encoding="utf-8-sig") as f:
            return list(csv.reader(f))
    doc = Document(path)
    table = doc.sheets[0].tables[0]
    return table.rows(values_only=True)


def slug(name):
    name = name.lower().replace("'s", "").replace("-grid view", "")
    name = name.replace("-responses", "").replace("-veena view", "")
    return re.sub(r"[^a-z0-9]+", "_", name).strip("_")


def main():
    dropped_cols, masked_cells, files = 0, 0, 0
    for path in sorted(glob.glob(str(SRC / "*" / "*.numbers")) +
                       glob.glob(str(SRC / "*" / "*.csv"))):
        year = Path(path).parent.name.replace("unitaryHack", "")
        kind = slug(Path(path).stem)
        rows = load(path)
        if not rows:
            continue
        hdr = [str(h) if h is not None else "" for h in rows[0]]
        keep = [i for i, h in enumerate(hdr) if not DROP_COLS.match(h.strip())]
        dropped_cols += len(hdr) - len(keep)

        out_rows = []
        for r in rows[1:]:
            row = []
            for i in keep:
                v = r[i] if i < len(r) else None
                mv = mask(v)
                if isinstance(v, str) and mv != v:
                    masked_cells += 1
                row.append("" if mv is None else mv)
            if any(str(c).strip() for c in row):
                out_rows.append(row)

        dest = OUT / f"{year}_{kind}.csv"
        with open(dest, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow([hdr[i] for i in keep])
            w.writerows(out_rows)
        files += 1
        print(f"  {dest.name:<34} {len(out_rows):>3} rows, "
              f"{len(hdr) - len(keep)} column(s) dropped")

    print(f"\n{files} files, {dropped_cols} identifying columns dropped, "
          f"{masked_cells} cells masked")
    # Prove the copy is clean rather than asserting it.
    leaks = 0
    for p in OUT.glob("*.csv"):
        text = p.read_text()
        leaks += len(EMAIL.findall(text)) + len(HANDLE.findall(text))
    print(f"residual emails or handles in the clean copy: {leaks}")


if __name__ == "__main__":
    main()
