## 21. 官方文档完整覆盖说明

本章到第 26 章用于保证本手册不只提炼“常用规则”，而是覆盖下列四份官方文档在 **2026-08-31** 版本中的全部有效信息：

| 官方文件 | 本文对应位置 | 覆盖内容 |
|---|---|---|
| `README.zh-CN.md` | 第 22 章 | 安装、在线入口、系统规格、模型架构、部署、768p 验证、2K 工作流、许可证与联系方式 |
| `skills/h3-prompt-writing/SKILL.md` | 第 23 章 | 官方 Skill 的工作流、模式路由、输出规则和效果建议 |
| `references/base-en.txt` / Hugging Face Base Guide | 第 24 章 | T2VA、I2VA、FL2VA、L2VA 的完整结构、规则、相机、对白、音频和四个案例 |
| `references/ref-en.txt` | 第 25 章 | Ref2VA 六段式、四类标签、任务类型、保留关系、说话人与音频规则和完整案例 |

### 21.1 “完整覆盖”的含义

- 所有官方章节、规则、限制、固定字符串、参数规格、部署命令和示例所表达的信息均写入本文。
- 固定字段、标签、时间格式、特殊 token、命令行参数和关键句式保留英文原形，避免中文翻译破坏可执行性。
- 官方长案例既给出可直接使用的英文结构，也给出中文解释。
- README 中纯装饰性的页眉 GIF、徽章和结果视频缩略图不复制进正文，但其指向的产品、仓库、脚本与结果资源均以链接或表格记录。
- 第 1–20 章包含生产经验；第 21–26 章是官方资料的中文化完整覆盖与版本快照。两者冲突时，以第 21–26 章记录的官方固定格式为准。

### 21.2 官方内容索引

```text
官方 README
├── 提示词编写技能
├── 在线 API / 在线应用
├── 系统概览与输入输出规格
├── H3-Context-IR
├── H3-Base
│   ├── H3-Encoder
│   ├── H3-VisualVAE / H3-AudioVAE
│   └── H3-Omni-Transformer
├── H3-Regenerate-2K
├── H3-Base 本地部署
├── SGLang 部署
├── 可复现 768p 示例
├── 完整 2K 工作流
└── 许可证 / 联系方式

官方 Prompt Skill
├── 模式识别
├── Base Guide 路由
├── Ref Guide 路由
├── 输出规则
└── 效果建议

官方 Base Guide
├── 四种任务
├── 固定首行与三段式
├── 关键帧路径
├── 镜头、运镜、对白、文字与声音
└── 四个完整案例

官方 Ref Guide
├── 六段式
├── Subject / Picture / Video / Audio
├── summary 任务类型
├── retention_analysis
├── detailed_description
├── 音频与说话人
└── 完整案例
```

---

## 22. 官方仓库 README 完整中文覆盖

## 22.1 官方提示词 Skill 的安装与兼容性

官方仓库一共内置九个 Skill。通用的 H3 提示词 Skill 安装命令为：

```bash
npx skills add https://github.com/MiniMax-AI/MiniMax-H3 --skill h3-prompt-writing
```

该 Skill 在 `skills/h3-prompt-writing/references/` 中提供：

- `base-en.txt`：文本与关键帧模式，即 T2VA、I2VA、FL2VA、L2VA。
- `ref-en.txt`：全参考 Ref2VA 模式。

`h3-prompt-writing` 是纯 Markdown 与本地参考文件，不调用外部 API，因而可移植到 Claude Code、Claude Agent SDK、Cursor、Windsurf、OpenAI/Codex 类 Agent、LangChain，以及任何能读取 `SKILL.md` 和本地文件的环境。`agents/openai.yaml` 只提供可选的 ChatGPT/Codex UI 元数据，不会把 Skill 限定在 OpenAI 环境。

其余八个 Skill 面向 MiniMax Hub 画布中的 `hub_generate_video`、`hub_generate_image`、画布节点和选择卡片等专有工作流，官方明确说明它们不能直接移植到通用 Agent：

1. `minimalist-product-ad-generator`
2. `3d-animation-short-generator`
3. `papercraft-stop-motion-explainer`
4. `brand-promo-video-generator`
5. `music-video-subtitle-generator`
6. `co-op-game-intro-generator`
7. `paper-collage-explainer-generator`
8. `handdrawn-live-video-generator`

## 22.2 官方在线入口

### API

- Global：[MiniMax Global Video Generation V2 API](https://platform.minimax.io/docs/api-reference/video-generation-v2-create)
- 中国区：[MiniMax CN Video Generation V2 API](https://platform.minimaxi.com/docs/api-reference/video-generation-v2-create)

### 应用

- Web Global：[hailuoai.video](https://hailuoai.video/tools/minimax-h3)
- Web 中国区：[hailuoai.com](https://hailuoai.com/)
- Desktop / Hub Global：[hub.minimax.io](https://hub.minimax.io/)
- Desktop / Hub 中国区：[hub.minimaxi.com](https://hub.minimaxi.com/)

### 官方站点与社区

- MiniMax 官网：<https://www.minimax.io>
- GitHub：<https://github.com/MiniMax-AI/MiniMax-H3>
- Hugging Face：<https://huggingface.co/MiniMaxAI/MiniMax-H3>
- ModelScope：<https://modelscope.cn/organization/minimax>
- 中国区联系入口：<https://platform.minimaxi.com/docs/faq/contact-us>
- Discord：<https://discord.com/invite/dbMxutw7tP>

官方 README 同时提供英文、简体中文、韩文、日文版本；本文以官方简体中文 README 与两份英文 Prompt Guide 为覆盖基准。

## 22.3 系统概览与官方规格

MiniMax H3 是通用全模态生成系统：统一理解由文本、图像、视频和音频组成的上下文，并生成带原生立体声音频的视频。官方系统最高可到 2K、最长 15 秒，重点是复杂多模态指令遵循与任务泛化。

| 类别 | 官方规格 |
|---|---|
| 输出时长 | 4–15 秒 |
| 宽高比 | 支持多种比例，包括但不限于 21:9、16:9、4:3、1:1、3:4、9:16 |
| 分辨率 | 多种尺寸；默认短边 768 像素；经 H3-Regenerate-2K 可生成 2K |
| 帧率 | 24 FPS |
| 音频 | 32 kHz 立体声 |
| 稳定对白语言 | 阿拉伯语、中文、英语、法语、德语、意大利语、日语、韩语、葡萄牙语、俄语、西班牙语，共 11 种；其他语言也有不同程度支持 |

### 两个模型变体

| 变体 | 输入模式 | 官方输入限制 |
|---|---|---|
| `H3-Base-FL2VA` | T2VA / I2VA / FL2VA / L2VA | 0 张图=T2VA；1 张图=首帧或尾帧；2 张图=首尾帧 |
| `H3-Base-Ref2VA` | 全参考 Ref2VA | 图片 ≤9；视频 ≤3，每段 2–15 秒且总时长 ≤15 秒；音频 ≤3，每段 2–15 秒且总时长 ≤15 秒；音频不能作为唯一输入，必须和图片或视频一起使用；混合输入总文件数 ≤12 |

### 完整 H3 系统的三层结构

1. **H3-Context-IR**：理解、关联和细化自由形式的多模态输入，转换为 H3-Base 容易执行的上下文中间表示。
2. **H3-Base**：根据 Context-IR 输出联合生成 768p 视频与音频。
3. **H3-Regenerate-2K**：把 768p 结果连同原始上下文再次送入 H3，以 in-context 方式重新生成 2K。

官方特别强调：H3-Context-IR 对最终质量非常重要。生产流水线应接入该模块，或依据官方提示词指南自行构建具有相同职责的上下文处理系统。

## 22.4 H3-Context-IR

H3-Context-IR 是托管式预处理与编排系统，面向自由形式的多模态输入。它负责：

- 解析文本、图像、音频、参考视频之间的关系。
- 解析这些素材与目标结果之间的关系。
- 执行指令解析、跨模态关联、时间理解和复杂逻辑推理。
- 把理解结果序列化为 H3-Base 可接受的结构化表示。
- 在不偏离用户原意的前提下，适度补全缺失或描述不足的语义细节。

因为 Context-IR 依赖多阶段工作流与多个托管模型/服务，初始开源版本不包含它。MiniMax 提供 API 复现官方工作流，并提供 Prompt Guide 供开发者自行实现上下文处理。

### 官方安全防护说明

用户提交的文本、图像、视频以及增强后的 Prompt 会经过自动审核；涉嫌违法、色情或侵犯第三方权利的内容可能被拦截。官方说明过滤无法完全消除误判与漏判，且不会替代被许可方在 MiniMax H3 Community License 下承担的合法使用义务。

## 22.5 H3-Base 架构

### 22.5.1 总体数据流

```text
文本 ───────────────→ H3-Encoder ──────────────┐
图像/视频 ─→ H3-Encoder + H3-VisualVAE ───────┤
音频 ───────────────→ H3-AudioVAE ─────────────┤
                                                ↓
                                  统一打包多模态序列 + RoPE
                                                ↓
                                    H3-Omni-Transformer
                                                ↓
                              联合预测视频 latent + 音频 latent
                                                ↓
                                  视频解码 + 32kHz 立体声音频
```

- 文本由 H3-Encoder 编码。
- 视觉输入同时由 H3-Encoder 和 H3-VisualVAE 编码。
- 音频只由 H3-AudioVAE 编码。
- 编码后的不同模态被打包成统一序列，并用 RoPE 表示必要的时空关系。
- H3-Omni-Transformer 联合预测视频和音频 latent，随后分别解码。
- H3 原生支持稀疏注意力训练与推理；初始开源版本只提供全注意力推理，官方计划后续发布稀疏注意力实现。

### 22.5.2 H3-Encoder

- 使用 **Qwen3-VL-32B 的完整预训练权重**。
- 将第 **50 层 hidden states** 提供给 H3-Omni-Transformer。
- tokenizer 中加入了包括 `<d>` 在内的特殊 token。
- 推理时必须使用 H3 仓库提供的 tokenizer 与相关配置，不能随意换成同源模型的普通 tokenizer。

### 22.5.3 H3-VisualVAE

- 时间因果视频自编码器。
- 空间压缩因子 16×。
- 时间压缩因子 4×。
- latent 通道数 24。
- 官方记法：`f16t4d24`。
- Transformer 前，visual latent 在 `(time, height, width)` 上按 `1 × 2 × 2` 继续 patchify。
- 因此进入 Transformer 的视觉 token 有效空间下采样为 32×，时间下采样仍为 4×。
- latent 空间同时为重建质量与生成学习便利性优化。
- 编码器训练后，官方额外训练了 ViT-based decoder，用于降低解码成本并提高重建质量。

### 22.5.4 H3-AudioVAE

- 左右声道使用相同编码器和解码器，但两个声道独立处理。
- 解码后再重新合并为立体声。
- 每个声道把 32 kHz 音频压缩为时间率 40 Hz 的 latent token 序列。
- latent 空间参考 VA-VAE 的思想，在音频重建质量与生成学习便利性之间优化。

### 22.5.5 H3-Omni-Transformer

- 33B 参数、稠密、单流 Transformer。
- 约 13B 参数位于 AdaLN 相关分支。
- AdaLN 调制输出可以预计算并缓存，因此纯推理部署无需加载这部分参数；官方仍发布完整权重以支持微调等二次开发。
- Attention 和 FFN 都没有模态特定结构。
- 模态特定参数仅位于输入/输出层与 AdaLN 分支。
- 模态特定 AdaLN 以较低训练与推理开销提升生成质量。
- 使用三维多模态旋转位置编码 `MM-RoPE`，表达 `(t, h, w)` 三个维度。
- 训练末期引入原生稀疏注意力；初始开源版本暂不包含实现。

## 22.6 H3-Regenerate-2K 的官方定义

H3 的 2K 不是传统“单独训练一个超分模型，对 768p 像素做放大”。官方做法是：让 H3 Base 在原始多模态上下文和低分辨率结果的共同条件下，进行 **in-context 重新生成**。

官方列出的优势：

1. 最大限度复用 H3 Base 自身的生成能力。
2. 重新利用原始上下文，恢复传统超分只能猜测的信息，例如小文字和精细细节。
3. 这是 H3 任务泛化能力的一种体现。

该模块因系统复杂度尚未开源；官方提供 API 验证完整结果，并表示准备就绪后再发布。

## 22.7 推荐工作流

官方给出两种验证路径：

### 路径 A：本地 768p

```text
符合 Guide 的 Prompt
→ 本地 H3-Base
→ 768p 原生音视频
```

### 路径 B：完整 2K

```text
原始多模态输入
→ 官方 H3-Context-IR API
→ 本地 H3-Base
→ 官方 H3-Regenerate-2K API
→ 2K 原生音视频
```

第二条路径把托管 API 和本地 Base 结合起来，用于复现官方直接 API 的 2K 质量。

## 22.8 本地 checkpoint 与目录结构

官方发布两个任务专用 BF16 checkpoint。每个 checkpoint 都包含专用 Omni Transformer，以及 processor、tokenizer、text encoder、Visual VAE、Audio VAE。

| Checkpoint | 支持任务 | 条件 | 输出 | 精度 |
|---|---|---|---|---|
| MiniMax-H3 Base FL2VA | `t2va`、`fl2va`，包含首帧/尾帧/首尾帧 | 文本；可选首帧、尾帧或两者 | 视频+音频 | BF16 |
| MiniMax-H3 Base Ref2VA | `ref2va` | 文本和参考图像/视频/音频 | 视频+音频 | BF16 |

官方发布的是经过 **CFG distillation** 的 Omni Transformer 权重。

每个任务仓库是自包含 Hugging Face 风格目录：

```text
<TASK>/
├── model_index.json
├── processor/
├── tokenizer/
├── text_encoder/
├── transformer/
├── visual_vae/
└── audio_vae/
```

仓库同时托管原始 checkpoint 与 diffusers 格式。仓库级公开入口为根目录 `model_index.json`；任务族索引仍在 `FL2VA/model_index.json` 与 `Ref2VA/model_index.json`。

```bash
# 原始 checkpoint：下载两个任务族，供 SGLang / vLLM 等使用
hf download MiniMaxAI/MiniMax-H3 \
  --include "model_index.json" "FL2VA/*" "Ref2VA/*" \
  --local-dir MiniMax-H3

# 只下载 FL2VA 任务族
hf download MiniMaxAI/MiniMax-H3 \
  --include "model_index.json" "FL2VA/*" \
  --local-dir MiniMax-H3
```

Diffusers 用户不必手工下载全部文件：

```python
ModularPipeline.from_pretrained("MiniMaxAI/MiniMax-H3")
```

它会按需拉取组件。

官方推荐推理框架：

- [SGLang Cookbook](https://docs.sglang.io/cookbook/diffusion/MiniMax/MiniMax-H3)
- [vLLM Recipes](https://recipes.vllm.ai/MiniMaxAI/MiniMax-H3)
- [Diffusers MiniMax H3 文档](https://github.com/huggingface/diffusers/blob/minimax-h3/docs/source/en/api/pipelines/minimax_h3.md)
- [ComfyUI 教程](https://docs.comfy.org/tutorials/video/minimax/minimax-h3)
- [ComfyUI R2V 模板](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json)
- [ComfyUI T2V 模板](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_t2v.json)

## 22.9 官方 SGLang 启动命令

### FL2VA

```bash
sglang serve \
  --model-path MiniMaxAI/MiniMax-H3 \
  --num-gpus 4 \
  --ulysses-degree 4 \
  --performance-mode speed \
  --host 0.0.0.0 \
  --port 30010 \
  --model-variant fl2va
```

### Ref2VA

```bash
sglang serve \
  --model-path MiniMaxAI/MiniMax-H3 \
  --num-gpus 4 \
  --ulysses-degree 4 \
  --performance-mode speed \
  --host 0.0.0.0 \
  --port 30011 \
  --model-variant ref2va
```

## 22.10 可复现的 768p 官方案例

官方仓库提供三个请求脚本与结果：

| 用例 | 请求脚本 | 官方结果 |
|---|---|---|
| T2VA | [`reproducible-768p-t2va-request.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/reproducible-768p-t2va-request.sh) | [`t2va.mp4`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/assets/t2va.mp4) |
| FL2VA | [`reproducible-768p-fl2va-request.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/reproducible-768p-fl2va-request.sh) | [`fl2va.mp4`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/assets/fl2va.mp4) |
| Ref2VA | [`reproducible-768p-ref2va-request.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/reproducible-768p-ref2va-request.sh) | [`ref2va.mp4`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/assets/ref2va.mp4) |

## 22.11 完整 2K 工作流

先设置本地 SGLang 服务地址、API 区域和 Token：

```bash
SGLANG_DEPLOYMENT_URL="<sglang-deployment-url>"

# 中国区
MINIMAX_API_BASE="https://api.minimaxi.com"

# Global（二选一）
# MINIMAX_API_BASE="https://api.minimax.io"

TOKEN="<token>"
```

涉及三个官方 API：

1. 创建 H3-2K：`/video-generation-v2-create`
2. Context-IR：`/video-generation-v2-h3-context-ir`
3. Regenerate-2K：`/video-generation-v2-regeneration`

README 示例为了演示，会把本地 H3-Base 输出编码成 Base64 Data URL；官方建议生产环境将 base video 上传到可公开访问的 URL，再把 URL 作为 `base_video` 传入，避免巨大 Base64 请求。

### 官方 2K 请求脚本与结果文件

#### T2VA

| 阶段 | 请求脚本 | 结果 |
|---|---|---|
| H3-Context-IR | [`full-2k-t2va-h3-context-ir.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/full-2k-t2va-h3-context-ir.sh) | 返回结构化 Prompt JSON |
| H3-Base | [`full-2k-t2va-h3-base.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/full-2k-t2va-h3-base.sh) | [`t2va.mp4`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/assets/t2va.mp4) |
| H3-Regenerate-2K | [`full-2k-t2va-h3-regenerate-2k.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/full-2k-t2va-h3-regenerate-2k.sh) | [`t2va_2k.mp4`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/assets/t2va_2k.mp4) |
| 开放平台直接 2K | [`full-2k-t2va-reference-2k-result-by-directly-calling-open-platform-api.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/full-2k-t2va-reference-2k-result-by-directly-calling-open-platform-api.sh) | [`h3_direct_2k.mp4`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/assets/h3_direct_2k.mp4) |
| 开放平台直接 768p | [`full-2k-t2va-reference-768p-result-by-directly-calling-open-platform-api.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/full-2k-t2va-reference-768p-result-by-directly-calling-open-platform-api.sh) | [`h3_direct_768p.mp4`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/assets/h3_direct_768p.mp4) |

#### I2VA

| 阶段 | 请求脚本 | 结果 |
|---|---|---|
| H3-Context-IR | [`full-2k-i2va-h3-context-ir.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/full-2k-i2va-h3-context-ir.sh) | 返回结构化 Prompt JSON |
| H3-Base | [`full-2k-i2va-h3-base.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/full-2k-i2va-h3-base.sh) | [`i2va.mp4`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/assets/i2va.mp4) |
| H3-Regenerate-2K | [`full-2k-i2va-h3-regenerate-2k.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/full-2k-i2va-h3-regenerate-2k.sh) | [`i2va_2k.mp4`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/assets/i2va_2k.mp4) |
| 开放平台直接 2K | [`full-2k-i2va-reference-2k-result-by-directly-calling-open-platform-api.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/full-2k-i2va-reference-2k-result-by-directly-calling-open-platform-api.sh) | [`i2va_direct_2k.mp4`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/assets/i2va_direct_2k.mp4) |
| 开放平台直接 768p | [`full-2k-i2va-reference-768p-result-by-directly-calling-open-platform-api.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/full-2k-i2va-reference-768p-result-by-directly-calling-open-platform-api.sh) | [`i2va_direct_768p.mp4`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/assets/i2va_direct_768p.mp4) |

#### Ref2VA

| 阶段 | 请求脚本 | 结果 |
|---|---|---|
| H3-Context-IR | [`full-2k-ref2va-h3-context-ir.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/full-2k-ref2va-h3-context-ir.sh) | 返回结构化 Prompt JSON |
| H3-Base | [`full-2k-ref2va-h3-base.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/full-2k-ref2va-h3-base.sh) | [`r2va.mp4`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/assets/r2va.mp4) |
| 开放平台直接 2K 参考结果 | [`full-2k-ref2va-reference-2k-result-by-directly-calling-open-platform-api.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/full-2k-ref2va-reference-2k-result-by-directly-calling-open-platform-api.sh) | [`r2va_2k.mp4`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/assets/r2va_2k.mp4) |
| 开放平台 H3 API 2K | [`full-2k-ref2va-h3-api-2k-in-open-platform-for-reference.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/full-2k-ref2va-h3-api-2k-in-open-platform-for-reference.sh) | [`r2va_direct_2k.mp4`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/assets/r2va_direct_2k.mp4) |
| 开放平台直接 768p | [`full-2k-ref2va-reference-768p-result-by-directly-calling-open-platform-api.sh`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/scripts/readme/full-2k-ref2va-reference-768p-result-by-directly-calling-open-platform-api.sh) | [`r2va_direct_768p.mp4`](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/assets/r2va_direct_768p.mp4) |

### 2K 案例总表

| 用例 | 类型 | 时长 | 比例 | Context-IR 示例语义 | 示例 usage |
|---|---|---:|---|---|---|
| T2VA | 文生音视频 | 10 秒 | 16:9 | 星舰舰桥、女舰长、舰队跃迁；两镜头；环境机械声与太空歌剧配乐 | total 8565 / prompt 5650 / completion 2915 |
| I2VA | 首帧图生音视频 | 8 秒 | 自适应（示例返回 16:9） | 日式家庭餐桌，前景拉面；静态机位完成从拉面到家人的平滑 rack focus | total 22822 / prompt 12800 / completion 10022 |
| Ref2VA | 视频+音频全参考 | 5 秒 | 自适应（示例返回 16:9） | 粉色西装男子抱黑色小羊；保留原视频与 BGM，参考另一音频的男声音色生成新对白 | total 39299 / prompt 33323 / completion 5976 |

每个案例都包含 Context-IR 请求、本地 Base、Regenerate-2K，以及直接开放平台 2K/768p 参考结果；Ref2VA 还给出开放平台 H3 API 的 2K 参考结果。官方脚本目录：

- [T2VA 完整 2K 脚本](https://github.com/MiniMax-AI/MiniMax-H3/tree/main/scripts/readme)
- [I2VA 完整 2K 脚本](https://github.com/MiniMax-AI/MiniMax-H3/tree/main/scripts/readme)
- [Ref2VA 完整 2K 脚本](https://github.com/MiniMax-AI/MiniMax-H3/tree/main/scripts/readme)

### 三个 Context-IR 案例的关键信息

- **T2VA 星舰案例**：`Shot 1` 从舰桥中景缓慢推进，女舰长背对镜头观察暗灰舰队；推进器蓝光增强。`Shot 2` 在 `00:04.500` 切脸部特写并强烈震动，跃迁白光、舰体应力声、舰长踉跄与最后闭眼形成完整状态变化。
- **I2VA 拉面案例**：固定机位 8 秒，不靠移动摄影，而是用焦点转移制造叙事。开始拉面、叉烧、葱、海苔、筷子、茶杯清晰，七人家庭虚化；随后焦点平滑转到家人，蒸汽持续作为前景动态层。
- **Ref2VA 羊群案例**：使用 `subject_definitions → summary → retention_analysis → detailed_description → overall_soundscape → non_diegetic_music`。人物、原视频、同步 BGM、声音音色分别定义；对白结束时明确嘴唇闭合，并继续抚摸小羊。

## 22.12 官方许可证与联系方式

官方 README 的“提示词指导”说明：为了保持 GitHub README 的 Markdown 布局简洁，Hugging Face 发布中的完整提示词指南没有重复嵌入 README；本手册第 24、25 章已经把对应 Base 与 Ref Guide 纳入同一份中文文档。

- 许可证：[MiniMax H3 Community License Agreement](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)
- 联系邮箱：[model@minimax.io](mailto:model@minimax.io)

---

## 23. 官方 `h3-prompt-writing` Skill 完整中文覆盖

官方 Skill 本身是一个路由与约束层，完整工作流如下：

1. 判断输入模式：T2VA、I2VA、FL2VA、L2VA 或 Ref2VA。
2. Base 文本/关键帧模式必须读取 `references/base-en.txt`，遵循其最终 Prompt 结构。
3. 全参考模式必须读取 `references/ref-en.txt`，遵循六段式。
4. 所选 Guide 中的字段名、章节顺序、标签和时间标记必须保持原样。

### 23.1 Base 模式职责

- T2VA：仅从文本构建完整视听时间线。
- I2VA：从首帧出发，向后连续发展。
- FL2VA：写清首帧与尾帧之间的连续可见路径。
- L2VA：推断合理的前置状态，并收敛到给定尾帧。

三个字段顺序固定：

```text
integrated_multimodal_description
→ overall_soundscape
→ non_diegetic_music
```

### 23.2 Ref2VA 职责

六个字段顺序固定：

```text
subject_definitions
→ summary
→ retention_analysis
→ detailed_description
→ overall_soundscape
→ non_diegetic_music
```

所有 Reference Label 必须跨六段保持一致。

### 23.3 官方输出规则

- Rewrite section 使用英文；只在 `<d>` 中的对白/歌词以及画面内可见文字保留原语言。
- 每个 shot 应描述构图、主体、环境、动作、相机、声音，以及参考内容实际出现或生效的准确位置。
- 避免只写剧情摘要。
- 避免未解析或前后不一致的 Reference Label。
- 时间必须与用户要求的 4–15 秒匹配。

### 23.4 官方效果建议

- 描述总时长必须与目标时长一致。
- `<Picture 1>`、`<Video 1>`、`<Audio 1>` 等标签必须在所有段落中保持一致。
- 比起抽象词 `cinematic`、`beautiful`，优先写具体可视、可听事实。
- I2VA / FL2VA / L2VA 必须明确首帧和/或尾帧如何连接到时间线。

---

## 24. 官方 Base Prompt Guide 完整中文覆盖

## 24.1 四种任务

| 模式 | 官方任务定义 |
|---|---|
| T2VA | 从文本构建完整音视频时间线 |
| I2VA | T2VA 主体 + 首帧固定指令 + 从首帧向前发展的视觉路径 |
| FL2VA | T2VA 主体 + 首尾帧固定指令 + 从首帧连续过渡到尾帧的路径 |
| L2VA | T2VA 主体 + 尾帧固定指令 + 从合理前态收敛到尾帧的路径 |

## 24.2 最终 Prompt 结构

### T2VA

不写图像对齐指令，直接以三个核心字段开头。

### I2VA 固定首行

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
```

### FL2VA 固定首行

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.
```

### L2VA 固定首行

```text
How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.
```

其中：

- `N` 是实际最后一个 shot 的编号。
- `S.SS` 是有效视频时长，严格保留两位小数。
- 指令必须位于最终 Prompt 第一行。
- 固定指令后空一行，再写核心字段。

### 三个核心字段

```text
integrated_multimodal_description: [Shot 1] ...

overall_soundscape: ...

non_diegetic_music: ...
```

- `integrated_multimodal_description`：按时间写视觉、动作、镜头、说话人、对白、歌唱和画内音频。
- `overall_soundscape`：总结环境、物理动作和非语言人声。
- `non_diegetic_music`：描述角色听不到、只有观众听到的配乐。

## 24.3 关键帧融入方式

### I2VA

`<Picture 1>` 是目标视频 0.00 秒真实首帧，属于 `[Shot 1]`。先建立图中的风格、主体、构图、场景锚点，再向后描述动作。人物身份、服装、颜色、关键物体、空间关系应保持一致。

```text
首帧锚点 → 动作启动 → 连续发展 → 结果或反应
```

### FL2VA

Picture 1 是开头，Picture 2 是结尾。重点写：主体怎么移动、姿势怎么变化、物体如何被操作、构图如何演化、场景或光线如何过渡。

官方通常更偏好单镜头插值；只有用户明确要求时才使用多镜头。结尾必须在视频末尾由最后 `[Shot N]` 到达。

```text
首帧状态 → 可观察的中间变化 → 差异逐渐缩小 → 尾帧状态
```

### L2VA

`<Picture 1>` 是目标视频最后一帧，属于最后 `[Shot N]`，并不天然属于 Shot 1。根据用户意图与尾帧推断前态，再让人物、物体、相机和场景逐步接近参考图。

```text
合理前态 → 明确动作/过渡路径 → 最后 Shot 中逐渐收敛 → 准确落到尾帧
```

## 24.4 主描述必须沿时间线展开

每个细节都应对应可见或可听事实：

- 视觉风格。
- 起始构图。
- 主体外观与位置。
- 场景和关键道具。
- 动作与反应。
- 镜头变化。
- 语言与对白。
- 同步画内声。

`[Shot 1]` 开始处应说明整体风格和初始构图。官方列举的风格包括：`Cinematic`、`live-action`、`2D-animated`、`3D CG`、`claymation`、`watercolor`、`vintage film`。关键帧任务从参考图推断风格；T2VA 从用户文本选择。

```text
[Shot 1] Live-action, cinematic, a medium-wide shot frames...
```

## 24.5 Shot 与 Cut

- Shot 1 不加时间戳。
- 后续 shot 编号连续。
- 每个后续 shot 必须用严格递增且位于视频时长内的切点开始。

```text
[Shot 2] At 00:03.500, the camera cuts to...
```

普通切镜可以使用：

- `the camera cuts to`
- `the shot cuts to`
- `the shot transitions to`
- `the shot changes to`
- `the shot switches to`

只有用户明确要求时才使用 cross-dissolve、fade 或 wipe。切镜应带来主体、空间、状态、视角或时间的新信息；如果只是轻微角度或景别变化，优先使用相机运动而不是切镜。

## 24.6 运镜词表：类型 + 幅度 + 速度

| 维度 | 官方表达 | 含义 |
|---|---|---|
| 类型 | `Zoom In / Zoom Out` | 机位不动，改变焦距 |
| 类型 | `Push In / Pull Out` | 相机前移 / 后移 |
| 类型 | `Pan Left / Pan Right` | 机位不动，镜头水平转动 |
| 类型 | `Truck Left / Truck Right` | 相机横向平移 |
| 类型 | `Tilt Up / Tilt Down` | 机位不动，镜头垂直转动 |
| 类型 | `Pedestal Up / Pedestal Down` | 整台相机上移 / 下移 |
| 类型 | `Arc Shot` | 围绕主体做弧线运动 |
| 类型 | `Tracking Shot` | 跟随移动主体 |
| 类型 | `Static Shot` | 机位与镜头保持静止 |
| 类型 | `Shake Slightly / Shake Strongly` | 轻微 / 强烈震动 |
| 类型 | `POV` | 主体主观视角 |
| 类型 | `Roll Clockwise / Roll Counterclockwise` | 围绕镜头轴顺 / 逆时针滚转 |
| 幅度 | `with small amplitude` | 小范围构图变化 |
| 幅度 | `with large amplitude` | 大范围构图变化 |
| 速度 | `at slow speed` | 慢速 |
| 速度 | `at fast speed` | 快速 |

中等幅度和正常速度通常省略。运镜要写成 shot 内自然英文动作，不要在句尾堆标签：

```text
The camera pushes in with small amplitude at slow speed toward the folded letter in her hands.
The camera pans right with large amplitude at fast speed, revealing the open doorway.
The camera holds a static shot as the runner exits the frame.
```

## 24.7 说话人、对白与歌唱

- 发声的人物、歌者或画外人声使用稳定 `(S1)`、`(S2)`。
- 多名已编号说话人同时发声使用 `(S1,S2)`。
- 同一发声者跨 shot 保持相同 ID。
- 从不发声的人不分配 speaker ID。
- 首次出现要用人物类型、年龄、性别、是否在画面、音高、音色、语速或口音等信息建立身份。
- 说话人身份、ID、动作、语气写在 `<d>` 外。
- `<d>` 内只放语言标签和用户原始台词。
- 用户原词与标点必须逐字保留，不翻译、不改写。

```text
The young woman with a quiet, breathy voice (S1) says: <d>[English] I get off at the next station.</d>
The two children (S1,S2) shout together, <d>[English] Wait for us!</d>
```

### 画外旁白固定写法

必须使用短语 `says in an off-screen voiceover`。每个旁白 `<d>` 后立刻说明对应画面人物嘴唇完全闭合：

```text
The man (S1) says in an off-screen voiceover: <d>[English] I still remember that road.</d> while his lips remain completely closed.
```

### 跨切镜对白

同一句对白或歌词跨 cut 时：

1. 两部分连接点都用 `<scenetrans>`。
2. 明确音频跨切镜连续。
3. 可用 `continues seamlessly across the cut`、`continues uninterrupted into the next shot`、`carries over from the previous shot`、`remains audible across the transition`。
4. 视频结束前台词被截断时用 `<cutoff>`。

## 24.8 画面文字

Banner、sign、label、subtitle、neon text 等实际可见文字必须放入英文双引号，原文和标点逐字保留，不翻译：

```text
A red neon sign reading "营业中" glows above the doorway.
```

## 24.9 `overall_soundscape`

- 1–4 个英文句子。
- 单段连续文字。
- 总结全片环境声、物理动作声和非语言人声，例如风雨、交通、脚步、衣物、碰撞、呼吸、笑声、喘息。
- 对白、歌唱、画内音乐已经属于主描述，不在这里重复。
- 只有用户明确要求全片完全静音时才写 `N/A`。

```text
overall_soundscape: Steady rain taps against the café windows while low room ambience continues underneath. The entrance bell rings once, followed by wet footsteps and the soft scrape of a chair.
```

## 24.10 `non_diegetic_music`

- 1–3 个英文句子。
- 只写角色听不到、观众听到的画外配乐。
- 聚焦乐器、速度、节奏与动态变化。
- 不用抽象 mood words，也不解释配乐的情绪功能。
- 角色能听到的歌唱、演奏、收音机、电视或手机音乐属于 diegetic event，应写进主描述。
- 没有画外配乐时写 `N/A`。

```text
non_diegetic_music: Sparse piano notes at a slow tempo, joined by sustained low strings that gradually increase in volume before fading out.
```

## 24.11 官方四个完整案例

以下保留官方 Prompt 的英文可执行形式。

### Case 1：T2VA 面包店

```text
integrated_multimodal_description: [Shot 1] Live-action, cinematic, a medium-wide shot frames a baker opening the shutters of a small street bakery before sunrise. The camera pushes in with small amplitude at slow speed as the middle-aged baker with a calm, slightly raspy voice (S1) places a fresh loaf on the wooden counter and says: <d>[English] First batch of the morning.</d> [Shot 2] At 00:05.000, the camera cuts to a close-up of steam rising from the sliced bread while the baker's final words carry over from the previous shot.

overall_soundscape: Wooden shutters scrape open over a quiet street as trays clink softly inside the bakery. The doorbell rings once, followed by light footsteps and the crisp sound of bread being sliced.

non_diegetic_music: A soft acoustic-guitar pattern at a moderate tempo, joined by sparse upright-bass notes and a gentle fade at the end.
```

### Case 2：I2VA 雨夜列车

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Live-action, cinematic, the young woman shown in <Picture 1> remains beside the rain-covered train window, preserving her appearance, clothing, seat position, and the carriage layout. The camera trucks right with small amplitude at slow speed as she lifts her gaze from the folded letter toward the passing city lights. Her reflection moves across the glass while the quiet, breathy young woman (S1) says: <d>[English] I get off at the next station.</d> She folds the letter along its existing crease.

overall_soundscape: The train wheels produce a steady metallic rhythm beneath a low ventilation hum. Rain ticks against the window while paper rustles softly in her hands.

non_diegetic_music: Sustained cello notes at a slow tempo with widely spaced piano tones, gradually decreasing in volume.
```

### Case 3：FL2VA 雨中自行车与雨伞

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 8.00-second mark of the target video.

integrated_multimodal_description: [Shot 1] Live-action, cinematic, a rain-soaked cyclist begins in the position and framing established by Picture 1, holding a closed black umbrella beside a silver bicycle. The camera pulls out with small amplitude at slow speed as she releases the bicycle handle, raises the umbrella above her shoulder, and presses the runner upward until the canopy opens. Water rolls from the expanding fabric while she steps beneath it, rotates the handle into the final angle, and settles into the pose, spacing, and composition established by Picture 2 at the end of the shot.

overall_soundscape: Rain falls steadily on the pavement, followed by the metallic click of the umbrella runner and the soft snap of the canopy opening. Water drips from the bicycle frame as distant traffic passes.

non_diegetic_music: N/A
```

### Case 4：L2VA 玻璃杯破碎并落到尾帧

```text
How the reference pictures align with the target video — <Picture 1> (from [Shot 1]) aligns with the 6.00-second mark of the target video.

integrated_multimodal_description: [Shot 1] Live-action, cinematic, a close shot begins with an intact drinking glass near the edge of a dark wooden table, while the same hand and sleeve visible in <Picture 1> approach from the right. The camera pushes in with small amplitude at slow speed as the fingertips strike the rim. The glass tips, falls, and hits the floor with a sharp impact; cracks spread through it as fragments slide outward. Toward the end, the moving pieces lose momentum and settle into the exact broken arrangement, hand position, camera angle, lighting, and final composition established by <Picture 1>.

overall_soundscape: Fingertips tap the glass before it scrapes across the tabletop, falls, and breaks with a sharp crash. Small fragments scatter and gradually stop sliding across the floor.

non_diegetic_music: A low electronic pulse at a slow tempo, ending immediately after the glass breaks.
```

---

## 25. 官方 Ref2VA Guide 完整中文覆盖

## 25.1 总则

- 六个 rewrite section 全部使用英文。
- 只有 `<d>` 内的对白、歌词以及场景中真实可见文字保留原语言。
- `detailed_description` 要尽可能具体；每个 shot 明确当前构图、主体外观与位置、环境与光线、动作与状态变化、相机运动、当前声音，以及参考内容真正出现或生效的时点。
- 不要把主描述压缩成剧情梗概或参考关系列表。
- Shot、运镜、speaker、dialogue 与 ordinary sound 的基础格式沿用 Base Guide；Ref Guide 重点规定引用标签、分析段与全参考差异。

## 25.2 六段式及固定顺序

| 顺序 | 字段 | 作用 |
|---:|---|---|
| 1 | `subject_definitions` | 定义参考内容及标签 |
| 2 | `summary` | 概述任务类型、目标视频和主要参考关系 |
| 3 | `retention_analysis` | 说明参考内容如何被保留、迁移或复用 |
| 4 | `detailed_description` | 按播放顺序写视觉、动作、镜头、声音和对白 |
| 5 | `overall_soundscape` | 总结环境与物理声音 |
| 6 | `non_diegetic_music` | 描述只有观众听到的配乐 |

## 25.3 四类 Reference Label

| 标签 | 官方含义 |
|---|---|
| `<Subject N>` | 从参考素材抽象出的、可在目标视频复用或修改的可见内容 |
| `<Picture N>` | 作为具体目标帧或镜头规划锚点的参考图 |
| `<Video N>` | 提供直接编辑源、续写起点或全视频时间结构的参考视频 |
| `<Audio N>` | 被复制或被参考的音频信号 |

标签一旦分配，跨六段必须保持相同含义。

`subject_definitions` 中每个需要单独追踪的参考内容各写一行，说明：标签指代什么、承担什么参考职责、哪些主要特征必须遵循，以及必要时的来源素材。如果某个 Picture/Video 只用来定义另一个 Subject，后续不会单独分析或使用，就只在 Subject 定义中引用来源，不单列 Picture/Video。

### 25.3.1 `<Subject N>`

可用于：

- 人、动物、物体。
- 场景、背景、环境。
- 服装、道具、界面、视觉特效。
- 风格、动作、表情、姿势。

它表示目标视频实际使用的“内容单元”，而不是文件本身。一个 Subject 可由多个素材共同定义，一个素材也可提供多个 Subject。

```text
<Subject 1> is the young woman in <Picture 1>, with long dark hair, a blue cardigan, and a thin silver necklace.
```

多源定义时要写清每个来源提供什么：

```text
<Subject 1> is the woman whose appearance comes from <Picture 1> and whose walking motion comes from <Video 1>.
```

### 25.3.2 `<Picture N>`

只有当图片本身承担以下职责时才单列：

- 首帧。
- 关键帧。
- 尾帧。
- 被编辑的关键帧。
- 构图锚点。

```text
<Picture 2> is the first frame of [Shot 1], showing a woman seated beside a café window.
```

若图片只定义角色、场景、服装或风格，不单列 Picture，而是在 Subject 中注明来源。

若图片充当 storyboard / shot-planning reference，要写明映射哪些 shot，以及提供了视角、主体位置、镜头顺序中的哪些信息：

```text
<Picture 3> is a storyboard reference for [Shot 1] and [Shot 2], defining their viewpoint, subject placement, and shot order.
```

### 25.3.3 `<Video N>`

只保留给整段视频关系：

- 直接编辑原视频。
- 从原视频末尾续写。
- 参考原视频的运镜、切镜、节奏或时间结构。

```text
<Video 1> is the source video for the target video edit.
```

从视频中复用的人、物、场景、动作或效果仍应定义为 Subject。Video 只表示素材/结构来源，不能代替 Subject。

### 25.3.4 `<Audio N>`

表示独立音频或从参考视频中启用的同步音轨，常见职责：

- 完整或部分复制音频信号。
- 参考 BGM 风格。
- 参考说话人音色与表达。
- 使用原音频对白、歌词或音效。
- 参考节拍、韵律或音频连续性。

若 Audio 明确对应目标 speaker，沿用目标视频的全局 speaker ID：对应已定义主体时写 `<Subject N> (Sx)`；否则写稳定声音描述再接 `(Sx)`。Audio 定义不独立分配新编号。

```text
<Audio 1> is the voice-timbre reference for <Subject 1> (S1).
```

一个音频承担多个职责时，在同一句自然语言里写清，不创建额外子段。

### 25.3.5 同一参考视频的视觉轨与音轨

- `<Video N>` 与 `<Audio N>` 独立编号。
- 索引只代表各自类别中的出现顺序，不编码配对。
- 因而同一个源文件完全可以是 `<Video 1>` 与 `<Audio 2>`。
- 普通参考视频即使文件带声音，也不会自动产生 `<Audio N>`；只有启用其音轨作为参考或复用时才定义 Audio。
- Audio 定义主要说明音频职责，不必总写来自哪个 Video；只有存在来源歧义时才说明。

```text
<Video 1> is the source video for the target video edit.
<Audio 2> is the synchronized audio track of <Video 1> and is reused in the target video.
```

## 25.4 `summary`

使用一个简短英文段落，并以方括号任务类型开头：

```text
[reference generation] ...
[video editing + reference generation + audio reuse] ...
```

### 六种任务类型

| 类型 | 使用条件 |
|---|---|
| `keyframe completion` | 图片是目标视频首帧、关键帧、尾帧、被编辑帧或其他具体帧锚点 |
| `reference generation` | 图片/视频/音频只提供角色、场景、风格、动作、运镜、storyboard 等生成指导，不是具体帧，也不是被编辑/续写源视频 |
| `video editing` | 直接修改已有源视频；编辑图片或静态关键帧之间生成不属于此类 |
| `video continuation` | 从现有源视频继续、扩展、恢复或过渡 |
| `audio reuse` | 完整或部分复用同一音频信号 |
| `audio reference` | 不直接复制信号，只参考音乐风格、音色、对白/歌词内容、音效质感、节拍或连续性 |

多种关系用 ` + ` 合并，不能重复：

```text
[video continuation + keyframe completion]
[video editing + audio reuse]
```

重要边界：

- 有视频/音频输入不等于自动产生对应 task type。
- 视频若只提供运镜、切镜或节奏，一般属于 `reference generation`。
- 只有直接修改或续写源视频，才用 `video editing` / `video continuation`。
- 编辑源视频且原声仍可听见时，同时写 `audio reuse`。
- 续写视频但不直接复制音频信号，仅延续其听觉特征时，用 `audio reference`。
- Summary 只能使用前面已经定义的标签，不得引入新标签。
- 视频编辑任务在前缀后固定以这句开头：

```text
The target video is an edited version of <Video 1>.
```

## 25.5 `retention_analysis`

每个 reference label 一行，说明它在目标视频中如何被保留、迁移、复制或参考。不得改变 `subject_definitions` 中已经确立的职责。

### 可见内容的固定关系值

| Marker | 含义 |
|---|---|
| `fully_preserved` | 所定义职责全部保留 |
| `partially_preserved` | 内容仍被使用，但部分特征改变或只保留一部分 |
| `attribute_transfer` | 把参考特征迁移到另一个可识别目标主体 |
| `weak_reference` | 只保留大类风格、类别、构图或氛围相似性 |

```text
<Subject 1> (appears in [Shot 1], [Shot 3]): fully_preserved - ...
<Picture 2> ([Shot 1] first frame): fully_preserved - ...
<Video 1> (cut and pacing structure): weak_reference - ...
```

### 音频的固定关系值

| Marker | 含义 |
|---|---|
| `fully_copy` | 完整源音频成为目标视频完整最终音轨 |
| `partially_copy` | 只复制部分时间/层，或复制后增删替换其他声音 |
| `reference` | 不复制信号，只参考音色、节奏、音乐风格、对白内容或声音质感 |
| `weak_reference` | 只保留宽泛类别或氛围相似性 |

```text
<Audio 1>: fully_copy - <Audio 1> is reused 1:1 as the target video's complete final audio track.
<Audio 2>: reference - the target speaker follows <Audio 2>'s voice timbre and measured delivery without copying the original signal.
```

Marker 只能在该标签已定义的职责内选择。目标视频新增动作、背景或剧情，并不自动意味着参考保真损失。

## 25.6 `detailed_description`

### 基础格式

- 正文英文，对白/歌词/可见文字保留原语言。
- `[Shot 1]` 无时间戳。
- 后续格式为 `[Shot N] At MM:SS.mmm, ...`。
- 相机运动写成自然英文；需要时包含类型、幅度、速度。
- 发声源使用稳定 `(S1)`、`(S2)`。
- 对白/歌词使用 `<d>[Language] ...</d>`。
- 跨 cut、结尾截断、连续音频使用 `<scenetrans>`、`<cutoff>` 及明确连续性描述。

### 与 T2VA 的差异

| 维度 | T2VA | Ref2VA |
|---|---|---|
| 主字段 | `integrated_multimodal_description` | `detailed_description` |
| 风格开头 | 写在 `[Shot 1]` 后 | 在 `[Shot 1]` 前用 1–2 句英文建立 |
| Reference Label | 不使用全参考标签 | 在首次出现及职责生效处插入 Subject/Picture/Video/Audio |
| 音频关系 | 写目标视频自身声音 | 在对应 shot 或音频阶段说明 Audio 被复制还是参考 |

```text
The target video is in a cinematic, literary music-video style with soft lighting and a slightly desaturated color palette.
[Shot 1] The scene opens in a crowded urban street...
[Shot 2] At 00:09.000, the shot cuts to an extreme close-up...
```

全参考生成任务的 `detailed_description` 通常为 **350–500 个英文单词**。对白密集任务优先保证完整口播时间线，不机械追字数；视频编辑描述按源视频复杂度伸缩。单镜头不等于描述可以很短，应按信息负载分配细节。

## 25.7 在 Shot 中使用 Reference Label

重要 Subject 第一次清晰出现时，要结合实际可见内容写：参考特征、画面位置和当前动作。后续继续使用同一标签，不重新定义。

具体关键帧锚点使用自然固定短语：

```text
the shot begins from <Picture 1>
the shot's keyframe corresponds to <Picture 2>
the shot ends on <Picture 3>
```

编辑或续写原视频时，在源状态、结构或续写关系真正生效处自然引用 `<Video N>`。Audio 在对应 shot 或语义阶段真正起作用时引用。

## 25.8 Speaker、Audio Source 与 Dialogue

参考主体物理发声时，必须同时保留 Subject 和 speaker ID：

```text
<Subject 2> (S1) turns toward the woman and says, <d>[English] Last summer, I went to my grandfather's house. He talked about you.</d>
```

- `<Subject N>` 识别参考主体。
- `(Sx)` 识别实际说话人。
- 同一主体画外发声仍保持相同形式，并标记 `off-screen`。
- 没有对应 Subject 的 speaker 使用稳定声音描述 + `(Sx)`。

### BGM 内歌词不一定是新 Speaker

若语言内容只是直接复用 BGM 或完整 soundtrack 中的 cue，并没有独立人物/旁白真正发声，则用 `<Audio N>` 作为声音来源，不虚构 `(Sx)`：

```text
When <Audio 1> reaches the phrase <d>[English] I'm lonely lonely lonely lonely lonely I'm lonely</d>, <Subject 1> performs the corresponding hand gesture without becoming a separate speaker source.
```

若由具体人物、角色、旁白或其他独立声音源产生，则必须分配并复用 `(Sx)`。

### 复用参考音频中的对白、旁白或歌词

- 直接复用，或用户明确要求重新表演时，保留源音频原词和原语言。
- 听不清处写 `[unclear]`，不得猜测。
- 标点标准化为表达句意所需的 `, . ? !`。
- 删除重复波浪线、emoji、项目符号和装饰性重复标点。
- 完整陈述句、疑问句、感叹句在 `</d>` 前分别以 `. ? !` 结束。
- 若只参考音色、节奏、情绪或 delivery，不要把参考音频原台词带入目标视频。

### Speaker ID 分配规则

- 按目标视频中“实际首次发声事件”的先后，只分配一次。
- `detailed_description` 中每次真实发声都复用同一 ID。
- `subject_definitions` 中绑定目标 speaker 的 Audio 复用同一 ID，但不能独立创造新 ID。
- `retention_analysis` 不写 `(Sx)`。
- 仅存在于复用 BGM/完整 soundtrack 中的语言 cue 使用 `<Audio N>`；由具体独立声音源产生的声音使用 `(Sx)`。

## 25.9 Ref2VA 的两个声音段

`overall_soundscape` 与 `non_diegetic_music` 定义仍与 Base Guide 相同。

- 环境与物理声音写 `overall_soundscape`。
- 对白、歌唱和与具体 shot 同步的声音事件留在 `detailed_description`。
- 观众可听、角色不可听的配乐写 `non_diegetic_music`。
- 引用 Audio 时，只在与听觉层匹配的 section 说明 copy/reference 关系。
- 同一 Audio 同时提供环境/音效和画外配乐时，在两个对应 section 分别说明。
- 完整对白与歌词只写在 `detailed_description` 的 `<d>` 中，不在两个声音段重复。

```text
overall_soundscape: The copied ambience layer from <Audio 1> continues throughout the target video.
non_diegetic_music: <Audio 2> is directly reused as the complete audience-only score.
```

## 25.10 官方完整 Ref2VA 案例

该案例包含：咖啡店环境、白色萨摩耶、金发女子、灰色连帽衫男子，以及女子音色参考。以下保留官方六段式英文结构。

```text
subject_definitions:
<Subject 1> is the coffee-shop environment in <Picture 1>, featuring an exposed brick wall, an orange tufted sofa with patterned pillows, a neon sign, and a wooden coffee table.
<Subject 2> is the fluffy white Samoyed in <Picture 2>, <Picture 3>, and <Picture 4>, with thick white fur, pointed ears, a dark nose, and a curved tail.
<Subject 3> is the young blonde woman in <Video 1>, with long blonde hair and a light-pink button-down shirt with rolled-up sleeves.
<Subject 4> is the young man in <Video 2>, with short wavy brown hair and a dark-grey hoodie with drawstrings.
<Audio 1> is the voice-timbre reference for <Subject 3> (S1), containing a spoken English vocal layer.

summary:
[reference generation + audio reference] The target video shows <Subject 3> eating a cookie in <Subject 1>. <Subject 4> enters with <Subject 2>, which lunges toward the cookie. The three-shot exchange uses <Audio 1> as the voice-timbre reference for <Subject 3> and ends with a canned audience laugh.

retention_analysis:
<Subject 1> (appears in [Shot 1], [Shot 2], [Shot 3]): fully_preserved - the exposed brick wall, orange tufted sofa, patterned pillows, neon sign, and wooden coffee table are retained.
<Subject 2> (appears in [Shot 1], [Shot 2]): fully_preserved - the Samoyed's thick white fur, pointed ears, dark nose, and curved tail are retained.
<Subject 3> (appears in [Shot 1], [Shot 2], [Shot 3]): fully_preserved - the blonde woman's identity, long hair, and light-pink shirt are retained.
<Subject 4> (appears in [Shot 1], [Shot 2]): fully_preserved - the young man's short wavy brown hair and dark-grey hoodie are retained.
<Audio 1>: reference - its vocal timbre guides the dialogue delivery of <Subject 3> without copying the original signal.

detailed_description:
The target video uses a realistic multi-camera sitcom style with warm indoor lighting.
[Shot 1] A medium shot establishes <Subject 1>, the coffee shop with its exposed brick wall, orange tufted sofa, patterned pillows, neon sign, and wooden coffee table. <Subject 3> (S1), the young woman with long blonde hair and a light-pink button-down shirt with rolled-up sleeves, sits on the sofa holding a chocolate-chip cookie. From the left, <Subject 4>, the young man with short wavy brown hair and a dark-grey hoodie with drawstrings, enters holding the leash of <Subject 2>, the thick-furred white Samoyed with pointed ears, a dark nose, and a curved tail. The dog lunges toward the cookie and pulls the leash taut. <Subject 3> (S1) jerks her hand back and, using the clear youthful voice timbre referenced from <Audio 1>, exclaims with light annoyance, <d>[English] Hey! Watch your dog!</d> She closes her lips and guards the cookie while <Subject 4> pulls the dog back.
[Shot 2] At 00:03.000, the shot cuts to a close-up of <Subject 4> (S2), the young man in the dark-grey hoodie from Shot 1, sitting beside <Subject 3> on the sofa and holding <Subject 2> securely in his arms. <Subject 4> (S2) says in a casual young male voice with a playful tone and an easy conversational pace, <d>[English] He just likes cookies more than me.</d> He closes his mouth into an apologetic smile and strokes the dog's thick white fur.
[Shot 3] At 00:05.000, the shot cuts to a close-up of <Subject 3> (S1), the blonde woman in the light-pink shirt from Shot 1. Her annoyance softens as she looks toward the Samoyed. <Subject 3> (S1) replies in the same clear youthful voice referenced from <Audio 1> with an amused cadence, <d>[English] Well, he has good taste at least.</d> She smiles and raises the cookie in a small toast-like gesture. A classic canned audience laugh begins immediately after the line and continues through the final frame.

overall_soundscape:
Soft indoor coffee-shop room tone continues throughout the scene.

non_diegetic_music:
N/A
```

---

## 26. 官方参考资料与版本快照

- MiniMax H3 官方仓库：<https://github.com/MiniMax-AI/MiniMax-H3>
- 官方中文 README：<https://github.com/MiniMax-AI/MiniMax-H3/blob/main/README.zh-CN.md>
- 官方 Base Prompt Guide：<https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md>
- 官方 H3 Prompt Writing Skill：<https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md>
- 官方 Base Guide 源文件：<https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/base-en.txt>
- 官方 Ref2VA Guide：<https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/ref-en.txt>
- 官方 Skills 目录：<https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills>
- Hugging Face 模型页：<https://huggingface.co/MiniMaxAI/MiniMax-H3>
- ModelScope MiniMax 组织页：<https://modelscope.cn/organization/minimax>

### 26.1 维护规则

1. 本文官方覆盖快照日期为 `2026-08-31`。
2. 官方字段、标签、模式、模型输入限制、API 或部署方式更新时，以最新官方仓库与模型页为准。
3. 更新时先比较 README、`SKILL.md`、`base-en.txt`、`ref-en.txt` 四份文件，再同步修订第 21–26 章。
4. 固定语法变更必须同时更新第 1–20 章中的生产模板，避免“官方附录”和“工程模板”不一致。
