"""Recompute the published descriptive summaries from sanitized public tables."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path

from scipy.stats import beta

METHODS = ("C0", "C1", "C2", "C4", "A1", "A2", "A3", "A4")
TRUTHS = ("D", "I", "A", "U")
STATES = ("DIRECT_PROMOTE", "NONDIRECT_WITHHOLD", "ABSTAIN")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def ratio(k: int, n: int) -> dict:
    if n == 0:
        return {"numerator": k, "denominator": n, "estimate": None,
                "ci95_lower": None, "ci95_upper": None, "ci_method": None}
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    values = (k / n, lo, hi)
    if not all(math.isfinite(x) for x in values):
        raise ValueError("Non-finite exact-binomial statistic")
    return {"numerator": k, "denominator": n, "estimate": k / n,
            "ci95_lower": lo, "ci95_upper": hi,
            "ci_method": "Clopper-Pearson exact"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--membership", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--truth", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise SystemExit("Output directory already exists; choose a new directory.")

    members = read_tsv(args.membership)
    predictions = read_tsv(args.predictions)
    truths = read_tsv(args.truth)
    ids = [r["case_id"] for r in members]
    if len(ids) != 80 or len(set(ids)) != 80:
        raise ValueError("Membership must contain 80 unique cases")
    by_pred = {r["case_id"]: r for r in predictions}
    by_truth = {r["case_id"]: r for r in truths}
    if (len(predictions) != 80 or len(truths) != 80 or len(by_pred) != 80 or len(by_truth) != 80
            or set(by_pred) != set(ids)
            or set(by_truth) != set(ids)):
        raise ValueError("Prediction/truth IDs must match the 80-case panel")
    if any(r.get("validation_status") != "VALID" for r in predictions):
        raise ValueError("Expected only valid sealed prediction rows")
    if any(by_truth[cid].get("final_truth_DIAU") not in TRUTHS for cid in ids):
        raise ValueError("Truth labels outside D/I/A/U")
    if any(by_pred[cid].get(m) not in STATES for cid in ids for m in METHODS):
        raise ValueError("Prediction states outside the frozen terminal vocabulary")

    truth_counts = Counter(by_truth[cid]["final_truth_DIAU"] for cid in ids)
    metrics, matrices = [], []
    for method in METHODS:
        counts = Counter((by_truth[cid]["final_truth_DIAU"], by_pred[cid][method]) for cid in ids)
        for truth in TRUTHS:
            matrices.append({"method": method, "truth": truth,
                             **{state: counts[truth, state] for state in STATES}})
        abstain = sum(counts[t, "ABSTAIN"] for t in TRUTHS)
        specs = (
            ("direct_recovery_D", counts["D", "DIRECT_PROMOTE"], truth_counts["D"]),
            ("erroneous_direct_promotion_I_plus_A",
             sum(counts[t, "DIRECT_PROMOTE"] for t in ("I", "A")),
             truth_counts["I"] + truth_counts["A"]),
            ("total_abstention", abstain, 80),
            ("resolved_coverage_nonabstention", 80 - abstain, 80),
            ("direct_promotion_U", counts["U", "DIRECT_PROMOTE"], truth_counts["U"]),
        )
        for metric, k, n in specs:
            metrics.append({"method": method, "metric": metric, **ratio(k, n)})

    member_by_id = {r["case_id"]: r for r in members}
    clusters: dict[str, list[str]] = {}
    for cid in ids:
        doi = member_by_id[cid].get("DOI", "").strip().lower()
        clusters.setdefault(doi or f"MISSING_DOI:{cid}", []).append(cid)
    sens = []
    specs = (
        ("direct_recovery_D", lambda c: by_truth[c]["final_truth_DIAU"] == "D", lambda c: by_pred[c]["C4"] == "DIRECT_PROMOTE"),
        ("erroneous_direct_promotion_I_plus_A", lambda c: by_truth[c]["final_truth_DIAU"] in ("I", "A"), lambda c: by_pred[c]["C4"] == "DIRECT_PROMOTE"),
        ("total_abstention", lambda c: True, lambda c: by_pred[c]["C4"] == "ABSTAIN"),
        ("resolved_coverage_nonabstention", lambda c: True, lambda c: by_pred[c]["C4"] != "ABSTAIN"),
        ("direct_promotion_U", lambda c: by_truth[c]["final_truth_DIAU"] == "U", lambda c: by_pred[c]["C4"] == "DIRECT_PROMOTE"),
    )
    subsets = (
        ("all_fixed_membership", lambda c: True),
        ("free_text_source_subset", lambda c: member_by_id[c].get("source_access", "").startswith(("EXISTING_FREE", "NEW_FREE"))),
    )
    for subset, eligible in subsets:
        selected = [cid for cid in ids if eligible(cid)]
        source_count = len({doi for doi, cluster in clusters.items() if any(c in selected for c in cluster)})
        for metric, denom_ok, numer_ok in specs:
            denominator = sum(1 / len(cluster) for cluster in clusters.values()
                              for c in cluster if c in selected and denom_ok(c))
            numerator = sum(1 / len(cluster) for cluster in clusters.values()
                            for c in cluster if c in selected and denom_ok(c) and numer_ok(c))
            sens.append({"method": "C4", "subset": subset, "metric": metric,
                         "estimator": "DOI_cluster_balanced", "weighted_numerator": numerator,
                         "weighted_denominator": denominator,
                         "weighted_estimate": numerator / denominator if denominator else None,
                         "ci95_lower": None, "ci95_upper": None,
                         "weighting": "each original DOI cluster total weight 1; descriptive only; no confidence interval",
                         "case_count": len(selected), "source_count_in_subset": source_count})
            if subset == "free_text_source_subset":
                n = sum(denom_ok(c) for c in selected)
                k = sum(denom_ok(c) and numer_ok(c) for c in selected)
                sens.append({"method": "C4", "subset": subset, "metric": metric,
                             "estimator": "unweighted_case_proportion", "weighted_numerator": k,
                             "weighted_denominator": n, "weighted_estimate": k / n if n else None,
                             "ci95_lower": None, "ci95_upper": None,
                             "weighting": "each case weight 1; free-full-text subset descriptive only; no CI",
                             "case_count": len(selected), "source_count_in_subset": source_count})

    args.output_dir.mkdir(parents=True)
    write_tsv(args.output_dir / "V3_METHOD_METRICS.tsv", list(metrics[0]), metrics)
    write_tsv(args.output_dir / "V3_TERMINAL_MATRICES.tsv", ["method", "truth", *STATES], matrices)
    write_tsv(args.output_dir / "V3_C4_SOURCE_SENSITIVITY.tsv", list(sens[0]), sens)
    reviewer_a = Counter(r["reviewer_A_label"] for r in truths)
    reviewer_b = Counter(r["reviewer_B_label"] for r in truths)
    agree = sum(by_truth[cid]["reviewer_A_label"] == by_truth[cid]["reviewer_B_label"] for cid in ids)
    observed = agree / 80
    expected = sum(reviewer_a[label] * reviewer_b[label] for label in TRUTHS) / (80 * 80)
    kappa = (observed - expected) / (1 - expected) if expected < 1 else None
    summary = {
        "analysis": "Public derivative reproduction; exploratory AI-reference descriptive statistics",
        "cases": 80,
        "method_names": list(METHODS),
        "truth_counts_DIAU": {label: truth_counts[label] for label in TRUTHS},
        "initial_AI_review_agreement": {"numerator": agree, "denominator": 80,
                                         "unweighted_cohen_kappa": kappa,
                                         "reviewer_A_counts": dict(reviewer_a),
                                         "reviewer_B_counts": dict(reviewer_b),
                                         "confidence_agreement_n": sum(
                                             by_truth[cid].get("reviewer_A_confidence") == by_truth[cid].get("reviewer_B_confidence")
                                             for cid in ids),
                                         "reviewer_A_full_text_reviewed_n": sum(
                                             by_truth[cid].get("reviewer_A_full_text_reviewed") == "YES" for cid in ids),
                                         "reviewer_B_full_text_reviewed_n": sum(
                                             by_truth[cid].get("reviewer_B_full_text_reviewed") == "YES" for cid in ids)},
        "distinct_original_DOI_sources": len(clusters),
        "consensus_origin_counts": dict(Counter(r.get("consensus_origin", "") for r in truths)),
        "source_weighting": "C4 only; each DOI cluster total weight 1; descriptive only; no CI",
        "intervals": "two-sided nominal 95% Clopper-Pearson exact binomial intervals",
        "provenance": "Derived from sanitized public tables; does not verify original internal seal hashes",
    }
    (args.output_dir / "V3_PUBLIC_REPRODUCTION_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Reproduced descriptive tables for 80 cases, 8 methods, {len(clusters)} DOI sources.")


if __name__ == "__main__":
    main()
