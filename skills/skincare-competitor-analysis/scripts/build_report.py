# -*- coding: utf-8 -*-
"""竞品分析报告生成 CLI：items.json / CSV → Excel（明细 + 横向对比 + 词频统计）

用法示例：
  python build_report.py --input items.json --output 竞品分析_双抗精华.xlsx
  python build_report.py --input items.json --output report.xlsx --keyword 双抗精华 --platform 淘宝
  python build_report.py --input data.csv --output report.xlsx
"""
import argparse
import csv
import json

from export_xlsx import default_filename, export_xlsx


def load_items(path):
    if path.lower().endswith(".csv"):
        rows = []
        with open(path, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                rows.append({k: (v if v not in ("", None) else None) for k, v in r.items()})
        return rows
    with open(path, encoding="utf-8-sig") as f:
        data = json.load(f)
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return data["items"]
    if isinstance(data, list):
        return data
    raise SystemExit(f"无法识别数据格式: {path}")


def main():
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="生成竞品分析 Excel（数据明细/横向对比/词频统计）")
    parser.add_argument("--input", required=True, help="输入 JSON 数组或 CSV 文件")
    parser.add_argument("--output", default="", help="输出 xlsx 路径（默认自动命名）")
    parser.add_argument("--keyword", default="", help="搜索词（写入词频表汇总）")
    parser.add_argument("--platform", default="", help="平台（用于默认文件名）")
    args = parser.parse_args()

    items = load_items(args.input)
    if not items:
        raise SystemExit("没有数据可导出")
    meta = {"keyword": args.keyword}
    output = args.output or default_filename(args.keyword, args.platform)
    with open(output, "wb") as f:
        f.write(export_xlsx(items, meta))
    print(f"已生成 {output}（{len(items)} 条商品）")


if __name__ == "__main__":
    main()
