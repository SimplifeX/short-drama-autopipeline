# 断点续跑约定（`state.json`）

短剧七段流水线耗时通常数小时，中断（会话重启、浏览器刷新、配额暂停、手工调镜）不可避免。为避免凭记忆判断进度或误重跑已成功的镜头，每个项目根目录统一维护 `state.json` 作为续跑锚点。

## 文件位置与 Schema

路径：`<项目>/state.json`

```json
{
  "project": "项目名",
  "canvas_project_id": "<canvas projectId>",
  "stage": 5,
  "updated_at": "2026-11-24T21:00:00+08:00",
  "assets": {
    "characters": {
      "角色A": { "node_id": "...", "storageKey": "image:...", "bytes": 1823412 }
    },
    "scenes": {
      "场景1": { "node_id": "...", "storageKey": "image:...", "bytes": 1542310 }
    }
  },
  "shots": [
    {
      "id": "s01",
      "first_frame_node": "...",
      "first_frame_key": "image:...",
      "first_frame_bytes": 1284723,
      "video_node": "...",
      "video_task_id": "...",
      "video_bytes": 4820193,
      "duration_ms": 5167
    },
    {
      "id": "s02",
      "first_frame_node": "...",
      "first_frame_key": "image:...",
      "first_frame_bytes": 993012,
      "video_node": "",
      "video_task_id": "",
      "video_bytes": 0,
      "duration_ms": 0
    }
  ]
}
```

## 续跑硬规则

1. **先同步再决策**：每次恢复作业时，先调用一次 `canvas_get_state`，将画布中已落盘的 `bytes > 0` 节点（image 的 `metadata.images[].bytes`、video 的 `metadata.bytes`）回填进 `state.json`。
2. **`bytes > 0` 一律跳过**：
   - Stage 2 资产：`assets.*.*.bytes > 0` 跳过不再生成。
   - Stage 3/4 首帧：`shot.first_frame_bytes > 0` 跳过；仅对 `first_frame_bytes == 0` 或人工标记重出的镜头重新提交。
   - Stage 5 视频：`shot.video_bytes > 0` 跳过；仅对 `video_bytes == 0` 的镜头按并发上限分批补跑。
3. **写盘时机**：每完成一个阶段验收门、或每批视频收片后，立刻更新 `state.json` 与 `spec.md`。
4. **切勿盲删重推**：若 `video_node` 非空但 `video_bytes == 0`，先检查 `generation_get_status`（以及可选的网关日志）确认任务已彻底失败，再重提。
