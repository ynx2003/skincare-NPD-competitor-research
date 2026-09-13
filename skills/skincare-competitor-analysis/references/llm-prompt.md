# LLM 结构化：提示词与配置

## 配置方式

优先级：`--config` JSON 文件 > 环境变量 > 默认值。

- 环境变量：`LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL`
- 配置文件 JSON：

```json
{
  "llm_api_key": "sk-xxx",
  "llm_base_url": "https://api.deepseek.com/v1",
  "llm_model": "deepseek-chat"
}
```

默认 base：`https://api.openai.com/v1`，默认模型：`gpt-4o-mini`。任何 OpenAI 兼容 `/chat/completions` 服务（OpenAI/DeepSeek/通义/Moonshot 等）均可。

## 系统提示词（SYSTEM_PROMPT）

```text
你是一名资深电商竞品分析师。请从给出的商品标题和原始描述文本中提取结构化竞品信息，
只输出一个 JSON 对象（不要 markdown 代码块）。
字段固定为：name(品名，去掉促销口水词), brand(品牌), keywords(关键词用、分隔最多10个),
effects(功效用、分隔), selling_points(核心卖点用；分隔), ingredients(成分用、分隔),
ingredient_diff(单品抽取时固定为空字符串，形成对比组并复核后再填), price(数字或null), sales(数字或null),
sales_text(销量原文如已售3.2万件), shop(店铺或作者)。
只依据原文提取，不要编造原文中不存在的成分或功效，无法确定的字段给空字符串或null。
```

用户消息格式：`商品标题：{name}\n\n描述/笔记内容：\n{raw_text[:4000]}`，`temperature=0`，`response_format={"type":"json_object"}`。

## 使用规则

- 未配置 Key 或调用失败 → 自动回退 `extractor.analyze` 规则抽取，不阻塞流程。
- 只依据原文，不编造成分/功效；无法确定给空值。
- 单条商品材料不能证明“差异”，所以 `ingredient_diff` 固定留空。
- 对长文本截取前 4000 字符，避免超限。
