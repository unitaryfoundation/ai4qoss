#!/usr/bin/env python
# Copyright 2026 Unitary Foundation
# SPDX-License-Identifier: Apache-2.0
"""API churn: how often each project announces deprecations and breaking changes.

Method. Count entries in each project's own release notes, so the measure reflects
what maintainers themselves chose to announce. Sources:

  Qiskit     reno YAML  releasenotes/notes/<ver>/*.yaml   keys: deprecations, upgrade
  PennyLane  markdown   doc/releases/changelog-<ver>.md   <h3>Deprecations / Breaking changes
  numpy      rst        doc/source/release/<ver>-notes.rst
  scipy      rst        doc/source/release/<ver>-notes.rst

Cirq is excluded from the churn comparison: its release notes are organized by module
(cirq-core, cirq-google, ...) with no deprecation or breaking-change sections, so the
same measurement cannot be made. It is included in the supplementary stock measure.

Caveats recorded with the results:
  - "breaking" aggregates each project's own category for incompatible changes. For
    Qiskit this is the reno `upgrade` section, which is broader than strictly breaking.
  - Counting announced entries measures documentation practice as well as churn.
  - Release dates come from the GitHub API; releases without a matching tag are dropped
    from the per-year figures only.

Output: out/api_churn.csv, out/api_churn_summary.csv, out/deprecation_markers.csv
"""
import csv, json, re, sys, urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out, repos  # noqa: E402

REPOS = repos()
OUT = out("api_churn")

GH = {"Qiskit": "Qiskit/qiskit", "PennyLane": "PennyLaneAI/pennylane",
      "numpy": "numpy/numpy", "scipy": "scipy/scipy", "Cirq": "quantumlib/Cirq"}

rows = []


def minor(v):
    m = re.match(r"v?(\d+)\.(\d+)", v)
    return f"{int(m.group(1))}.{int(m.group(2))}" if m else None


def api(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ai4qoss-analysis"})
    return json.load(urllib.request.urlopen(req, timeout=30))


# ------------------------------------------------------------------ sources
def qiskit():
    per = defaultdict(lambda: [0, 0])
    for d in sorted((REPOS / "qiskit" / "releasenotes" / "notes").iterdir()):
        ver = minor(d.name) if d.is_dir() else None
        if not ver:
            continue
        for f in d.glob("*.yaml"):
            text = f.read_text(errors="ignore")
            for key, idx in (("deprecations", 0), ("upgrade", 1)):
                m = re.search(rf"^{key}:\s*$(.*?)(?=^\S|\Z)", text, re.M | re.S)
                if m:
                    per[ver][idx] += len(re.findall(r"^\s+-\s", m.group(1), re.M))
    for v, (dep, brk) in per.items():
        rows.append(["Qiskit", v, dep, brk])


def pennylane():
    per = defaultdict(lambda: [0, 0])
    for f in sorted((REPOS / "pennylane" / "doc" / "releases").glob("changelog-*.md")):
        ver = minor(f.stem.replace("changelog-", ""))
        if not ver:
            continue
        parts = re.split(r"<h3>(.*?)</h3>", f.read_text(errors="ignore"))
        for i in range(1, len(parts), 2):
            title, body = parts[i].lower(), parts[i + 1]
            n = len(re.findall(r"^\s*\*\s", body, re.M))
            if "deprecat" in title:
                per[ver][0] += n
            elif "breaking" in title:
                per[ver][1] += n
    for v, (dep, brk) in per.items():
        rows.append(["PennyLane", v, dep, brk])


def rst_project(name, folder):
    base = REPOS / folder / "doc" / "source" / "release"
    if not base.exists():
        base = REPOS / folder / "doc" / "release"
    per = defaultdict(lambda: [0, 0])
    for f in sorted(base.glob("*-notes.rst")):
        ver = minor(f.stem.replace("-notes", ""))
        if not ver:
            continue
        lines = f.read_text(errors="ignore").splitlines()
        sections = []
        for i in range(len(lines) - 1):
            t, u = lines[i].strip(), lines[i + 1].strip()
            if t and u and len(u) >= max(3, len(t) - 2) and set(u) <= set("=-~^\"'`*+#"):
                sections.append((i, t.lower()))
        for k, (i, title) in enumerate(sections):
            end = sections[k + 1][0] if k + 1 < len(sections) else len(lines)
            body = "\n".join(lines[i + 2:end])
            n = len(re.findall(r"^[\*\-]\s", body, re.M))
            if "deprecat" in title and "expired" not in title:
                per[ver][0] += n
            elif ("backwards incompatible" in title or "compatibility notes" in title
                  or "expired deprecation" in title or "removed" in title):
                per[ver][1] += n
    for v, (dep, brk) in per.items():
        rows.append([name, v, dep, brk])


qiskit(); pennylane()
rst_project("numpy", "numpy"); rst_project("scipy", "scipy")

# ------------------------------------------------------------------ release dates
dates = {}  # (project, minor) -> earliest release date
for proj, slug in GH.items():
    try:
        for page in (1, 2, 3):
            data = api(f"https://api.github.com/repos/{slug}/releases?per_page=100&page={page}")
            if not data:
                break
            for rel in data:
                v = minor(rel.get("tag_name", "") or "")
                d = (rel.get("published_at") or "")[:10]
                if v and d:
                    key = (proj, v)
                    if key not in dates or d < dates[key]:
                        dates[key] = d
    except Exception as e:
        print(f"  note: release dates for {proj} unavailable ({e})", file=sys.stderr)

for r in rows:
    r.append(dates.get((r[0], r[1]), ""))

# ------------------------------------------------------------------ write per-release
rows.sort(key=lambda r: (r[0], [int(x) for x in r[1].split(".")]))
with open(OUT / "api_churn.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["project", "minor_release", "deprecation_entries",
                "breaking_or_upgrade_entries", "release_date"])
    w.writerows(rows)

# ------------------------------------------------------------------ summary
summary = defaultdict(lambda: {"n": 0, "dep": 0, "brk": 0, "dated": []})
for proj, ver, dep, brk, date in rows:
    s = summary[proj]
    s["n"] += 1; s["dep"] += dep; s["brk"] += brk
    if date:
        s["dated"].append((date, dep, brk))

with open(OUT / "api_churn_summary.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["project", "minor_releases", "deprecations_total", "breaking_total",
                "deprecations_per_release", "breaking_per_release",
                "span_years", "deprecations_per_year", "releases_per_year"])
    print(f"{'project':<11}{'rel':>5}{'dep/rel':>9}{'brk/rel':>9}{'dep/yr':>8}{'rel/yr':>8}  span")
    for proj, s in sorted(summary.items()):
        n, dep, brk = s["n"], s["dep"], s["brk"]
        span = dpy = rpy = ""
        if len(s["dated"]) >= 2:
            ds = sorted(d for d, _, _ in s["dated"])
            years = (datetime.fromisoformat(ds[-1]) - datetime.fromisoformat(ds[0])).days / 365.25
            if years > 0.5:
                dep_dated = sum(d for _, d, _ in s["dated"])
                span = round(years, 1)
                dpy = round(dep_dated / years, 1)
                rpy = round(len(s["dated"]) / years, 1)
        w.writerow([proj, n, dep, brk, round(dep / n, 2), round(brk / n, 2), span, dpy, rpy])
        print(f"{proj:<11}{n:>5}{dep/n:>9.1f}{brk/n:>9.1f}{str(dpy):>8}{str(rpy):>8}  {span} yr")

# ------------------------------------------------------------------ supplementary: stock of deprecation markers
markers = []
# Project-agnostic: decorators plus any *DeprecationWarning class (projects define
# their own, e.g. PennyLaneDeprecationWarning).
PATTERNS = [r"@deprecat\w*", r"\w*DeprecationWarning\b", r"deprecate_func",
            r"deprecate_arg", r"deprecated_parameter"]
for proj, folder in (("Qiskit", "qiskit"), ("PennyLane", "pennylane"), ("Cirq", "Cirq"),
                     ("numpy", "numpy"), ("scipy", "scipy")):
    root = REPOS / folder
    hits = files = 0
    for p in root.rglob("*.py"):
        if any(x in p.parts for x in (".git", "test", "tests", "docs", "doc")):
            continue
        try:
            t = p.read_text(errors="ignore")
        except Exception:
            continue
        files += 1
        hits += sum(len(re.findall(pat, t)) for pat in PATTERNS)
    markers.append([proj, files, hits, round(1000 * hits / files, 1) if files else ""])

with open(OUT / "deprecation_markers.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["project", "source_files", "deprecation_markers", "markers_per_1000_files"])
    w.writerows(markers)

print("\nsupplementary: live deprecation markers in source")
for proj, files, hits, rate in markers:
    print(f"  {proj:<11}{hits:>6} markers in {files:>5} files  ({rate}/1000 files)")
print(f"\nwrote {OUT}/api_churn.csv, api_churn_summary.csv, deprecation_markers.csv")
