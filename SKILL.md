---
name: short-drama-autopipeline
description: 端到端全自动 AI 短剧制作流水线：从参考片或剧本出发，经角色资产表、moss 资产（三视图/场景）、qwen-image 参考分镜、选帧、H3 视频（原生音画）、到 ffmpeg/PIL 装配出带字幕的成片。适用于用户要求「复刻某条视频」「全自动做一条短剧」「出成片」等从零到 mp4 的完整任务。含无限画布 MCP 操作规范、收片判真规则、断点续跑与全部实测结论。
version: 1.0.0
updated: 2026-11-24
agent_created: true
dependencies:
  required: []
  optional:
    - name: baige-duanju-juese
      purpose: 角色八项规范与硬校验
      fallback: scripts/character_check.py
---

# 全自动短剧流水线（参考片/剧本 → 成片 mp4）

七段式流水线，每段有验收门，验收不过不进下一段。所有结论来自已交付片子（《做梦都在学408》30s 监控体、《共享网约车》125s 竖屏多角色）的实测。

## 开工前自检（必做）

1. **本地环境自检**：运行 `python3 scripts/preflight.py [--config config.json] [--origin <域名>]`，一次性验证 MCP 配置、blob 目录、ffmpeg 滤镜（判定字幕走 libass 还是 PIL）、Python 依赖（`requirements.txt`）与中文字体。首次部署可参考 `config.example.json` 创建项目 `config.json`。
2. **画布连接态实测**：工具出现在列表里 ≠ 已连通网页画布。必须先实测调用一次 `canvas_get_state`（能返回节点列表才算连上），再调用 `workbench_image_get_config` / `workbench_video_get_config` 读取当前可用模型 ID；若未挂载或不通，按 `references/canvas-ops.md` 顶部的「MCP 安装与画布连接」完成配置和重连。

## 总流程

```
Stage 0 拆解      参考片结构/台词/切点 → spec.md 分镜表 + 角色台词归档
Stage 1 资产表    角色八项 + 结构化声线锚 → characters.json（硬校验）
Stage 2 资产出图  moss：角色三视图 + 场景图
Stage 3 参考分镜  qwen-image-2.1 挂参考出每镜首帧（每镜 2 张）
Stage 4 选帧      验收一致性，弱镜重出，固化选帧字节
Stage 5 H3 视频   首帧 i2v + 结构化声线锚（按需加载 references/h3/），分批提交
Stage 6 收片装配  blob 收片 → 尺寸校验/字幕/电平/时长 → 成片 + 验收
```

各段细则按需加载：
- `references/storyboard.md`（Stage 0–4）
- `references/h3-video.md`（Stage 5 提交参数、17k+5 帧网格表与声线锚）
- `references/h3/00-index.md`（H3 官方提示词工程手册路由索引，按任务加载对应分章）
- `references/assembly.md`（Stage 6 收片装配与验收清单）
- `references/canvas-ops.md`（MCP 安装配置、画布节点操作、收片与网关兜底）
- `references/resume.md`（长耗时任务 `state.json` 断点续跑规范）

## 硬规则（全程生效，违反即返工）

1. **模型 ID 不写死**：提交任何生成前，先用 `workbench_image_get_config` / `workbench_video_get_config` 读当前渠道与模型 ID。渠道会换，写死旧值会静默不启动。
2. **生成成败只看节点 bytes**：避免依赖 UI 主观状态，判定唯一依据是 `canvas_get_state` 返回的 image 节点 `metadata.images[].bytes > 0` 或 video 节点 `metadata.bytes > 0`（页面刷新或中断恢复后重跑前先查 bytes）。
3. **生成阶段零文字**：视频不烧字幕、不加水印、不出标题，**不生成 BGM**（`generateAudio: true` 只指台词）。每条运动提示词末尾统一带 `No on-screen text, no subtitles, no captions, no watermark.`。OSD/字幕卡/档案卡全部后期叠。
4. **画布连线扇出上限 ≈4**：同一 image 节点连到第 5 个 config 时静默拒绝。解法：`add_node` 建副本 image 节点（metadata 直接给原 `storageKey`）分担连线。

> **关于动态标识与能力上限的区分**：第 1 条针对渠道动态标识（模型 ID、渠道 ID），必须每次开工实测读取；文中出现的 `vquality: "720"`、视频并发 `3`、连线扇出 `4`、单镜入参上限 `14s` 属于模型/服务端能力上限的实测默认值，统一收敛至 `config.json` 的 `limits` 段——渠道升级后需重测并更新配置，不要把旧值当永恒常量。

## 关键决策规则

- **角色资产校验降级路径**：若环境已安装 `baige-duanju-juese`，优先用其规范与 `character_check.py`；否则使用本技能内置 `scripts/character_check.py` 执行最小硬校验（接受字段颗粒度略降，但不跳过验收门）。
- **角色提示词风格**：知名 IP 角色（灭霸/钢铁侠/蜘蛛侠级认知度）**直呼其名**，模型会给出电影级长相；知名度不足或自创角色必须「参考图 + 一致性锁定项文字」。反例：直写 "Hulk" 会被拉去真人班纳，加 green-skinned 锚也救不回——绿巨人这类中间态用参考图路线。
- **moss vs qwen 分工**：moss 出资产（结构遵从强，但不支持 references）；qwen-image-2.1 出分镜（支持多参考，角色一致性高）。参考图自带场景光会被后续每帧继承，三视图**不注入**颗粒/电影色调/体积光。
- **首尾帧（fl2va）现状**：网关支持且 mp4 自带 aac；画布 MCP 建不出（第二张图连不进）；内容必须同源否则中途变形。**单镜内动作用提示词写，跨镜衔接才考虑截上一镜尾帧当下一镜首帧**。
- **视频分辨率与时长**：`vquality` 默认 `"720"`（上限 768P）；官方单次视频时长硬上限 **15s**，但 **`seconds: 15` 不可直接作为入参**——360 帧会向上落到 `15.083s` 越限，**贴上限请传 `seconds: 14`**（→14.375s）。完整帧网格见 `references/h3-video.md` 的 17k+5 换算表。

## 常用脚本（本技能自带）

- `scripts/preflight.py`——开工前六项环境自检（MCP 配置、画布快照、blob 目录、ffmpeg 滤镜与字幕路线、Python 依赖、中文字体）。
- `scripts/character_check.py`——Stage 1 角色资产表 `characters.json` 最小硬校验（含八项字段与结构化声线锚校验）。
- `scripts/collect_blobs.py`——跨平台从 Edge/Chrome IndexedDB blob 目录收图/收片：先按 `storageKey` 复用（兼容扇出副本共享同一 blob），同字节数不同 key 才消费式弹出；输出 `manifest.json`。
- `scripts/contact_sheet.py`——拼验收联系表（自动中文字体探测、实测宽截断、按扩展名保存）。
- `scripts/f0_check.py`——人声基频检测（60–1000Hz、半频错判修正、多说话人离散度判别、支持对照 `characters.json` 的 `voice_ref_hz` 验收）。`.wav` 输入不依赖 ffmpeg，视频/其他格式才需 ffmpeg。
- `tests/test_scripts.py`——9 项脚本回归测试（`python -m unittest discover -s tests -v` 或 `pytest -v`）。改动脚本后先跑它。

## 交付形态

- 成片 mp4（画幅跟参考片：竖屏 9:16 / 横屏 16:9）+ 咬合参考片的逐镜时长
- `spec.md`（分镜表、选帧字节、复用链）、`characters.json` 与 `state.json` 随片归档
- 时长压回参考片 ±0.5s；响度对齐参考片（`volumedetect` 对照）
