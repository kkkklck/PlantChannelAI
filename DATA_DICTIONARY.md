# Data dictionary and table index

Tables are UTF-8, tab-delimited text. Some files have a UTF-8 byte-order mark; readers should use `encoding="utf-8-sig"`. Nested evidence fields are JSON inside TSV cells; parse with a TSV reader before decoding JSON. Do not split rows on literal tabs without respecting quoting.

## Units and identifiers

- Main-panel `case_id`: `PCAV3-001` to `PCAV3-080`. A case is a specified target + original source + mechanism claim. Eighty cases are not eighty independent papers; there are 76 distinct DOI sources.
- Exploratory-series `case_id`: `PCAOC-001` to `PCAOC-004`. A record links specified apparent-direct evidence and its subsequent/confounding evidence chain. These are separate from the 80-case panel.
- `source_stratum`: R1/R2/R3 are recruitment routes, not biological truth labels. Their final counts are 21/40/19.
- `DOI`, `PMID`, `PMCID_if_any`, and `source`: source identifiers, not licenses or redistribution permissions. Article locators identify sections, figures, panels, methods, and supplements.
- `target`, `species`, and construct fields specify the target under review. Shared-paper targets remain separate.

## References and rule outputs

`D`: direct transport/conduction at the whole-paper interpretation level; `I`: indirect ion-related evidence; `A`: alternative primary mechanism; `U`: unresolved. Channels, cotransporters, exchangers and pumps may all be D. AI and author references use the same conceptual labels but remain separate datasets. `confidence` is HIGH/MODERATE/LOW.

Frozen rule outputs are `DIRECT_PROMOTE`, `NONDIRECT_WITHHOLD`, and `ABSTAIN`. These are rule decisions, not replacement human-reference labels. `historical_state` preserves the engine's detailed evidence state; the unchanged mapping is in `Code/91_publication_validation_benchmark_v1/operational/B5_STATE_MAPPING_V1.0.tsv`.

`direct_recovery_D` and related legacy metric names denote the fraction of reference-D cases satisfying the relevant structured criteria in this analysis. They do not make the whole-paper D definition identical to C2 or C4. Estimates and confidence-interval bounds in metric tables are proportions between 0 and 1. Counts and denominators are case counts unless an estimator explicitly applies DOI balancing.

## Supplementary tables

| Table | Contents and principal fields |
| --- | --- |
| S1 | Four exploratory attribution chains: apparent-direct and confounding sources, DOI, evidence, locations, access routes, and retained eligibility record |
| S2 | Fixed 80-case membership: target, species, recruitment stratum, source identifiers/access, key experiment and location |
| S3 | Final evidence: assay, localization, current/flux, perturbations, experimental system, attribution, host/catalytic context, construct, provenance, confidence, unresolved fields and `evidence_json` |
| S4 | Frozen outputs: validation status, historical state, C0/C1/C2/C4 and A1–A4 |
| S5 | AI-assisted reference: final D/I/A/U, confidence, two context labels/confidences, reconciliation origin, rationale and source locations |
| S6 | Single-author reference: independent retained label/confidence, notes, paper metadata and evidence locations |
| S7 | Case-level AI–author agreement and D-versus-non-D agreement |
| S8 | Eight disagreements, with both labels, rationales and difference type; not overwritten by consensus |
| S9 | Author-reference metrics for all eight frozen methods, numerator/denominator, estimate and exact interval |
| S10 | Author-reference C2/C4 paired transition counts, exact two-sided McNemar test and paired difference |
| S11 | All 36 AI-D cases: C2/C4 outputs, historical state, six unmet dimensions and source locations |
| S12 | Marginal gap counts and exhaustive exact gap combinations; combinations are mutually exclusive but marginal dimensions are not |
| S13 | AI-reference method metrics, count denominators, estimates and exact intervals |
| S14 | AI-reference D/I/A/U by three-state terminal output matrices |
| S15 | DOI-balanced and source-access descriptive sensitivity; weighting/estimator fields distinguish weighted from case-based estimates |
| S16 | Post hoc 41/39 recruitment-history and 11/69 extractor-history sensitivity, separately for AI and author references |
| S17 | Author-reference terminal output matrices |
| S18 | Recorded initial extractor history per case, source record, exact-backend availability and interpretation |

`why_this_is_hard_negative` and `ELIGIBLE` in S1 are historical recruitment fields. The current manuscript uses the retained four records as exploratory attribution examples, not as a homogeneous set of proven false-positive transporters or a quantitative validation panel.

## Evidence and missing values

The schema is `Methods/CURRENT_OWNERSHIP_INPUT_SCHEMA.json`. `evidence_json` contains the frozen executable vector: `target`, `provenance`, `observation`, `carrier_tests`, `ownership_tests`, `catalytic_context`, `host_context`, `source_citations` and `notes`. Nested narrative fields generally record evidence, source location and extraction confidence. Source spans in this public package are locators/structured summaries, not a redistributable full-text corpus.

`UNKNOWN`, `UNRESOLVED`, `PARTIAL`, `CONFLICTING`, and `NOT_APPLICABLE` retain their field-specific historical meanings. Blank identifiers or notes mean not supplied, not a negative finding. A Boolean `false` is the retained encoding that a positive requirement is not established in that vector; read the accompanying source/provenance fields rather than inferring biological absence.

In S11, six `*_unmet` flags identify unmet physical-ion, target-attribution, host-separation, current/flux, catalytic-separation and provenance requirements. The exact executable predicates are in `Code/final_result_tables.py` and the frozen engine. A not-applicable host/catalytic requirement is not counted as a gap. Fifteen cases have exactly physical-ion + attribution + host gaps, and eight have exactly attribution + host gaps.

Source-access categories are EXISTING_FREE (26), UNKNOWN_LOCAL_ACCESS (15), NEW_FREE_PUBLISHER (5), and NEW_FREE_PMC (34). UNKNOWN_LOCAL_ACCESS does not assert illegal access or free redistribution. The mixed-source panel is not an all-open-access article collection.

## Source data and figures

Source-data filenames retain the earlier five-figure numbering because the supplied reproduction script validates those exact tables. The current manuscript has four figures; the unambiguous current-to-historical mapping is in [FIGURE_SOURCE_MAP.md](FIGURE_SOURCE_MAP.md). No scientific values were changed to accommodate this numbering.
