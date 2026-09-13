# Skincare Competitor Research Skills

一组用于护肤、美妆和个护NPD阶段竞品研究的 Codex Skills：

- `skincare-competitor-research`：负责调研判断、竞品推荐、市场阶段判断、页面采集编排和证据化业务结论。
- `skincare-competitor-analysis`：负责已有资料的字段抽取、质量检查、横向对比、词频统计和 Excel 导出。

完整工作流是：`判断 → 用户确认 → browser67 采集 → 数据整理 → 业务解释`。只整理已有数据时，可单独使用下层 Skill。

## 依赖

- Codex Skills 环境；
- 需要操作真实 Chrome/Edge 页面时，另行安装并配置 [`browser67`](https://github.com/bigKING67/browser67)；
- 需要导出 Excel 时，安装 Python 依赖：

```bash
python3 -m pip install -r skills/skincare-competitor-analysis/requirements.txt
```

本仓库不包含浏览器登录状态、API Key 或平台采集结果。

## 安装

克隆仓库后，将两个 Skill 复制到个人 Skills 目录：

```bash
git clone <your-repository-url>
cd skincare-competitor-research
mkdir -p ~/.agents/skills
cp -R skills/skincare-competitor-research ~/.agents/skills/
cp -R skills/skincare-competitor-analysis ~/.agents/skills/
```

重启 Codex 或新建任务后，通过 `$skincare-competitor-research` 启动完整调研；通过 `$skincare-competitor-analysis` 整理已有数据。

## 数据边界

- 页面价格、销量和宣称必须保留来源 URL、采集时间和原文；
- 微信公众号和二手文章只作为线索，优先回溯原始报告；
- 明确区分已确认事实、合理推测、建议和暂时无法验证的信息；
- 不绕过登录、验证码或平台保护，不提交 `.env`、`research_bundle.json` 等私人数据。

## 仓库结构

```text
skills/
├── skincare-competitor-research/
└── skincare-competitor-analysis/
```
