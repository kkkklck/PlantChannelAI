#!/usr/bin/env python3
"""V2.1 same-input comparators and diagnostic ablations; no truth input.

This file does not retrieve sources, abstract evidence, adjudicate truth, or
select cases. Real-case execution is intentionally gated outside this module.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = ROOT / "77_v3_2_54_current_ownership_audit/current_ownership_audit.py"
MAPPING_PATH = ROOT / "91_publication_validation_benchmark_v1/operational/B5_STATE_MAPPING_V1.0.tsv"
ENGINE_SHA256 = "309A4BA7DB8AF4EFBBA295D7F456081CAAF76A03ADA605F6A4698BA044A15861"
MAPPING_SHA256 = "F155E7ECCFBB6627ECEA438EDCC337570D361E8B25E6DFBB74D4D5B91F902942"
STATES = {"DIRECT_PROMOTE", "NONDIRECT_WITHHOLD", "ABSTAIN"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def load_frozen_sources():
    if sha256(ENGINE_PATH) != ENGINE_SHA256 or sha256(MAPPING_PATH) != MAPPING_SHA256:
        raise RuntimeError("Frozen V1 engine or mapping bytes changed")
    spec = importlib.util.spec_from_file_location("plantchannelai_v2_pinned_engine", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load pinned engine")
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    with MAPPING_PATH.open(encoding="utf-8", newline="") as handle:
        mapping = {r["historical_state"]: r["benchmark_terminal_state"] for r in csv.DictReader(handle, delimiter="\t")}
    if len(mapping) != 9 or set(mapping.values()) != STATES:
        raise RuntimeError("Unexpected frozen terminal mapping")
    return engine, mapping


def evaluate_one(data: dict) -> dict:
    """Evaluate one preabstracted source vector; never sees truth labels."""
    engine, mapping = load_frozen_sources()
    result = engine.audit(data)
    base = mapping[result["state"]]
    invalid = bool(result.get("validation_errors"))
    if invalid:
        return {
            "case_id": str(data.get("record_id", "")),
            "historical_state": result["state"],
            "validation_status": "INVALID_VECTOR",
            "C0": "ABSTAIN", "C1": "NONDIRECT_WITHHOLD", "C2": "ABSTAIN", "C4": "ABSTAIN",
            "A1": "ABSTAIN", "A2": "ABSTAIN", "A3": "NONDIRECT_WITHHOLD", "A4": "ABSTAIN",
        }

    ev = result["evidence_vector"]
    provenance_ok = ev["provenance_integrity"] not in {"UNRESOLVED", "CONFLICTING"}
    ionic = ev["current_or_flux_observed"] and ev["physical_ion_identity_supported"]
    ownership = ev["target_molecular_support"] or ev["purified_reconstitution_support"]
    host_ok = ev["host_separation"] in {"ADEQUATE", "NOT_APPLICABLE"}
    catalytic_ok = ev["catalytic_separation"] in {"ADEQUATE", "NOT_APPLICABLE"}
    direct_host_assignment = data["host_context"]["host_current_directly_established"]
    direct_nonion_assignment = data["carrier_tests"]["nonion_current_identity_directly_established"]

    observation = data["observation"]
    any_observation = any(observation[k] for k in (
        "current_detected", "direct_ion_flux_detected", "calcium_indicator_change", "genetic_or_phenotype_association"
    ))
    c2 = "DIRECT_PROMOTE" if ionic else "NONDIRECT_WITHHOLD" if any_observation else "ABSTAIN"

    # A1 removes only molecular ownership, preserving provenance and alternatives.
    a1_promote = provenance_ok and ionic and host_ok and catalytic_ok and not direct_host_assignment and not direct_nonion_assignment
    # A2 removes host/catalytic alternative gates, preserving ownership and provenance.
    a2_promote = provenance_ok and ionic and ownership and not direct_nonion_assignment
    a1 = "DIRECT_PROMOTE" if a1_promote else base
    a2 = "DIRECT_PROMOTE" if a2_promote else base
    a3 = "NONDIRECT_WITHHOLD" if base == "ABSTAIN" else base

    if not provenance_ok:
        amended = copy.deepcopy(data)
        amended["provenance"] = {key: "EXACT" for key in amended["provenance"]}
        altered = engine.audit(amended)
        if altered.get("validation_errors"):
            raise RuntimeError("A4 synthetic provenance rerun failed schema validation")
        a4 = mapping[altered["state"]]
    else:
        a4 = base

    output = {
        "case_id": data["record_id"],
        "historical_state": result["state"],
        "validation_status": "VALID",
        "C0": "ABSTAIN", "C1": "NONDIRECT_WITHHOLD", "C2": c2, "C4": base,
        "A1": a1, "A2": a2, "A3": a3, "A4": a4,
    }
    if any(output[k] not in STATES for k in ("C0", "C1", "C2", "C4", "A1", "A2", "A3", "A4")):
        raise RuntimeError("Nonterminal output")
    return output
