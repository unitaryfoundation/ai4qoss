#!/usr/bin/env python
"""Random circuits or structured ones: what do the test suites exercise?

A coding assistant asked for test circuits tends to produce random ones, closer to
fuzzing, while the circuits worth getting right carry structured entanglement and
correlation. This counts which kind the projects' own tests use, as a baseline for
that comparison.

Random construction is counted from calls that draw a circuit, unitary, state, or
Clifford at random. Structured construction is counted from named states and routines
whose entanglement pattern is fixed: GHZ, Bell, W, QFT, and the standard variational
ansatz families. Both are counted per occurrence in test files.

A named construction is evidence about intent; a random draw may still be seeded and
checked against a reference. The counts describe what appears in the source, not what a
maintainer meant by it.

Output: out/circuit_kind.csv
"""
import csv
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out, repos  # noqa: E402

REPOS = repos()
OUT = out("test_suite_audit")
FOLDER = {"Qiskit": "qiskit", "Cirq": "Cirq", "PennyLane": "pennylane"}

RANDOM = re.compile(
    r"\brandom_circuit\b|\brandom_unitary\b|\brandom_statevector\b|"
    r"\brandom_density_matrix\b|\brandom_clifford\b|\brandom_pauli\b|"
    r"\brandom_hermitian\b|\brandom_quantum_state\b|\brandom_state\b|"
    r"\btestlib\.random\b|\brandom_two_qubit_circuit\b|\brandom_gate\b|"
    r"\brandom_qubit\b|\brandom_superposition\b", re.I)
STRUCTURED = re.compile(
    r"\bGHZ\b|\bbell_state\b|\bbell_pair\b|\bBellState\b|\bW_state\b|\bw_state\b|"
    r"\bQFT\b|\bquantum_fourier\b|\bEfficientSU2\b|\bRealAmplitudes\b|"
    r"\bTwoLocal\b|\bExcitationPreserving\b|\bStronglyEntanglingLayers\b|"
    r"\bBasicEntanglerLayers\b|\bgrover\b|\bphase_estimation\b|\bQPE\b|"
    r"\bsurface_code\b|\brepetition_code\b|\btoric\b", re.I)

rows = []
print(f"{'project':<12}{'test files':>11}{'random':>9}{'structured':>12}"
      f"{'random share':>14}")
tot_r = tot_s = 0
for proj, folder in FOLDER.items():
    root = REPOS / folder
    r = s = files = 0
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
        files += 1
        r += len(RANDOM.findall(text))
        s += len(STRUCTURED.findall(text))
    tot_r += r
    tot_s += s
    share = 100 * r / (r + s) if (r + s) else 0
    print(f"{proj:<12}{files:>11}{r:>9}{s:>12}{share:>13.0f}%")
    rows.append([proj, files, r, s, round(share, 1)])

share = 100 * tot_r / (tot_r + tot_s)
print(f"{'combined':<12}{'':>11}{tot_r:>9}{tot_s:>12}{share:>13.0f}%")
rows.append(["combined", "", tot_r, tot_s, round(share, 1)])

with open(OUT / "circuit_kind.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["project", "test_files", "random_constructions",
                "structured_constructions", "random_share_pct"])
    w.writerows(rows)
print(f"\nwrote {OUT}/circuit_kind.csv")
