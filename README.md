<div align="center">

# PlantChannelAI

**Molecular-attribution evidence analysis of direct ion transport by plant membrane proteins**

[![Reproducibility](https://github.com/kkkklck/PlantChannelAI/actions/workflows/reproduce.yml/badge.svg)](https://github.com/kkkklck/PlantChannelAI/actions/workflows/reproduce.yml)
[![Release](https://img.shields.io/github/v/release/kkkklck/PlantChannelAI?color=2563eb)](https://github.com/kkkklck/PlantChannelAI/releases/tag/v1.0.0)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](Code/requirements.txt)

[Quick start](#quick-start) · [Findings](#key-findings) · [Repository guide](#repository-guide) · [Methods](Methods/METHODS.md) · [Citation](CITATION.cff)

</div>

---

Detecting an ion current, identifying its ionic component, and identifying the protein that carries it are distinct experimental questions. **PlantChannelAI** organizes source-linked literature evidence to examine which requirements for molecular attribution are met, and which remain unresolved.

This repository provides the data and deterministic analysis code supporting an **80-case mixed-literature study**, together with **four exploratory attribution case studies**.

                                        | Study cases | DOI sources | Analysis methods | Supplementary tables |
                                        | :---: | :---: | :---: | :---: |
                                        | **80** | **76** | **8** | **18** |

## Quick start

Run these commands from the repository root with **Python 3.12**:

```bash
python -m pip install -r Code/requirements.txt
python Code/reproduce_final_results.py --output-dir Reproduced_results
```

Choose an output directory that does not already exist. This snapshot was verified with Python 3.12 and SciPy 1.18.1. No API key, language-model account, GPU, model weights, or downloaded article corpus is required.

The reproduction command checks **all 640 method outputs** against the frozen results and recomputes the reported statistics and figure source tables. GitHub Actions runs the same verification on repository updates.

<details>
<summary><strong>What the reproduction covers</strong></summary>

1. Re-evaluates the 80 finalized evidence vectors using the unchanged engine and terminal mapping, the C0/C1/C2/C4 comparators, and the A1–A4 ablations.
2. Recomputes AI-reference statistics, terminal matrices, and DOI-balanced and free-access descriptive sensitivity analyses.
3. Recomputes author–AI agreement, author-reference metrics, paired transitions, gate-gap matrices and exact combinations, recruitment/extractor-history sensitivity, and their source-data tables.

The supplied tables remain untouched. Reproduction begins with finalized evidence vectors; it does not repeat an immutable AI extraction run, recruit cases, or re-adjudicate literature.

</details>

## Key findings

Of the **36 cases** labeled as direct transport by the AI-assisted reference:

| Evidence criterion or gap | Cases |
| --- | ---: |
| Meet the fixed ionic-component criteria (C2) | **12 / 36** |
| Meet the full-attribution criteria (C4) | **1 / 36** |
| Unmet target-attribution requirements | **34 / 36** |
| Unmet host-background separation requirements | **31 / 36** |
| Unmet physical ion-identity requirements | **24 / 36** |

Fifteen cases have exactly the three gaps listed above; eight have only target-attribution and host-background separation gaps.

> **Interpreting an evidence gap:** an unmet dimension means that the designated source evidence does not satisfy a predefined field requirement. It does not establish that the protein lacks the relevant function. Whole-paper reference labels and structured evidence criteria answer different questions.

A single project-author review agrees with the AI-assisted reference on **72/80 labels**, with unweighted Cohen's **κ = 0.837** (unrounded: 0.836984). The author did not see case-level AI labels or rule outputs during labeling but already knew some aggregate results. This is a reference-source sensitivity analysis, not independent external dual-human validation.

The **OsHKT2;4, VvCCC, Tic110, and GHR1** case studies illustrate different attribution questions. They form an exploratory case series, not an additional quantitative validation panel.

## Repository guide

| Location | What you will find |
| --- | --- |
| [Code/](Code/) | Frozen attribution engine, B5 mapping, same-input comparators and ablations, and reproduction scripts |
| [Supplementary_Tables/](Supplementary_Tables/) | Tables S1–S18: case membership, evidence vectors, outputs, separate AI/author labels, agreement, gate gaps, sensitivity analyses, and extractor history |
| [Methods/](Methods/) | Evidence schema, retained prompts, historical model configuration, and [method definitions](Methods/METHODS.md) |
| [Source_Data/](Source_Data/) | Machine-readable figure source tables, retained under their historical filenames |
| [Figures/](Figures/) | Four PNG figures extracted unchanged from the author-provided manuscript |
| [Historical/](Historical/) | V1 result-interpretation record, V2.1 recruitment-shortfall record, and original V3 protocol and search documents |

**Reading the data:** S1 contains the four exploratory cases; S2 onward covers the 80-case main panel. AI and author references are retained separately, without merging their labels after review.

**Supporting documentation**

- [Data dictionary](DATA_DICTIONARY.md) — table index, field definitions, missing-value conventions, and interpretation notes.
- [Figure source map](FIGURE_SOURCE_MAP.md) — current four-figure numbering, captions, and source-table mapping.
- [AI use statement](AI_USE.md) — actual AI roles and recorded model-history limitations.
- [Results summary](CURRENT_RESULTS_SUMMARY.json) — machine-readable summary of the supplied results.
- [Citation metadata](CITATION.cff) — metadata for citing this repository snapshot.

## Study scope and provenance

The 80 cases are specified target–paper–mechanism claims from 76 DOI sources: **41 previously screened cases** and **39 newly recruited cases**. Recruitment strata R1/R2/R3 contain 21/40/19 cases.

Historical V3 documents record plans at their original stages; they do not establish that every planned procedure occurred. V1 results were known before V3. V2.1 stopped after recruitment fell short of its planned 80 cases; its 41 screened candidates contributed to the separately registered V3 mixed-source study. See the [historical record](Historical/README.md).

The panel includes shared-paper, target-specific cases. Case-level exact confidence intervals do not adjust for source clustering. The 41/39 recruitment and 11/69 initial-extractor strata are post hoc descriptive comparisons, not randomized experiments. Legacy identifiers such as `direct_recovery_D` are retained for reproducibility; here they mean the proportion of D-labeled cases meeting the relevant evidence criteria.

## Version, citation, and access

The fixed research snapshot is available as **[v1.0.0](https://github.com/kkkklck/PlantChannelAI/releases/tag/v1.0.0)**, released on **12 October 2026**. Use the versioned release when referring to the supplied analysis materials; citation metadata is provided in [CITATION.cff](CITATION.cff).

The repository has no archival DOI and makes no claim of journal acceptance or publication. The unpublished manuscript, third-party article PDFs/XML and supplements, publisher images, private correspondence, local paths, credentials, and model weights are excluded. Sources can be located using the DOI/PMID/PMCID identifiers and article/figure locators in the tables.

An open-source/data reuse license has not yet been assigned by the author. Public access does not imply broader reuse permissions; see [RIGHTS.md](RIGHTS.md).
