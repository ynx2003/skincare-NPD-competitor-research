---
name: skincare-competitor-analysis
description: 将已有护肤、美妆或个护竞品资料抽取为统一字段，完成确定性的分组、对比、词频统计与 Excel 导出。适用于已有页面原文、JSON 或 CSV 数据；不负责竞品推荐、网页采集、市场阶段判断或独立作出产品策略结论。
---

# 护肤竞品数据整理与导出

本 Skill 是竞品研究的数据加工层：回答“样本数据里有什么”，不单独回答“这对业务意味着什么”。端到端研究使用上层 `skincare-competitor-research`。

## 输入

- 商品标题、详情页或笔记原文；
- JSON 数组，或包含 `items` 数组的 `research_bundle.json`；
- 使用内部英文字段名的 CSV。当前不要声称会自动映射任意中文表头。

上游尽量保留 `raw_text`、`url`、`platform`、`captured_at`、`extraction_method` 和 `review_status`。现有 Excel 未单列容纳的证据字段留在 `research_bundle.json` 中，不丢弃原文。

## 工作流

1. **验收数据**：检查样本分组、来源、时间、价格/销量口径和必填字段；缺失或冲突值保留为空并标记，不猜测。
2. **字段抽取**：默认用 `scripts/quick_parse.py` 规则抽取；用户要求且已配置兼容接口时可用 LLM。LLM 失败回退规则时，交付中必须说明实际抽取方式。
3. **人工核验点**：优先复核价格类型、销量周期、品牌、成分名称和宣称原文。`ingredient_diff` 只有在组内对比后才可填写。
4. **确定性对比**：按 `keyword_group` 生成横向表，统计功效、成分和关键词 TOP10。可报告样本内数量和分布，但不把高频直接解释为需求，也不把低频直接解释为机会。
5. **导出**：运行 `scripts/build_report.py --input research_bundle.json --output 竞品分析.xlsx`，产出“竞品数据明细、横向对比、词频统计”三个 Sheet。

## 输出边界

可输出字段表、缺失/异常项、样本内对比、词频和 Excel。不独立输出竞品推荐、市场生命周期、需求强弱、品类机会、新品定位、配方/宣称/定价建议。

## 资源

- [字段与 Excel 结构](references/field-schema.md)
- [上游数据与兜底录入](references/data-collection.md)
- [LLM 抽取](references/llm-prompt.md)
- [确定性对比边界](references/analysis-framework.md)

