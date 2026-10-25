#!/usr/bin/env python
# Copyright 2026 Unitary Foundation
# SPDX-License-Identifier: Apache-2.0
"""Aggregate the per-task annotations of the candidate maintenance tasks.

The 417 candidate tasks (canonical repository and issue number, deduplicated as in
aggregates.py and attributed to the first year an issue was offered) were annotated
one by one with a maintenance task type, software domains, the technologies involved,
proposed capabilities and verification methods, and quality flags. The codebook is
CHARACTERIZATION.md in this directory. The annotations name issues and pull requests
and are not published; this script turns them into the aggregate CSVs that are, in
../../data/benchmarks/.

Inputs, both unpublished, under the working directory (see ../paths.py):
  benchmark_characterization/annotations.jsonl   one adjudicated record per task
  benchmark_characterization/task_scope.csv      scripted change-scope features per
                                                 task, written by task_scope.py

Output: out/benchmark_characterization/*.csv

Denominators. Every share is over the 417 tasks unless a row says otherwise. Domain,
technology, capability and verification labels are multi-label, so their shares can
sum to more than 100 percent. Primary type is single-label. Lines changed come from the
reference pull request's additions plus deletions and are not a measure of difficulty;
a changed test file does not show that a task can be scored automatically.

How it can be wrong. The labels are semantic judgments from issue and pull request
text, made with LLM assistance and a second independent LLM pass (see
CHARACTERIZATION.md). Running this script reproduces the aggregates from the
annotations; it does not re-check the annotations themselves.
"""
import csv
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import out, private  # noqa: E402

TYPES = ["bug_fix", "feature", "compat_integration", "performance", "refactor", "testing",
         "build_ci", "docs_examples_ui", "other_unclear"]
DOMAINS = ["circuit_ir_operators", "compilation_optimization", "simulation_numerics",
           "algorithms_applications", "error_mitigation", "qec_fault_tolerance",
           "hardware_control_execution", "characterization_benchmarking",
           "quantum_information_theory", "visualization_ui", "education_content",
           "classical_support", "infrastructure_general", "unclear"]
CAPS = ["fault_localization", "api_understanding", "cross_file_integration",
        "compatibility_migration", "scientific_numerical_reasoning",
        "algorithm_implementation", "performance_optimization", "test_design",
        "documentation_writing", "build_tooling", "ui_frontend"]
VERS = ["reproducer_regression", "interface_contract", "semantic_comparison",
        "reference_value", "invariant_property", "statistical",
        "correctness_plus_performance", "clean_build", "executable_examples",
        "browser_ui_workflow", "maintainer_review"]
KNOW = ["general_engineering", "quantum_api_workflow", "quantum_semantics", "unclear"]

# Main limitation of each task type as an evaluation item, written from the per-type
# columns of task_capability_verification.csv and task_scope_by_type.csv. Interpretive
# text, not a measurement.
LIMITS = {
    "bug_fix": "Fail-before/pass-after needs the historical environment; a silent wrong "
               "result needs an independent expected value, not only the fix's own test",
    "feature": "Open-ended requirements and multiple admissible implementations can limit "
               "what one selected reference establishes about acceptance",
    "compat_integration": "Depends on external package versions of the time; conversions "
                          "need semantic comparison across frameworks",
    "performance": "Timing depends on hardware and environment; correctness has to be held "
                   "fixed while speed is measured",
    "refactor": "Behavior preservation needs verification of affected contracts beyond a mere build",
    "testing": "The deliverable is a test; judging it needs evidence that it detects defects, "
               "for example mutation testing",
    "build_ci": "Verification requires running CI or packaging infrastructure",
    "docs_examples_ui": "The labels propose example/build/UI verification and content review; "
                        "their completeness and automatic scorability are unvalidated",
    "other_unclear": "",
}

# Names below this many tasks are pooled into one "other" row, so that a rare library
# does not point at a single issue.
MIN_NAMED = 3



def norm(name):
    # Technology names are normalized when the annotations are finalized (spelling
    # variants merged, simulator variants grouped by family), so only whitespace here.
    return name.strip()


def pct(n, d):
    return round(100 * n / d, 1) if d else ""


def quartiles(xs):
    xs = sorted(xs)
    if not xs:
        return "", "", ""
    q = statistics.quantiles(xs, n=4, method="inclusive") if len(xs) > 1 else [xs[0]] * 3
    return q[0], statistics.median(xs), q[2]


def write(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    src = private("benchmark_characterization",
                  "The per-task annotations of the unitaryHACK candidate tasks, which name "
                  "issues and pull requests.")
    recs = [json.loads(l) for l in open(src / "annotations.jsonl") if l.strip()]
    scope = {r["task_id"]: r for r in csv.DictReader(open(src / "task_scope.csv"))}
    assert len(recs) == len(scope) == len({r["task_id"] for r in recs}), "task sets differ"
    for r in recs:
        r["_scope"] = scope[r["task_id"]]
    N = len(recs)
    years = sorted({r["_scope"]["year"] for r in recs})
    o = out("benchmark_characterization")

    # 1. Primary type, with secondary labels counted separately.
    prim = Counter(r["primary_type"] for r in recs)
    anyl = Counter(t for r in recs for t in {r["primary_type"], *r["secondary_types"]})
    write(o / "task_types.csv",
          ["task_type", "primary_n", "primary_pct", "primary_or_secondary_n",
           "primary_or_secondary_pct", "denominator"],
          [[t, prim[t], pct(prim[t], N), anyl[t], pct(anyl[t], N), N] for t in TYPES])

    # 2. Domains, knowledge level, languages, technologies.
    dom = Counter(d for r in recs for d in set(r["domains"]))
    write(o / "task_domains.csv", ["domain", "n_tasks", "pct", "denominator"],
          [[d, dom[d], pct(dom[d], N), N] for d in DOMAINS])

    know = Counter(r["knowledge"] for r in recs)
    write(o / "task_knowledge.csv", ["knowledge_level", "n_tasks", "pct", "denominator"],
          [[k, know[k], pct(know[k], N), N] for k in KNOW])

    lang = Counter(l for r in recs for l in r["_scope"]["code_languages"].split(";") if l)
    nolang = sum(1 for r in recs if not r["_scope"]["code_languages"])
    rows = [[l, n, pct(n, N), N] for l, n in sorted(lang.items(), key=lambda kv: (-kv[1], kv[0]))]
    rows.append(["(no code file changed)", nolang, pct(nolang, N), N])
    write(o / "task_languages.csv", ["language", "n_tasks", "pct", "denominator"], rows)

    tech_rows = []
    for field, label in (("frameworks", "framework_or_library"), ("simulators", "simulator"),
                         ("hardware", "hardware_or_provider")):
        dtasks, btasks = {}, {}
        for r in recs:
            d = {norm(x) for x in r[f"{field}_direct"] if x != "unclear"}
            for x in d:
                dtasks.setdefault(x, set()).add(r["task_id"])
            for x in {norm(x) for x in r[f"{field}_background"] if x != "unclear"} - d:
                btasks.setdefault(x, set()).add(r["task_id"])
        names = sorted(set(dtasks) | set(btasks),
                       key=lambda k: (-len(dtasks.get(k, ())), -len(btasks.get(k, ())), k))
        pool_d, pool_b, pooled = set(), set(), 0
        for k in names:
            d, b = dtasks.get(k, set()), btasks.get(k, set())
            if len(d) + len(b) >= MIN_NAMED:
                tech_rows.append([label, k, len(d), pct(len(d), N),
                                  len({t.split("#")[0] for t in d}), len(b), N])
            else:
                pool_d |= d; pool_b |= b; pooled += 1
        if pooled:
            tech_rows.append([label, f"other ({pooled} names, under {MIN_NAMED} tasks each)",
                              len(pool_d), pct(len(pool_d), N),
                              len({t.split("#")[0] for t in pool_d}), len(pool_b - pool_d), N])
        none = sum(1 for r in recs if not r[f"{field}_direct"])
        unclear = sum(1 for r in recs if "unclear" in r[f"{field}_direct"])
        some = N - none - unclear
        tech_rows.append([label, "(any named, direct)", some, pct(some, N), "", "", N])
        tech_rows.append([label, "(none involved)", none, pct(none, N), "", "", N])
        tech_rows.append([label, "(material insufficient)", unclear, pct(unclear, N), "", "", N])
    plat = Counter(norm(x) for r in recs for x in set(r["platform_modeled"]))
    for k, n in sorted(plat.items(), key=lambda kv: (-kv[1], kv[0])):
        tech_rows.append(["platform_modeled_not_executed", k, n, pct(n, N), "", "", N])
    write(o / "task_technologies.csv",
          ["category", "name", "n_tasks_direct", "pct_direct", "n_host_repositories_direct",
           "n_tasks_background_only", "denominator"], tech_rows)

    # Host repositories, as concentration only.
    repo = Counter(r["task_id"].split("#")[0] for r in recs)
    c = sorted(repo.values(), reverse=True)
    write(o / "task_repository_concentration.csv", ["statistic", "value", "denominator"], [
        ["repositories", len(repo), ""],
        ["tasks", N, ""],
        ["largest repository, tasks", c[0], N],
        ["largest repository, pct of tasks", pct(c[0], N), N],
        ["top five repositories, pct of tasks", pct(sum(c[:5]), N), N],
        ["top ten repositories, pct of tasks", pct(sum(c[:10]), N), N],
        ["repositories with one task", sum(1 for x in c if x == 1), len(repo)],
        ["median tasks per repository", statistics.median(c), len(repo)],
    ])

    # 3. Type x domain, multi-label domain counted once per task.
    write(o / "task_type_by_domain.csv", ["task_type"] + DOMAINS + ["n_tasks"],
          [[t] + [sum(1 for r in recs if r["primary_type"] == t and d in r["domains"])
                  for d in DOMAINS] + [prim[t]] for t in TYPES])

    # 4. Type by first-offered year.
    ny = Counter(r["_scope"]["year"] for r in recs)
    write(o / "task_type_by_year.csv", ["task_type"] + years,
          [[t] + [sum(1 for r in recs if r["primary_type"] == t and r["_scope"]["year"] == y)
                  for y in years] for t in TYPES] + [["n_tasks"] + [ny[y] for y in years]])

    # 5. Change scope per type. The one reference pull request merged with no changed
    # file is excluded from the size statistics. The two that now return 404 keep the
    # file and line counts recorded when they were still available.
    rows = []
    for t in TYPES + ["all"]:
        g = [r for r in recs if t == "all" or r["primary_type"] == t]
        ok = [r for r in g if r["_scope"]["pr_status"] != "pr_empty"]
        files = [int(r["_scope"]["files_changed"]) for r in ok]
        lines = [int(r["_scope"]["lines_changed"]) for r in ok]
        tests = sum(int(r["_scope"]["changes_test_files"]) for r in g)
        fq, lq = quartiles(files), quartiles(lines)
        rows.append([t, len(g), len(ok), *fq, *lq, tests, pct(tests, len(g))])
    write(o / "task_scope_by_type.csv",
          ["task_type", "n_tasks", "n_with_size", "files_p25", "files_median", "files_p75",
           "lines_p25", "lines_median", "lines_p75", "n_changing_test_files",
           "pct_changing_test_files"], rows)

    # 6. Type -> capabilities, proposed verification, knowledge level.
    rows = []
    for t in TYPES:
        g = [r for r in recs if r["primary_type"] == t]
        if not g:
            continue
        cap = Counter(x for r in g for x in set(r["capabilities"]))
        ver = Counter(x for r in g for x in set(r["verification"]))
        kn = Counter(r["knowledge"] for r in g)
        # Ties broken by name, so the output does not depend on hash ordering.
        top = lambda cnt: "; ".join(f"{k} {v}" for k, v in
                                    sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[:3])
        pm = sum(1 for r in g if r["reference_match"] in ("partial", "mismatch"))
        rows.append([t, len(g), top(cap), top(ver),
                     kn["general_engineering"], kn["quantum_api_workflow"],
                     kn["quantum_semantics"], kn["unclear"], pct(pm, len(g)), LIMITS[t]])
    write(o / "task_capability_verification.csv",
          ["task_type", "n_tasks", "top_capabilities_n", "top_proposed_verification_n",
           "knowledge_general_engineering", "knowledge_quantum_api_workflow",
           "knowledge_quantum_semantics", "knowledge_unclear",
           "pct_reference_partial_or_mismatch", "main_limitation"], rows)

    cap = Counter(x for r in recs for x in set(r["capabilities"]))
    ver = Counter(x for r in recs for x in set(r["verification"]))
    write(o / "task_capabilities.csv", ["capability", "n_tasks", "pct", "denominator"],
          [[k, cap[k], pct(cap[k], N), N] for k in CAPS])
    # Two groupings: tasks with at least one proposed method that compares results with
    # an expected quantity, and tasks whose bounded method labels contain only build, example, UI or review categories.
    semantic = {"semantic_comparison", "reference_value", "invariant_property", "statistical"}
    build_example_review = {"maintainer_review", "clean_build", "executable_examples", "browser_ui_workflow"}
    n_sem = sum(1 for r in recs if set(r["verification"]) & semantic)
    n_build_example_review = sum(1 for r in recs if set(r["verification"]) <= build_example_review)
    write(o / "task_verification_methods.csv",
          ["proposed_verification", "n_tasks", "pct", "denominator"],
          [[k, ver[k], pct(ver[k], N), N] for k in VERS] +
          [["(any of semantic_comparison, reference_value, invariant_property, statistical)",
            n_sem, pct(n_sem, N), N],
           ["(only clean_build, executable_examples, browser_ui_workflow, maintainer_review)",
            n_build_example_review, pct(n_build_example_review, N), N]])

    # 7. Quality limits.
    q = []
    for field in ("material", "confidence", "reference_match"):
        for k, n in sorted(Counter(r[field] for r in recs).items()):
            q.append([field, k, n, pct(n, N), N])
    for k, n in sorted(Counter(r["_scope"]["pr_status"] for r in recs).items()):
        q.append(["reference_pr_status", k, n, pct(n, N), N])
    shared = sum(1 for r in recs if int(r["_scope"]["pr_shared_by_tasks"]) > 1)
    multi = sum(1 for r in recs if int(r["_scope"]["n_merged_closing_prs"]) > 1)
    q.append(["reference_pr_shared_with_another_task", "yes", shared, pct(shared, N), N])
    q.append(["issue_linked_to_more_than_one_merged_pr", "yes", multi, pct(multi, N), N])
    for k, n in sorted(Counter(r["_scope"]["reference_pr_repository"] for r in recs).items()):
        q.append(["reference_pr_repository", k, n, pct(n, N), N])
    # Whether a pull request merged into a non-default branch later reached the default
    # branch is not checked.
    for k, n in sorted(Counter(r["_scope"]["reference_pr_base_branch"] for r in recs).items()):
        q.append(["reference_pr_base_branch", k, n, pct(n, N), N])
    for k, n in sorted(Counter(r["review"]["status"] for r in recs).items()):
        q.append(["initial_review_status", k, n, pct(n, N), N])
    audit_status = Counter(
        r["review"].get("source_audit", {}).get("subset", "not_source_audited")
        for r in recs)
    for k, n in sorted(audit_status.items()):
        q.append(["codex_source_audit", k, n, pct(n, N), N])
    n_corrected = sum("post_audit_correction" in r["review"] for r in recs)
    q.append(["post_audit_correction", "applied", n_corrected, pct(n_corrected, N), N])
    write(o / "task_quality.csv", ["flag", "value", "n_tasks", "pct", "denominator"], q)

    # Agreement between the first and the blind second annotation pass, before
    # adjudication. Consistency between LLM passes, not correctness.
    rows = []
    for subset in ("targeted", "random", "all"):
        g = [r for r in recs if "agreement" in r["review"]
             and (subset == "all" or r["review"]["subset"] == subset)]
        if not g:
            continue
        for field in ("primary_type", "knowledge", "reference_match"):
            n = sum(1 for r in g if r["review"]["agreement"][field])
            rows.append([subset, field, "exact agreement", n, len(g), pct(n, len(g))])
        j = [r["review"]["agreement"]["domains_jaccard"] for r in g]
        rows.append([subset, "domains", "mean Jaccard overlap", round(statistics.mean(j), 2),
                     len(g), ""])
        n = sum(1 for x in j if x >= 0.5)
        rows.append([subset, "domains", "Jaccard >= 0.5", n, len(g), pct(n, len(g))])
    write(o / "task_annotation_agreement.csv",
          ["review_subset", "field", "measure", "value", "n_tasks", "pct"], rows)

    print(f"{N} tasks, {len(repo)} repositories; wrote {o}")


if __name__ == "__main__":
    main()
