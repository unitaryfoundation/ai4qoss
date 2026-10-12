#!/usr/bin/env python
"""Does test size follow what the code under test needs, or a shared ceiling?

A pooled statement such as "99 percent at or below 20 qubits" mixes two situations.
Some tests need two qubits and are complete at two, such as one on argument handling
or on the matrix of a single gate. Others use two qubits because more is
unaffordable. The pooled distribution cannot tell them apart.

This splits the counts by the module the test file sits in. If size follows the code
under test, modules differ: simulation and error correction should reach further than
argument parsing or visualization. If a common ceiling dominates, the modules look
alike whatever they cover.

Same patterns and caveats as run.py; this adds the file path of each occurrence.

Output: out/qubit_by_module.csv
"""
import csv
import re
import sys
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
MAXQ = 200

# Grouped by what the code under test does, from the path of the test file.
THEME = [
    ("simulation and states", r"simulat|statevector|density|state_vector|aer|quantum_info|"
                              r"stabilizer|clifford|state\b"),
    ("error correction", r"error_correct|qec|code|decoder|surface|repetition|parity"),
    ("compilation and transpiling", r"transpil|compil|passes|routing|layout|synthesis|"
                                    r"optimiz|scheduling|dagcircuit"),
    ("circuits and gates", r"circuit|gate|operation|instruction|register|ops\b|library"),
    ("algorithms and applications", r"algorithm|chemistry|optimization_app|finance|"
                                    r"machine_learning|qaoa|vqe|template"),
    ("hardware and providers", r"provider|backend|device|pulse|calibrat|hardware|"
                               r"runtime|engine|ionq|google"),
    ("io, visualization, docs", r"visual|draw|qasm|qpy|serializ|json|latex|text\b|"
                                r"converters|utils"),
]


def theme_of(path):
    p = str(path).lower()
    for name, pat in THEME:
        if re.search(pat, p):
            return name
    return "other"


rows = []
per = defaultdict(list)
for proj, pats in PATTERNS.items():
    root = REPOS / FOLDER[proj]
    for p in root.rglob("*.py"):
        parts = p.parts
        if ".git" in parts:
            continue
        if not (any(x in ("test", "tests") for x in parts) or p.name.startswith("test_")
                or p.name.endswith("_test.py")):
            continue
        try:
            text = p.read_text(errors="ignore")
        except Exception:
            continue
        rel = p.relative_to(root)
        found = []
        for pat in pats:
            for m in re.finditer(pat, text):
                n = int(m.group(1))
                if 1 <= n <= MAXQ:
                    found.append(n)
        if proj == "Cirq":
            for m in re.finditer(GRID, text):
                n = int(m.group(1)) * int(m.group(2))
                if 1 <= n <= MAXQ:
                    found.append(n)
        if found:
            th = theme_of(rel)
            per[th].extend(found)
            per[(proj, th)].extend(found)

print(f"{'area of the code under test':<32}{'n':>7}{'median':>8}{'p90':>6}"
      f"{'p99':>6}{'max':>6}{'>20 qubits':>12}")
summary = []
for name, _ in THEME + [("other", "")]:
    v = sorted(per.get(name, []))
    if not v:
        continue
    q = lambda f: v[min(int(f * len(v)), len(v) - 1)]
    over = sum(1 for x in v if x > 20)
    print(f"{name:<32}{len(v):>7}{q(0.5):>8}{q(0.9):>6}{q(0.99):>6}{v[-1]:>6}"
          f"{100 * over / len(v):>11.1f}%")
    summary.append([name, len(v), q(0.5), q(0.9), q(0.99), v[-1],
                    round(100 * over / len(v), 2)])

with open(OUT / "qubit_by_module.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["area", "instances", "median", "p90", "p99", "max", "pct_above_20"])
    w.writerows(summary)

allv = sorted(x for k, v in per.items() if isinstance(k, str) for x in v)
print(f"\npooled: n={len(allv)} median={allv[len(allv)//2]} "
      f"above 20 qubits={100*sum(1 for x in allv if x>20)/len(allv):.1f}%")
print(f"\nwrote {OUT}/qubit_by_module.csv")
