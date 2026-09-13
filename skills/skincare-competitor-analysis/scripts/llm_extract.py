# -*- coding: utf-8 -*-
"""可选 AI 结构化抽取（OpenAI 兼容接口，urllib 实现，无额外依赖）

配置优先级：config 参数 dict > 环境变量 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL
未配置时自动降级为规则抽取（extractor.analyze）。
"""
import os
import json
import urllib.request

from extractor import analyze


SYSTEM_PROMPT = (
    "你是一名资深电商竞品分析师。请从给出的商品标题和原始描述文本中提取结构化竞品信息，"
    "只输出一个 JSON 对象（不要 markdown 代码块）。"
    "字段固定为：name(品名，去掉促销口水词), brand(品牌), keywords(关键词用、分隔最多10个), "
    "effects(功效用、分隔), selling_points(核心卖点用；分隔), ingredients(成分用、分隔), "
    "ingredient_diff(单品抽取时固定为空字符串，形成对比组并复核后再填), price(数字或null), sales(数字或null), "
    "sales_text(销量原文如已售3.2万件), shop(店铺或作者)。"
    "只依据原文提取，不要编造原文中不存在的成分或功效，无法确定的字段给空字符串或null。"
)


def llm_analyze(name, raw_text, shop="", platform="", keyword_group="", config=None):
    """调用 LLM 结构化，失败时回退规则抽取。返回 (dict, used_llm)"""
    cfg = config or {}
    key = (cfg.get("llm_api_key") or os.environ.get("LLM_API_KEY") or "").strip()
    if not key:
        return analyze(name, raw_text, shop, platform, keyword_group), False
    base = (cfg.get("llm_base_url") or os.environ.get("LLM_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    model = cfg.get("llm_model") or os.environ.get("LLM_MODEL") or "gpt-4o-mini"
    url = base + "/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "商品标题：" + (name or "") + "\n\n描述/笔记内容：\n" + (raw_text or "")[:4000]},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + key,
    })
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        parsed.setdefault("platform", platform)
        parsed.setdefault("keyword_group", keyword_group)
        parsed.setdefault("shop", shop)
        parsed["ingredient_diff"] = ""
        return parsed, True
    except Exception as e:
        print("[llm] LLM 抽取失败，回退规则抽取:", e)
        return analyze(name, raw_text, shop, platform, keyword_group), False


if __name__ == "__main__":
    import argparse
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="AI 结构化抽取（未配置 Key 时自动回退规则抽取）")
    parser.add_argument("--name", default="", help="商品标题/品名")
    parser.add_argument("--text", default="", help="商品描述/笔记正文")
    parser.add_argument("--shop", default="", help="店铺或作者")
    parser.add_argument("--platform", default="", help="平台")
    parser.add_argument("--keyword-group", dest="keyword_group", default="", help="搜索词分组")
    parser.add_argument("--config", default="", help="可选配置文件（JSON，含 llm_api_key/llm_base_url/llm_model）")
    args = parser.parse_args()
    cfg = {}
    if args.config:
        with open(args.config, encoding="utf-8") as f:
            cfg = json.load(f)
    result, used = llm_analyze(args.name, args.text, args.shop, args.platform, args.keyword_group, cfg)
    print(json.dumps({"used_llm": used, "item": result}, ensure_ascii=False, indent=2))
