# -*- coding: utf-8 -*-
"""规则式字段抽取引擎

从商品标题 / 详情文本 / 笔记正文中抽取结构化竞品字段：
品名、品牌、关键词、功效、卖点、成分、价格、销量。
规则无法覆盖的部分可通过 LLM 结构化（见 llm_extract.py）或人工编辑兜底。
"""
import re


# ---------------------------------------------------------------- 词典
EFFECT_WORDS = [
    "保湿", "补水", "滋润", "美白", "淡斑", "提亮", "亮肤", "焕亮", "抗皱", "淡纹",
    "紧致", "提拉", "紧实", "舒缓", "修复", "修护", "维稳", "控油", "祛痘", "去痘",
    "祛闭口", "清洁", "去角质", "温和清洁", "防晒", "隔离", "抗氧化", "抗糖", "抗老",
    "抗初老", "滋养", "嫩肤", "柔嫩", "细腻", "收缩毛孔", "隐形毛孔", "去黑头",
    "去粉刺", "去屑", "止痒", "防脱", "防脱发", "育发", "蓬松", "柔顺", "顺滑",
    "遮瑕", "持妆", "持久", "防水", "防汗", "防晕染", "显白", "显瘦", "减龄",
    "消肿", "紧致提拉", "深层清洁", "平衡水油", "水油平衡", "褪红", "抗敏",
    "敏感肌可用", "温和不刺激", "去黄", "去暗沉", "光滑", "细腻毛孔", "强韧",
    "弹润", "嘭弹", "充盈", "饱满", "透亮", "水润", "莹润", "润泽", "丝滑",
    "清爽", "易吸收", "好吸收", "吸收快", "不粘腻", "不油腻", "不闷痘", "不堵塞毛孔",
    "不拔干", "不假白", "不搓泥", "零添加", "无添加", "无香精", "无酒精", "无色素",
    "纯天然", "有机", "医美", "刷酸", "修红", "祛黄气", "亮泽", "抚平", "淡化细纹",
    "改善暗沉", "提亮肤色", "匀净", "透白", "净白", "改善粗糙", "软化角质",
]

INGREDIENT_WORDS = [
    "烟酰胺", "玻尿酸", "透明质酸", "玻尿酸钠", "视黄醇", "A醇", "维A醇", "维A酸",
    "维生素C", "维C", "VC", "抗坏血酸", "神经酰胺", "角鲨烷", "水杨酸", "果酸",
    "杏仁酸", "壬二酸", "传明酸", "氨甲环酸", "熊果苷", "α-熊果苷", "胜肽", "多肽",
    "胶原蛋白", "重组胶原", "玻色因", "麦角硫因", "虾青素", "辅酶Q10", "泛醇",
    "B5", "维生素B5", "维生素E", "生育酚", "二裂酵母", "酵母精华", "积雪草",
    "金盏花", "茶树", "茶树精油", "芦荟", "人参", "灵芝", "冬虫夏草", "海藻",
    "薄荷", "艾草", "生姜", "姜根", "何首乌", "侧柏叶", "氨基酸", "氨基酸表活",
    "皂基", "无硅油", "硅油", "水解蛋白", "水解胶原", "尿囊素", "甘草酸二钾",
    "红没药醇", "姜黄素", "白藜芦醇", "阿魏酸", "富勒烯", "依克多因", "Ectoin",
    "腺苷", "咖啡因", "茶多酚", "橄榄油", "椰子油", "乳木果油", "霍霍巴油",
    "荷荷巴油", "玫瑰果油", "马齿苋", "洋甘菊", "母菊", "薰衣草", "迷迭香",
    "薄荷醇", "樱花", "樱花提取物", "莲花", "睡莲", "天山雪莲", "雪绒花",
    "蓝铜胜肽", "六胜肽", "五胜肽", "乙酰基六肽", "神经酰胺NP", "神经酰胺1",
    "神经酰胺2", "神经酰胺3", "聚谷氨酸", "PGA", "甘油", "丙二醇", "丁二醇",
    "戊二醇", "辛酰羟肟酸", "对羟基苯乙酮", "北美金缕梅", "金缕梅", "茶树油",
    "迷迭香叶", "小分子", "大分子", "微分子", "玻色因溶液", "玻尿酸分子",
]

POINT_MARKERS = [
    "卖点", "功效", "特点", "亮点", "主打", "专为", "针对", "核心成分", "关键成分",
    "成分党", "配方", "黑科技", "专利", "独家", "首创", "升级版", "加量", "赠",
    "买一送一", "性价比", "一瓶多用", "温和", "敏感肌", "孕妇可用", "婴儿可用",
    "实测", "亲测", "口碑", "回购", "无限回购", "空瓶", "见效", "立竿见影",
    "一次见效", "坚持使用", "28天", "14天", "7天", "三天", "一周", "一个月",
]

TITLE_NOISE = [
    "包邮", "正品", "官方", "旗舰店", "专卖店", "自营", "新品", "爆款", "热卖",
    "特价", "促销", "活动", "限时", "秒杀", "清仓", "特惠", "优惠", "满减",
    "领券", "券后", "到手价", "拍下", "立减", "赠品", "买一送一", "买二送一",
    "同款", "推荐", "必入", "必买", "人气", "销量", "好评", "五星", "排行",
    "排行榜", "大牌", "小众", "平价", "贵妇", "学生党", "打工人", "懒人",
    "油皮", "干皮", "混油", "混干", "中性皮", "敏感皮", "痘肌", "新手",
    "推荐指数", "颜值", "高级感", "氛围感", "仪式感", "一用就爱上", "绝了",
    "超好用", "巨好用", "闭眼入", "冲", "冲鸭", "yyds", "YYDS", "天花板",
    "王者", "平价替代", "平替", "国货之光", "空瓶记", "回购清单", "宝藏",
    "挖到宝", "捡到宝", "不踩雷", "避雷", "测评", "评测", "开箱", "分享",
    "种草", "拔草", "指南", "攻略", "教程", "合集", "清单", "红黑榜",
]

BRAND_HINTS = [
    "欧莱雅", "兰蔻", "雅诗兰黛", "SK-II", "SK2", "海蓝之谜", "赫莲娜", "娇兰",
    "娇韵诗", "资生堂", "CPB", "肌肤之钥", "黛珂", "奥尔滨", "悦木之源", "科颜氏",
    "倩碧", "理肤泉", "薇姿", "雅漾", "修丽可", "城野医生", "雪肌精", "澳尔滨",
    "后", "雪花秀", "whoo", "WHOO", "爱茉莉", "兰芝", "悦诗风吟", "伊思", "AHC",
    "自然乐园", "蒂佳婷", "梦妆", "菲诗小铺", "谜尚", "赫拉", "HERA", "兰芝",
    "百雀羚", "相宜本草", "自然堂", "珀莱雅", "丸美", "韩束", "一叶子", "膜法世家",
    "御泥坊", "美即", "佰草集", "高姿", "温碧泉", "卡姿兰", "玛丽黛佳", "完美日记",
    "花西子", "毛戈平", "橘朵", "酵色", "INTO YOU", "into you", "珂拉琪", "colorkey",
    "尔木萄", "溪木源", "薇诺娜", "玉泽", "至本", "瑷尔博士", "米蓓尔", "润百颜",
    "夸迪", "可复美", "敷尔佳", "绽妍", "创福康", "芙清", "博乐达", "上水和肌",
    "至盈", "华熙生物", "福瑞达", "优时颜", "HBN", "hbn", "谷雨", "半亩花田",
    "多芬", "力士", "潘婷", "海飞丝", "清扬", "飘柔", "沙宣", "施华蔻", "欧莱雅男士",
    "高夫", "妮维雅", "曼秀雷敦", "大宝", "隆力奇", "六神", "舒肤佳", "滴露",
    "花王", "狮王", "高露洁", "佳洁士", "云南白药", "片仔癀", "同仁堂", "修正",
    "仁和", "哈药", "养生堂", "汤臣倍健", "Swisse", "斯维诗", "FANCL", "芳珂",
    "DHC", "蝶翠诗", "Fancl", "无印良品", "MUJI", "muji", "MINISO", "名创优品",
    "屈臣氏", "丝芙兰", "宝洁", "联合利华", "欧舒丹", "茱莉蔻", "伊索", "Aesop",
    "野兽派", "观夏", "闻献", "祖玛珑", "Jo Malone", "jo malone", "Diptyque",
    "蒂普提克", "帕尔玛之水", "Byredo", "百瑞德", "Tom Ford", "汤姆福特",
    "阿玛尼", "ARMANI", "armani", "YSL", "圣罗兰", "迪奥", "Dior", "dior",
    "香奈儿", "Chanel", "chanel", "纪梵希", "Givenchy", "givenchy", "古驰",
    "Gucci", "gucci", "普拉达", "Prada", "prada", "爱马仕", "Hermès", "hermes",
    "巴宝莉", "Burberry", "burberry", "蔻驰", "Coach", "coach", "MK", "迈克科尔斯",
    "MCM", "mcm", "凯迪拉克", "五菱", "比亚迪", "华为", "小米", "苹果", "iPhone",
    "iphone", "戴森", "Dyson", "dyson", "飞利浦", "松下", "索尼", "Sony", "sony",
    "美的", "格力", "海尔", "九阳", "苏泊尔", "小熊", "米家", "京东京造",
    "网易严选", "严选", "三只松鼠", "良品铺子", "百草味", "卫龙", "旺旺", "康师傅",
    "统一", "农夫山泉", "元气森林", "喜茶", "奈雪", "霸王", "章光101", "养元青",
    "吕", "滋源", "阿道夫", "欧芭", "卡诗", "KÉRASTASE", "卡诗", "馥绿德雅",
]

# ---------------------------------------------------------------- 基础工具
def clean_title(title):
    """去掉促销/口水词，保留品名主体"""
    if not title:
        return ""
    t = re.sub(r"【[^】]*】", " ", title)
    t = re.sub(r"\[[^\]]*\]", " ", t)
    t = re.sub(r"\([^)]*\)", " ", t)
    t = re.sub(r"（[^）]*）", " ", t)
    for noise in TITLE_NOISE:
        t = t.replace(noise, " ")
    t = re.sub(r"\s+", " ", t).strip(" -_|｜·")
    return t


def split_sentences(text):
    if not text:
        return []
    parts = re.split(r"[。！？!?\n；;]+", text)
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if len(p) > 60:
            for sub in re.split(r"[，,]+", p):
                sub = sub.strip()
                if sub:
                    out.append(sub)
        else:
            out.append(p)
    return out


def find_matches(text, words):
    if not text:
        return []
    found = []
    for w in words:
        if w in text and w not in found:
            found.append(w)
    return found


def extract_keywords(title, raw_text=""):
    """关键词 = 话题标签 + 标题有效词元"""
    text = (title or "") + " " + (raw_text or "")
    kws = []
    for m in re.findall(r"#([\w\u4e00-\u9fff]+)", text):
        if m not in kws:
            kws.append(m)
    t = clean_title(title or "")
    for tok in re.split(r"[\s,，、|｜/]+", t):
        tok = tok.strip()
        if len(tok) >= 2 and not any(c.isdigit() for c in tok):
            if tok not in kws and tok not in TITLE_NOISE:
                kws.append(tok)
    # 标题里常见的功效词也是关键词
    for w in find_matches((title or "") + (raw_text or "")[:200], EFFECT_WORDS):
        if w not in kws:
            kws.append(w)
    return "、".join(kws[:12])


def extract_effects(text):
    found = find_matches(text, EFFECT_WORDS)
    # 顺序调整：功效词较长者优先（如"收缩毛孔" 优于 "毛孔"）
    return "、".join(found[:10])


def extract_ingredients(text):
    found = find_matches(text, INGREDIENT_WORDS)
    found.sort(key=len, reverse=True)
    return "、".join(found[:20])


def extract_selling_points(title, raw_text):
    """卖点 = 标题【】内容 + 含功效/成分/程度词的句子"""
    points = []
    text = (title or "") + " " + (raw_text or "")
    for m in re.findall(r"[【\[]([^】\]]{2,30})[】\]]", title or ""):
        if m not in points:
            points.append(m)
    for sent in split_sentences(raw_text):
        if len(sent) > 200:
            sent = sent[:200]
        score = 0
        if any(mk in sent for mk in POINT_MARKERS):
            score += 2
        if find_matches(sent, EFFECT_WORDS):
            score += 1
        if find_matches(sent, INGREDIENT_WORDS):
            score += 1
        if re.search(r"\d+[%％]|\d+倍|\d+秒|立竿见影|即刻|瞬间|持久|一次见效|有效改善", sent):
            score += 1
        if re.search(r"[￥¥]|到手价|券后价|\d+元|已售|月销|销量|拍下立减", sent):
            score -= 2
        if score >= 2 and sent not in points:
            points.append(sent)
    # 标题中带功效词的短句
    for seg in re.split(r"[\s,，、|｜]+", title or ""):
        seg = seg.strip()
        has_marker = any(mk in seg for mk in
                         ["质地", "清爽", "不", "温和", "敏感", "持久", "秒", "倍",
                          "%", "深层", "主打", "专为", "针对", "修护", "紧致",
                          "提亮", "美白", "抗皱", "淡纹", "控油", "保湿", "补水"])
        if 2 <= len(seg) <= 18 and find_matches(seg, EFFECT_WORDS) and has_marker:
            if seg not in points:
                points.append(seg)
    return "；".join(points[:12])


def extract_price(text):
    if not text:
        return None
    patterns = [
        r"[￥¥]\s*(\d+(?:\.\d{1,2})?)",
        r"(\d+(?:\.\d{1,2})?)\s*元",
        r"到手价\s*(\d+(?:\.\d{1,2})?)",
        r"券后价\s*(\d+(?:\.\d{1,2})?)",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                continue
    return None


def extract_sales(text):
    """销量：'已售3.2万件' / '月销5000+' / '5000+人付款' -> (数值, 原文)"""
    if not text:
        return None, ""
    text = text.replace(" ", "")
    m = re.search(
        r"(?:已售|月销|销量|售出|热卖|付款|人付款|件售出)[:：]?\s*([\d.]+)\s*([万wW]?)\s*(\+?)\s*(件|单|瓶|盒|个|箱|双|片)?",
        text,
    )
    if not m:
        m = re.search(r"([\d.]+)\s*([万wW]?)\s*\+?\s*(?:人付款|件|笔)", text)
    if not m:
        m = re.search(
            r"(?:已售|月销|销量)[:：]?\s*([\d.]+)\s*([万wW]?)\s*(\+?)\s*(件|单|瓶|盒|个|箱|双|片)?",
            text,
        )
    if m:
        num = float(m.group(1))
        unit = m.group(2) or ""
        plus = bool(m.group(3) if m.lastindex >= 3 else False)
        if unit in ("万", "w", "W"):
            num = num * 10000
        raw = m.group(0)
        if plus and not raw.endswith("+"):
            raw += "+"
        return int(num) if num.is_integer() else num, raw
    return None, ""


def guess_brand(name, shop=""):
    text = (name or "") + " " + (shop or "")
    best = None
    for b in BRAND_HINTS:
        if b in text:
            if best is None or len(b) > len(best):
                best = b
    if best:
        return best
    # 店铺名常见后缀
    m = re.search(r"^([\u4e00-\u9fffA-Za-z]{2,10})(?:旗舰店|官方店|专卖店|自营店|企业店)", shop or "")
    if m:
        return m.group(1)
    return ""


def analyze(name="", raw_text="", shop="", platform="", keyword_group="", price=None, sales=None, sales_text=""):
    """对单个商品做全字段抽取，返回可直接入库的 dict"""
    title = name or ""
    text = raw_text or ""
    cleaned = clean_title(title)
    if not cleaned and text:
        cleaned = clean_title(text[:80])
    price = price if price is not None else extract_price(text + " " + title)
    sales_val, sales_raw = extract_sales(text + " " + title) if sales is None else (sales, sales_text)
    return {
        "name": cleaned or title[:80],
        "brand": guess_brand(cleaned, shop),
        "keywords": extract_keywords(title, text),
        "effects": extract_effects(text + " " + title),
        "selling_points": extract_selling_points(title, text),
        "ingredients": extract_ingredients(text + " " + title),
        "ingredient_diff": "",
        "price": price,
        "sales": sales_val if sales is None else sales,
        "sales_text": sales_raw,
        "shop": shop,
        "platform": platform,
        "keyword_group": keyword_group,
    }


if __name__ == "__main__":
    import argparse
    import json
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="规则式竞品字段抽取（可离线运行，无需 API Key）")
    parser.add_argument("--name", default="", help="商品标题/品名")
    parser.add_argument("--text", default="", help="商品描述/笔记正文")
    parser.add_argument("--shop", default="", help="店铺或作者")
    parser.add_argument("--platform", default="", help="平台（淘宝/小红书/抖音等）")
    parser.add_argument("--keyword-group", dest="keyword_group", default="", help="搜索词分组")
    args = parser.parse_args()
    result = analyze(args.name, args.text, args.shop, args.platform, args.keyword_group)
    print(json.dumps(result, ensure_ascii=False, indent=2))
