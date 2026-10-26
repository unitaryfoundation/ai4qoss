#!/usr/bin/env python
# Copyright 2026 Unitary Foundation
# SPDX-License-Identifier: Apache-2.0
"""2026 Quantum Open Source Software Survey: the questions this paper uses.

Source: the SurveyMonkey per-respondent export of 2026-10-26, which we hold and do not
publish. The survey was still open at that point (announced to run through
29 October 2026), so every count here is a mid-collection snapshot.

The export carries one row per respondent, which the 2026-10-07 summary export did
not, so the overlap between options of a multiple-answer question is now recoverable.
It also carries direct identifiers (IP address, email address, name). Nothing here
reads those columns, and only counts leave this script.

Denominators differ by question, because respondents drop out as the survey proceeds.
Every output row states the denominator it was computed against.

Q56 asked how respondents verify AI-generated code and offered both "Automated tests"
and "Automation verification" without defining either. The two are reported here as one
category: 127 of the 162 who chose automation verification also chose automated tests,
so the split reflects the wording of the instrument rather than a difference in what
respondents do.

Output: out/survey_tasks.csv, out/survey_agreement.csv, out/survey_verification.csv
"""
import csv
from pathlib import Path

import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from paths import out, private  # noqa: E402

SRC = private("26SurveyData_All_261026/CSV/2026 Quantum Open Source Software Survey.csv",
              "the per-respondent survey export")
OUT = out("qoss_survey")

RQ_FLAG = 9          # SurveyMonkey's poor-quality flag, "1.0" when set

TASKS = [            # first column of each task's manual / with-AI / N/A triple
    ("Discovering & summarizing research papers (e.g., arXiv)", 505),
    ("Learning new quantum concepts or SDKs", 508),
    ("Writing quantum circuits or algorithm code", 511),
    ("Debugging or optimizing quantum code", 514),
    ("Generating code documentation", 517),
    ("Hardware calibration or signal/pulse tuning", 520),
]
VERIFY = [           # Q56; the two automated options are reported as one
    ("Never do", [524]),
    ("Manual reviews", [525]),
    ("Automated test/verification", [526, 527]),
    ("Formal verification", [528]),
]
AGREE = [536, 537, 538]
SCALE = ["Strongly agree", "Agree", "Neutral", "Disagree", "Strongly disagree", "N/A"]


def load():
    with open(SRC, encoding="utf-8-sig") as f:
        r = csv.reader(f)
        head, choices = next(r), next(r)
        return head, choices, list(r)


def pct(n, d):
    return round(100 * n / d, 1) if d else ""


head, choices, rows = load()
ticked = lambda row, i: bool(row[i].strip())

# ----------------------------------------------------------------- workflow tasks
with open(OUT / "survey_tasks.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["task", "manually", "with_ai", "not_applicable", "row_total",
                "does_task", "ai_pct_of_doers", "manual_pct_of_doers", "na_pct_of_row"])
    for name, i in TASKS:
        man = sum(1 for r in rows if ticked(r, i))
        ai = sum(1 for r in rows if ticked(r, i + 1))
        na = sum(1 for r in rows if ticked(r, i + 2))
        doers = sum(1 for r in rows if ticked(r, i) or ticked(r, i + 1))
        total = sum(1 for r in rows
                    if ticked(r, i) or ticked(r, i + 1) or ticked(r, i + 2))
        w.writerow([name, man, ai, na, total, doers,
                    pct(ai, doers), pct(man, doers), pct(na, total)])

# ------------------------------------------------- Q56, how generated code is verified
answered = [r for r in rows if any(ticked(r, i) for _, cols in VERIFY for i in cols)]
with open(OUT / "survey_verification.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["method", "responses", "answered", "percent_of_answered"])
    for name, cols in VERIFY:
        n = sum(1 for r in answered if any(ticked(r, i) for i in cols))
        w.writerow([name, n, len(answered), pct(n, len(answered))])

# --------------------------------------------------------------- agreement statements
with open(OUT / "survey_agreement.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["statement", "strongly_agree", "agree", "neutral", "disagree",
                "strongly_disagree", "not_applicable", "row_total", "rated",
                "agree_pct", "neutral_pct", "disagree_pct"])
    for i in AGREE:
        c = {s: sum(1 for r in rows if r[i].strip() == s) for s in SCALE}
        total = sum(c.values())
        rated = total - c["N/A"]
        w.writerow([choices[i], c["Strongly agree"], c["Agree"], c["Neutral"],
                    c["Disagree"], c["Strongly disagree"], c["N/A"], total, rated,
                    pct(c["Strongly agree"] + c["Agree"], rated),
                    pct(c["Neutral"], rated),
                    pct(c["Disagree"] + c["Strongly disagree"], rated)])

# ------------------------------------------------------------------------ console
clean = [r for r in rows if r[RQ_FLAG].strip() != "1.0"]
ans_clean = [r for r in clean if any(ticked(r, i) for _, cols in VERIFY for i in cols)]
print(f"{len(rows)} respondents, {len(answered)} answered the verification question")


def shares(rs):
    """Every share the three files publish, recomputed on a subset of respondents."""
    out = []
    for _, i in TASKS:
        d = sum(1 for r in rs if ticked(r, i) or ticked(r, i + 1))
        out += [100 * sum(ticked(r, i + k) for r in rs) / d for k in (0, 1)]
    ans = [r for r in rs if any(ticked(r, i) for _, cols in VERIFY for i in cols)]
    out += [100 * sum(1 for r in ans if any(ticked(r, i) for i in cols)) / len(ans)
            for _, cols in VERIFY]
    for i in AGREE:
        c = {s: sum(1 for r in rs if r[i].strip() == s) for s in SCALE}
        rated = sum(c.values()) - c["N/A"]
        out.append(100 * (c["Strongly agree"] + c["Agree"]) / rated)
    return out


shift = max(abs(a - b) for a, b in zip(shares(rows), shares(clean)))
print(f"dropping the {len(rows) - len(clean)} responses SurveyMonkey flags as poor "
      f"quality leaves {len(ans_clean)} and moves no share by more than "
      f"{shift:.1f} points")
both = sum(1 for r in answered if ticked(r, 526) and ticked(r, 527))
only_v = sum(1 for r in answered if not ticked(r, 526) and ticked(r, 527))
print(f"automated tests and automation verification: {both} chose both, {only_v} chose "
      f"automation verification alone")
print(f"wrote {OUT}/survey_tasks.csv, survey_verification.csv, survey_agreement.csv")
