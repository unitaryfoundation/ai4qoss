#!/usr/bin/env python
# Copyright 2026 Unitary Foundation
# SPDX-License-Identifier: Apache-2.0
"""Re-check the source records and the clean copy for identifying material.

Run after any change to the sources. Reports counts and column names only; it never
prints a cell's contents, so the audit itself cannot leak what it is looking for.
"""
import csv, glob, os, re, sys
from pathlib import Path
from numbers_parser import Document

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out, private  # noqa: E402

SRC = private(
    "unitaryHackData",
    "It is the unitaryHACK organizers' own bounty sheets and post-event "
    "surveys, which are not public.",
)
CLEAN = out("unitaryhack/clean")

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
HANDLE = re.compile(r"(?<![\w/])@[A-Za-z0-9][A-Za-z0-9-]{2,}")
NAMEY = re.compile(r"submitter|e-?mail|pronoun|country|handle|twitter|discord|"
                   r"linkedin|phone|address", re.I)

def tables():
    for p in sorted(glob.glob(str(SRC / "*" / "*.numbers"))):
        d = Document(p)
        for sh in d.sheets:
            for t in sh.tables:
                yield "source", p, t.name, t.rows(values_only=True)
    for p in sorted(glob.glob(str(SRC / "*" / "*.csv"))):
        with open(p, encoding="utf-8-sig") as f:
            yield "source", p, Path(p).stem, list(csv.reader(f))
    for p in sorted(glob.glob(str(CLEAN / "*.csv"))):
        with open(p) as f:
            yield "clean", p, Path(p).stem, list(csv.reader(f))

findings = 0
for origin, path, tname, rows in tables():
    if not rows:
        continue
    label = f"{origin}:{Path(path).parent.name}/{Path(path).name}"
    hdr = [str(h or "") for h in rows[0]]
    for i, h in enumerate(hdr):
        if h and NAMEY.search(h):
            n = sum(1 for r in rows[1:] if i < len(r) and r[i] not in (None, ""))
            if n:
                print(f"  {label}: column {h!r} has {n} values"); findings += 1
    mails = handles = 0
    for r in rows[1:]:
        for v in r:
            if isinstance(v, str):
                mails += len(EMAIL.findall(v))
                handles += len(HANDLE.findall(v))
    if mails:
        print(f"  {label}: {mails} email-shaped strings"); findings += 1
    if handles:
        print(f"  {label}: {handles} @handles"); findings += 1
    if re.search(r"'s view|[A-Z][a-z]+'s ", tname):
        print(f"  {label}: table name may carry a person: {tname!r}"); findings += 1

print(f"\n{findings} finding(s)" if findings else "\nclean: no identifying material found")
sys.exit(0)
