#!/usr/bin/env python
"""Geometry-only vector panels for the paper's three figures.

Each panel is its own matplotlib figure at the exact size it occupies in the
assembled figure, carrying shapes, lines, fills and the data-coupled tick labels
and nothing else. Axis names, annotations, series labels and panel tags are added
as editable text when the panels are assembled, which is a separate step not
included in this repository.

Reads only the CSVs in ../../data/figures, so every panel can be checked against
the published data with nothing else in hand. Writes SVG and PDF into
./components.

    python3 components.py           draw the panels
    python3 components.py --emf     also write EMF fallbacks, needs LibreOffice

The task panels take their stage counts from task_pipeline_by_year.csv rather
than from the per-task list, which is not published.
"""
import csv
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter

import figstyle
from figstyle import C, FIG_CORPUS, FIG_DISCLOSURE, FIG_TASKS, blend

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from paths import published  # noqa: E402

DATA = published()
COMP = HERE / "components"
COMP.mkdir(exist_ok=True)

figstyle.apply_style()


def read(name):
    """One of the CSVs this repository publishes, by file name."""
    with open(DATA / name) as f:
        return list(csv.DictReader(f))


def new_component(fig_spec, name):
    """A figure sized to its slide box, with the axes fixed by the shared layout."""
    spec = fig_spec["components"][name]
    _, _, w, h = spec["box"]
    left, bottom, right, top = spec["axes"]
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=left, bottom=bottom, right=right, top=top)
    return fig, ax


def save(fig, name):
    fig.savefig(COMP / f"{name}.svg")
    fig.savefig(COMP / f"{name}.pdf")
    plt.close(fig)
    print(f"  {name}")


def si_label(v, _=None):
    for div, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "k")):
        if v >= div:
            return f"{v / div:.0f}{suffix}"
    return f"{v:.0f}"


def log_x(ax, si=True, every=1):
    """Log scale, decade ticks as plain text. `every=2` labels every other decade,
    which keeps a six-decade axis from crowding."""
    ax.set_xscale("log")
    if every > 1:
        ax.xaxis.set_major_locator(LogLocator(base=10 ** every))
    ax.xaxis.set_major_formatter(
        FuncFormatter(si_label if si else (lambda v, _: f"{v:g}")))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(axis="x", which="minor", length=1.2)


def grid(ax, axis):
    ax.set_axisbelow(True)
    ax.grid(axis=axis, color=C["grid"], lw=0.5)


# =============================================================== figure: corpus
def corpus_components():
    rows = read("corpus_size.csv")
    order = sorted(rows, key=lambda r: (r["group"] != "quantum",
                                        int(r["github_files_import"])))
    names = [r["library"] for r in order]
    cols = [C["quantum"] if r["group"] == "quantum" else C["main"] for r in order]
    ypos = np.arange(len(order))

    for name, key, show_names in (("corpus_github", "github_files_import", True),
                                  ("corpus_pypi", "pypi_downloads_last_month", False)):
        fig, ax = new_component(FIG_CORPUS, name)
        vals = [int(r[key]) if r[key] else np.nan for r in order]
        for y, v, c in zip(ypos, vals, cols):
            if np.isnan(v):
                continue
            ax.plot([1, v], [y, y], color=blend(c, 0.35), lw=0.6, zorder=1)
            ax.plot(v, y, "o", ms=3.0, color=c, zorder=3,
                    markeredgecolor="white", markeredgewidth=0.35)
        log_x(ax, every=2)
        grid(ax, "x")
        q = [v for v, r in zip(vals, order)
             if r["group"] == "quantum" and not np.isnan(v) and v > 0]
        m = [v for v, r in zip(vals, order)
             if r["group"] == "mainstream" and not np.isnan(v) and v > 0]
        ax.axvspan(max(q), min(m), color=blend(C["accent"], 0.11), zorder=0)
        ax.set_xlim(min(min(q), min(m)) / 2.5, max(max(q), max(m)) * 1.8)
        ax.set_ylim(-0.8, len(order) - 0.2)
        ax.set_yticks(ypos)
        if show_names:
            ax.set_yticklabels(names)
            for tick, c in zip(ax.get_yticklabels(), cols):
                tick.set_color(c)
        else:
            ax.set_yticklabels([])
            ax.tick_params(axis="y", length=0)
        save(fig, name)

    # ------------------------------------------------------------- survival
    surv = [r for r in read("api_survival.csv")
            if float(r["unparsed_pct"]) <= 5]
    fig, ax = new_component(FIG_CORPUS, "survival")
    years = ["2019", "2020", "2021", "2022", "2023", "2024", "2025"]
    style = {"Qiskit": (C["quantum"], "-"), "PennyLane": (C["quantum_mid"], "-"),
             "Cirq": (C["quantum_soft"], "-"), "numpy": (C["main"], "--"),
             "scipy": (C["main_soft"], "--")}
    for proj, (col, ls) in style.items():
        d = {r["year"]: float(r["toplevel_survival_strict_pct"])
             for r in surv if r["project"] == proj}
        xs = [i for i, y in enumerate(years) if y in d]
        ax.plot(xs, [d[years[i]] for i in xs], ls, color=col, marker="o", ms=1.9,
                lw=1.0)
    # The only clear space in this panel is the band below the lowest data point
    # (16.2%), so the key is a single row along the bottom. Positions are axes
    # fractions shared with the deck via figstyle.SURVIVAL_KEY_X.
    for x0, (col, ls) in zip(figstyle.SURVIVAL_KEY_X,
                             [(C["quantum"], "-"), (C["quantum_mid"], "-"),
                              (C["quantum_soft"], "-"), (C["main"], "--"),
                              (C["main_soft"], "--")]):
        ax.plot([x0, x0 + 0.045], [figstyle.SURVIVAL_KEY_Y] * 2, ls, color=col,
                lw=1.0, marker="o", ms=1.8, markevery=[0],
                transform=ax.transAxes, clip_on=False)
    ax.set_xticks(range(len(years)))
    ax.set_xticklabels([f"'{y[2:]}" for y in years])
    ax.set_xlim(-0.35, len(years) - 0.65)
    ax.set_ylim(0, 105)
    ax.set_yticks([0, 50, 100])
    grid(ax, "y")
    save(fig, "survival")

    # ---------------------------------------------------------------- churn
    churn = {r["project"]: float(r["deprecations_per_year"])
             for r in read("api_churn_summary.csv")}
    fig, ax = new_component(FIG_CORPUS, "churn")
    # Only projects whose release notes carry a deprecation section can be counted.
    labels = ["Qiskit", "PennyLane", "numpy", "scipy"]
    vals = [churn[p] for p in labels]
    bcols = [C["quantum"], C["quantum_mid"], C["main"], C["main_soft"]]
    ax.barh(range(len(labels)), vals, color=bcols, height=0.62, edgecolor="none")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 68)
    ax.set_xticks([0, 20, 40, 60])
    grid(ax, "x")
    save(fig, "churn")


# =========================================================== figure: disclosure
def disclosure_components():
    qubits = read("qubit_counts.csv")
    fig, ax = new_component(FIG_DISCLOSURE, "qubits")
    pcols = {"Qiskit": C["quantum"], "PennyLane": C["quantum_mid"],
             "Cirq": C["quantum_soft"]}
    counts = {}
    for proj, col in pcols.items():
        vals = []
        for r in qubits:
            if r["project"] != proj:
                continue
            vals.extend([int(r["qubits"])] * int(r["occurrences"]))
        vals = np.sort(np.array(vals))
        counts[proj] = len(vals)
        ax.step(vals, np.arange(1, len(vals) + 1) / len(vals) * 100,
                where="post", color=col, lw=1.2)
    log_x(ax, si=False)
    ax.set_xlim(0.8, 400)
    ax.set_ylim(0, 103)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.axvline(20, color=C["accent"], lw=0.8, ls=":")
    grid(ax, "y")
    save(fig, "qubits")
    print("    n per project:", counts)

    # ------------------------------------------------- disclosure over time
    commits = read("ai_disclosure_commits.csv")
    pulls = read("ai_disclosure_pulls.csv")
    quarters = sorted({r["quarter"] for r in commits if r["quarter"] >= "2024Q1"})

    def pooled(rows, group, num, den):
        out = []
        for q in quarters:
            sel = [r for r in rows if r["quarter"] == q and r["group"] == group]
            n = sum(int(r[den]) for r in sel)
            out.append(100 * sum(int(r[num]) for r in sel) / n if n else np.nan)
        return np.array(out)

    fig, ax = new_component(FIG_DISCLOSURE, "disclosure")
    xs = np.arange(len(quarters))
    for group, col in (("quantum", C["quantum"]), ("mainstream", C["main"])):
        ax.plot(xs, pooled(pulls, group, "any_signal", "pulls"), "-", color=col,
                marker="o", ms=2.1, lw=1.1)
        ax.plot(xs, pooled(commits, group, "disclosed", "commits"), "--", color=col,
                marker="^", ms=2.1, lw=0.9)
    # Line-style key drawn as geometry; its words are added in the deck.
    ax.plot([0.25, 0.95], [16.4] * 2, "-", color=C["ink"], marker="o", ms=2.1,
            lw=1.1, clip_on=False)
    ax.plot([0.25, 0.95], [13.6] * 2, "--", color=C["ink"], marker="^", ms=2.1,
            lw=0.9, clip_on=False)
    ax.set_xticks(xs)
    ax.set_xticklabels([q[2:] if q.endswith("Q1") else q[-2:] for q in quarters])
    ax.set_xlim(-0.4, len(quarters) + 0.9)
    ax.set_ylim(0, 21)   # 2026Q3 mainstream commits reach 18.3%; keep headroom
    ax.set_yticks([0, 5, 10, 15, 20])
    grid(ax, "y")
    save(fig, "disclosure")

    # ------------------------------------------------------ policy vs rate
    policy = {r["project"]: (r["template_asks_about_ai"] == "yes", r["group"])
              for r in read("ai_disclosure_pr_template_policy.csv")}
    rate = {}
    for r in pulls:
        if r["quarter"] < "2026":
            continue
        a = rate.setdefault(r["project"], [0, 0])
        a[0] += int(r["pulls"])
        a[1] += int(r["any_signal"])

    groups = {k: [] for k in (("yes", "quantum"), ("no", "quantum"),
                              ("yes", "mainstream"), ("no", "mainstream"))}
    for proj, (n, h) in rate.items():
        if n < 100 or proj not in policy:
            continue
        ask, grp = policy[proj]
        groups[("yes" if ask else "no", grp)].append(100 * h / n)

    fig, ax = new_component(FIG_DISCLOSURE, "policy")
    positions = {("yes", "quantum"): 0, ("no", "quantum"): 1,
                 ("yes", "mainstream"): 2.5, ("no", "mainstream"): 3.5}
    for key, vals in groups.items():
        x = positions[key]
        col = C["quantum"] if key[1] == "quantum" else C["main"]
        if not vals:
            continue
        k = len(vals)
        off = np.linspace(-0.13, 0.13, k) if k > 1 else np.zeros(1)
        ax.plot(x + off, vals, "o", ms=2.8, color=blend(col, 0.85),
                markeredgecolor="white", markeredgewidth=0.35)
        ax.plot([x - 0.26, x + 0.26], [np.median(vals)] * 2, color=C["ink"], lw=1.0)
    ax.set_xticks(list(positions.values()))
    ax.set_xticklabels(["asks", "no", "asks", "no"])
    ax.set_xlim(-0.6, 4.1)
    ax.set_ylim(-1, 24)
    ax.set_yticks([0, 10, 20])
    grid(ax, "y")
    save(fig, "policy")

    # --------------------------------------------------------- concentration
    conc = read("ai_disclosure_concentration.csv")
    shares = [(r["project"], 100 * int(r["commits_by_top_discloser"]) /
               int(r["disclosed_total"]), r["group"])
              for r in conc if int(r["disclosed_total"]) >= 5]
    shares.sort(key=lambda t: t[1])
    fig, ax = new_component(FIG_DISCLOSURE, "concentration")
    ax.barh(np.arange(len(shares)), [s[1] for s in shares], height=0.6,
            color=[C["quantum"] if s[2] == "quantum" else C["main"] for s in shares])
    ax.set_yticks(np.arange(len(shares)))
    ax.set_yticklabels([s[0] for s in shares])
    ax.set_xlim(0, 105)
    ax.set_xticks([0, 50, 100])
    grid(ax, "x")
    save(fig, "concentration")


# ============================================================ figure: tasks
def task_components():
    """unitaryHACK records: what the community produced and what can be reused."""
    # ------------------------------------------------------------- a  funnel
    # The per-task list is not published, so the stage counts come from the
    # per-year aggregate, which carries one column per stage.
    pipeline = read("task_pipeline_by_year.csv")

    def total(col):
        return sum(int(r[col]) for r in pipeline)

    stages = [
        ("bounties listed", total("bounties_listed")),
        ("issue closed", total("issue_closed")),
        ("closed by merged PR", total("closed_by_merged_pr")),
        ("usable as a task", total("usable_as_task")),
        ("test in the solution", total("solution_changes_tests")),
    ]
    fig, ax = new_component(FIG_TASKS, "funnel")
    ys = np.arange(len(stages))[::-1]
    shades = [C["quantum_soft"], C["quantum_soft"], C["quantum_mid"],
              C["quantum_mid"], C["quantum"]]
    ax.barh(ys, [n for _, n in stages], height=0.58, color=shades, edgecolor="none")
    ax.set_yticks(ys)
    ax.set_yticklabels([s for s, _ in stages])
    ax.set_xlim(0, max(n for _, n in stages) * 1.16)
    ax.set_xticks([0, 200, 400, 600, 800])
    grid(ax, "x")
    save(fig, "funnel")
    print(f"    funnel: {stages}")

    # ------------------------------------------- b  by year: usable and tested
    fig, ax = new_component(FIG_TASKS, "byyear")
    rows_by_year = sorted(pipeline, key=lambda r: r["year"])
    years = [r["year"] for r in rows_by_year]
    # Two different denominators: usable out of that year's bounties, tested out
    # of that year's usable tasks.
    usable_pct = [100 * int(r["usable_as_task"]) / int(r["bounties_listed"])
                  for r in rows_by_year]
    tested_pct = [100 * int(r["solution_changes_tests"]) / int(r["usable_as_task"])
                  for r in rows_by_year]
    xs = np.arange(len(years))
    ax.plot(xs, usable_pct, "-o", color=C["quantum"], ms=3.0, lw=1.2)
    ax.plot(xs, tested_pct, "--s", color=C["quantum_soft"], ms=2.8, lw=1.1)
    ax.set_xticks(xs)
    ax.set_xticklabels([y[2:] for y in years])
    ax.set_xlim(-0.4, len(years) - 0.6)
    ax.set_ylim(0, 106)          # headroom so the 100 tick label is not clipped
    ax.set_yticks([0, 50, 100])
    grid(ax, "y")
    save(fig, "byyear")
    print(f"    usable%: {[round(v) for v in usable_pct]}  "
          f"tested%: {[round(v) for v in tested_pct]}")

    # ------------------------------- c  how each workflow task is performed (Q55)
    tasks55 = read("survey_tasks.csv")
    # Survey order, which runs from reading to writing to hardware, reversed so
    # that the first task sits at the top.
    short = {"Discovering & summarizing research papers (e.g., arXiv)": "research papers",
             "Learning new quantum concepts or SDKs": "concepts and SDKs",
             "Writing quantum circuits or algorithm code": "writing circuit code",
             "Debugging or optimizing quantum code": "debugging and optimizing",
             "Generating code documentation": "documentation",
             "Hardware calibration or signal/pulse tuning": "hardware calibration"}
    # Drawn as a connected pair of points rather than as two more bars. The two
    # shares are not parts of a whole, since a respondent can report both modes
    # for one task, and the distance between the points is what the panel is
    # about.
    fig, ax = new_component(FIG_TASKS, "surveytasks")
    rows55 = [r for r in tasks55 if r["task"] in short]
    ys = np.arange(len(rows55))[::-1]
    ai = [float(r["ai_pct_of_doers"]) for r in rows55]
    man = [float(r["manual_pct_of_doers"]) for r in rows55]
    for y, a, m in zip(ys, ai, man):
        ax.plot([m, a], [y, y], color=blend(C["quantum"], 0.42), lw=1.3, zorder=1)
        ax.plot(m, y, "o", ms=4.2, color=C["main"], zorder=3,
                markeredgecolor="white", markeredgewidth=0.45)
        ax.plot(a, y, "o", ms=4.2, color=C["quantum"], zorder=3,
                markeredgecolor="white", markeredgewidth=0.45)
    ax.set_yticks(ys)
    ax.set_yticklabels([short[r["task"]] for r in rows55])
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 50, 100])
    # Headroom above the top row for the two direct labels the deck places there.
    ax.set_ylim(-0.6, len(rows55) - 0.1)
    grid(ax, "x")
    save(fig, "surveytasks")
    print(f"    survey tasks, with AI: {[round(v) for v in ai]}  "
          f"manual: {[round(v) for v in man]}  "
          f"n: {[r['does_task'] for r in rows55]}")

    # ------------------------- d  how AI-generated code is verified (Q56), n = 294
    v = read("survey_verification.csv")
    order = ["Manual reviews", "Automated tests", "Automation verification",
             "Formal verification", "Never do"]
    vals = [float(next(r for r in v if r["method"] == o)["percent_of_answered"])
            for o in order]
    labels = ["manual review", "automated tests", "automation verification",
              "formal verification", "no verification"]
    # The last row is the share reporting no verification at all, which is the
    # one category that is not a method; the accent color marks that difference.
    cols = [C["quantum"]] * 4 + [C["accent"]]
    fig, ax = new_component(FIG_TASKS, "surveyverify")
    ys = np.arange(len(order))[::-1]
    for y, v, col in zip(ys, vals, cols):
        ax.plot([0, v], [y, y], color=blend(col, 0.45), lw=1.0, zorder=1)
        ax.plot(v, y, "o", ms=4.0, color=col, zorder=3,
                markeredgecolor="white", markeredgewidth=0.4)
    ax.set_yticks(ys)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_ylim(-0.6, len(order) - 0.4)
    grid(ax, "x")
    save(fig, "surveyverify")
    print(f"    survey verification: {dict(zip(labels, [round(x, 1) for x in vals]))}")

    # ------------------------------------- e  agreement statements (Q59), stacked
    # Shares are taken over the respondents who placed themselves on the scale,
    # so the "not applicable" column is out of the denominator and each bar runs
    # to 100. The two disagree levels are merged; both are small.
    agree = read("survey_agreement.csv")
    short59 = {"AI assistants help me do quantum computing work more efficiently and effectively.":
               "AI assistants make me more efficient",
               "The information generated by AI assistants regarding quantum computing concepts is accurate.":
               "AI information on concepts is accurate",
               "The code generated by AI assistants is accurate.":
               "AI-generated code is accurate"}
    rows59 = [next(r for r in agree if r["statement"] == k) for k in short59]
    fig, ax = new_component(FIG_TASKS, "surveyagree")
    ys = np.arange(len(rows59))[::-1]

    def pct(r, *keys):
        return 100 * sum(int(r[k]) for k in keys) / int(r["rated"])

    # Diverging: zero sits at the boundary between agreeing and not agreeing, so
    # the reach to the right is the agreement on each statement and the three
    # statements can be compared at a glance.
    agr = [pct(r, "agree") for r in rows59]
    sagr = [pct(r, "strongly_agree") for r in rows59]
    neu = [pct(r, "neutral") for r in rows59]
    dis = [pct(r, "disagree", "strongly_disagree") for r in rows59]
    ax.barh(ys, agr, height=0.54, color=C["quantum_mid"], edgecolor="none")
    ax.barh(ys, sagr, left=agr, height=0.54, color=C["quantum"], edgecolor="none")
    ax.barh(ys, [-v for v in neu], height=0.54, color=C["main_soft"],
            edgecolor="none")
    ax.barh(ys, [-v for v in dis], left=[-v for v in neu], height=0.54,
            color=C["accent"], edgecolor="none")
    ax.axvline(0, color=C["ink"], lw=0.7, zorder=4)

    # The key is the four words in their own colors, placed by the deck above the
    # panel in the order the segments appear from left to right. Swatches were
    # tried and dropped, since anything drawn above the axes falls outside this
    # component's canvas and is clipped on export.
    ax.set_yticks(ys)
    ax.set_yticklabels([short59[r["statement"]] for r in rows59])
    ax.set_xlim(-45, 92)
    ax.set_xticks([-25, 0, 25, 50, 75])
    ax.set_xticklabels(["25", "0", "25", "50", "75"])
    ax.set_ylim(-0.6, len(rows59) - 0.4)
    grid(ax, "x")
    save(fig, "surveyagree")
    print(f"    survey agreement, agree/strongly/neutral/disagree: "
          f"{[[round(v, 1) for v in s] for s in (agr, sagr, neu, dis)]}"
          f"  n: {[r['rated'] for r in rows59]}")


def make_emf(soffice="soffice"):
    """EMF fallback per component, for renderers older than PowerPoint 2019."""
    svgs = sorted(COMP.glob("*.svg"))
    subprocess.run([soffice, "--headless", "--convert-to", "emf",
                    "--outdir", str(COMP), *[str(p) for p in svgs]],
                   check=True, capture_output=True)
    missing = [p.stem for p in svgs if not p.with_suffix(".emf").exists()]
    if missing:
        raise RuntimeError(f"EMF not produced for {missing}")
    print(f"  {len(svgs)} EMF fallbacks")


if __name__ == "__main__":
    print("corpus components")
    corpus_components()
    print("disclosure components")
    disclosure_components()
    print("task components")
    task_components()
    # The EMF fallbacks matter only when the panels are assembled into a
    # PowerPoint deck, which needs LibreOffice. Drawing the panels does not, so
    # this step is opt-in and the script runs with matplotlib alone.
    if "--emf" in sys.argv:
        print("fallbacks")
        make_emf()
