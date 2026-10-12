# PlantChannelAI

**Molecular-attribution evidence analysis of direct ion transport by plant membrane proteins**  
植物膜蛋白直接离子运输的分子归属证据分析

Detecting a current or ion flux, identifying its ionic component, and identifying the protein that carries it are related but distinct experimental questions. PlantChannelAI organizes literature evidence for these questions in a fixed, source-linked representation.

This repository contains the paper-support data and deterministic analysis code for an **80-case mixed-literature study**, plus **four exploratory attribution case studies**. It follows the current manuscript's evidence-gap analysis rather than presenting a new-protein discovery model. The supplied GitHub Actions workflow repeats the frozen-result verification on repository updates.

## Main findings

- The 80 cases represent specified target–paper–mechanism claims from 76 DOI sources: 41 previously screened cases and 39 newly recruited cases. Recruitment strata R1/R2/R3 contain 21/40/19 cases.
- Among the 36 cases judged as direct transport by the AI-assisted reference, 12 meet the fixed ionic-component criteria (C2), and one meets the full-attribution criteria (C4).
- The most frequent unmet dimensions are target attribution (34/36), host-background separation (31/36), and physical ion identity (24/36). Fifteen cases have exactly these three gaps; eight have only attribution and host-separation gaps.
- A single project-author review agrees with the AI-assisted reference on 72/80 labels (unweighted Cohen's κ = 0.836984, rounded to 0.837). The author did not see case-level AI labels or rule outputs during labeling but already knew some aggregate results. This is a reference-source sensitivity analysis, not independent external dual-human validation.
- The OsHKT2;4, VvCCC, Tic110, and GHR1 case studies illustrate different attribution questions. They are an exploratory case series, not an additional quantitative validation panel.

An unmet dimension means the designated source evidence does not satisfy a predefined field requirement. It is not a finding that the protein lacks the relevant function. Whole-paper reference labels and stricter structured evidence criteria answer different questions.

## Reproduce the results

Python 3.12 with SciPy 1.18.1 was used to verify this public snapshot. No API key, language-model account, GPU, model weights, or downloaded article corpus is needed.

```bash
python -m pip install -r Code/requirements.txt
python Code/reproduce_final_results.py --output-dir Reproduced_results
```

Run from the repository root. Choose an output directory that does not already exist. The command:

1. Re-evaluates the 80 published evidence vectors with the unchanged engine, terminal mapping, C0/C1/C2/C4 comparators, and A1–A4 ablations, checking all 640 method outputs against the supplied frozen outputs.
2. Recomputes the AI-reference statistics, terminal matrices, DOI-balanced and free-access descriptive sensitivity analyses.
3. Recomputes author–AI agreement, author-reference metrics and paired transitions, gate-gap matrices and exact combinations, recruitment/extractor-history sensitivity, and their source-data tables.

The supplied tables remain untouched. Reproduction starts from finalized evidence vectors; it does not reproduce an immutable AI extraction run, recruit cases, or re-adjudicate literature.

## Contents

| Directory or file | Contents |
| --- | --- |
| [Code/](Code/) | Frozen attribution engine and B5 mapping, same-input comparators/ablations, and reproduction scripts |
| [Supplementary_Tables/](Supplementary_Tables/) | S1–S18: case membership, evidence vectors, outputs, separate AI/author labels, agreement, gate gaps, sensitivity analyses, and extractor history |
| [Methods/](Methods/) | Evidence schema, retained prompts and historical model configuration; method definitions in `METHODS.md` |
| [Source_Data/](Source_Data/) | Existing machine-readable figure source tables, retained under their historical filenames |
| [Figures/](Figures/) | Four PNG figures extracted unchanged from the current author-provided manuscript |
| [FIGURE_SOURCE_MAP.md](FIGURE_SOURCE_MAP.md) | Current four-figure numbering, captions, and source-table mapping |
| [Historical/](Historical/) | V1 result-interpretation record, V2.1 recruitment-shortfall record, and original V3 protocol/search documents |
| [DATA_DICTIONARY.md](DATA_DICTIONARY.md) | Table index, field meanings, missing-value conventions, and interpretation notes |
| [AI_USE.md](AI_USE.md) | Actual AI roles and recorded model-history limitations |
| [CURRENT_RESULTS_SUMMARY.json](CURRENT_RESULTS_SUMMARY.json) | Compact summary of the supplied current results |
| [CITATION.cff](CITATION.cff) | Citation metadata for this repository snapshot |

The historical V3 documents record plans at their original stages; they are not a statement that all planned procedures occurred. V1 results were known before V3. V2.1 stopped after recruitment fell short of its planned 80 cases; its 41 screened candidates contributed to the separately registered V3 mixed-source study. See [Historical/README.md](Historical/README.md).

The panel includes shared-paper, target-specific cases. Case-level exact confidence intervals do not adjust for source clustering. The 41/39 recruitment and 11/69 initial-extractor strata are post hoc descriptive comparisons, not randomized experiments. Legacy code/table identifiers such as `direct_recovery_D` are retained for reproducibility; here they mean the proportion of D-labeled cases meeting the relevant evidence criteria.

## Access, rights, and version

This is a public GitHub reproducibility snapshot, **v1.0.0**, dated 2026-10-12. It has no archival DOI and does not assert journal acceptance or publication. The unpublished manuscript itself, third-party article PDFs/XML and supplements, publisher images, private correspondence, local paths, credentials, and model weights are not distributed. Sources can be located by DOI/PMID/PMCID and article/figure locators in the tables.

An open-source/data reuse license has not yet been assigned by the author. Public access is provided; broader reuse permissions are described in [RIGHTS.md](RIGHTS.md), rather than assumed from GitHub visibility or free access to cited literature.

## 中文使用说明

这是当前论文的代码与数据支持仓库，不是整个本地项目的备份。主线是“已有运输研究中，哪些分子归属证据尚未被明确建立”。下载后按上述两条命令即可复现已公开向量的结果及主要统计。S1保留四个探索性案例；S2起为80例主面板。AI参考与作者复核分别保留，不事后合并标签。当前四张论文配图与历史来源文件的编号对应关系见 `FIGURE_SOURCE_MAP.md`。
