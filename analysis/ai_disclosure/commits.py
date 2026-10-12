#!/usr/bin/env python
"""AI disclosure in commit messages, over time.

What is counted. A commit is "disclosed" when its message carries a machine-written
marker that names an AI tool: the `Co-authored-by:` trailer that coding agents append,
the address they sign with, or the generation footer they add. These markers are written
by the tool, not typed by the author, so they are the closest thing to a reliable signal
of AI involvement that a repository records.

This is a floor, not a rate of AI use. Contributors can strip the trailer, squash it away,
or never enable it, and work done with an assistant that leaves no trailer is invisible
here. What the numbers support is a statement about disclosure, not about how much of the
code was written with help.

Bare mentions of a tool's name are not matched: "Claude" and "Copilot" also appear in
prose and in people's names. Only trailers, signing addresses, and generation footers
count.

Runs offline against the clones in ../_repos, which must have full history.

Output: out/ai_disclosure_commits.csv, out/ai_disclosure_commits_by_tool.csv
"""
import csv
import re
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out, repos  # noqa: E402

REPOS = repos()
OUT = out("ai_disclosure")

# (label, group, git dir under ../_repos, clone url or None if already present)
PROJECTS = [
    ("Qiskit", "quantum", "qiskit", None),
    ("Qiskit Aer", "quantum", "meta/qiskit-aer.git", "https://github.com/Qiskit/qiskit-aer"),
    ("Qiskit IBM Runtime", "quantum", "meta/qiskit-ibm-runtime.git",
     "https://github.com/Qiskit/qiskit-ibm-runtime"),
    ("PennyLane", "quantum", "pennylane", None),
    ("PennyLane Lightning", "quantum", "meta/pennylane-lightning.git",
     "https://github.com/PennyLaneAI/pennylane-lightning"),
    ("Cirq", "quantum", "Cirq", None),
    ("OpenFermion", "quantum", "meta/openfermion.git",
     "https://github.com/quantumlib/OpenFermion"),
    ("Stim", "quantum", "meta/stim.git", "https://github.com/quantumlib/Stim"),
    ("QuTiP", "quantum", "meta/qutip.git", "https://github.com/qutip/qutip"),
    ("Mitiq", "quantum", "meta/mitiq.git", "https://github.com/unitaryfund/mitiq"),
    ("tket", "quantum", "meta/tket.git", "https://github.com/CQCL/tket"),
    ("numpy", "mainstream", "numpy", None),
    ("scipy", "mainstream", "scipy", None),
    ("matplotlib", "mainstream", "meta/matplotlib.git",
     "https://github.com/matplotlib/matplotlib"),
    ("pandas", "mainstream", "meta/pandas.git", "https://github.com/pandas-dev/pandas"),
    ("sympy", "mainstream", "meta/sympy.git", "https://github.com/sympy/sympy"),
    ("astropy", "mainstream", "meta/astropy.git", "https://github.com/astropy/astropy"),
    ("scikit-learn", "mainstream", "meta/scikit-learn.git",
     "https://github.com/scikit-learn/scikit-learn"),
    ("networkx", "mainstream", "meta/networkx.git", "https://github.com/networkx/networkx"),
]

# Each marker is written by the tool itself. Trailers are anchored to line start so a
# sentence mentioning a tool does not match.
TRAILER = r"^[ \t]*co-authored-by:[ \t]*"
MARKERS = [
    ("claude", re.compile(
        TRAILER + r"claude\b|noreply@anthropic\.com|generated with \[?claude code\]?",
        re.I | re.M)),
    ("copilot", re.compile(
        TRAILER + r"copilot\b|copilot@users\.noreply\.github\.com|"
        r"copilot-swe-agent\[bot\]", re.I | re.M)),
    ("cursor", re.compile(
        TRAILER + r"cursor(agent)?\b|cursoragent@cursor\.com", re.I | re.M)),
    ("devin", re.compile(
        TRAILER + r"devin\b|devin-ai-integration\[bot\]", re.I | re.M)),
    ("aider", re.compile(TRAILER + r"aider\b|aider\.chat", re.I | re.M)),
    ("openai", re.compile(TRAILER + r"(openai|codex|chatgpt)\b", re.I | re.M)),
    ("other-agent", re.compile(
        TRAILER + r"[^<\n]*\b(ai|llm)[- ]?(bot|agent)\b|"
        r"^[ \t]*(generated|written) (with|by) [^\n]*\b(gpt|llm|ai assistant)\b",
        re.I | re.M)),
]

AI_BOT = re.compile(
    r"copilot-swe-agent|devin-ai-integration|cursoragent|claude\[bot\]|"
    r"codex\[bot\]|sweep-ai|codegen-sh|openhands-agent", re.I)
ROUTINE_BOT = re.compile(
    r"dependabot|pre-commit-ci|github-actions|renovate|mergify|codecov", re.I)

# Commits on or after this date are ignored, so that the last quarter in the output is a
# complete one. Set to the first day of the quarter following the collection date.
UNTIL = "2026-10-01"

US, RS = "\x1f", "\x1e"  # field and record separators, safe inside commit messages


def ensure_clone(gitdir, url):
    """Blobless bare clone: commit metadata only, no file contents."""
    path = REPOS / gitdir
    if path.exists():
        return True
    if not url:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"  cloning {url} ...", flush=True)
    r = subprocess.run(["git", "clone", "--bare", "--filter=tree:0", "--quiet", url,
                        str(path)], capture_output=True, text=True)
    if r.returncode:
        print(f"    failed: {r.stderr.strip()[:120]}", file=sys.stderr)
        return False
    return True


def git_at(gitdir):
    """Locate args for a repo. Bare clones need --git-dir: a -C into a bare repo is
    refused when the user has safe.bareRepository set to 'explicit'."""
    path = REPOS / gitdir
    if (path / "HEAD").exists() and not (path / ".git").exists():
        return ["--git-dir", str(path)]
    return ["-C", str(path)]


def commits(gitdir):
    """Yield (date, author, committer, message) for every commit reachable from HEAD."""
    proc = subprocess.Popen(
        ["git", *git_at(gitdir), "log",
         f"--format=%aI{US}%an <%ae>{US}%cn <%ce>{US}%B{RS}"],
        stdout=subprocess.PIPE, text=True, errors="ignore")
    buf = ""
    for chunk in iter(lambda: proc.stdout.read(1 << 16), ""):
        buf += chunk
        while RS in buf:
            rec, buf = buf.split(RS, 1)
            rec = rec.lstrip("\n")
            parts = rec.split(US)
            if len(parts) == 4:
                yield parts[0], parts[1], parts[2], parts[3]
    proc.stdout.close()
    proc.wait()


def quarter(iso):
    return f"{iso[:4]}Q{(int(iso[5:7]) - 1) // 3 + 1}"


def main():
    rows, tool_rows, author_rows = [], [], []
    group_total = defaultdict(int)
    group_hit = defaultdict(int)
    group_hit_x = defaultdict(int)
    per_project_2026 = defaultdict(list)

    for proj, group, gitdir, url in PROJECTS:
        if not ensure_clone(gitdir, url):
            print(f"  skip {proj}: no clone", file=sys.stderr)
            continue
        total = defaultdict(int)
        hit = defaultdict(int)
        bot = defaultdict(int)
        routine = defaultdict(int)
        by_tool = defaultdict(lambda: defaultdict(int))
        disclosers = defaultdict(lambda: defaultdict(int))  # author -> quarter -> n

        for date, author, committer, msg in commits(gitdir):
            if len(date) < 7 or not date[:4].isdigit() or date[:10] >= UNTIL:
                continue
            q = quarter(date)
            total[q] += 1
            who = f"{author} {committer}"
            found = [name for name, pat in MARKERS if pat.search(msg)]
            if AI_BOT.search(who):
                bot[q] += 1
                found.append("ai-bot-author")
            elif ROUTINE_BOT.search(who):
                routine[q] += 1
            if found:
                hit[q] += 1
                for name in set(found):
                    by_tool[q][name] += 1
                if "ai-bot-author" not in found:
                    disclosers[author][q] += 1

        n_all, h_all = sum(total.values()), sum(hit.values())
        per_author = {a: sum(q.values()) for a, q in disclosers.items()}
        n_disc = sum(per_author.values())
        top_author = max(per_author, key=per_author.get) if per_author else None
        top = per_author[top_author] if top_author else 0
        conc = (f"; {len(disclosers)} distinct authors, top one {100 * top / n_disc:.0f}%"
                if n_disc else "")
        print(f"\n{proj} ({group}): {n_all} commits, {h_all} with an AI marker{conc}")
        author_rows.append([proj, group, n_all, h_all, sum(bot.values()),
                            len(per_author), top, top_author or ""])
        n26 = sum(v for k, v in total.items() if k >= "2026")
        h26 = sum(v for k, v in hit.items() if k >= "2026")
        if n26 >= 100:
            per_project_2026[group].append((proj, h26, n26, 100 * h26 / n26))
        for q in sorted(total):
            if q < "2024":
                continue  # the tools and their trailers postdate this
            n, h = total[q], hit[q]
            tools = " ".join(f"{k}={v}" for k, v in sorted(by_tool[q].items()))
            rows.append([proj, group, q, n, h, round(100 * h / n, 2) if n else "",
                         bot[q], routine[q]])
            for k, v in sorted(by_tool[q].items()):
                tool_rows.append([proj, group, q, k, v])
            group_total[(group, q)] += n
            group_hit[(group, q)] += h
            # same pool, minus the single largest discloser in this project
            group_hit_x[(group, q)] += h - (disclosers[top_author][q] if top_author else 0)
            if h:
                print(f"  {q}  {n:>5} commits  {h:>4} disclosed "
                      f"({100 * h / n:>5.2f}%)  {tools}")

    with open(OUT / "ai_disclosure_commits.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["project", "group", "quarter", "commits", "disclosed",
                    "disclosed_pct", "ai_bot_authored", "routine_bot_commits"])
        w.writerows(rows)
    with open(OUT / "ai_disclosure_commits_by_tool.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["project", "group", "quarter", "tool", "commits"])
        w.writerows(tool_rows)
    with open(OUT / "ai_disclosure_concentration.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["project", "group", "commits_total", "disclosed_total",
                    "ai_bot_authored", "distinct_disclosing_authors",
                    "commits_by_top_discloser", "top_discloser"])
        w.writerows(author_rows)

    # ------------------------------------------------------------- pooled by group
    print("\npooled disclosure rate; 'ex-top' removes each project's single largest "
          "discloser")
    quarters = sorted({q for _, q in group_total})
    print(f"{'quarter':<9}{'quantum':>10}{'ex-top':>9}   {'mainstream':>11}{'ex-top':>9}")
    for q in quarters:
        cells = []
        for g in ("quantum", "mainstream"):
            n, h, hx = group_total[(g, q)], group_hit[(g, q)], group_hit_x[(g, q)]
            cells += [f"{100 * h / n:>8.2f}%" if n else f"{'-':>9}",
                      f"{100 * hx / n:>8.2f}%" if n else f"{'-':>9}"]
        print(f"{q:<9}{cells[0]}{cells[1]}   {cells[2]}{cells[3]}")

    print("\n2026 disclosure rate by project (projects with 100+ commits in 2026)")
    for g in ("quantum", "mainstream"):
        items = sorted(per_project_2026[g], key=lambda x: -x[3])
        rates = [x[3] for x in items]
        med = statistics.median(rates) if rates else 0
        print(f"  {g:<11} median {med:>5.2f}%   " +
              "  ".join(f"{p} {r:.1f}%" for p, _, _, r in items[:6]))
    print(f"\nwrote {OUT}/ai_disclosure_commits.csv, ai_disclosure_commits_by_tool.csv")


if __name__ == "__main__":
    main()
