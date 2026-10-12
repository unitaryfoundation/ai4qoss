#!/usr/bin/env python
"""Test-suite audit: how large are the circuits that quantum test suites actually run?

Method. Scan the test files of the major frameworks for literal qubit counts in the
constructors that create qubits, and report the distribution. This locates, empirically,
the circuit sizes at which these projects verify their own code.

Patterns (literal integers only; expressions and parameterized fixtures are skipped):
  Qiskit     QuantumCircuit(n), QuantumRegister(n), num_qubits=n
  Cirq       LineQubit.range(n), GridQubit.rect(a, b) -> a*b, LineQid.range(n)
  PennyLane  wires=n, qml.device(..., wires=n)

Caveats recorded with the results:
  - Only literal integers are counted. Tests that parameterize over sizes, or build
    circuits programmatically, are invisible to this measure.
  - A qubit count in a constructor is not always the size of the simulated state.
  - The measure describes routine unit tests, not the separate large-scale benchmarks
    some projects run outside their test suite.

Output: out/qubit_counts.csv, out/qubit_summary.csv
"""
import csv, re, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out, repos  # noqa: E402

REPOS = repos()
OUT = out("test_suite_audit")

PATTERNS = {
    "Qiskit": [r"QuantumCircuit\(\s*(\d+)\s*[,)]", r"QuantumRegister\(\s*(\d+)\s*[,)]",
               r"num_qubits\s*=\s*(\d+)"],
    "Cirq": [r"LineQubit\.range\(\s*(\d+)\s*\)", r"LineQid\.range\(\s*(\d+)\s*[,)]"],
    "PennyLane": [r"wires\s*=\s*(\d+)"],
}
GRID = r"GridQubit\.rect\(\s*(\d+)\s*,\s*(\d+)\s*[,)]"
FOLDER = {"Qiskit": "qiskit", "Cirq": "Cirq", "PennyLane": "pennylane"}

MAXQ = 200  # ignore absurd literals (usually unrelated constants caught by wires=)

counts = defaultdict(Counter)
for proj, pats in PATTERNS.items():
    root = REPOS / FOLDER[proj]
    for p in root.rglob("*.py"):
        parts = p.parts
        if ".git" in parts:
            continue
        # test files only
        if not (any(x in ("test", "tests") for x in parts) or p.name.startswith("test_")
                or p.name.endswith("_test.py")):
            continue
        try:
            text = p.read_text(errors="ignore")
        except Exception:
            continue
        for pat in pats:
            for m in re.finditer(pat, text):
                n = int(m.group(1))
                if 1 <= n <= MAXQ:
                    counts[proj][n] += 1
        if proj == "Cirq":
            for m in re.finditer(GRID, text):
                n = int(m.group(1)) * int(m.group(2))
                if 1 <= n <= MAXQ:
                    counts[proj][n] += 1

# ------------------------------------------------------------------ write
with open(OUT / "qubit_counts.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["project", "qubits", "occurrences"])
    for proj in sorted(counts):
        for n in sorted(counts[proj]):
            w.writerow([proj, n, counts[proj][n]])


def pct(sorted_vals, q):
    if not sorted_vals:
        return ""
    i = min(int(q * len(sorted_vals)), len(sorted_vals) - 1)
    return sorted_vals[i]


with open(OUT / "qubit_summary.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["project", "instances", "median", "p90", "p99", "max",
                "pct_le_10", "pct_le_20", "pct_le_30"])
    print(f"{'project':<11}{'n':>7}{'median':>8}{'p90':>6}{'p99':>6}{'max':>6}"
          f"{'<=10q':>8}{'<=20q':>8}{'<=30q':>8}")
    for proj in sorted(counts):
        vals = sorted(v for n, c in counts[proj].items() for v in [n] * c)
        tot = len(vals)
        le10 = 100 * sum(1 for v in vals if v <= 10) / tot
        le20 = 100 * sum(1 for v in vals if v <= 20) / tot
        le30 = 100 * sum(1 for v in vals if v <= 30) / tot
        w.writerow([proj, tot, pct(vals, .5), pct(vals, .9), pct(vals, .99), vals[-1],
                    round(le10, 1), round(le20, 1), round(le30, 1)])
        print(f"{proj:<11}{tot:>7}{pct(vals,.5):>8}{pct(vals,.9):>6}{pct(vals,.99):>6}"
              f"{vals[-1]:>6}{le10:>7.1f}%{le20:>7.1f}%{le30:>7.1f}%")

# combined
allvals = sorted(v for proj in counts for n, c in counts[proj].items() for v in [n] * c)
print(f"\ncombined: {len(allvals)} instances, median {pct(allvals,.5)} qubits, "
      f"{100*sum(1 for v in allvals if v<=20)/len(allvals):.1f}% at or below 20 qubits, "
      f"{100*sum(1 for v in allvals if v<=30)/len(allvals):.1f}% at or below 30")
print(f"wrote {OUT}/qubit_counts.csv, qubit_summary.csv")
