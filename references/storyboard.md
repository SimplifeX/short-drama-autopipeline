# Stage 0–4：拆解、资产表、资产出图、参考分镜、选帧

## Stage 0 拆解参考片

拿到参考片先量四个维度，产出分镜表（`spec.md`）并初始化 `state.json`（见 `references/resume.md`）：

1. **基本参数**：`ffprobe` 取 duration / 分辨率 / 帧率 / 音轨。竖片 9:16、横片 16:9，成片画幅跟参考片。
2. **切点**：`ffmpeg -i ref.mp4 -vf "select='gt(scene,0.25)',showinfo" -f null -` 提取场景切点，对照关键帧联系表（`fps=1/4` 抽帧 + `contact_sheet.py` 拼表）逐镜确认内容。
3. **台词**：`ffmpeg -i ref.mp4 -vn -ac 1 -ar 16000 ref.wav` → 语音转写全量校对，按角色归档台词（一字不差，复刻片的生命线）。
4. **笑点配方**：一句话总结这条片的机制（如「身份错位连击」「反转戳破体面」），后续所有取舍围绕它。

**验收门**：分镜表每镜有「时长 / 画面内容 / 台词 / 机位」四项，角色清单与台词归属无遗漏。

## Stage 1 角色资产表

落盘 `characters.json`，每个角色需包含八项必填字段（`name` 姓名 / `identity` 身份 / `appearance` 外貌 / `costume` 服装 / `signature_items` 标志性物品 / `personality` 性格 / `variants` 变体 / `consistency_locks` 一致性锁定项），并建议同步结构化声线字段供 Stage 5 自动填充与 Stage 6 验收：

```json
{
  "characters": [
    {
      "name": "老周",
      "identity": "中年网约车司机",
      "appearance": "...",
      "costume": "...",
      "signature_items": ["黑色对讲机"],
      "personality": "嘴碎但讲义气",
      "variants": [],
      "consistency_locks": [
        "四十岁出头偏瘦脸型，蓄短黑胡茬。",
        "身穿褪色深蓝工装夹克，左胸带反光条。"
      ],
      "voice_anchor": "a man in his late forties with a short black beard and a deep, resonant, heavy chest voice, low-pitched and unhurried",
      "voice_ref_hz": [120, 158]
    }
  ]
}
```

- **硬校验（双轨）**：若环境已安装 `baige-duanju-juese`，优先使用其规范与 `character_check.py`；否则执行本技能内置的 `python3 scripts/character_check.py characters.json [--require-voice]`，校验八项字段齐全、姓名唯一、`consistency_locks` 为 2–4 条且独立成句。
- **双通道一致性**：锁定项只写**肉眼可辨、跨分镜不变**的特征，后续直接拼进生图提示词复用——AI 生图不会自动保持一致，一致性靠「参考图 + 锁定项文字」双通道。
- **结构化声线锚**：有台词的角色把 `voice_anchor` 与参考音高区间 `voice_ref_hz` 固化在 `characters.json`，禁止 Stage 5 靠记忆手抄改写。

## Stage 2 资产出图（moss）

**先验证画幅**：用一张测试图确认目标比例（moss 直接支持 9:16 出 864×1536）。

资产清单 = 每角色一张三视图 + 每场景一张设定图：

- **三视图提示词模板**（16:9 横版）：
  - `Character turnaround reference sheet, three full-body views of the SAME character side by side on one plain light-grey studio background: front view, side view, back view`
  - 风格段：`photorealistic character design sheet, neutral even studio lighting, soft and flat, no cast shadows, no film grain, no cinematic colour grade, no volume light`（**例外规则**：参考图不注入颗粒/电影色调/体积光，否则后续每帧继承同一束场景光）
  - 角色段：外貌 + 服装的绝对描述（从锁定项展开），末尾 `Same face, same costume in all three views. Full body head to toe.`
- **场景资产**：与成片同比例（竖片 9:16）；`No people anywhere in the frame`；中性日光不加色调。
- 每资产 `count: 2` 出两张备选，拼表人工选优。

**验收门**：每角色/场景有一张三视图可用（同一角色三个视图同脸同装、无畸变），选定 `storageKey` 与 `bytes` 记录进 `spec.md` 与 `state.json`。

## Stage 3 参考分镜（qwen-image-2.1）

每镜一个 text 节点 + 一个 config 节点：

```
config: model=<渠道>::qwen-image-2.1, size=<成片比例>, count=2,
        references=[角色三视图 storageKey, 场景 storageKey],  # 车内镜挂内饰、车外镜挂外观
        composerContent="@[node:tqN]"
```

同时从 image 资产节点 `connect_nodes` 连到 config（扇出超 `config.limits.fanout`（默认 4）时建副本节点分担，见 `references/canvas-ops.md`）。

**提示词模板**（两种风格按角色选）：

- **知名 IP 角色 → 直呼其名**（实测灭霸/钢铁侠/蜘蛛侠直写可得电影级长相）：
  `Thanos (reference image 1) squeezed into the back seat of the yellow taxi (reference image 2), one huge hand raised in a stopping gesture, ...`
- **自创/低认知度角色 → 锁定项绑定**：
  `Keep the raccoon in reference image 1 exactly as designed: same <锁定项1>, same <锁定项2>. Use reference image 2 as the taxi interior. New shot: <姿态/表情/机位>`
- 通用尾段：`Photorealistic cinematic film still, vertical 9:16, handheld stabilizer look, natural daylight, mild warm colour grade. No text overlay, no subtitles, no watermark.`
- 双人镜挂三参考（角色A + 角色B + 场景），文字里写明 `reference image 1/2/3` 各是谁。

**已知反例**：直写 "Hulk" 会被拉去真人班纳（人类脸），加 `green-skinned giant` 锚也救不回；此类角色一律走锁定项路线。

**验收门**：全部分镜出图（每镜 2 张），拼联系表 + 逐镜核对角色一致性。

## Stage 4 选帧与重出

- 逐镜对比 a/b 两张，按「角色一致性 > 构图正确 > 表情到位」排序选帧。
- 弱镜单独 `run_generation` 重出（改提示词风格往往比改细节词有效——形容词版不行换直呼其名，反之亦然），重出只影响该镜不动画布其他节点。
- 重跑后**先查 bytes 再判断**（页面刷新会造成假失败，见 `references/canvas-ops.md`）。
- 选帧结果（`storageKey` 与 `bytes`）写进 `spec.md` 与 `state.json` 固化，后续 H3 视频直接按选定首帧提交。
