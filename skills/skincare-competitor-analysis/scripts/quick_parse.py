# -*- coding: utf-8 -*-
"""文本快解析 CLI：粘贴商品标题/详情/笔记正文 → 结构化竞品字段（JSON）

用法示例：
  python quick_parse.py --name "珀莱雅双抗精华液 30ml 抗糖抗氧提亮肤色" --text "..."
  python quick_parse.py --text "【热卖】多肽紧致精华 烟酰胺提亮 已售3.2万件 到手价199元" --platform 淘宝 --keyword-group 紧致精华
  python quick_parse.py --text "..." --append items.json
"""
import argparse
import json
import os
import sys

from extractor import analyze as rule_analyze
from llm_extract import llm_analyze


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="文本快解析：商品标题/详情/笔记 → 结构化竞品字段")
    parser.add_argument("--name", default="", help="商品标题/品名")
    parser.add_argument("--text", default="", help="商品描述/笔记正文（可从 stdin 读取）")
    parser.add_argument("--shop", default="", help="店铺或作者")
    parser.add_argument("--platform", default="", help="平台（淘宝/小红书/抖音等）")
    parser.add_argument("--keyword-group", dest="keyword_group", default="", help="搜索词分组")
    parser.add_argument("--use-llm", action="store_true", help="使用 LLM 结构化（需配置 LLM_API_KEY 或 --config）")
    parser.add_argument("--config", default="", help="LLM 配置文件（JSON：llm_api_key/llm_base_url/llm_model）")
    parser.add_argument("--append", default="", help="把结果追加到指定 JSON 数组文件")
    args = parser.parse_args()

    name = args.name
    text = args.text
    if not text and not sys.stdin.isatty():
        text = sys.stdin.read().strip()

    cfg = {}
    if args.config:
        with open(args.config, encoding="utf-8") as f:
            cfg = json.load(f)

    if args.use_llm:
        item, used_llm = llm_analyze(name, text, args.shop, args.platform, args.keyword_group, cfg)
    else:
        item = rule_analyze(name, text, args.shop, args.platform, args.keyword_group)
        used_llm = False
    item.setdefault("source", "quick_parse")
    item.setdefault("raw_text", text)
    item.setdefault("extraction_method", "llm" if used_llm else "rule")
    item.setdefault("review_status", "unreviewed")

    if args.append:
        rows = []
        if os.path.exists(args.append):
            with open(args.append, encoding="utf-8") as f:
                rows = json.load(f)
        if not isinstance(rows, list):
            rows = []
        rows.append(item)
        with open(args.append, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        print(f"已追加到 {args.append}，当前共 {len(rows)} 条")
    else:
        print(json.dumps(item, ensure_ascii=False, indent=2))
        print(f"# 解析方式: {'LLM' if used_llm else '规则'}", file=sys.stderr)


if __name__ == "__main__":
    main()
