#!/usr/bin/env python
"""API survival: how much of a project's public API from year t still exists today.

Motivation. A language model writes code against the API it saw in training, which is
the API as it stood some time in the past. This measures directly how much of that API
is still there, without needing model API access: take the public API surface of each
project at one release per year, and check what fraction of it still exists in the
project's latest release.

Method. For each project, pick the last stable release tag in each calendar year, export
that tree, and reconstruct the importable public namespace with `ast`. A symbol is
identified by the import path a user would write, `scipy.optimize.minimize`, not by the
file that defines it: every project keeps its implementations in private modules and
re-exports them, so counting definitions where they are written would measure internal
layout rather than the API. Every module is parsed, including private ones; the public
namespace of a public module is `__all__` when present, otherwise the public names it
defines or imports, with `from ._x import *` expanded through the same rule. Public
methods are added for names that resolve to a class definition.

Two measures, reported as bounds:

  strict   symbol survives only if the same import path exists in the latest release.
           A symbol that moved to a different public module counts as lost. This is what
           a snippet using the full import path experiences.
  loose    symbol survives if its bare name (`minimize`, `QuantumCircuit.qasm`) exists
           anywhere in the latest public namespace. Moves between modules are forgiven;
           this is closer to code that imports from the package top level. Both measures
           run over the same denominator, so loose is always at least strict.

The truth for a real snippet lies between the two, since some moves are covered by
re-exports and some are not.

Caveats recorded with the results:
  - Static resolution. Names created at runtime (dynamic `__getattr__`, generated
    wrappers) are missed, and a lazy-loading `__init__` that lists submodules in
    `__all__` without importing them is followed only as far as the source states.
  - Signature changes are invisible: a function that survives by name may have gained a
    required argument or changed its return type.
  - Deprecated-but-present symbols count as surviving. Survival here is "still imports",
    not "still recommended".
  - The reference point is each project's latest stable tag, not its default branch:
    scipy's main branch is part-way through a lazy-loading rewrite of its __init__ files
    that hides about a thousand symbols from static resolution. The reference year itself
    is omitted, since it would be compared against itself.
  - Python 2 sources do not parse under Python 3. numpy before 2014 and scipy before 2013
    lose 20% to 57% of their files this way; those years are reported with the unparsed
    fraction and excluded from the summary table.
  - The size of the measured surface moves by tens of percent between adjacent releases
    when a project changes its `__all__` or re-export conventions (scipy 1.9, PennyLane
    0.43). Compare projects within a year and trends across several years, not single
    year-to-year steps.

Input: ../_repos/<project> as full clones with tags
  git clone https://github.com/Qiskit/qiskit
  git clone https://github.com/PennyLaneAI/pennylane
  git clone https://github.com/quantumlib/Cirq
  git clone https://github.com/numpy/numpy
  git clone https://github.com/scipy/scipy

Output: out/api_survival.csv, out/api_survival_tags.csv
"""
import ast
import csv
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out, repos, tmp  # noqa: E402

REPOS = repos()
TMP = tmp()
OUT = out("api_survival")

# project -> (clone dir, package roots relative to the repo)
PROJECTS = [
    ("Qiskit", "qiskit", ["qiskit"]),
    ("PennyLane", "pennylane", ["pennylane"]),
    ("Cirq", "Cirq", ["cirq-core/cirq", "cirq-google/cirq_google"]),
    ("numpy", "numpy", ["numpy"]),
    ("scipy", "scipy", ["scipy"]),
]

STABLE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
SKIP_DIR = {"test", "tests", "testing", "_test", "doc", "docs", "examples", "benchmarks",
            "conftest.py", "setup.py", "site-packages", "vendored", "_vendor"}


def git(repo, *args):
    return subprocess.run(["git", "-C", str(REPOS / repo), *args],
                          capture_output=True, text=True, check=True).stdout


def yearly_tags(repo):
    """Last stable tag of each calendar year -> {year: (tag, date)}."""
    out = git(repo, "for-each-ref", "--sort=creatordate",
              "--format=%(refname:short)\t%(creatordate:short)", "refs/tags")
    per = {}
    for line in out.splitlines():
        if "\t" not in line:
            continue
        tag, date = line.split("\t", 1)
        if not STABLE.match(tag.strip()):
            continue
        per[date[:4]] = (tag.strip(), date.strip())  # later tags overwrite earlier ones
    return per


def export(repo, tag, dest):
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    p1 = subprocess.Popen(["git", "-C", str(REPOS / repo), "archive", tag],
                          stdout=subprocess.PIPE)
    subprocess.run(["tar", "-x", "-C", str(dest)], stdin=p1.stdout, check=True)
    p1.stdout.close()
    p1.wait()


def public(name):
    return bool(name) and not name.startswith("_")


def literal_strings(node):
    """Set of strings if `node` is a literal list/tuple/set of strings, else None."""
    if not isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return None
    out = set()
    for e in node.elts:
        if isinstance(e, ast.Constant) and isinstance(e.value, str):
            out.add(e.value)
        else:
            return None
    return out


def flatten(body):
    """Module-level statements, descending into if/try blocks.

    numpy guards its top-level imports with `if __NUMPY_SETUP__: ... else: ...` and
    several projects wrap optional imports in try/except, so the names they bind are not
    direct children of the module body.
    """
    for node in body:
        yield node
        if isinstance(node, ast.If):
            yield from flatten(node.body)
            yield from flatten(node.orelse)
        elif isinstance(node, ast.Try):
            yield from flatten(node.body)
            yield from flatten(node.orelse)
            yield from flatten(node.finalbody)
            for h in node.handlers:
                yield from flatten(h.body)


def module_name(rel_parts):
    """('scipy', 'optimize', '__init__.py') -> 'scipy.optimize'."""
    parts = list(rel_parts)
    parts[-1] = parts[-1][:-3]  # drop .py
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def parse_tree(tree_root, pkg_roots):
    """Parse every module, private ones included.

    Returns {module: {"defs": {name: ast node}, "all": set|None,
                      "from": {name: (src_module, src_name)}, "star": [src_module]}}
    """
    mods, stats = {}, {"parsed": 0, "failed": 0}
    for pkg in pkg_roots:
        base = tree_root / pkg
        if not base.exists():
            continue
        top = pkg.split("/")[-1]
        for path in base.rglob("*.py"):
            rel = (top,) + path.relative_to(base).parts
            if any(p in SKIP_DIR for p in rel):
                continue
            try:
                tree = ast.parse(path.read_text(errors="ignore"))
            except (SyntaxError, ValueError):
                stats["failed"] += 1   # Python 2 sources fail here
                continue
            stats["parsed"] += 1
            mod = module_name(rel)
            m = {"defs": {}, "all": None, "from": {}, "star": []}
            all_literal, all_dynamic = set(), False
            for node in flatten(tree.body):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    m["defs"][node.name] = node
                elif isinstance(node, (ast.Assign, ast.AugAssign)):
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    for t in targets:
                        if not isinstance(t, ast.Name):
                            continue
                        if t.id == "__all__":
                            # Only a literal list of strings is usable. scipy and numpy
                            # build __all__ from dir() or extend it with submodule lists;
                            # treating those as empty would erase the whole namespace.
                            lit = literal_strings(node.value)
                            if lit is None:
                                all_dynamic = True
                            else:
                                all_literal |= lit
                        else:
                            m["defs"].setdefault(t.id, node)
                elif isinstance(node, ast.ImportFrom):
                    src = node.module or ""
                    if node.level:  # relative import
                        pkg_parts = mod.split(".")
                        if path.name != "__init__.py":
                            pkg_parts = pkg_parts[:-1]
                        up = node.level - 1
                        base_parts = pkg_parts[:len(pkg_parts) - up] if up else pkg_parts
                        src = ".".join(base_parts + ([src] if src else []))
                    for a in node.names:
                        if a.name == "*":
                            m["star"].append(src)
                        else:
                            m["from"][a.asname or a.name] = (src, a.name)
                elif isinstance(node, ast.Import):
                    for a in node.names:
                        local = a.asname or a.name.split(".")[0]
                        target = a.name if a.asname else a.name.split(".")[0]
                        m["from"][local] = (target, None)  # module alias
            if all_literal and not all_dynamic:
                m["all"] = all_literal
            mods[mod] = m
    return mods, stats


def exported(mods, mod, cache, tops, stack=()):
    """Public names a module exposes, following __all__ and star imports.

    Without `__all__`, re-exported names count only when they come from inside the
    project: `import os` also binds a module attribute, but no user writes
    `from scipy.optimize import os`.
    """
    if mod in cache:
        return cache[mod]
    if mod in stack or mod not in mods:
        return set()
    m = mods[mod]
    if m["all"] is not None:
        names = {n for n in m["all"] if public(n)}
    else:
        names = {n for n in m["defs"] if public(n)}
        names |= {n for n, (src, sn) in m["from"].items()
                  if public(n) and sn is not None and src.split(".")[0] in tops}
        for src in m["star"]:
            names |= exported(mods, src, cache, tops, stack + (mod,))
    cache[mod] = names
    return names


def resolve(mods, mod, name, depth=0):
    """Follow re-export chains to the ast node defining `name`, or None."""
    if depth > 12 or mod not in mods:
        return None
    m = mods[mod]
    if name in m["defs"]:
        return m["defs"][name]
    if name in m["from"]:
        src, src_name = m["from"][name]
        if src_name is None:
            return None
        return resolve(mods, src, src_name, depth + 1)
    for src in m["star"]:
        node = resolve(mods, src, name, depth + 1)
        if node is not None:
            return node
    return None


def surface(tree_root, pkg_roots):
    """Importable public API, as {import path: bare name}.

    'top' holds only names bound in a module namespace ('scipy.optimize.minimize' ->
    'minimize'); 'all' adds the public methods of public classes
    ('qiskit.QuantumCircuit.measure' -> 'QuantumCircuit.measure'). Methods dominate the
    totals, so the two are reported separately. Keeping the map from import path to bare
    name lets the strict and loose measures share a denominator.
    """
    mods, stats = parse_tree(tree_root, pkg_roots)
    tops = {p.split("/")[-1] for p in pkg_roots}
    cache = {}
    out = {"top": {}, "all": {}, "stats": stats}
    for mod in mods:
        if any(not public(p) for p in mod.split(".")):
            continue  # private module: reachable only through a re-export
        for name in exported(mods, mod, cache, tops):
            out["top"][f"{mod}.{name}"] = name
            out["all"][f"{mod}.{name}"] = name
            node = resolve(mods, mod, name)
            if isinstance(node, ast.ClassDef):
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                            and public(sub.name):
                        out["all"][f"{mod}.{name}.{sub.name}"] = f"{name}.{sub.name}"
    return out


def main():
    TMP.mkdir(exist_ok=True)
    rows, tag_rows = [], []

    for proj, repo, pkgs in PROJECTS:
        if not (REPOS / repo).exists():
            print(f"  skip {proj}: no clone at {REPOS / repo}", file=sys.stderr)
            continue
        try:
            tags = yearly_tags(repo)
        except subprocess.CalledProcessError as e:
            print(f"  skip {proj}: {e}", file=sys.stderr)
            continue
        if not tags:
            print(f"  skip {proj}: no stable tags (clone may still be shallow)",
                  file=sys.stderr)
            continue

        # Reference point is the latest stable release, not the default branch. scipy's
        # main branch is mid-way through a lazy-loading rewrite of its __init__ files,
        # which hides about a thousand symbols from static resolution and would show up
        # as API loss in every year at once.
        ref_year = max(tags)
        ref_tag, ref_date = tags[ref_year]
        ref_dir = TMP / f"{repo}-ref"
        export(repo, ref_tag, ref_dir)
        now = surface(ref_dir, pkgs)
        shutil.rmtree(ref_dir)
        now_top_names = set(now["top"].values())
        now_all_names = set(now["all"].values())
        print(f"\n{proj}: reference {ref_tag} ({ref_date}), "
              f"{len(now['top'])} top-level names, {len(now['all'])} with methods, "
              f"{now['stats']['failed']} of "
              f"{now['stats']['parsed'] + now['stats']['failed']} files unparsed")

        for year in sorted(tags):
            if year == ref_year:
                continue  # would compare the reference against itself
            tag, date = tags[year]
            work = TMP / f"{repo}-{year}"
            export(repo, tag, work)
            s = surface(work, pkgs)
            shutil.rmtree(work)
            if not s["top"]:
                continue
            st = s["stats"]
            unparsed = 100 * st["failed"] / max(1, st["parsed"] + st["failed"])
            top_strict = 100 * len(set(s["top"]) & set(now["top"])) / len(s["top"])
            top_loose = 100 * sum(v in now_top_names for v in s["top"].values()) / len(s["top"])
            all_strict = 100 * len(set(s["all"]) & set(now["all"])) / len(s["all"])
            all_loose = 100 * sum(v in now_all_names for v in s["all"].values()) / len(s["all"])
            flag = "  <- unreliable" if unparsed > 5 else ""
            rows.append([proj, year, tag, date, ref_tag, len(s["top"]),
                         round(top_strict, 1), round(top_loose, 1), len(s["all"]),
                         round(all_strict, 1), round(all_loose, 1),
                         st["failed"], st["parsed"] + st["failed"], round(unparsed, 1)])
            tag_rows.append([proj, year, tag, date, len(s["top"]), len(s["all"])])
            print(f"  {year} {tag:<12} {len(s['top']):>6} names  "
                  f"top-level: strict {top_strict:>5.1f}%  loose {top_loose:>5.1f}%"
                  f"   methods incl.: strict {all_strict:>5.1f}%"
                  f"   unparsed {unparsed:>4.1f}%{flag}")

    with open(OUT / "api_survival.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["project", "year", "tag", "tag_date", "reference_tag",
                    "toplevel_names", "toplevel_survival_strict_pct",
                    "toplevel_survival_loose_pct", "symbols_with_methods",
                    "survival_strict_pct", "survival_loose_pct",
                    "unparsed_files", "total_files", "unparsed_pct"])
        w.writerows(rows)

    with open(OUT / "api_survival_tags.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["project", "year", "tag", "date", "toplevel_names", "symbols_with_methods"])
        w.writerows(tag_rows)

    # ---------------------------------------------------------- headline summary
    print("\ntop-level public names of year t still importable at the latest release "
          "(strict / loose); years with over 5% unparsed files omitted")
    by_proj = defaultdict(dict)
    for r in rows:
        if r[13] <= 5:
            by_proj[r[0]][r[1]] = (r[6], r[7])
    years = sorted({y for p in by_proj.values() for y in p})
    print(f"{'project':<11}" + "".join(f"{y[2:]:>10}" for y in years))
    for proj in by_proj:
        line = f"{proj:<11}"
        for y in years:
            line += f"{by_proj[proj][y][0]:>4.0f}/{by_proj[proj][y][1]:<5.0f}" \
                if y in by_proj[proj] else f"{'':>10}"
        print(line)
    print(f"\nwrote {OUT}/api_survival.csv, api_survival_tags.csv")


if __name__ == "__main__":
    main()
