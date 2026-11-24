# 画布与网关操作规范（MCP 通道）

适用于无限画布（目标域名通过 `config.json` 的 `canvas.origin` 配置）的全部 MCP 调用。所有结论均为实测。

## MCP 安装与画布连接（若当前环境未接入 MCP）

如果当前会话没有 `canvas_*` / `workbench_*` 工具，先按以下方式安装并连接 `infinite-canvas` MCP（依赖 Node.js / `npx`）：

1. **配置 MCP 服务**（Stdio 模式，命令：`npx -y @basketikun/canvas-agent@latest mcp`）：
   - **Antigravity**（`~/.gemini/config/mcp_config.json`）或通用 MCP JSON 配置：
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
   - **Claude Code**：`claude mcp add --scope user --transport stdio infinite-canvas -- npx -y @basketikun/canvas-agent@latest mcp`
   - **Codex**：`codex mcp add infinite-canvas -- npx -y @basketikun/canvas-agent@latest mcp`
   配置后刷新 MCP 服务或新开对话即可加载全部画布工具。
2. **连接本地画布网页**：
   - 在终端运行 `npx -y @basketikun/canvas-agent@latest`，记录输出的 `Local URL`（如 `http://127.0.0.1:17371`）与 `Connect token`。
   - 在画布网页右上角点击 **Agent**，填入上述地址与 token 完成连接。
3. **验证连通态**：MCP 工具出现在列表里 ≠ 已连上网页。必须实测调用一次 `canvas_get_state` 成功返回节点列表，才算真正连通。

## 提交前必做

- **先读配置再提交**：`workbench_image_get_config` / `workbench_video_get_config` 拿当前模型 ID（形如 `<渠道ID>::moss-image`、`<渠道ID>::qwen-image-2.1`、`<渠道ID>::minimax-h3`）。渠道会换，写死旧值会静默不启动。
- **查队列空闲**：`generation_get_status`（scope=canvas）确认 running 数量；默认视频并发上限 `config.limits.video_concurrency = 3`，第 4 条可能直接报「请求失败」。

## 节点操作模式（`canvas_apply_ops`）

一条 `apply_ops` 携带多组操作，标准三件套：

```
1. add_node  text   → 提示词正文（metadata.content）
2. add_node  config → 生成配置（model / size / count / references / composerContent="@[node:<文本节点ID>]"）
3. connect_nodes + run_generation(mode, nodeId, prompt="@[node:<文本节点ID>]")
```

- config 的 `references` 传 storageKey 数组（`image:<key>`），同时从 image 节点 `connect_nodes` 连到 config，双保险。
- 修改节点用 `update_node` 的 **`metadata` 字段**（`patch` 实测不生效）。
- 一批 `apply_ops` 的返回 JSON 是全画布状态（很大，会落盘到客户端 tool-results 文件），用 `jq` 或 Python 按需查，校验连线数与 references 数量是否与预期一致。

## 已知坑与判真规则

1. **连线扇出上限（`config.limits.fanout`，默认 4）**：同一 image 节点连到第 5 个 config 时静默拒绝（返回 200 但连线不存在）。解法：`add_node` 建副本 image 节点，metadata 直接给原 `storageKey` + `content` 放 blob URL，用副本分担连线。
2. **页面刷新中断生成**：任务报「页面刷新后生成已中断，请重新生成」——多数时候服务端已完成或正在跑。**重新提交前先查节点 bytes**：`canvas_get_state` 查 image 节点 `.metadata.images[].bytes` 或 video 节点 `.metadata.bytes`，`bytes > 0` 就直接收片，不要重跑（曾误删过两条已成功的视频）。
3. **视频轮询与拉取**：画布前端轮询/拉取超时问题已解决，生成完成后节点会自动同步为 `status: success` 并写入 `bytes`、`durationMs` 等字段；判定收片仍以 `bytes > 0` 为准。
4. **succeeded / 失败误报**：网关已受理但画布标失败、或前端标成功但字节为 0 的情况仍需防备。判定只看 `bytes > 0` / 网关日志。
5. **视频挂首帧三步校验**：只 `connect_nodes` 不计入 references。`canvas_generate_video` 提交时 `referenceNodeIds` 必须图片在前、文本在后，且 `prompt` 以 `@[node:<图片ID>]` 开头；提交后必须用 `canvas_get_state` 校验 video 节点的 `metadata.references` 包含 `image:<storageKey>`，并确认任务 prompt 出现 `图片1`（见 `references/h3-video.md`）。
6. **返回体超大**：`canvas_get_state` / `apply_ops` 常超 100KB，客户端会自动落盘到工具结果目录（具体路径由宿主客户端决定，可在 `config.tools.tool_results_dir` 记录），用 `jq` / Python 按需查询，不要整读。

## 收片（跨平台浏览器 IndexedDB blob）

画布生成产物缓存在浏览器 IndexedDB blob 目录中。不要在脚本或命令里写死本机路径，统一用 `scripts/collect_blobs.py` 自动探测或通过配置指定：

```bash
python3 scripts/collect_blobs.py \
  --state <canvas_get_state落盘JSON> \
  --out build/shots \
  [--config config.json] \
  [--origin <canvas.origin>] \
  [--blob-dir <显式路径>] \
  [--minutes 0]
```

- **路径解析优先级**：`--blob-dir` > 环境变量 `CANVAS_BLOB_DIR` > `config.json`（`canvas.blob_dir`）> 跨平台自动探测 macOS / Windows / Linux 的 Edge & Chrome IndexedDB 目录（可自动从 `state.json` 的 blob URL 提取域名；未指定 `--origin` 且命中多个站点目录时会打印提示）。
- **防串图与副本兼容**：脚本递归扫描目录（不依赖固定 `1/*/*` 层级），先按 `storageKey` 复用已认领的 blob（兼容画布扇出副本共享同一 `storageKey`），不同 `storageKey` 但同字节数时再按 `size -> 文件列表`（mtime 降序）消费式弹出；默认 `--minutes 0` 不限时间窗，`--min-bytes` 过滤项会显式打印提示，真缺片则返回非零退出码并输出诊断信息。
- **`storageKey` 口径**：实测画布 `state.json` 中节点 `storageKey` 原值已带 `image:` / `video:` 前缀，manifest 与提交 `references` 直接原样复用，勿重复拼接前缀。

## 直连网关（可选兜底通道）

若部署了自建网关，请在项目 `config.json` 中配置 `gateway.host`、`gateway.port`、`gateway.token_file`、`ssh_alias`、`tools.comfyui_output`（模板见 `config.example.json`）：

- 查任务：`curl -H "Authorization: Bearer $(cat <config.gateway.token_file>)" http://<config.gateway.host>:<config.gateway.port>/v1/videos/<gid>`
- 查日志：通过 `ssh <config.ssh_alias>` 检查网关日志中的 `VIDEO` 受理/排队/失败记录
- ComfyUI 产物目录：见 `config.tools.comfyui_output`
- **分辨率坑**：`fl2va` 直连不传 size 时默认 **1344×768**，与画布出片常见 `1248×704` 不一致；调用时须显式传 size，且 Stage 6 装配脚本入口已强制校验全部分镜尺寸一致。

## 模型能力速查

| 模型 | 出图 | 挂参考 | 特点 |
|---|---|---|---|
| moss-image | ✅ 9:16 / 16:9（864×1536 / 1536×864） | ❌ 带 references 直接失败 | 结构遵从强、织物/面部好 |
| qwen-image-2.1 | ✅ | ✅ 多参考 | 角色一致性高，分镜主力 |
| minimax-h3（视频） | — | — | 原生音画；官方单次上限 4–15s；支持 `frames`（首尾帧）/ `reference`（全能参考）模式与 `default`/`action`/`final` 预设；上限 768P；默认并发 3 |
