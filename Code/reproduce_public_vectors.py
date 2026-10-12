"""Reproduce public vector-only method outputs into a fresh directory."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--expected", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--method-dir", type=Path, required=True,
                        help="path to packaged Code/v2_method")
    args = parser.parse_args()
    if args.output_dir.exists():
        raise SystemExit("Output directory already exists; choose a new directory to preserve prior results.")
    sys.path.insert(0, str(args.method_dir.resolve()))
    from v2_method import evaluate_one  # noqa: E402

    evidence = read_tsv(args.evidence)
    expected = read_tsv(args.expected)
    methods = ("C0", "C1", "C2", "C4", "A1", "A2", "A3", "A4")
    if len(evidence) != 80 or len(expected) != 80:
        raise ValueError("Expected exactly 80 evidence and prediction rows")
    expected_by_id = {row["case_id"]: row for row in expected}
    if len(expected_by_id) != 80 or {r["case_id"] for r in evidence} != set(expected_by_id):
        raise ValueError("Evidence and expected prediction case IDs must match exactly")
    results = []
    mismatch = []
    for row in evidence:
        vector = json.loads(row["evidence_json"])
        if vector.get("record_id") != row["case_id"]:
            raise ValueError(f"Evidence vector ID mismatch for {row['case_id']}")
        result = evaluate_one(vector)
        results.append(result)
        for method in methods:
            if result.get(method) != expected_by_id[row["case_id"]].get(method):
                mismatch.append((row["case_id"], method))
    args.output_dir.mkdir(parents=True)
    out = args.output_dir / "reproduced_predictions.tsv"
    with out.open("x", encoding="utf-8", newline="") as handle:
        fields = ["case_id", "historical_state", "validation_status", *methods]
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    summary = {"cases": len(results), "methods": list(methods), "exact_match": not mismatch,
               "mismatch_count": len(mismatch), "mismatches": mismatch}
    (args.output_dir / "comparison.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if mismatch:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
