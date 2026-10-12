#!/usr/bin/env python
"""What the 2026 unitaryHACK surveys say about AI.

2026 is the first year either survey asked about AI: the maintainer form added a
policy question, a prior-usage question and an AI-session question, and the hacker
form added one question about using AI and LLMs during the event.

Free text is never reproduced. Each response is scored for the presence of topics and
only counts are reported, so nothing here quotes a respondent or names a project. The
topic patterns were written after inspecting the vocabulary of the responses rather
than guessed, but keyword incidence still only detects whether a subject was raised.

Sizes: 10 maintainers (9 answered the policy question), 26 hackers (16 answered the AI
question). Every count below is out of single digits or low tens and describes these
respondents only.

Output: out/ai_attitudes.csv
"""
import csv
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out  # noqa: E402

CLEAN = out("unitaryhack/clean")
OUT = out("unitaryhack")
OUT.mkdir(exist_ok=True)

# Written against the actual vocabulary of the responses: 'human' and 'understand'
# recur in both audiences, 'determine'/'hard' cluster around telling AI work apart.
TOPICS = {
    "wants a human in the loop": r"\bhuman\b",
    "contributor understanding of the PR": r"\bunderstand|\bexplain\b|\bcomprehend",
    "hard to tell AI work apart": r"\b(hard|difficult|impossible|can'?t|cannot)\b[^.]{0,40}"
                                  r"\b(determine|tell|know|detect|identif|distinguish)",
    "review burden or time": r"\breview|\bburden\b|\bworkload\b|\btime\b",
    "quality of submissions": r"\bquality\b|\bslop\b|\bspam\b|\bnoise\b|\blow[- ]effort\b|"
                              r"\bgarbage\b|\buseless\b",
    "names a specific tool": r"\bcopilot\b|\bclaude\b|\bchatgpt\b|\bgpt\b|\bcursor\b|"
                             r"\bgemini\b|\bdevin\b|\bcodex\b",
    "disclosure or attribution": r"\bdisclos|\bdeclare\b|\battribut|\bcredit\b",
    "mentions a written policy": r"\bpolic(y|ies)\b|\bguideline|\brule\b",
    "AI helped them": r"\bhelp|\buseful\b|\bfaster\b|\bsped up\b|\bproductiv",
    "AI got things wrong": r"\bwrong\b|\bhallucinat|\bincorrect\b|\bbroke\b|\bfail|"
                           r"\bmislead|\bfrustrat",
}


def load(name):
    with open(CLEAN / name) as f:
        return list(csv.DictReader(f))


def col(rows, needle):
    return next((h for h in rows[0] if h and needle.lower() in h.lower()), None)


def topics(texts, label, out_rows):
    print(f"\n  {label}  ({len(texts)} responses)")
    scored = []
    for topic, pattern in TOPICS.items():
        hits = sum(1 for t in texts if re.search(pattern, t, re.I))
        if hits:
            scored.append((hits, topic))
    for hits, topic in sorted(scored, reverse=True):
        print(f"      {hits:>2}/{len(texts)}   {topic}")
        out_rows.append([label, topic, hits, len(texts)])


def main():
    out_rows = []
    m = load("2026_maintainer_survey.csv")
    h = load("2026_hackers_survey.csv")
    print(f"2026 maintainer survey, n = {len(m)}")

    # multi-select: options are comma separated within one cell
    c = col(m, "AI usage prior")
    picks = Counter()
    answered = 0
    for r in m:
        v = (r[c] or "").strip()
        if not v:
            continue
        answered += 1
        for part in re.split(r",(?=[A-Z I])", v):
            part = part.strip()
            if part:
                picks[part] += 1
    print(f"\n  prior AI use, multi-select ({answered} responded)")
    for v, n in picks.most_common():
        print(f"      {n:>2}/{answered}   {v}")
        out_rows.append(["maintainer: prior AI use", v, n, answered])

    c = col(m, "Would you join an dedicated AI session")
    vals = [r[c].strip() for r in m if r[c].strip()]
    print(f"\n  would join a dedicated AI session ({len(vals)} responded)")
    for v, n in Counter(vals).most_common():
        print(f"      {n:>2}/{len(vals)}   {v}")
        out_rows.append(["maintainer: AI session", v, n, len(vals)])

    c = col(m, "AI Policy")
    topics([r[c].strip() for r in m if r[c].strip()],
           "maintainer: what the policy answer raises", out_rows)

    c = col(m, "Other Feedback")
    texts = [r[c].strip() for r in m if r[c].strip()]
    ai = sum(1 for t in texts
             if re.search(r"\bai\b|\bllm|" + TOPICS["names a specific tool"], t, re.I))
    print(f"\n  general feedback box: {ai}/{len(texts)} raise AI without being asked")
    out_rows.append(["maintainer: unprompted", "raises AI in general feedback",
                     ai, len(texts)])

    print(f"\n2026 hacker survey, n = {len(h)}")
    c = col(h, "experience with AI and LLM")
    topics([r[c].strip() for r in h if r[c].strip()],
           "hacker: what the AI answer raises", out_rows)

    with open(OUT / "ai_attitudes.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["group", "topic_or_option", "count", "answered"])
        w.writerows(out_rows)
    print(f"\nwrote {OUT}/ai_attitudes.csv")


if __name__ == "__main__":
    main()
