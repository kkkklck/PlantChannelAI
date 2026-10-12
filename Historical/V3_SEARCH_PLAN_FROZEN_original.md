# PlantChannelAI V3 新增免费全文检索规则

状态：`SEARCH_DESIGN_FROZEN`，2026-09-29；本文件在第一次新增检索请求前定稿。它取代本目录先前的 `FREE_FULLTEXT_DISCOVERY_PLAN_DRAFT.md`，不修改 V1/V2.1 的检索或结果。

检索窗口为首次发表日期 2016-01-01 至 2026-09-28。固定六个列表、固定顺序：R1 Europe PMC、R1 PMC OA、R2 Europe PMC、R2 PMC OA、R3 Europe PMC、R3 PMC OA。每列表按数据库相关性排序取前 300 条；不足 300 条取全部。保存请求、响应、总命中和返回顺序。Europe PMC 使用 `format=json&resultType=core&pageSize=300&cursorMark=*&synonym=false`，不按 `OPEN_ACCESS:y` 预先限制；PMC 使用 ESearch `db=pmc&retmode=json&retmax=300&retstart=0&sort=relevance`，附加 OA Subset 过滤器。未取得真实响应的列表不得补猜或改源。两源都失败则记录失败，不能伪称检索完成。

## Europe PMC 原样查询

R1：

```text
FIRST_PDATE:[2016-01-01 TO 2026-09-28] AND (TITLE_ABS:plant OR TITLE_ABS:Arabidopsis OR TITLE_ABS:rice OR TITLE_ABS:maize) AND (TITLE_ABS:electrophysiology OR TITLE_ABS:"ion flux" OR TITLE_ABS:reconstitution) AND (TITLE_ABS:"membrane protein" OR TITLE_ABS:receptor OR TITLE_ABS:transporter OR TITLE_ABS:oxidase)
```

R2：

```text
FIRST_PDATE:[2016-01-01 TO 2026-09-28] AND (TITLE_ABS:plant OR TITLE_ABS:Arabidopsis OR TITLE_ABS:rice OR TITLE_ABS:maize) AND (TITLE_ABS:"calcium signal" OR TITLE_ABS:"membrane potential" OR TITLE_ABS:"ion homeostasis") AND (TITLE_ABS:receptor OR TITLE_ABS:membrane OR TITLE_ABS:transporter)
```

R3：

```text
FIRST_PDATE:[2016-01-01 TO 2026-09-28] AND (TITLE_ABS:plant OR TITLE_ABS:Arabidopsis OR TITLE_ABS:rice OR TITLE_ABS:maize) AND (TITLE_ABS:"NADPH oxidase" OR TITLE_ABS:"receptor kinase" OR TITLE_ABS:"membrane enzyme" OR TITLE_ABS:"protein kinase" OR TITLE_ABS:oxidoreductase) AND (TITLE_ABS:ion OR TITLE_ABS:current OR TITLE_ABS:flux OR TITLE_ABS:calcium)
```

## PMC OA Subset 原样查询

R1：

```text
"open access"[filter] AND 2016/01/01:2026/09/28[dp] AND (plant[tiab] OR Arabidopsis[tiab] OR rice[tiab] OR maize[tiab]) AND (electrophysiology[tiab] OR "ion flux"[tiab] OR reconstitution[tiab]) AND ("membrane protein"[tiab] OR receptor[tiab] OR transporter[tiab] OR oxidase[tiab])
```

R2：

```text
"open access"[filter] AND 2016/01/01:2026/09/28[dp] AND (plant[tiab] OR Arabidopsis[tiab] OR rice[tiab] OR maize[tiab]) AND ("calcium signal"[tiab] OR "membrane potential"[tiab] OR "ion homeostasis"[tiab]) AND (receptor[tiab] OR membrane[tiab] OR transporter[tiab])
```

R3：

```text
"open access"[filter] AND 2016/01/01:2026/09/28[dp] AND (plant[tiab] OR Arabidopsis[tiab] OR rice[tiab] OR maize[tiab]) AND ("NADPH oxidase"[tiab] OR "receptor kinase"[tiab] OR "membrane enzyme"[tiab] OR "protein kinase"[tiab] OR oxidoreductase[tiab]) AND (ion[tiab] OR current[tiab] OR flux[tiab] OR calcium[tiab])
```

## 去重、阅读与停止

先规范化 DOI，再用 PMID、PMCID、题名与年份合并同一原始研究，保留首次命中的列表与位次；不同版本不重复。先排除既有 41 篇相同来源、V1/开发/历史 13 的精确靶点–来源重叠，再判定新病例。相同原始实验链/同一目标只取首次可核实来源；无法确认的列入一份疑难清单。R1/R2/R3 是发现路径，不是预测或真值。

新增病例必须是已发表植物膜蛋白原始研究，目标与指定原始来源可确认，涉及离子相关电流、通量、运输、信号或有针对该声明的替代机制；完整原文、相关图表、方法及机制判定必需的补充材料均可无需付费/订阅合法阅读。免费阅读与再分发许可证分别记载。无法确定的字段写 `UNKNOWN`；仅摘要、PMCID、OA 标记、HTTP 200 登录页或推测的补充 URL 均不等于合格。自动初筛只给 `ELIGIBLE_VERIFIED`、`EXCLUDED_VERIFIED` 或 `PENDING_SCIENTIFIC_OR_ACCESS_REVIEW`，不能用弱证据填充合格数。

目标总量 80，来源路径目标 R1=30/R2=25/R3=25；现有 41 例全部保留，若后续个别确证关键材料不可用，则明确报告而非按来源类别剔除。以资格和固定顺序招募；满足各路径缺口后，剩余名额按 R1、R2、R3 顺序从已检索固定池补足。最多处理固定六列表各前 300 条，不追引文、不临时扩展查询、不根据预测/真值或类别比例补招；固定池不足时报告实际缺口。检索可以在真人真值审阅者和预测执行程序尚未就绪时开始，但病例集冻结、预测与真值另按 V3 方案门槛执行。

官方依据：[Europe PMC REST](https://europepmc.org/RestfulWebService)、[PMC OA Subset](https://pmc.ncbi.nlm.nih.gov/tools/openftlist/)、[NCBI ESearch](https://www.ncbi.nlm.nih.gov/books/NBK25499/)、[PMC 批量获取规则](https://pmc.ncbi.nlm.nih.gov/about/copyright/)。
