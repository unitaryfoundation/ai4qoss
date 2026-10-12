#!/usr/bin/env python
"""2026 Quantum Open Source Software Survey: the questions this paper uses.

Source: ../26SurveyData_All_261007/, the SurveyMonkey summary export taken on
2026-10-07. The survey was still open at that point (announced to run through
29 October 2026), so every count here is a mid-collection snapshot and the
published totals will be larger.

The export is already aggregated: one block per question with the count and
percentage of each answer choice. Per-respondent rows are not in it, so nothing
here can be cross-tabulated, and the overlap between options of a multiple-answer
question is not recoverable.

Denominators differ by question. Each question reports its own "Answered" count,
which falls through the survey as respondents drop out: 733 accept the privacy
notice, 543 answer the demographics, and the AI block is answered by 275 to 420.
Percentages below are always against the question's own answered count, stated in
every output row.

Output: out/survey_ai_block.csv, out/survey_tasks.csv, out/survey_agreement.csv,
out/survey_verification.csv (the Q56 rows alone, which is what the paper figure
draws and what is published to the companion repository)
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out, private  # noqa: E402

SRC = private(
    "26SurveyData_All_261007",
    "It is the SurveyMonkey export of the 2026 Quantum Open Source Software "
    "Survey, which the Unitary Foundation holds and summarizes itself.",
) / "2026 Quantum Open Source Software Survey.csv"
OUT = out("qoss_survey")

SNAPSHOT = "2026-10-07"

# Single-answer and multiple-answer questions used in the paper.
SIMPLE = {
    2: "role (multiple answers)",
    15: "years of professional quantum experience",
    19: "role in the project most involved in",
    42: "contributes code to quantum OSS",
    53: "uses AI tools for quantum tasks",
    54: "which AI tools (multiple answers)",
    56: "how AI-generated code is verified (multiple answers)",
    57: "how often AI answers on quantum information are verified",
    58: "when AI output is verified (multiple answers)",
    60: "where AI will have the largest impact (multiple answers)",
    61: "reasons for not using AI (multiple answers)",
    64: "resources helpful for learning or contributing (multiple answers)",
}
MATRIX_TASKS = 55      # manual / with AI / not applicable, per workflow task
MATRIX_AGREE = 59      # five-point agreement, per statement


def blocks():
    """Split the export into one block per question."""
    rows = list(csv.reader(open(SRC)))
    out, cur = [], None
    for r in rows:
        if len(r) == 1 and re.match(r"^Q\d+\.", r[0]):
            cur = {"n": int(re.match(r"^Q(\d+)\.", r[0]).group(1)),
                   "title": r[0], "rows": []}
            out.append(cur)
        elif cur is not None and any(c.strip() for c in r):
            cur["rows"].append(r)
    return {b["n"]: b for b in out}


def answered(b):
    for r in b["rows"]:
        for i, c in enumerate(r):
            if c.strip() == "Answered":
                return int(r[i + 1])
    return None


def main():
    B = blocks()

    # ------------------------------------------------ single and multiple answer
    rows = []
    for q, label in SIMPLE.items():
        b = B[q]
        n = answered(b)
        for r in b["rows"][1:]:
            if not r[0].strip() or r[1].strip() in ("Answered", "Skipped"):
                continue
            count = int(r[2])
            rows.append([q, label, r[0].strip(), count, n,
                         round(100 * count / n, 1)])
    with open(OUT / "survey_ai_block.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["question", "topic", "answer_choice", "responses",
                    "answered", "percent_of_answered"])
        w.writerows(rows)

    # The verification question on its own, since that is the panel the paper
    # publishes and a reader should not have to filter the whole block for it.
    with open(OUT / "survey_verification.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["method", "responses", "answered", "percent_of_answered"])
        w.writerows([[r[2], r[3], r[4], r[5]] for r in rows if r[0] == 56])

    # ------------------------------------------------------------ Q55, task mode
    # Columns are Manually / With AI Assistance / N/A, select all that apply, so a
    # respondent can be in both the manual and the AI column. The share that uses
    # AI is taken over those who do the task at all, that is the row total minus
    # the respondents who marked the task as not applicable.
    b = B[MATRIX_TASKS]
    task_rows = []
    for r in b["rows"][1:]:
        if not r[0].strip() or r[0].startswith("Other") or r[1].strip() in (
                "", "Answered", "Skipped"):
            continue
        manual, ai, na, total = int(r[1]), int(r[2]), int(r[3]), int(float(r[4]))
        does_task = total - na
        task_rows.append([r[0].strip(), manual, ai, na, total, does_task,
                          round(100 * ai / does_task, 1),
                          round(100 * manual / does_task, 1),
                          round(100 * na / total, 1)])
    with open(OUT / "survey_tasks.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["task", "manually", "with_ai", "not_applicable", "row_total",
                    "does_task", "ai_pct_of_doers", "manual_pct_of_doers",
                    "na_pct_of_row"])
        w.writerows(task_rows)

    # ------------------------------------------------------- Q59, agreement scale
    b = B[MATRIX_AGREE]
    agree_rows = []
    for r in b["rows"][1:]:
        if not r[0].strip() or r[1].strip() in ("", "Answered", "Skipped"):
            continue
        sa, a, neu, d, sd, na = (int(x) for x in r[1:7])
        total = int(float(r[7]))
        rated = total - na           # respondents who placed themselves on the scale
        agree_rows.append([r[0].strip(), sa, a, neu, d, sd, na, total, rated,
                           round(100 * (sa + a) / rated, 1),
                           round(100 * neu / rated, 1),
                           round(100 * (d + sd) / rated, 1)])
    with open(OUT / "survey_agreement.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["statement", "strongly_agree", "agree", "neutral", "disagree",
                    "strongly_disagree", "not_applicable", "row_total", "rated",
                    "agree_pct", "neutral_pct", "disagree_pct"])
        w.writerows(agree_rows)

    # ------------------------------------------------------------------- console
    print(f"2026 QOSS survey, snapshot {SNAPSHOT}, collection still open\n")
    for q in (53, 56, 57, 58, 61):
        b = B[q]
        print(f"Q{q}. {SIMPLE[q]}  (answered {answered(b)})")
        for r in rows:
            if r[0] == q:
                print(f"    {r[5]:>5.1f}%  {r[3]:>4}  {r[2][:70]}")
        print()

    print("Q55. how each workflow task is performed "
          "(share of those who do the task; a respondent can report both)")
    print(f"    {'task':<46}{'with AI':>9}{'manual':>9}{'n':>7}{'not applicable':>16}")
    for t in task_rows:
        print(f"    {t[0][:45]:<46}{t[6]:>8.1f}%{t[7]:>8.1f}%{t[5]:>7}"
              f"{t[8]:>15.1f}%")

    print("\nQ59. agreement (share of those who placed themselves on the scale)")
    print(f"    {'statement':<62}{'agree':>8}{'neutral':>9}{'disagree':>10}{'n':>6}")
    for a in agree_rows:
        print(f"    {a[0][:61]:<62}{a[9]:>7.1f}%{a[10]:>8.1f}%{a[11]:>9.1f}%"
              f"{a[8]:>6}")

    print(f"\nwrote {OUT}/survey_ai_block.csv, survey_tasks.csv, "
          f"survey_agreement.csv")


if __name__ == "__main__":
    main()
