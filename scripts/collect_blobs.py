#!/usr/bin/env python3
"""从画布浏览器 IndexedDB blob 目录收图/收片，按字节匹配 canvas state 里的节点。

用法:
  python3 collect_blobs.py --state <canvas_state.json> --out build/shots \
      [--blob-dir <IndexedDB blob 目录>] [--origin <域名>] [--config config.json] \
      [--kind image|video|all] [--minutes 0] [--min-bytes 0]

特性:
  - 跨平台自动探测 Edge / Chrome IndexedDB blob 目录（显式参数 > 环境变量 CANVAS_BLOB_DIR > config.json > 平台探测）
  - 可自动从 state.json 的 blob URL 解析 origin，找不到目录时显式报错退出
  - 递归扫描 blob 目录，按 size -> 路径列表（mtime 降序）消费式认领，防止同字节串图
  - 默认不限时间窗（--minutes 0）；开启时间窗且存在漏收时自动二次扫描提示窗外可找回数量
"""
import argparse
import glob
import json
import os
import re
import shutil
import sys
import time
from urllib.parse import urlparse

DEFAULT_ROOTS = {
    "darwin": [
        "~/Library/Application Support/Microsoft Edge/Default/IndexedDB",
        "~/Library/Application Support/Google/Chrome/Default/IndexedDB",
    ],
    "win32": [
        r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\IndexedDB",
        r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\IndexedDB",
    ],
    "linux": [
        "~/.config/microsoft-edge/Default/IndexedDB",
        "~/.config/google-chrome/Default/IndexedDB",
    ],
}


def load_config(config_path: str = "") -> dict:
    """加载可选的 config.json（显式路径 > 当前目录 > 技能根目录）。"""
    candidates = []
    if config_path:
        candidates.append(config_path)
    else:
        candidates.append(os.path.join(os.getcwd(), "config.json"))
        skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates.append(os.path.join(skill_root, "config.json"))
    for path in candidates:
        if path and os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
    if config_path:
        raise SystemExit(f"错误：指定的配置文件不存在：{config_path}")
    return {}


def infer_origin_from_state(state: dict) -> str:
    """从画布节点 metadata 的 blob URL 中提取域名（如 blob:https://canvas.example.com:8080/...）。"""
    for node in state.get("nodes", []):
        md = node.get("metadata") or {}
        urls = [md.get("content", "")]
        for img in md.get("images") or []:
            urls.append(img.get("url", ""))
            urls.append(img.get("content", ""))
        for u in urls:
            if isinstance(u, str) and u.startswith("blob:http"):
                parsed = urlparse(u[5:])
                if parsed.hostname:
                    return parsed.hostname
    return ""


def resolve_blob_dir(explicit: str, origin: str, config: dict) -> str:
    """按优先级解析 IndexedDB blob 目录：显式参数 > 环境变量 > config.json > 跨平台探测。"""
    if explicit:
        return os.path.expandvars(os.path.expanduser(explicit))
    env_dir = os.environ.get("CANVAS_BLOB_DIR", "").strip()
    if env_dir:
        return os.path.expandvars(os.path.expanduser(env_dir))
    cfg_canvas = (config or {}).get("canvas") or {}
    cfg_dir = (cfg_canvas.get("blob_dir") or "").strip()
    if cfg_dir:
        return os.path.expandvars(os.path.expanduser(cfg_dir))

    target_origin = (origin or cfg_canvas.get("origin") or "").strip()
    pattern = f"*{target_origin}*.indexeddb.blob" if target_origin else "*.indexeddb.blob"
    candidates = []
    for root in DEFAULT_ROOTS.get(sys.platform, []):
        expanded = os.path.expandvars(os.path.expanduser(root))
        if not os.path.isdir(expanded):
            continue
        hits = glob.glob(os.path.join(expanded, pattern))
        for h in hits:
            if os.path.isdir(h):
                candidates.append(h)
    if candidates:
        # 优先选择最近修改的 blob 目录；若未指定 origin 且命中多个候选目录，向 stderr 提示
        candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        if not target_origin and len(candidates) > 1:
            print(
                f"提示：未指定 --origin，发现 {len(candidates)} 个候选 blob 目录，已默认选择最新：{candidates[0]} "
                "（建议用 --origin 或 config.json 的 canvas.origin 锁定站点）。",
                file=sys.stderr,
            )
        return candidates[0]
    return ""


def sanitize(name: str) -> str:
    """清洗节点标题作为安全文件名。"""
    name = name.splitlines()[0] if name.splitlines() else "node"
    name = re.sub(r"【[^】]*】", "", name)  # 去掉「【文本1】」类前缀
    name = name.strip()
    if not name:
        name = "node"
    name = re.sub(r"[^\w\u4e00-\u9fff.-]+", "_", name)
    return name.strip("_")[:60] or "untitled"


def build_size_index(blob_dir: str, minutes: int, min_bytes: int) -> dict:
    """递归扫描 blob 目录，构建 size -> 按 mtime 降序排列的文件路径列表。"""
    idx = {}
    now = time.time()
    cutoff = now - minutes * 60 if minutes and minutes > 0 else None
    for dirpath, _dirs, files in os.walk(blob_dir):
        for name in files:
            p = os.path.join(dirpath, name)
            try:
                st = os.stat(p)
            except OSError:
                continue
            if cutoff is not None and st.st_mtime < cutoff:
                continue
            if min_bytes and st.st_size < min_bytes:
                continue
            idx.setdefault(st.st_size, []).append((st.st_mtime, p))
    return {
        size: [p for _mtime, p in sorted(items, key=lambda x: x[0], reverse=True)]
        for size, items in idx.items()
    }


def sniff_type(path: str) -> str:
    """通过文件魔数判断产物扩展名。"""
    with open(path, "rb") as fh:
        head = fh.read(16)
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if head[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return ".webp"
    if head[4:8] == b"ftyp":
        return ".mp4"
    return ""


def unique_dest(out_dir: str, title: str, ext: str, seen_names: dict) -> str:
    """为同名节点生成不冲突的输出路径。"""
    base = f"{title}{ext}"
    n = seen_names.get(base, 0)
    seen_names[base] = n + 1
    filename = base if n == 0 else f"{title}_{n}{ext}"
    return os.path.join(out_dir, filename)


def collect_items(state: dict, kind: str) -> list:
    """从 canvas state 中抽取所有 bytes > 0 的待收片条目。"""
    img_to_config = {}
    node_titles = {n.get("id"): n.get("title", "") for n in state.get("nodes", [])}
    for conn in state.get("connections", []):
        frm, to = conn.get("fromNodeId"), conn.get("toNodeId")
        if frm in node_titles and to not in img_to_config:
            img_to_config[to] = node_titles[frm]

    items = []
    for node in state.get("nodes", []):
        node_id = node.get("id", "node")
        raw_title = img_to_config.get(node_id) or node.get("title") or node_id
        title = sanitize(raw_title)
        ntype = node.get("type")
        md = node.get("metadata") or {}

        if ntype == "image" and kind in ("image", "all"):
            for img in md.get("images") or []:
                b = img.get("bytes") or 0
                if b > 0:
                    items.append({
                        "kind": "image",
                        "node": node_id,
                        "title": raw_title,
                        "safe_title": title,
                        "storageKey": img.get("storageKey"),
                        "bytes": b,
                    })
        elif ntype == "video" and kind in ("video", "all"):
            b = md.get("bytes") or 0
            if b > 0:
                items.append({
                    "kind": "video",
                    "node": node_id,
                    "title": node.get("title") or raw_title,
                    "safe_title": title,
                    "storageKey": md.get("storageKey"),
                    "bytes": b,
                })
            for vid in md.get("videos") or []:
                vb = vid.get("bytes") or 0
                if vb > 0:
                    vid_suffix = f"_{vid.get('id')}" if vid.get("id") else ""
                    items.append({
                        "kind": "video",
                        "node": node_id,
                        "title": node.get("title") or raw_title,
                        "safe_title": f"{title}{vid_suffix}",
                        "storageKey": vid.get("storageKey"),
                        "bytes": vb,
                    })
    return items


def main():
    ap = argparse.ArgumentParser(description="按字节从浏览器 IndexedDB blob 目录收集画布产物")
    ap.add_argument("--state", required=True, help="canvas_get_state 结果 JSON 路径")
    ap.add_argument("--out", required=True, help="输出目录")
    ap.add_argument("--blob-dir", default="", help="IndexedDB blob 目录（留空则自动探测）")
    ap.add_argument("--origin", default="", help="画布域名过滤词（留空则从 config.json 或 state 自动提取）")
    ap.add_argument("--config", default="", help="可选 config.json 路径")
    ap.add_argument("--kind", default="all", choices=["image", "video", "all"], help="收集类型")
    ap.add_argument("--minutes", type=int, default=0, help="只收最近 N 分钟的 blob（0 表示不限时间窗）")
    ap.add_argument("--min-bytes", type=int, default=0, help="忽略小于该字节数的 blob（默认 0 不过滤）")
    args = ap.parse_args()

    with open(args.state, "r", encoding="utf-8") as fh:
        state = json.load(fh)

    config = load_config(args.config)
    origin = args.origin or infer_origin_from_state(state)
    blob_dir = resolve_blob_dir(args.blob_dir, origin, config)
    if not blob_dir or not os.path.isdir(blob_dir):
        raise SystemExit(
            f"错误：未找到有效的 IndexedDB blob 目录（origin={origin or '未指定'}）。\n"
            "请通过 --blob-dir、环境变量 CANVAS_BLOB_DIR 或 config.json 的 canvas.blob_dir 指定路径。"
        )

    os.makedirs(args.out, exist_ok=True)
    idx = build_size_index(blob_dir, args.minutes, args.min_bytes)
    items = collect_items(state, args.kind)

    manifest = []
    unmatched = []
    skipped_small = []
    seen_names = {}
    by_key = {}  # 同一 storageKey（如画布扇出副本节点）共享同一份 blob，不重复消费

    for item in items:
        b = item["bytes"]
        if args.min_bytes and b < args.min_bytes:
            skipped_small.append(item)
            continue

        skey = (item.get("storageKey") or "").strip()
        if skey and skey in by_key:
            src = by_key[skey]
        else:
            candidates = idx.get(b)
            if not candidates:
                unmatched.append(item)
                continue
            # 不同 storageKey 且同字节数时消费式弹出，防止串图
            src = candidates.pop(0)
            if skey:
                by_key[skey] = src

        default_ext = ".mp4" if item["kind"] == "video" else ".png"
        ext = sniff_type(src) or default_ext
        dst = unique_dest(args.out, item["safe_title"], ext, seen_names)
        shutil.copy2(src, dst)
        manifest.append({
            "node": item["node"],
            "title": item["title"],
            "storageKey": item["storageKey"],
            "bytes": b,
            "file": dst,
            "kind": item["kind"],
        })

    manifest_path = os.path.join(args.out, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print(f"blob 目录: {blob_dir}")
    print(f"收 {len(manifest)} 项 -> {args.out}（manifest.json 记录节点映射）")

    if skipped_small:
        print(
            f"提示：按 --min-bytes={args.min_bytes} 过滤跳过 {len(skipped_small)} 项小体积产物：",
            file=sys.stderr,
        )
        for s in skipped_small[:10]:
            print(f"  - [{s['kind']}] node={s['node']} bytes={s['bytes']} title={s['title']}", file=sys.stderr)
        if len(skipped_small) > 10:
            print(f"  ... 其余 {len(skipped_small) - 10} 项省略", file=sys.stderr)

    if unmatched:
        print(f"警告：未匹配 {len(unmatched)} 项：", file=sys.stderr)
        for u in unmatched[:10]:
            print(f"  - [{u['kind']}] node={u['node']} bytes={u['bytes']} title={u['title']}", file=sys.stderr)
        if len(unmatched) > 10:
            print(f"  ... 其余 {len(unmatched) - 10} 项省略", file=sys.stderr)

        # 若启用了时间窗，则全量二次扫描以诊断是否为窗口过期导致的漏收
        if args.minutes and args.minutes > 0:
            full_idx = build_size_index(blob_dir, 0, args.min_bytes)
            outside_hits = sum(1 for u in unmatched if full_idx.get(u["bytes"]))
            if outside_hits > 0:
                print(
                    f"诊断：未匹配 {len(unmatched)} 项中，有 {outside_hits} 项在时间窗（{args.minutes} 分钟）外可找到 "
                    "→ 请调大 --minutes 或置 0。",
                    file=sys.stderr,
                )
        sys.exit(1)


if __name__ == "__main__":
    main()
