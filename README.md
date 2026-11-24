# short-drama-autopipeline

端到端 AI 短剧制作流水线。从一条参考片或一份剧本出发，自动走完「角色资产 → 场景/三视图 → 参考分镜 → 选帧 → H3 视频（原生台词）→ 装配成片 mp4」。

- **版本**：1.0.0（2026-11-24）
- **适用**：竖屏/横屏短剧、复刻某条视频的结构与画质、同 IP 多集量产
- **不适用**：单镜头试片（直接用 H3 单技能更快）、需要精确字幕排版（字幕是后期叠的）、需要帧级剪辑控制

---

## 一、先看你能不能满足前置条件

这套流水线不是纯本地工具，它依赖三样东西，缺一样就跑不通：

| 依赖 | 用途 | 怎么检查 |
|---|---|---|
| **无限画布 + 平台网关** | 出图、出视频的全部算力都走这里 | 能打开画布网页并登录 |
| **Node.js 18+** | 挂载画布 MCP（`npx`） | `node -v` |
| **ffmpeg / ffprobe** | 量参数、抽音轨、拼片、加字幕 | `ffmpeg -version` |
| **Python 3.9+** | 五个辅助脚本 | `python -V` |

> **ffmpeg 没有的话**：Windows 用 `winget install Gyan.FFmpeg`，macOS 用 `brew install ffmpeg`。
> 装完必须新开一个终端，`ffmpeg -version` 能出东西才算成功。

---

## 二、三步装好

### 1. 放到技能目录

**WorkBuddy / Cursor / Claude Code 用户**，解压到用户级技能目录：

```
Windows:  %USERPROFILE%\.workbuddy\skills\short-drama-autopipeline\
macOS:    ~/.workbuddy/skills/short-drama-autopipeline/
```

解压后确认这个路径下能直接看到 `SKILL.md`（不要再套一层文件夹）。

**其他 Agent 客户端**：放到它约定的 skill / rules 目录即可，本技能不依赖特定宿主。

### 2. 装 Python 依赖

```bash
cd <技能目录>
pip install -r requirements.txt
```

### 3. 建配置文件

```bash
cd <技能目录>
cp config.example.json config.json
```

`config.json` 已经预置了画布域名（`canvas.simplife.icu`），**一般不用改**。只有在你访问的是其它实例时，才需要改 `canvas.origin`。

---

## 三、装完必须做一次自检

```bash
cd <技能目录>
python scripts/preflight.py --config config.json
```

六项全绿（`OK` / `INFO` / `SKIP`）才算装好。看到 `FAIL` 先修，不要带着问题开工。

想更彻底一点，跑一遍脚本回归测试（9 项，约 10 秒）：

```bash
python -m unittest discover -s tests -v
```

---

## 四、连上画布（最容易漏的一步）

**MCP 工具出现在列表里 ≠ 已经连上网页画布。** 这两步都要做：

1. **挂载 MCP**（在 Agent 的 MCP 配置里加）：

```json
{
  "mcpServers": {
    "infinite-canvas": {
      "command": "npx",
      "args": ["-y", "@basketikun/canvas-agent@latest", "mcp"]
    }
  }
}
```

Claude Code / Codex 用户可以直接：

```bash
claude mcp add --scope user --transport stdio infinite-canvas -- npx -y @basketikun/canvas-agent@latest mcp
codex mcp add infinite-canvas -- npx -y @basketikun/canvas-agent@latest mcp
```

2. **连本地桥**：终端跑 `npx -y @basketikun/canvas-agent@latest`，记下输出的 `Local URL` 和 `Connect token`，然后在**画布网页右上角点 Agent**，填进去。

3. **验证**：让 Agent 调一次 `canvas_get_state`，能返回节点列表才算真连上。

---

## 五、怎么用

装好之后不需要记命令，直接用自然语言提需求，例如：

- 「照着这条视频做一版，30 秒，竖屏」+ 参考片
- 「用这个剧本出一集，10 个镜头」
- 「把上次的《XXX》第 3 集做出来」

Agent 会自己按七段流程推进。你需要在几个验收点做判断：角色资产表、选帧、成片验收。

**完整的流程、判真规则和踩坑结论都在 `SKILL.md` 与 `references/` 里，Agent 会自己读，你不用先背。**

---

## 六、开始前必须知道的七件事

1. **生成阶段零文字、零 BGM。** 视频里不会烧字幕，也不会配乐——字幕和音乐全是后期加的。别指望一次出成片带字幕。

2. **时长拿不到整秒。** H3 按 `17k+5` 帧走，想要 8 秒实际是 8.000 秒（这个运气好），但想要 4 秒实际是 4.458 秒、想要 5 秒是 5.167 秒。**每镜会多出 0.2–0.5 秒**，靠后期提速压回来。

3. **`seconds: 15` 不能直接用。** 会溢出到 15.083 秒越官方上限。贴上限请传 `14`（得到 14.375 秒）。这条已写进 `config.json` 的 `max_seconds: 14`。

4. **角色一致性靠「参考图 + 一致性锁定项」，不靠 prompt 描述。** 声线锚必须**逐字复制**，换个形容词就是换个人（实测同一角色两种描述能差 100Hz 以上）。

5. **判定成败只看 bytes，不看界面状态。** 页面提示「生成已中断」多数是假报警，服务端可能已经跑完。**重推前先查 `bytes > 0`**，否则会白烧一次生成。

6. **连线扇出最多 4 个。** 第 5 个会静默失败（返回 200 但连线不存在）。脚本侧用 `add_node` 建副本分担，别硬连。

7. **多人场面控不住。** 人群只会往「更多更密」走，同一首帧两次生成密度都不同。想控人数请改构图/景别，不要靠 prompt。

---

## 七、出问题怎么办

| 现象 | 先查什么 |
|---|---|
| 提交后什么都没发生 | 模型 ID 是不是写死了 → 用 `workbench_*_get_config` 读当前值 |
| 画布工具调用成功但没反应 | MCP 挂了但网页没连 → 回到第四节第 2 步 |
| 收片收到错图 | `state.json` 里节点有没有 `storageKey`；跑 `collect_blobs.py` 看 stderr 告警 |
| 字幕是方块/乱码 | 中文字体没探到 → `preflight.py` 第 6 项 |
| 成片比参考片长 | 每镜的帧网格多出 0.2–0.5 秒 → Stage 6 用 `setpts` 压缩，同时**字幕时间轴要重排** |

先跑 `preflight.py`，它通常能直接指出问题在哪。搞不定找维护者，附上 `preflight.py` 的完整输出。

---

## 八、目录说明

```
SKILL.md              七段流程 + 硬规则（Agent 主入口）
config.example.json   配置模板（复制成 config.json 使用）
requirements.txt      Python 依赖
references/           各段细则：分镜、H3 参数、装配、画布操作、断点续跑
references/h3/        H3 提示词工程手册（按任务分章加载）
scripts/              五个辅助脚本
tests/                9 项回归测试
```

---

## 九、已知限制

- **手册基于 2026-08-31 的官方文档快照**。官方字段/参数更新后需要重新核对 `references/h3/90-official.md`。
- **帧网格表 11–14 秒档为推算值**，首次跑到这些档位请核对返回的 `durationMs`。
- **`vquality` 只有 `"720"` 有效**，实际上限 768P。写 1080 不会报错，会静默降级。
- **手册里的并发/扇出数字是某一时刻的观测值**，渠道升级后要重测，不要当常量。

---

## 十、致谢与开源项目

本技能的完整流水线基于以下优秀的开源项目与社区生态构建，特此致谢：

- **[@basketikun/infinite-canvas](https://github.com/basketikun/infinite-canvas)**（by @basketikun）— 提供开源无限画布工作台与 `@basketikun/canvas-agent` MCP 桥接能力，是本流水线的画布编排与资产交互底座。
- **[@MiniMax-AI/MiniMax-H3](https://github.com/MiniMax-AI/MiniMax-H3)** — 提供 MiniMax H3 开源音画视频生成模型及官方提示词规范（`references/h3/` 基于其官方文档整理）。
- **[ComfyUI](https://github.com/comfyanonymous/ComfyUI)** / **[Comfy-Org](https://github.com/Comfy-Org)** — 提供底层工作流推理引擎与官方模型模板生态。
- **[FFmpeg](https://github.com/FFmpeg/FFmpeg)** & **[Pillow](https://github.com/python-pillow/Pillow)** — 提供音视频分析、字幕压制、联系表生成与后期成片装配能力。

