# 上游数据与兜底录入

本 Skill 不实现淘宝、小红书或抖音采集器。端到端任务由 `skincare-competitor-research` 调用 browser67 采集；本 Skill 只验收和加工交接数据。

交接优先级：`research_bundle.json` → JSON 数组 → 内部英文字段名 CSV → 用户粘贴原文。没有页面证据时可继续整理，但来源必须标记为“用户提供”或“待核验”，不得写成实时采集。

