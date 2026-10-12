#!/usr/bin/env python
"""unitaryHACK participant and maintainer surveys, 2023 to 2026.

Reads only the de-identified copies in ./clean. 2022 is excluded: its exit survey has
three responses, too few to report.

Comparability is not assumed. Several questions kept the same option set across all
four years and are reported as a time series; the rest changed wording or scale and are
reported per year with the change noted. `Impression` moved from a Likert scale in 2023
to a 0 to 10 score in 2024, so the two are never pooled.

Sample sizes are small throughout (7 to 14 maintainers, 16 to 33 hackers per year).
Everything here is descriptive. No test is run and none would be meaningful at this size.

Output: out/survey_comparable.csv, out/survey_per_year.csv
"""
import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out  # noqa: E402

CLEAN = out("unitaryhack/clean")
OUT = out("unitaryhack")
OUT.mkdir(exist_ok=True)

YEARS = [2023, 2024, 2025, 2026]

COMPARABLE = {
    "hacker": {"Event Duration": ["Just right", "Too short", "Too long"]},
    "maintainer": {
        "Duration": ["Just right", "Too short", "Too long"],
        "Workload": ["Expected", "More than expected", "Less than expected"],
        "Project Activity": ["More than expected", "Expected", "Less than expected"],
        "Comparison to last year": ["Better", "Similar", "Worse",
                                    "Did not participate last year"],
    },
}


def load(year, kind):
    for stem in (f"{year}_{kind}s_survey", f"{year}_{kind}_survey"):
        p = CLEAN / f"{stem}.csv"
        if p.exists():
            with open(p) as f:
                return list(csv.DictReader(f))
    return []


def norm(v):
    """Fold spelling drift in the option strings (Nuetral, Less than Expected)."""
    v = (v or "").strip()
    fixes = {"nuetral": "Neutral", "less than expected": "Less than expected",
             "more than expected": "More than expected"}
    return fixes.get(v.lower(), v)


def numeric(vals):
    out = []
    for v in vals:
        try:
            out.append(float(v))
        except (TypeError, ValueError):
            pass
    return out


def main():
    comparable_rows, per_year_rows = [], []

    print("questions with an unchanged option set\n")
    for kind, questions in COMPARABLE.items():
        for q, options in questions.items():
            print(f"  {kind}: {q}")
            print("    year   n   " + "  ".join(f"{o[:13]:>13}" for o in options))
            for year in YEARS:
                rows = load(year, kind)
                if not rows or q not in rows[0]:
                    continue
                vals = [norm(r.get(q)) for r in rows if norm(r.get(q))]
                c = Counter(vals)
                cells = "  ".join(
                    f"{c.get(o, 0):>4} {100 * c.get(o, 0) / len(vals):>4.0f}%"
                    for o in options)
                print(f"    {year}  {len(vals):>3}   {cells}")
                for o in options:
                    comparable_rows.append([kind, q, year, len(vals), o, c.get(o, 0)])
            print()

    print("questions whose scale or options changed, reported per year\n")
    print("  hacker Impression: Likert in 2023, 0-10 score from 2024")
    for year in YEARS:
        rows = load(year, "hacker")
        vals = [r.get("Impression", "").strip() for r in rows
                if r.get("Impression", "").strip()]
        nums = numeric(vals)
        if nums:
            nums.sort()
            lo = sum(1 for v in nums if v <= 5)
            print(f"    {year}  n={len(nums):<3} median {nums[len(nums) // 2]:.0f}"
                  f"   range {nums[0]:.0f}-{nums[-1]:.0f}   at or below 5: {lo}")
            per_year_rows.append(["hacker", "Impression", year, len(nums),
                                  f"median {nums[len(nums) // 2]:.0f}",
                                  f"{lo} at or below 5"])
        elif vals:
            c = Counter(vals)
            print(f"    {year}  n={len(vals):<3} Likert: " +
                  "; ".join(f"{k} {v}" for k, v in c.most_common()))
            per_year_rows.append(["hacker", "Impression", year, len(vals), "Likert",
                                  "; ".join(f"{k}={v}" for k, v in c.most_common())])

    print("\n  maintainer Impression: 0-10 score from 2024")
    for year in YEARS:
        nums = numeric([r.get("Impression", "") for r in load(year, "maintainer")])
        if nums:
            nums.sort()
            print(f"    {year}  n={len(nums):<3} median {nums[len(nums) // 2]:.0f}"
                  f"   range {nums[0]:.0f}-{nums[-1]:.0f}")
            per_year_rows.append(["maintainer", "Impression", year, len(nums),
                                  f"median {nums[len(nums) // 2]:.0f}",
                                  f"range {nums[0]:.0f}-{nums[-1]:.0f}"])

    print("\n  hacker Bounty Difficulty: 'A good range of easy to hard' added in 2024")
    for year in YEARS:
        rows = load(year, "hacker")
        vals = [norm(r.get("Bounty Difficulty")) for r in rows
                if norm(r.get("Bounty Difficulty"))]
        if vals:
            c = Counter(vals)
            hard = c.get("Too hard", 0)
            print(f"    {year}  n={len(vals):<3} too hard: {hard} "
                  f"({100 * hard / len(vals):.0f}%)")
            per_year_rows.append(["hacker", "Bounty Difficulty", year, len(vals),
                                  "too hard", f"{hard} ({100 * hard / len(vals):.0f}%)"])

    with open(OUT / "survey_comparable.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["audience", "question", "year", "n", "option", "count"])
        w.writerows(comparable_rows)
    with open(OUT / "survey_per_year.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["audience", "question", "year", "n", "measure", "value"])
        w.writerows(per_year_rows)
    print(f"\nwrote {OUT}/survey_comparable.csv, survey_per_year.csv")


if __name__ == "__main__":
    main()
