# Stage 5：H3 视频生成（原生音画）

> **提示词编写规范（按需加载）**：编写 H3 提示词前，先打开本技能内置路由索引 [`references/h3/00-index.md`](./h3/00-index.md)，按任务加载对应分章（普通 I2VA 读 `10-structure.md` + `20-dialogue.md`，多参考读 `30-ref2va.md`，排查返工读 `50-qa.md`，官方边界查 `90-official.md`），再结合本页画布 MCP 参数与实测结论执行。

## 提交模式与首帧挂载校验

用 `canvas_generate_video`，首帧挂载两件事同时做：

1. `referenceNodeIds: [<首帧图片节点ID>, <提示词文本节点ID>]`（**图片在前**）；
2. `prompt` 传 composerContent 的 token 串（`@[node:<图片ID>]\n@[node:<文本ID>]`）。

**可执行三步首帧挂载校验**（任一不满足即判定“未挂上”，撤销重提）：

1. 提交参数中 `prompt` 字段以 `@[node:<首帧图片节点ID>]` 开头，与 `referenceNodeIds[0]` 一致；
2. 调一次 `canvas_get_state`，确认新建 video 节点的 `metadata.references` 非空且包含首帧图片节点的 `image:<storageKey>`；
3. 调 `generation_get_status`（或核查节点 `metadata.prompt`），确认任务提示词中出现 `图片1` 字样（只提文本会被上游当纯 T2V）。

## 参数基准

```
model: <渠道>::minimax-h3（从 workbench_video_get_config 实时读取）
seconds: 4–14（可安全提交的入参范围；官方硬上限 15s 见 config.limits.hard_limit_seconds，但传 15 会溢出，见下方帧网格表）
vquality: "720"（config.limits.vquality 默认值，上限 768P）
mode: "frames"（首尾帧模式）或 "reference"（全能参考模式）
preset: "default"（常规）/ "action"（武打）/ "final"（精修）
generateAudio: true, watermark: false
```

- **时长上限说明**：官方 H3 手册（`references/h3/90-official.md`）明确单次输出硬上限为 **4–15 秒**。尽管部分渠道/工作台 UI 开放到 `4–30s`，但 `15–30s` 属渠道扩展且未经官方承诺，**默认禁用**（除非用户显式要求并先单镜实测）。
- **并发控制**：默认并发上限 `config.limits.video_concurrency = 3`，第 4 条可能直接报「请求失败」；分批提交（3+3+3…），上一批收片并更新 `state.json` 再提下一批。

## 17k+5 帧网格换算表（24 FPS）

H3 输出帧数遵循 `frames = 17k + 5`（24 FPS）；整数入参秒数按 `ceil(24t)` 换算后向上落至最近的 `17k + 5` 网格。以下列出 4–15s 范围内的全部网格与入参映射（标 ✅ 为实测画布 `durationMs` 精确命中的档位，11–14 为按实测规则推算值）：

| k | frames | 实际秒数 | 整数 `seconds` 入参 | 状态 |
|---|---|---|---|---|
| 6 | 107 | **4.458s** | `4`（96 帧）→ 4458ms | ✅ 已实测 |
| 7 | 124 | **5.167s** | `5`（120 帧）→ 5167ms | ✅ 已实测 |
| 8 | 141 | 5.875s | —（入参 `6` 落至 k=9） | 整数秒不可达 |
| 9 | 158 | **6.583s** | `6`（144 帧）→ 6583ms | ✅ 已实测 |
| 10 | 175 | **7.292s** | `7`（168 帧）→ 7292ms | ✅ 已实测 |
| 11 | 192 | **8.000s** | `8`（192 帧）→ 8000ms | ✅ 已实测 |
| 12 | 209 | 8.708s | —（入参 `9` 落至 k=13） | 整数秒不可达 |
| 13 | 226 | **9.417s** | `9`（216 帧）→ 9417ms | ✅ 已实测 |
| 14 | 243 | **10.125s** | `10`（240 帧）→ 10125ms | ✅ 已实测 |
| 15 | 260 | 10.833s | —（入参 `11` 落至 k=16） | 整数秒不可达（推算） |
| 16 | 277 | **11.542s** | `11`（264 帧） | 推算（首跑需核对 `durationMs`） |
| 17 | 294 | **12.250s** | `12`（288 帧） | 推算 |
| 18 | 311 | 12.958s | —（入参 `13` 落至 k=19） | 整数秒不可达（推算） |
| 19 | 328 | **13.667s** | `13`（312 帧） | 推算 |
| 20 | 345 | **14.375s** | `14`（336 帧） | 推算（官方 ≤15s 最大可用档） |
| 21 | 362 | **15.083s** | `15`（360 帧） | ⚠️ **超 15s 硬上限，禁用** |

**三条关键结论**：
- **拿不到 4.0 秒整**：最短合法档为 `4.458s`（k=6），按 4s 切分镜必然多出约 `0.46s`，需在 Stage 6 裁剪气口或提速消化。
- **`seconds: 15` 不可用**：360 帧向上落到 k=21 = 362 帧 = `15.083s`，越过官方 15s 硬上限（可能导致提交被拒或超限）。贴近上限请传 **`seconds: 14`**（→ `14.375s`）。
- **k=8 / 12 / 15 / 18 整数秒不可达**：对应帧数会被向上顶至下一档网格，排分镜时长时直接按可达档估算。

## 提示词结构（结构化模板）

从 `characters.json` 程序化读取 `{voice_anchor}` 填入模板，**禁止靠记忆手写或改写声线描述**：

```
For the target video, at 0.00 seconds into the target video <Picture 1> is fully referenced as the FIRST frame.

integrated_multimodal_description: [Shot 1] <画面+动作+台词时序描述>。
The voice comes from <说话人位置描述>, <角色身份描述>, {voice_anchor} (S1): <d>[Chinese] 台词原文。</d>
<S2>: <d>[Chinese] 第二句。</d>
<动作收尾描述>。Locked-off camera with only a very slight handheld breath, no zoom, no dolly, no cut.

overall_soundscape: <环境声描述>

non_diegetic_music: N/A

No on-screen text, no subtitles, no captions, no watermark.
```

## 声线锚（音色控制的全部实测结论）

- **结构化存储 + 脚本填充**：在 Stage 1 把每个角色的 `voice_anchor` 和 `voice_ref_hz` 写入 `characters.json`，Stage 5 从 JSON 填充，Stage 6 用 `f0_check.py --characters characters.json --role <角色名>` 闭环验收。
- **声线锚写在 `<d>` 标签外**：如 `a man in his late forties with a short black beard and a deep, resonant, heavy chest voice, low-pitched and unhurried`；`<d>` 内只放语言标签与台词原文。
- **同一角色跨镜必须逐字相同**：实测同一角色写 `A young man's voice` → 254Hz；改写 `late forties, deep resonant heavy chest voice` → 120–158Hz。换词等于换人。
- **H3 音高跟台词表演能量走，不由首帧嘴型决定**（实测改嘴微张首帧后音高不变）：惊叹句（「快看啊！」）必然偏高。参考片原声本就高时，高音是忠实复刻不是 bug——**改音色前先量参考片**（`scripts/f0_check.py`）。
- 群像合呼（山呼万岁类）写 `dozens of voices in unison, deep and powerful, drawn out, echoing`。

## 生成阶段红线

- **零文字**：不烧字幕、不加水印、不出标题（尾段统一带 `No on-screen text...`）。
- **不出 BGM**：声音后期制作；`generateAudio: true` 只指台词原生音频。
- 监控体裁的 OSD 时间戳、机位名、字幕卡、档案卡全部**后期叠加**，不算违规。

## 收片

- 画布前端轮询/拉取超时问题已解决，生成完成后节点会自动更新为 `status: success` 并写入 `metadata.bytes > 0` 与 `durationMs`；切勿在生成中删节点重推。
- 判定只看视频节点 `metadata.bytes > 0`；收片用 `scripts/collect_blobs.py`（默认 `--minutes 0`）或按 `config.gateway` 走网关兜底通道（见 `references/canvas-ops.md`）。
- 收片后立刻将 `video_bytes`、`duration_ms` 回写 `state.json`。

## 已验证的能力边界

| 能力 | 状态 |
|---|---|
| i2v 首帧驱动 | ✅ 主力通道，按首帧比例自动定画布（首帧竖屏即出竖屏视频） |
| 原生台词+音轨 | ✅ mp4 自带 aac 32kHz |
| 多人大场面 | ⚠️ 人群规模控制不住，只会往「更多更密」走；同一首帧两次生成的人群密度都不同 |
| fl2va 首尾帧 | ⚠️ 网关通、画布 MCP 建不出、内容必须同源（两次独立出图布局必不一致，中途穿帮）。用途限于跨镜衔接（截上一镜尾帧当下一镜首帧），**不要用于单镜内动作控制** |
| TTS 语音克隆 | 画布 audio 节点（metadata.content 传 base64 mp3）+ `canvas_generate_audio` + `canvas_run_generation`（prompt 必须传 token 串，不传静默停在 idle）；优先克隆，不写音色描述 |
