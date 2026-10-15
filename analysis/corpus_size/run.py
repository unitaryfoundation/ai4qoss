#!/usr/bin/env python
# Copyright 2026 Unitary Foundation
# SPDX-License-Identifier: Apache-2.0
"""Corpus size: how much public code imports each library.

Two independent proxies, because neither is trustworthy alone.

GitHub code search counts files on default branches of public, non-fork repositories that
contain an import of the library. Its `total_count` is an estimate for large result sets,
not a count: every value returned is an integer multiple of a high power of two (scipy
came back as exactly 2^21, numpy as 699 x 2^16), so the relative precision is roughly one
part in the leading factor and can be as poor as a factor of two when that factor is 1.
Two query forms are issued per library and reported separately; agreement between them is
the only internal check available.

PyPI download counts over the last 30 days come from pypistats.org and need no
credentials. They measure installs rather than code, and continuous integration dominates
the totals for widely depended-on packages, which inflates libraries that sit deep in
dependency trees relative to those a person imports directly.

The two disagree in known directions, so they bound the comparison rather than settle it.
What both can support is an order of magnitude, not a ratio.

Reads GITHUB_TOKEN from the environment (code search allows 10 requests per minute
authenticated, and is not available unauthenticated).

Output: out/corpus_size.csv
"""
import csv
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out  # noqa: E402

OUT = out("corpus_size")

# (label, group, import name, PyPI name)
LIBS = [
    ("Qiskit", "quantum", "qiskit", "qiskit"),
    ("PennyLane", "quantum", "pennylane", "pennylane"),
    ("Cirq", "quantum", "cirq", "cirq"),
    ("QuTiP", "quantum", "qutip", "qutip"),
    ("OpenFermion", "quantum", "openfermion", "openfermion"),
    ("Stim", "quantum", "stim", "stim"),
    ("Mitiq", "quantum", "mitiq", "mitiq"),
    ("pytket", "quantum", "pytket", "pytket"),
    ("Braket", "quantum", "braket", "amazon-braket-sdk"),
    ("numpy", "mainstream", "numpy", "numpy"),
    ("scipy", "mainstream", "scipy", "scipy"),
    ("pandas", "mainstream", "pandas", "pandas"),
    ("matplotlib", "mainstream", "matplotlib", "matplotlib"),
    ("sympy", "mainstream", "sympy", "sympy"),
    ("astropy", "mainstream", "astropy", "astropy"),
    ("scikit-learn", "mainstream", "sklearn", "scikit-learn"),
    ("networkx", "mainstream", "networkx", "networkx"),
]

TOKEN = os.environ.get("GITHUB_TOKEN", "")
CODE_SEARCH_INTERVAL = 9   # 10 per minute, plus room for the secondary limit


def get(url, headers=None, retries=4):
    req = urllib.request.Request(url, headers=headers or {})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                wait = int(e.headers.get("Retry-After", 60))
                print(f"    rate limited, waiting {wait}s", file=sys.stderr, flush=True)
                time.sleep(wait)
                continue
            if e.code == 404:
                return None
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(5 * (attempt + 1))
    return None


def code_search(phrase):
    q = urllib.parse.quote(f'"{phrase}" language:python')
    d = get(f"https://api.github.com/search/code?q={q}&per_page=1",
            {"Authorization": f"Bearer {TOKEN}",
             "Accept": "application/vnd.github+json",
             "User-Agent": "ai4qoss-analysis"})
    time.sleep(CODE_SEARCH_INTERVAL)
    return d.get("total_count") if d else None


def pypi_recent(name):
    """pypistats.org applies its own rate limit and answers 429 without Retry-After."""
    for attempt in range(4):
        d = get(f"https://pypistats.org/api/packages/{name}/recent",
                {"User-Agent": "ai4qoss-analysis"})
        v = (d or {}).get("data", {}).get("last_month")
        if v:
            return v
        time.sleep(20 * (attempt + 1))
    return None


def leading_factor(n):
    """Report the quantization: total_count is always k * 2^m. Small k means few
    significant digits, so the value carries little precision."""
    if not n:
        return ""
    m = 0
    while n % 2 == 0:
        n //= 2
        m += 1
    return f"{n}x2^{m}" if m >= 8 else "exact-ish"


def main():
    if not TOKEN:
        print("no GITHUB_TOKEN; code search is unavailable unauthenticated",
              file=sys.stderr)
        return 1

    rows = []
    print(f"{'library':<14}{'group':<11}{'import X':>12}{'from X import':>15}"
          f"{'quantization':>14}{'PyPI/month':>13}")
    for label, group, imp, pypi in LIBS:
        a = code_search(f"import {imp}")
        b = code_search(f"from {imp} import")
        d = pypi_recent(pypi)
        rows.append([label, group, imp, pypi, a, b, leading_factor(a), d])
        print(f"{label:<14}{group:<11}{str(a):>12}{str(b):>15}"
              f"{leading_factor(a):>14}{str(d):>13}")

    with open(OUT / "corpus_size.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["library", "group", "import_name", "pypi_name",
                    "github_files_import", "github_files_from_import",
                    "github_quantization", "pypi_downloads_last_month"])
        w.writerows(rows)

    # ---------------------------------------------------------------- group summary
    print("\ngroup medians (GitHub 'import X' files; PyPI downloads per month)")
    for g in ("quantum", "mainstream"):
        gh = sorted(r[4] for r in rows if r[1] == g and r[4])
        pp = sorted(r[7] for r in rows if r[1] == g and r[7])
        print(f"  {g:<11} GitHub {round(statistics.median(gh)):>12,}   "
              f"PyPI {round(statistics.median(pp)):>14,}")
    print(f"\nwrote {OUT}/corpus_size.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
