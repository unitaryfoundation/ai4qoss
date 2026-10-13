#!/usr/bin/env python
"""unitaryHACK bounties, 2022 to 2026, normalized to one row per bounty.

The organizers' sheets changed shape over the years: 2022 lists one bounty per row,
2023 onward list one project per row with up to six bounty columns. This flattens
both into (year, project, repo, url, amount) and reports what each year looked like.

Reads only the de-identified copies in ./clean, written by scrub.py.

Output: out/bounties_long.csv, out/bounties_by_year.csv, out/bounties_by_repo.csv
"""
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out  # noqa: E402

CLEAN = out("unitaryhack/clean")
OUT = out("unitaryhack")
OUT.mkdir(exist_ok=True)

REPO = re.compile(r"github\.com/([\w.-]+/[\w.-]+)")


def repo_key(name):
    """Identity of a repository, for counting.

    GitHub owner and repository names are case-insensitive, and the sheets spell
    the same repository both ways across years, for example quantumlib/Cirq and
    quantumlib/cirq. Counting the raw strings reports one repository too many.
    """
    return name.lower()


def money(v):
    if v is None:
        return None
    s = str(v).replace("$", "").replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def rows_of(year):
    with open(CLEAN / f"{year}_bounties.csv") as f:
        return list(csv.DictReader(f))


def flatten():
    out = []
    # 2022: one bounty per row, its own column names
    for r in rows_of(2022):
        url = (r.get("bounty_url (Issue)") or "").strip()
        out.append(["2022", (r.get("Participating Project") or "").strip(),
                    url, money(r.get("Payment"))])
    # 2023 onward: one project per row, up to six bounty column groups
    for year in (2023, 2024, 2025, 2026):
        for r in rows_of(year):
            project = (r.get("Participating Project")
                       or r.get("Participating Projects") or r.get("Name") or "").strip()
            for i in range(1, 7):
                ucol = "Bounty URL" if i == 1 else f"Bounty {i} URL"
                acol = "Bounty Amount" if i == 1 else f"Bounty {i} Amount"
                url = (r.get(ucol) or "").strip()
                amt = money(r.get(acol))
                if url or amt:
                    out.append([str(year), project, url, amt])
    return out


def main():
    rows = []
    for year, project, url, amount in flatten():
        m = REPO.search(url)
        repo = m.group(1) if m else ""
        if not (url or amount):
            continue
        rows.append([year, project, repo, url, "" if amount is None else amount])

    with open(OUT / "bounties_long.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "project", "repo", "url", "amount_usd"])
        w.writerows(rows)

    per_year = defaultdict(list)
    for r in rows:
        per_year[r[0]].append(r)

    print(f"{'year':<6}{'bounties':>9}{'with URL':>10}{'projects':>10}"
          f"{'repos':>7}{'paid $':>9}{'median $':>10}")
    ysum = []
    for year in sorted(per_year):
        rs = per_year[year]
        amts = [float(r[4]) for r in rs if r[4] != ""]
        repos = {repo_key(r[2]) for r in rs if r[2]}
        projects = {r[1] for r in rs if r[1]}
        withurl = sum(1 for r in rs if r[3])
        med = sorted(amts)[len(amts) // 2] if amts else 0
        print(f"{year:<6}{len(rs):>9}{withurl:>10}{len(projects):>10}{len(repos):>7}"
              f"{sum(amts):>9,.0f}{med:>10,.0f}")
        ysum.append([year, len(rs), withurl, len(projects), len(repos),
                     round(sum(amts)), round(med)])

    with open(OUT / "bounties_by_year.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "bounties", "with_url", "projects", "repos",
                    "total_usd", "median_usd"])
        w.writerows(ysum)

    repo_year = defaultdict(Counter)
    repo_name = {}
    for r in rows:
        if r[2]:
            key = repo_key(r[2])
            repo_year[key][r[0]] += 1
            repo_name.setdefault(key, r[2])
    with open(OUT / "bounties_by_repo.csv", "w", newline="") as f:
        w = csv.writer(f)
        years = sorted(per_year)
        w.writerow(["repo", *years, "total"])
        for key, c in sorted(repo_year.items(), key=lambda kv: -sum(kv[1].values())):
            w.writerow([repo_name[key], *(c.get(y, 0) for y in years), sum(c.values())])

    print(f"\n{len(repo_year)} distinct repositories across all years")
    print(f"repositories appearing in every year: "
          f"{sum(1 for c in repo_year.values() if len(c) == len(per_year))}")
    print(f"\nwrote {OUT}/bounties_long.csv, bounties_by_year.csv, bounties_by_repo.csv")


if __name__ == "__main__":
    main()
