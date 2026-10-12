#!/usr/bin/env python3
"""Mechanical, no-score current-ownership evidence audit for PlantChannelAI."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

VERSION = "CURRENT_OWNERSHIP_AUDIT_V1"
PROV = {"EXACT", "PARTIAL", "UNRESOLVED", "CONFLICTING"}
SYSTEMS = {"PURIFIED_RECONSTITUTED", "HETEROLOGOUS_CELL", "NATIVE_CELL", "CELLULAR_IMAGING", "ORGANISM", "OTHER"}
CONFOUNDERS = {"CALCIUM_ACTIVATED_CHLORIDE", "ACID_HYPERPOLARIZATION_CURRENT", "ENDOGENOUS_CATION_CHANNEL", "OXIDANT_ACTIVATED_CURRENT", "EXPRESSION_STRESS", "CHARGE_COMPENSATION"}
SEPARATIONS = {"CATALYTIC_NULL_RETAINS_IONIC_ENDPOINT", "SUBSTRATE_COFACTOR_ACCEPTOR_WITHDRAWAL_RETAINS_IONIC_ENDPOINT", "SIMULTANEOUS_CATALYTIC_ELECTRICAL_DISSOCIATION", "PURIFIED_INDEPENDENT_ION_AND_CATALYSIS_MEASUREMENTS"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bools(obj: dict, keys: list[str], prefix: str, errors: list[str]) -> None:
    for key in keys:
        if not isinstance(obj.get(key), bool):
            errors.append(f"{prefix}.{key}: expected boolean")


def validate_input(data: dict) -> list[str]:
    errors: list[str] = []
    required = {"schema_version", "record_id", "development_role", "target", "provenance", "observation", "carrier_tests", "ownership_tests", "catalytic_context", "host_context", "source_citations"}
    missing = required - set(data)
    if missing: errors.append("missing top-level fields: " + ", ".join(sorted(missing)))
    if errors: return errors
    if data["schema_version"] != "CURRENT_OWNERSHIP_INPUT_V1": errors.append("schema_version mismatch")
    if data["development_role"] not in {"RETROSPECTIVE_DEVELOPMENT", "SYNTHETIC_REACHABILITY", "PROSPECTIVE_APPLICATION"}: errors.append("development_role: invalid")
    if not str(data["record_id"]).strip(): errors.append("record_id is empty")
    target = data["target"]
    for k in ("name", "accession", "construct"):
        if not str(target.get(k, "")).strip(): errors.append(f"target.{k}: empty")
    provenance = data["provenance"]
    for k in ("source_identity", "target_identity", "construct_mapping", "assay_description"):
        if provenance.get(k) not in PROV: errors.append(f"provenance.{k}: invalid")
    obs = data["observation"]
    if obs.get("system") not in SYSTEMS: errors.append("observation.system: invalid")
    _bools(obs, ["current_detected", "direct_ion_flux_detected", "calcium_indicator_change", "genetic_or_phenotype_association"], "observation", errors)
    carrier = data["carrier_tests"]
    _bools(carrier, ["controlled_gradient_reversal", "bi_ionic_permeability", "direct_tracer_or_encapsulated_flux", "single_channel_ion_identity", "salt_amplitude_only", "nonion_current_identity_directly_established"], "carrier_tests", errors)
    if carrier.get("ion_identity") not in {"CA2", "CATION", "ANION", "PROTON", "MIXED_ION", "UNRESOLVED", "NONION_ELECTRON"}: errors.append("carrier_tests.ion_identity: invalid")
    own = data["ownership_tests"]
    _bools(own, ["purified_target_reconstitution", "protein_free_control", "surface_expression_verified", "target_specific_current_loss_and_rescue", "pathway_mutation_abolishes_ionic_endpoint_while_other_function_retained"], "ownership_tests", errors)
    catalytic = data["catalytic_context"]
    if not isinstance(catalytic.get("plausible_electrogenic_reaction"), bool): errors.append("catalytic_context.plausible_electrogenic_reaction: expected boolean")
    if catalytic.get("reaction_type") not in {"NONE", "ELECTRON_TRANSFER", "PROTON_TRANSPORT", "COUPLED_TRANSPORT", "OTHER", "UNRESOLVED"}: errors.append("catalytic_context.reaction_type: invalid")
    methods = catalytic.get("separation_methods")
    if not isinstance(methods, list) or not set(methods) <= SEPARATIONS: errors.append("catalytic_context.separation_methods: invalid")
    host = data["host_context"]
    applicable, excluded = host.get("applicable_confounders"), host.get("excluded_confounders")
    if not isinstance(applicable, list) or not set(applicable) <= CONFOUNDERS: errors.append("host_context.applicable_confounders: invalid")
    if not isinstance(excluded, list) or not set(excluded) <= CONFOUNDERS: errors.append("host_context.excluded_confounders: invalid")
    elif isinstance(applicable, list) and not set(excluded) <= set(applicable): errors.append("excluded_confounders must be a subset of applicable_confounders")
    _bools(host, ["host_current_directly_established", "ionic_endpoint_survives_controls"], "host_context", errors)
    if not isinstance(data["source_citations"], list) or not data["source_citations"]: errors.append("source_citations must be non-empty")
    if carrier.get("direct_tracer_or_encapsulated_flux") and not obs.get("direct_ion_flux_detected"): errors.append("direct tracer/encapsulated flux requires direct_ion_flux_detected")
    if (carrier.get("controlled_gradient_reversal") or carrier.get("bi_ionic_permeability") or carrier.get("single_channel_ion_identity") or carrier.get("nonion_current_identity_directly_established") or carrier.get("salt_amplitude_only")) and not obs.get("current_detected"): errors.append("electrical carrier tests require current_detected")
    if own.get("purified_target_reconstitution") and obs.get("system") != "PURIFIED_RECONSTITUTED": errors.append("purified_target_reconstitution requires PURIFIED_RECONSTITUTED system")
    if catalytic.get("plausible_electrogenic_reaction") and catalytic.get("reaction_type") in {"NONE", "UNRESOLVED"}: errors.append("plausible electrogenic reaction requires a resolved non-NONE reaction_type")
    if not catalytic.get("plausible_electrogenic_reaction") and (catalytic.get("reaction_type") != "NONE" or catalytic.get("separation_methods")): errors.append("non-applicable catalytic context must use reaction_type NONE and no separation methods")
    if host.get("host_current_directly_established") and not obs.get("current_detected"): errors.append("host current assignment requires current_detected")
    return errors


def audit(data: dict) -> dict:
    errors = validate_input(data)
    if errors:
        return {"audit_version": VERSION, "record_id": data.get("record_id"), "state": "NOT_EVALUABLE_PROVENANCE", "validation_errors": errors}

    p, o, c, w, cat, host = (data[x] for x in ("provenance", "observation", "carrier_tests", "ownership_tests", "catalytic_context", "host_context"))
    provenance_values = list(p.values())
    provenance_integrity = "CONFLICTING" if "CONFLICTING" in provenance_values else "UNRESOLVED" if "UNRESOLVED" in provenance_values else "PARTIAL" if "PARTIAL" in provenance_values else "EXACT"
    physical_ion_identity = any((c["controlled_gradient_reversal"], c["bi_ionic_permeability"], c["direct_tracer_or_encapsulated_flux"], c["single_channel_ion_identity"])) and c["ion_identity"] not in {"UNRESOLVED", "NONION_ELECTRON"}
    current_or_flux = o["current_detected"] or o["direct_ion_flux_detected"]
    target_molecular_support = w["target_specific_current_loss_and_rescue"] or w["pathway_mutation_abolishes_ionic_endpoint_while_other_function_retained"]
    purified_support = o["system"] == "PURIFIED_RECONSTITUTED" and w["purified_target_reconstitution"] and w["protein_free_control"]

    if o["system"] == "PURIFIED_RECONSTITUTED":
        host_separation = "NOT_APPLICABLE"
    elif not host["applicable_confounders"]:
        host_separation = "UNRESOLVED"
    elif set(host["excluded_confounders"]) == set(host["applicable_confounders"]) and host["ionic_endpoint_survives_controls"]:
        host_separation = "ADEQUATE"
    elif host["excluded_confounders"]:
        host_separation = "PARTIAL"
    else:
        host_separation = "ABSENT"

    if not cat["plausible_electrogenic_reaction"]:
        catalytic_separation = "NOT_APPLICABLE"
    elif cat["separation_methods"]:
        catalytic_separation = "ADEQUATE"
    else:
        catalytic_separation = "ABSENT"

    alternatives = []
    if cat["plausible_electrogenic_reaction"] and catalytic_separation != "ADEQUATE":
        alternatives.append("CATALYTIC_ELECTRON_CURRENT" if cat["reaction_type"] == "ELECTRON_TRANSFER" else "CATALYTIC_PROTON_OR_COUPLED_CHARGE")
    if host["applicable_confounders"] and host_separation != "ADEQUATE": alternatives.append("HOST_CONDUCTANCE_ACTIVATION")
    if "CALCIUM_ACTIVATED_CHLORIDE" in host["applicable_confounders"] and "CALCIUM_ACTIVATED_CHLORIDE" not in host["excluded_confounders"]: alternatives.append("CALCIUM_ACTIVATED_CHLORIDE_CURRENT")
    if "EXPRESSION_STRESS" in host["applicable_confounders"] and "EXPRESSION_STRESS" not in host["excluded_confounders"]: alternatives.append("EXPRESSION_OR_MEMBRANE_STRESS")
    if c["salt_amplitude_only"] and not physical_ion_identity: alternatives.append("ION_ACTIVITY_WITHOUT_SELECTIVITY_PROOF")
    if (o["calcium_indicator_change"] or o["genetic_or_phenotype_association"]) and not physical_ion_identity: alternatives.append("PHYSIOLOGICAL_NETWORK_EFFECT")
    alternatives = list(dict.fromkeys(alternatives))

    rationale = []
    if provenance_integrity in {"CONFLICTING", "UNRESOLVED"}:
        state = "NOT_EVALUABLE_PROVENANCE"; rationale.append("Critical source, target, construct or assay provenance is unresolved/conflicting.")
    elif host["host_current_directly_established"]:
        state = "HOST_CONDUCTANCE_SUPPORTED_TARGET_NOT_OWNER"; rationale.append("Controls directly assign the observed current to a host conductance.")
    elif c["nonion_current_identity_directly_established"] and not physical_ion_identity:
        state = "NONION_ELECTROGENIC_CURRENT_SUPPORTED"; rationale.append("The current carrier is directly assigned to a nonionic electrogenic reaction.")
    elif purified_support and current_or_flux and physical_ion_identity and catalytic_separation in {"ADEQUATE", "NOT_APPLICABLE"}:
        state = "DIRECT_TARGET_ION_CONDUIT_SUPPORTED"; rationale.append("Purified target reconstitution, protein-free control and physical ion identification establish molecular ownership.")
    elif current_or_flux and physical_ion_identity and target_molecular_support and host_separation in {"ADEQUATE", "NOT_APPLICABLE"} and catalytic_separation in {"ADEQUATE", "NOT_APPLICABLE"}:
        state = "TARGET_OWNED_ION_CURRENT_SUPPORTED"; rationale.append("Ion identity, target-specific dependence, host separation and catalytic separation all pass.")
    elif current_or_flux and physical_ion_identity:
        state = "IONIC_COMPONENT_SUPPORTED_OWNERSHIP_UNRESOLVED"; rationale.append("A physical ionic component is supported, but molecular ownership is incomplete.")
    elif o["current_detected"]:
        state = "EXPRESSION_ASSOCIATED_CURRENT_CARRIER_UNRESOLVED"; rationale.append("A current is observed, but salt amplitude, localization or pharmacology do not identify its carrier or owner.")
    elif o["direct_ion_flux_detected"] or o["calcium_indicator_change"] or o["genetic_or_phenotype_association"]:
        state = "INDIRECT_ION_ASSOCIATION_ONLY"; rationale.append("Ion-related cellular or physiological evidence is present without a qualifying molecular current/flux assignment.")
    else:
        state = "NO_CURRENT_OR_ION_MOVEMENT_EVIDENCE"; rationale.append("No qualifying electrical, flux, imaging or ion-associated phenotype is recorded.")

    return {
        "audit_version": VERSION,
        "record_id": data["record_id"],
        "target": data["target"],
        "state": state,
        "evidence_vector": {
            "current_or_flux_observed": current_or_flux,
            "physical_ion_identity_supported": physical_ion_identity,
            "ion_identity": c["ion_identity"],
            "target_molecular_support": target_molecular_support,
            "purified_reconstitution_support": purified_support,
            "catalytic_separation": catalytic_separation,
            "host_separation": host_separation,
            "provenance_integrity": provenance_integrity,
            "salt_amplitude_only": c["salt_amplitude_only"]
        },
        "alternative_explanations": alternatives,
        "rationale": rationale,
        "does_not_prove": ["channel-family identity", "physiological relevance outside the assayed system", "ion selectivity beyond physically tested conditions"],
        "source_citations": data["source_citations"],
        "no_score": True
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(json.loads(args.input.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
