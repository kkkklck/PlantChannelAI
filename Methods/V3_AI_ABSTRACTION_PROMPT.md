# V3 prediction-side AI evidence extraction prompt

Primary extractor model for remaining cases: `gpt-6-luna` (Codex cloud model identifier). Retain the completed cloud pilot and interrupted-batch extractions with their original model provenance. Do not call Astra. Use Luna for routine extraction and mechanical checks; use a second Luna review or `gpt-6-sol` only for substantive ambiguous/conflicting fields. The service does not expose an immutable snapshot identifier; do not claim one.

Input schema: `CURRENT_OWNERSHIP_INPUT_V1`, defined by `../77_v3_2_54_current_ownership_audit/CURRENT_OWNERSHIP_INPUT_SCHEMA.json`. Retain the nine human-readable evidence fields listed below alongside the engine input. Do not change the frozen engine, B5 mapping, thresholds, or case membership.

## Fixed primary extraction instruction

Read only the specified case's original paper, Results, Methods, Figures, and necessary Supporting Information. Do not read truth adjudication, historical truth labels, model predictions, or another AI's extraction. The fixed case claim helps locate the experiment but is not evidence. Extract only findings from this original source for this exact target and construct. Distinguish experiments on other proteins in the same article. Never upgrade tissue flux, ion content, calcium indicators, expression, phenotype, or a target-associated whole-cell current into direct molecular ion conduction. Never borrow an experiment or control from a different target, construct, paper, or prior citation. Preserve direct, indirect, and alternative evidence at the level actually tested. If source text, target identity, construct identity, assay ownership, or a required figure/SI panel cannot be verified, write `UNKNOWN`/`UNRESOLVED`; do not guess. A false Boolean means the paper does not establish the criterion, not that the mechanism is proven absent. Do not assign D/I/A/U or a prediction state.

For each case output: `case_id`, `target`, `source` (DOI/PMCID), material path or lawful URL, and these nine fields: `assay_system`, `localization_evidence`, `ion_current_flux_evidence`, `target_specific_perturbation_evidence`, `heterologous_native_system`, `carrier_current_ownership_evidence`, `host_conductance_possibility`, `catalytic_alternative_mechanism_evidence`, `construct_identity`. For each field supply a concise finding and precise source location. Also output `extraction_confidence` and `unresolved_fields`.

Translate the verified findings into one complete `CURRENT_OWNERSHIP_INPUT_V1` JSON object. Use only the enum values in the schema. Include `field_provenance` keyed by exact field path for every positive Boolean, nonempty evidence list, resolved ion identity, and `EXACT` provenance field. Each location must include DOI or PMCID, article version, section, figure/table/panel or SI filename/page when applicable, and method paragraph when relevant. An unsupported positive or `EXACT` must be downgraded. C2 and C4 must later read this same final evidence object.

## Mechanical checks and targeted review

Routine cases receive mechanical source-span, target/construct, schema and system-consistency checks. Include an exact source span and readable material path for key positive fields so these checks can verify source presence. Do not reread every paper with a second model. Substantive ambiguous/conflicting fields receive targeted independent Luna or Sol review of the relevant original locations. Do not choose a prediction state.

If Sol still cannot resolve a substantive field, retain UNKNOWN/UNRESOLVED and continue the batch. Do not require routine human confirmation of positive fields. Do not fabricate review completion. C2 and C4 use one identical final evidence vector.
