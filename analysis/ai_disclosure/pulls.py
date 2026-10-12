#!/usr/bin/env python
"""AI disclosure in pull request descriptions.

Complements commits.py in two ways: it sees pull requests that were never merged, whose
commits are absent from the repository history, and it sees disclosure written as prose
in the description rather than as a trailer.

Three signals, kept apart because they fail differently:

  tool marker    a footer written by the tool, e.g. "Generated with Claude Code". Same
                 status as a commit trailer: reliable when present, absent whenever the
                 contributor removes it or never enabled it.
  prose          the author says in their own words that an assistant was involved
                 ("written with Copilot", "AI-generated"). Voluntary and unevenly worded,
                 so this is the weakest of the three and the most prone to false
                 positives; matches are sampled and checked by hand.

                 Boilerplate has to be removed first. numpy's pull request template
                 carries the lines "specify what code or text is AI generated" and
                 "policy on AI generated code at", which appear in every pull request
                 whether or not a tool was used; scoring the raw text put numpy at 17%
                 and sympy at 72%, all of it template. Lines that repeat verbatim across
                 at least 5% of a project's pull requests are treated as template and
                 dropped before matching, which needs no per-project hardcoding.
  bot author     the pull request was opened by a coding agent's account. Not subject to
                 the author's willingness to disclose, but covers only autonomous agents.

All three are lower bounds on AI involvement. A contributor who uses an assistant and says
nothing is invisible in every one of them, so none of these numbers is a usage rate.

Reads GITHUB_TOKEN from the environment. Run through an interactive shell if the token
lives in ~/.zshrc:  zsh -i -c 'python3 ai_disclosure/pulls.py'

Output: out/ai_disclosure_pulls.csv, out/ai_disclosure_pull_samples.csv
"""
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out  # noqa: E402

OUT = out("ai_disclosure")
RAW = out("ai_disclosure/raw")

# A line repeated verbatim this many times is template: nobody writes the same 15+
# character sentence 20 times by hand. An absolute count is needed because templates get
# introduced part-way through a project's history and so cover only recent pull requests;
# numpy's AI policy text is in a few hundred of its 4726 pull requests, under any
# percentage threshold that is not also low enough to catch ordinary sentences.
TEMPLATE_MIN_COUNT = 20

SINCE = "2024-01-01"
# Pull requests created on or after this date are left out of the scoring, so that the
# last quarter reported is complete. The cache still holds them.
UNTIL = "2026-10-01"

REPOS = [
    ("Qiskit", "quantum", "Qiskit/qiskit"),
    ("Qiskit Aer", "quantum", "Qiskit/qiskit-aer"),
    ("Qiskit IBM Runtime", "quantum", "Qiskit/qiskit-ibm-runtime"),
    ("PennyLane", "quantum", "PennyLaneAI/pennylane"),
    ("PennyLane Lightning", "quantum", "PennyLaneAI/pennylane-lightning"),
    ("Cirq", "quantum", "quantumlib/Cirq"),
    ("OpenFermion", "quantum", "quantumlib/OpenFermion"),
    ("Stim", "quantum", "quantumlib/Stim"),
    ("QuTiP", "quantum", "qutip/qutip"),
    ("Mitiq", "quantum", "unitaryfund/mitiq"),
    ("tket", "quantum", "CQCL/tket"),
    ("numpy", "mainstream", "numpy/numpy"),
    ("scipy", "mainstream", "scipy/scipy"),
    ("matplotlib", "mainstream", "matplotlib/matplotlib"),
    ("pandas", "mainstream", "pandas-dev/pandas"),
    ("sympy", "mainstream", "sympy/sympy"),
    ("astropy", "mainstream", "astropy/astropy"),
    ("scikit-learn", "mainstream", "scikit-learn/scikit-learn"),
    ("networkx", "mainstream", "networkx/networkx"),
]

TOOL_MARKER = re.compile(
    r"generated with \[?claude code\]?|noreply@anthropic\.com|"
    r"^[ \t]*co-authored-by:[ \t]*(claude|copilot|cursor|devin|aider|openai|codex)\b|"
    r"🤖 generated with|opened by \[?devin\]?|this pull request was created by",
    re.I | re.M)

# Deliberately narrow: an assistant has to be named as having done work, not merely
# mentioned. "Fixes the copilot integration" must not match.
PROSE = re.compile(
    r"\b(written|generated|created|implemented|drafted|authored|produced)\b[^.\n]{0,40}\b"
    r"(with|using|by|via)\b[^.\n]{0,25}\b"
    r"(claude|chatgpt|gpt-?[45]|copilot|cursor|devin|aider|codex|an? (ai|llm))\b"
    r"|\b(ai|llm)[- ](generated|assisted|written|authored)\b"
    r"|\bwith (the )?(help|assistance) of\b[^.\n]{0,20}\b"
    r"(claude|chatgpt|copilot|cursor|an? (ai|llm))\b",
    re.I)

# A match is discarded when its sentence negates it ("code and logic is all mine and not
# AI generated") or discusses the rules rather than disclosing ("looks purely AI generated
# and does not comply with our policy"). Both appeared in hand-checked samples.
NEGATION = re.compile(r"\b(not|no|never|without|n't|nothing)\b", re.I)
META = re.compile(r"\b(policy|policies|guideline|does not comply|please (write|state|"
                  r"specify|describe)|if no ai|requirement)\b", re.I)


def prose_hit(text):
    """First prose disclosure that is neither negated nor a discussion of the rules."""
    for m in PROSE.finditer(text):
        start = max(text.rfind(".", 0, m.start()), text.rfind("\n", 0, m.start())) + 1
        end = text.find(".", m.end())
        sentence = text[start:end if end > 0 else len(text)]
        if NEGATION.search(text[start:m.start()]) or META.search(sentence):
            continue
        return m
    return None


# Whether the project's own pull request template asks contributors to disclose AI use.
# This turns out to explain most of the between-project variation in disclosure rate, so
# it is recorded alongside the rates rather than left as background.
POLICY = re.compile(r"\b(ai|llm|copilot|claude|chatgpt|generative)\b", re.I)


BOT_AUTHOR = re.compile(
    r"copilot-swe-agent|devin-ai-integration|cursoragent|claude\[bot\]|codex\[bot\]|"
    r"sweep-ai|codegen-sh|openhands-agent|github-copilot", re.I)

TOKEN = os.environ.get("GITHUB_TOKEN", "")


def api(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai4qoss-analysis",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r), r.headers
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):  # rate limited
                # Unauthenticated calls get no Retry-After, only the reset time of the
                # hourly window, so wait until that window opens.
                reset = int(e.headers.get("X-RateLimit-Reset", 0))
                wait = max(int(e.headers.get("Retry-After", 0)),
                           reset - int(time.time()) + 5 if reset else 0, 60)
                print(f"    rate limited, waiting {wait}s", file=sys.stderr, flush=True)
                time.sleep(wait)
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"giving up on {url}")


def pulls(slug):
    """Pull requests created on or after SINCE, newest first."""
    page = 1
    while True:
        data, _ = api(f"https://api.github.com/repos/{slug}/pulls"
                      f"?state=all&sort=created&direction=desc&per_page=100&page={page}")
        if not data:
            return
        for pr in data:
            if pr["created_at"][:10] < SINCE:
                return
            yield pr
        if len(data) < 100:
            return
        page += 1


def quarter(iso):
    return f"{iso[:4]}Q{(int(iso[5:7]) - 1) // 3 + 1}"


def record(pr):
    return {"number": pr["number"], "created_at": pr["created_at"],
            "login": (pr.get("user") or {}).get("login", ""),
            "title": pr.get("title") or "", "body": pr.get("body") or ""}


def fetch(proj, slug, update=False):
    """Cache the fields we score, one JSON object per line. Re-run is free.

    With `update`, an existing cache is brought forward instead of reused as is: pull
    requests created on or after the newest cached one are fetched again and merged in
    by number, so the cache extends to the present without refetching its older part.
    The body of a pull request older than the cache is not refreshed.
    """
    path = RAW / f"{proj.replace(' ', '_')}.jsonl"
    if path.exists() and not update:
        return path
    old = {}
    if path.exists():
        for line in open(path):
            if line.strip():
                r = json.loads(line)
                old[r["number"]] = r
    since = max((r["created_at"][:10] for r in old.values()), default=SINCE)
    new = {}
    for pr in pulls(slug):
        if pr["created_at"][:10] < since:
            break
        new[pr["number"]] = record(pr)
    merged = {**old, **new}
    tmp = path.with_suffix(".part")
    with open(tmp, "w") as f:
        for r in sorted(merged.values(), key=lambda r: r["created_at"], reverse=True):
            json.dump(r, f)
            f.write("\n")
    tmp.rename(path)
    added = len(merged) - len(old)
    print(f"  fetched {len(new)} PRs since {since}, {added} new, {len(merged)} cached",
          flush=True)
    return path


def normalize(line):
    line = line.strip().lower()
    line = re.sub(r"^[-*]\s*\[[ xX]?\]\s*", "", line)   # checkbox markers
    line = re.sub(r"\s+", " ", line)
    return line


def template_lines(records):
    """Lines repeated verbatim across many pull requests: the project's template."""
    seen = defaultdict(int)
    for r in records:
        for line in {normalize(l) for l in r["body"].splitlines() if len(l.strip()) > 15}:
            seen[line] += 1
    return {line for line, c in seen.items() if c >= TEMPLATE_MIN_COUNT}


def strip_template(body, template):
    return "\n".join(l for l in body.splitlines()
                     if normalize(l) not in template)


def main():
    update = "--update" in sys.argv   # bring an existing cache forward to today
    if not TOKEN and not update:
        print("no GITHUB_TOKEN in environment; the unauthenticated limit of 60 requests "
              "per hour is not enough for a full scan", file=sys.stderr)
        return 1
    if not TOKEN:
        print("no GITHUB_TOKEN; running the update unauthenticated at 60 requests per "
              "hour, which is enough for a few months of pull requests", file=sys.stderr)

    rows, samples, policy_rows = [], [], []
    group_total = defaultdict(int)
    group_hit = defaultdict(lambda: defaultdict(int))

    for proj, group, slug in REPOS:
        print(f"\n{proj}", flush=True)
        path = fetch(proj, slug, update)
        records = [json.loads(l) for l in open(path) if l.strip()]
        records = [r for r in records if r["created_at"][:10] < UNTIL]
        template = template_lines(records)

        policy_lines = [l for l in template if POLICY.search(l)]
        total = defaultdict(int)
        counts = defaultdict(lambda: defaultdict(int))
        authors = defaultdict(int)
        n = 0
        for pr in records:
            q = quarter(pr["created_at"])
            total[q] += 1
            n += 1
            raw = f"{pr['title']}\n{pr['body']}"
            text = f"{pr['title']}\n{strip_template(pr['body'], template)}"
            login = pr["login"]
            kinds = []
            if BOT_AUTHOR.search(login):
                kinds.append("bot_author")
            if TOOL_MARKER.search(raw):
                kinds.append("tool_marker")   # machine text, repeats by design
            pm = prose_hit(text)
            if pm:
                kinds.append("prose")
            if kinds:
                for k in kinds:
                    counts[q][k] += 1
                counts[q]["any"] += 1
                authors[login] += 1
                if len(samples) < 400:
                    samples.append([proj, pr["number"], pr["created_at"][:10], login,
                                    "+".join(kinds),
                                    (pm.group(0)[:90] if pm else "")])
        tot = sum(total.values())
        anyc = sum(counts[q]["any"] for q in counts)
        top = max(authors.values()) if authors else 0
        policy_rows.append([proj, group, tot, len(template), len(policy_lines),
                            "yes" if policy_lines else "no",
                            (sorted(policy_lines, key=len, reverse=True)[0][:120]
                             if policy_lines else "")])
        print(f"{proj} ({group}): {tot} PRs, template asks about AI: "
              f"{'yes' if policy_lines else 'no'}, {anyc} with a disclosure "
              f"signal" + (f"; {len(authors)} distinct authors, top one "
                           f"{100 * top / anyc:.0f}%" if anyc else ""))
        for q in sorted(total):
            c = counts[q]
            rows.append([proj, group, q, total[q], c["any"], c["tool_marker"],
                         c["prose"], c["bot_author"],
                         round(100 * c["any"] / total[q], 2) if total[q] else ""])
            group_total[(group, q)] += total[q]
            for k in ("any", "tool_marker", "prose", "bot_author"):
                group_hit[(group, q)][k] += c[k]
            if c["any"]:
                print(f"  {q}  {total[q]:>5} PRs  {c['any']:>4} "
                      f"({100 * c['any'] / total[q]:>5.2f}%)  "
                      f"marker={c['tool_marker']} prose={c['prose']} bot={c['bot_author']}")

    with open(OUT / "ai_disclosure_pulls.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["project", "group", "quarter", "pulls", "any_signal", "tool_marker",
                    "prose", "bot_author", "any_signal_pct"])
        w.writerows(rows)
    with open(OUT / "ai_disclosure_pull_samples.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["project", "pr_number", "created", "author", "signals", "prose_match"])
        w.writerows(samples)

    with open(OUT / "ai_disclosure_pr_template_policy.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["project", "group", "pulls", "template_lines", "ai_policy_lines",
                    "template_asks_about_ai", "example_line"])
        w.writerows(policy_rows)

    n_q = sum(1 for r in policy_rows if r[1] == "quantum" and r[5] == "yes")
    n_m = sum(1 for r in policy_rows if r[1] == "mainstream" and r[5] == "yes")
    t_q = sum(1 for r in policy_rows if r[1] == "quantum")
    t_m = sum(1 for r in policy_rows if r[1] == "mainstream")
    print(f"\npull request template asks about AI use: "
          f"quantum {n_q}/{t_q}, mainstream {n_m}/{t_m}")

    print("\npooled pull request disclosure rate")
    print(f"{'quarter':<9}{'quantum':>10}{'mainstream':>13}")
    for q in sorted({q for _, q in group_total}):
        cells = []
        for g in ("quantum", "mainstream"):
            n, h = group_total[(g, q)], group_hit[(g, q)]["any"]
            cells.append(f"{100 * h / n:>9.2f}%" if n else f"{'-':>10}")
        print(f"{q:<9}{cells[0]}{cells[1]:>13}")
    print(f"\nwrote {OUT}/ai_disclosure_pulls.csv, ai_disclosure_pull_samples.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
