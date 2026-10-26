# Copyright 2026 Unitary Foundation
# SPDX-License-Identifier: Apache-2.0

"""Single source of truth for the paper's figure style and composite layout.

Imported by `components.py` (which draws geometry-only vector components) and by
`build_deck.py` (which assembles them on a PowerPoint slide and adds every word as
native, editable text). Both read the same numbers here, so a label placed in the
deck lands where the component's plotting area actually is.

Division of labor follows the component-and-assembly workflow: components carry
shapes, lines, fills and the data-coupled tick labels; the deck carries axis names,
annotations, direct series labels, panel tags, and the summary tables.
"""
import matplotlib as mpl

# ----------------------------------------------------------------- palette
# Semantic, not decorative: one family for quantum, one neutral for mainstream,
# one accent reserved for the qualifications the figures must not hide.
C = {
    "quantum": "#31507f",
    "quantum_mid": "#4a6fa5",
    "quantum_soft": "#8fa9cd",
    "main": "#7d838c",
    "main_soft": "#b6bac0",
    "accent": "#ab5f3c",
    "ink": "#252a33",
    "rule": "#d5d8dc",
    "grid": "#e8eaec",
}

# Per-package series style, shared by every panel that draws one line per project
# (Fig. 1b, 1c, 2a) so a package looks the same wherever it appears. The three
# quantum packages stay in the blue family but are separated by lightness, dash
# pattern and marker, so they remain distinct in grayscale; mainstream projects
# are gray and dotted.
PKG = {
    "Qiskit":    {"color": "#1d3461", "ls": "-",               "marker": "o"},
    "PennyLane": {"color": "#3f7fc8", "ls": (0, (4.0, 1.6)),   "marker": "s"},
    "Cirq":      {"color": "#86b6e3", "ls": (0, (5.0, 1.4, 1.2, 1.4)), "marker": "^"},
    "numpy":     {"color": "#6f757e", "ls": (0, (1.0, 1.3)),   "marker": "o"},
    "scipy":     {"color": "#adb2b9", "ls": (0, (1.0, 1.3)),   "marker": "o"},
}


def blend(hex_color, alpha, bg="#ffffff"):
    """Flatten a translucent color against the background.

    EMF has no alpha channel, so LibreOffice rasterizes any translucent element
    when it converts a component to the EMF fallback, and PowerPoint builds that
    raster into its PDF. Pre-blending keeps every path vector on both routes.
    """
    fg = [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(bg[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(alpha * f + (1 - alpha) * v):02x}"
                         for f, v in zip(fg, b))


MM = 1 / 25.4
WIDTH = 183 * MM                       # double column, 7.20 in

# Plot-area margins as a fraction of each component's own size. Fixed rather than
# tight_layout so the geometry does not shift between regenerations and the labels
# placed in the deck stay valid.
FONT_TICK = 6.5


def apply_style():
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "svg.fonttype": "path",        # glyph outlines: renderer-independent
        "pdf.fonttype": 42,
        "font.size": FONT_TICK,
        "xtick.labelsize": FONT_TICK,
        "ytick.labelsize": FONT_TICK,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.linewidth": 0.7,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "xtick.major.size": 2.4,
        "ytick.major.size": 2.4,
        "xtick.major.pad": 1.8,
        "ytick.major.pad": 1.8,
        "lines.linewidth": 1.1,
        "legend.frameon": False,
    })


# ------------------------------------------------------------------ layouts
# Every entry is (x, y, w, h) in inches on the slide, plus the fraction of that box
# taken by the axes. `axes` is (left, bottom, right, top) as fractions of the
# component, matching subplots_adjust, so the deck can compute the true plot-area
# rectangle for label placement.

# Survival-panel key: axes fractions, shared so the component draws the line
# segments and the deck places the words against them.
SURVIVAL_KEY_X = (0.0, 0.215, 0.485, 0.635, 0.825)
SURVIVAL_KEY_Y = 0.065
# Fig. 2a: the deck writes each project's label at these rows (fractions from the
# bottom of the plot area); the component draws a line sample to the left of each.
QUBIT_KEY_Y = (0.365, 0.312, 0.259)
QUBIT_KEY_X = 0.565          # line samples start right of the 20-qubit rule
QUBIT_LABEL_X = 0.645        # project labels start right of the samples

FIG_CORPUS = {
    "size": (WIDTH, 3.36),   # the exported PDF is cropped to content by export_pdf.sh
    "components": {
        "corpus_github": {"box": (0.12, 0.30, 2.92, 2.62),
                          "axes": (0.255, 0.075, 0.995, 0.995)},
        "corpus_pypi":   {"box": (3.10, 0.30, 1.42, 2.62),
                          "axes": (0.025, 0.075, 0.985, 0.995)},
        "survival":      {"box": (4.72, 0.30, 2.42, 1.30),
                          "axes": (0.135, 0.185, 0.995, 0.985)},
        "churn":         {"box": (4.72, 2.00, 2.42, 1.06),
                          "axes": (0.245, 0.225, 0.995, 0.985)},
    },
    "table_top": 3.28,
    "table_left": 0.30,
    "table_cols": (0.0, 2.02, 2.98, 3.94, 4.66),
    "table_row_h": 0.175,
}

FIG_DISCLOSURE = {
    "size": (WIDTH, 3.50),
    "components": {
        "qubits":       {"box": (0.12, 0.30, 3.06, 2.86),
                         "axes": (0.185, 0.135, 0.995, 0.99)},
        "disclosure":   {"box": (3.42, 0.30, 3.72, 1.30),
                         "axes": (0.105, 0.235, 0.965, 0.985)},
        # c and d start 0.18 higher than b's box ends and grow by the same amount,
        # so their bottoms stay level with panel a and the gap under b closes. The
        # axes fractions keep the same absolute margins as at the old height, which
        # leaves everything the deck places below these panels where it was.
        "policy":       {"box": (3.42, 1.80, 1.72, 1.36),
                         "axes": (0.205, 0.152, 0.995, 0.987)},
        "concentration": {"box": (5.36, 1.80, 1.78, 1.36),
                          "axes": (0.335, 0.152, 0.995, 0.987)},
    },
    "table_top": 3.54,
    "table_left": 0.30,
    "table_cols": (0.0, 2.02, 3.06, 4.28),
    "table_row_h": 0.175,
}


# Agreement-panel key: axes fractions giving where the deck puts each word, in the
# order the segments run from left to right, and how far above the axes the row sits.
AGREE_KEY_X = (0.0, 0.215, 0.410, 0.690)
AGREE_KEY_Y = 1.17

FIG_TASKS = {
    "size": (WIDTH, 3.98),
    "components": {
        # Two rows. The first holds the benchmark pipeline and the task panel,
        # with the year panel narrow because it carries ten points. The second
        # holds the two survey panels whose categories are written out, so their
        # left margins are wide.
        "funnel":    {"box": (0.12, 0.34, 2.56, 1.56),
                      "axes": (0.375, 0.170, 0.975, 0.99)},
        "byyear":    {"box": (2.90, 0.34, 1.60, 1.56),
                      "axes": (0.265, 0.170, 0.965, 0.99)},
        "surveytasks":  {"box": (4.62, 0.34, 2.46, 1.56),
                         "axes": (0.495, 0.170, 0.945, 0.99)},
        "surveyverify": {"box": (0.12, 2.34, 2.96, 1.40),
                         "axes": (0.390, 0.200, 0.950, 0.99)},
        "surveyagree":  {"box": (3.12, 2.34, 3.96, 1.40),
                         "axes": (0.408, 0.200, 0.977, 0.99)},
    },
    "table_top": 4.02,
    "table_left": 0.30,
    "table_cols": (0.0, 2.30, 3.40, 4.60),
    "table_row_h": 0.205,
}


def plot_rect(fig, name):
    """True plotting-area rectangle of a component, in slide inches.

    Returns (x0, y0, x1, y1) with y measured from the top of the slide, which is
    the coordinate system PowerPoint text boxes use.
    """
    c = fig["components"][name]
    bx, by, bw, bh = c["box"]
    al, ab, ar, at = c["axes"]
    return (bx + al * bw, by + (1 - at) * bh, bx + ar * bw, by + (1 - ab) * bh)
