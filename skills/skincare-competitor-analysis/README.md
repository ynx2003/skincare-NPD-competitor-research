# skincare-competitor-analysis

护肤、美妆和个护竞品数据的整理与导出 Skill。接收已有文本、标准 JSON、`research_bundle.json` 或使用内部英文字段名的 CSV，完成字段标准化、数据质检、分组横向对比、词频统计和 Excel 导出。

它不负责推荐竞品、操作网页、判断市场阶段或提出产品策略。完整的“判断 → 采集 → 整理 → 解释”流程使用上层 `skincare-competitor-research`。

## 快速使用

需要 Python 3.9+ 与 `openpyxl`：

```bash
pip install -r requirements.txt

python scripts/quick_parse.py \
  --name "珀莱雅双抗精华液 30ml 抗糖抗氧提亮肤色" \
  --text "双抗体系抗糖+抗氧，2%麦角硫因+虾青素，已售8.2万件，到手价269元" \
  --platform 淘宝 --keyword-group 双抗精华

python scripts/build_report.py \
  --input examples/items.sample.json \
  --output 竞品分析_双抗精华.xlsx \
  --keyword 双抗精华
```

配置 `LLM_API_KEY` 后可给 `quick_parse.py` 增加 `--use-llm`；调用失败会回退到规则抽取，并在输出中记录实际抽取方式。

## 输出

- 结构化 JSON：包含标准字段、原始文本、抽取方式和复核状态。
- Excel：竞品数据明细、按 `keyword_group` 横向对比、功效/成分/关键词 TOP10。

详细字段与边界以 `SKILL.md` 和 `references/` 为准。
