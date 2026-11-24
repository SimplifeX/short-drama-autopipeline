# MiniMax H3 提示词工程手册索引（按需加载）

本目录由 MiniMax H3 官方中文提示词工程手册无损拆分而成，用于 Stage 5 按任务按需加载，避免一次性将 2395 行全量载入上下文。

## 工作流与优先级

1. **判断模式**：`T2VA`、`I2VA`、`FL2VA`、`L2VA` 或 `Ref2VA`。
2. **先结构后正文**：先定时间轴、参考素材角色表和说话人 ID，再写镜头正文。
3. **保留原语言**：用户对白、歌词和画面文字保留原语言，不自行改写。
4. **规则优先级**：官方固定字段、标签、时间格式与能力边界（`90-official.md` 第 21–26 章）为最高优先级；第 1–20 章为生产工程方法，不得覆盖官方硬限制。

## 任务 → 必读章节路由表

| 当前任务 | 必读文件 | 涵盖章节 |
|---|---|---|
| 写普通首帧 I2VA / T2VA / FL2VA / L2VA 镜头结构与运镜 | [`10-structure.md`](./10-structure.md) | §1–9：目标、官方边界（4–15s）、工作流、Base 三段式、四种模式、Shot 时间轴、运镜、连续性 |
| 写中文/多角色对白、口型、旁白、环境声分层 | [`20-dialogue.md`](./20-dialogue.md) | §10–12：稳定说话人 ID、`<d>` 标签、旁白/跨镜对白、画面文字、声音分层 |
| 写多参考素材（Ref2VA 全参考模式） | [`30-ref2va.md`](./30-ref2va.md) | §13：四类标签、`subject_definitions`、`summary`、`retention_analysis`、`detailed_description` |
| 套用现成模板或理解约束竞争/状态守恒原理 | [`40-principles.md`](./40-principles.md) | §14–15：条件图原理、时间约束、信息污染、五种模式生产模板与中文对白示例 |
| 出片前审计、出片失败排查与返工修正 | [`50-qa.md`](./50-qa.md) | §16–20：常见失败与修正、生成前审计清单、生成后验收清单、Agent 执行规范、十条原则 |
| 核查官方固定语法、字段顺序、输入上限或 2K 再生成 | [`90-official.md`](./90-official.md) | §21–26：官方 README、Base Guide、Ref2VA Guide 完整中文覆盖与版本快照 |

## 来源与版本

- 派生自 MiniMax H3 中文提示词工程手册 **v2.0.0**（官方文档快照日期：**2026-08-31**）
- 官方仓库：https://github.com/MiniMax-AI/MiniMax-H3
- 中文 README：https://github.com/MiniMax-AI/MiniMax-H3/blob/main/README.zh-CN.md
- Base Prompt Guide：https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md
- 官方 Skill：https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md
- Ref2VA Guide：https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/ref-en.txt
- 拆分方式：按章无损切分（正文内容与原手册 2395 行完全一致，已去除分片内残留 front matter 以免被技能扫描器误识别为嵌套技能）
