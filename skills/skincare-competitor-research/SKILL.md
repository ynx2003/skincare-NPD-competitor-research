---
name: skincare-competitor-research
description: 编排护肤、美妆和个护竞品的端到端研究：根据关键词与调研目的设计维度、推荐竞品、判断是否需要市场阶段研究，待用户确认后通过 browser67 采集页面，再调用 skincare-competitor-analysis 整理导出并给出证据化业务结论。适用于新品立项、产品定位、卖点/成分/价格对比和品类机会研究；单纯整理已有数据时改用 skincare-competitor-analysis。
---

# 护肤竞品研究编排

负责“判断 → 确认 → 采集 → 整理 → 解释”的闭环。执行层 Skill 不重复决定研究问题或统计数据。

## 1. 判断

从用户获取或合理推定：关键词/产品、调研目的、市场范围、平台、人群、价格带和时间范围。只有缺失信息会改变样本边界或结论时才追问。

先交付 `ResearchBrief`：

- 要回答的业务问题；
- 调研维度及每个维度服务的决策；
- 样本纳入/排除规则；
- 直接竞品、需求替代品、标杆参考及纳入理由；
- 目标页面清单；
- `market_stage_required: yes|no`、理由、待验证指标和来源计划。

竞品推荐必须搜索并核对当前在售产品、官方信息和直接页面，不凭记忆编名单。不把“品牌有名”当成“产品可比”；说明人群、需求、形态、价格和渠道的匹配与不匹配。

## 2. 市场阶段（条件性）

品类进入、新品立项、增长/空白、上市时机、产品组合、中长期定位、定价或渠道策略默认需要。单品页面拆解、文案/成分宣称对比或已确定样本的数据整理通常不需要。边界不清时，看结论是否需要推断“需求和供给随时间的变化”。

需要时读取 [市场阶段证据规则](references/market-stage.md)，搜索当前研报、消费调查和原始统计。

## 3. 确认门

采集前请用户确认 ResearchBrief、竞品名单和市场阶段方案；未确认时不进入大规模采集。用户确认已打开目标页面后再启动 browser67。该确认只授权本次研究范围内的页面采集。

## 4. browser67 采集

实时页面工作前读取 `browser67` Skill 和宿主浏览器规则。

- 先列出 Browser Instance；多实例时不猜测。
- 定位用户确认的 exact tabs。纯读取保持只读；需展开、滚动、切换规格或执行脚本时，按 browser67 契约执行 `inspect_adoption -> adopt_existing`。
- 采集页面事实：品牌、商品名、规格、价格类型/原文、销量类型/原文、成分/功效/卖点宣称、店铺/作者、URL、采集时间和 `raw_text`。
- 失败时记录原因，改用用户粘贴或手动录入；不绕过登录、CAPTCHA 或平台保护。
- 结束时在同一 Browser Instance 内执行 scoped `finalize_task`，释放采用的用户标签页而不关闭它们。

## 5. 数据交接

生成 `research_bundle.json`：

```json
{
  "research": {
    "keyword": "",
    "objective": "",
    "scope": "",
    "sample_rule": "",
    "market_stage_required": "yes|no",
    "market_stage_reason": ""
  },
  "raw_records": [{"record_id": "", "platform": "", "url": "", "captured_at": "", "raw_text": ""}],
  "items": [{"record_id": ""}]
}
```

`raw_records` 是证据底座，`items` 是 `skincare-competitor-analysis` 的标准化输入，两者用稳定 `record_id` 串联。调用下层 Skill 完成抽取、质量标记、横向对比、词频和 Excel；上层不重复这些计算。

## 6. 业务解释

回到 ResearchBrief 的业务问题，分开输出：页面/报告/数据表支持的**已确认事实**，由多条证据归纳的**合理推测**，面向业务决策的**建议**，以及证据不足的**未知**。说明推理链、反证和样本偏差。

不将词频、单平台销量、一份二手研报或“竞品没写”单独视为市场需求或机会证明。每条核心结论尽量回指数据记录或来源。
