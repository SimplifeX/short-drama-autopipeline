#!/usr/bin/env python3
"""短剧流水线开工前环境自检脚本（Preflight）。

一次性排查最常见的静默失败前置条件：
  [1/6] MCP 配置检查（探测常见客户端是否已配置 infinite-canvas）
  [2/6] 画布状态快照（可选 --state 校验连通结果、节点数与已用模型）
  [3/6] 浏览器 blob 目录探测（复用 collect_blobs.resolve_blob_dir）
  [4/6] ffmpeg / ffprobe 与关键滤镜能力（自动判定字幕走 libass 还是 PIL）
  [5/6] Python 依赖检查（numpy / Pillow）
  [6/6] 配置与中文字体探测（供 PIL 字幕与 contact_sheet.py 使用）

用法:
  python3 preflight.py [--config config.json] [--origin canvas.example.com] [--state canvas_state.json]
"""
import argparse
import json
import os
import shutil
import subprocess as sp
import sys
import time

# 复用同目录下 collect_blobs 的配置与路径探测逻辑
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import collect_blobs  # noqa: E402

MCP_CONFIG_CANDIDATES = [
    ("Antigravity", "~/.gemini/config/mcp_config.json"),
    ("Claude Code", "~/.claude.json"),
    ("Codex", "~/.codex/config.toml"),
    ("WorkBuddy", "~/.workbuddy/mcp.json"),
    ("Cursor", "~/.cursor/mcp.json"),
    ("Windsurf", "~/.codeium/windsurf/mcp_config.json"),
    ("VS Code (macOS)", "~/Library/Application Support/Code/User/mcp.json"),
    ("VS Code (Windows)", r"%APPDATA%\Code\User\mcp.json"),
    ("VS Code (Linux)", "~/.config/Code/User/mcp.json"),
]

FONT_CANDIDATES = [
    # macOS
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    # Windows
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    # Linux
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]


def dwidth(text: str) -> int:
    """估算终端等宽显示宽度（非 ASCII 字符按 2 列计）。"""
    return sum(2 if ord(ch) > 127 else 1 for ch in text)


def pad_display(text: str, width: int) -> str:
    """按终端显示宽度右补空格，确保中英文混排列对齐。"""
    return text + " " * max(0, width - dwidth(text))


def check_mcp_config():
    """检查本地常见 Agent 客户端配置中是否已注册 infinite-canvas MCP（仅作静态提示）。"""
    hits = []
    for name, raw_path in MCP_CONFIG_CANDIDATES:
        path = os.path.expandvars(os.path.expanduser(raw_path))
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
            if "infinite-canvas" in content or "canvas-agent" in content:
                hits.append(f"{name} ({path})")
        except OSError:
            continue
    if hits:
        return "OK", f"已配置：{'; '.join(hits)}"
    return "INFO", "未在本地配置文件中找到（若当前会话已能调用 canvas_* 工具，可忽略此项）"


def check_canvas_state(state_path: str):
    """若提供 canvas_get_state 落盘文件，校验连通结果与模型信息。"""
    if not state_path:
        return "SKIP", "未传 --state（由 Agent 实测调用一次 canvas_get_state + workbench_*_get_config 验证连通）"
    if not os.path.isfile(state_path):
        return "FAIL", f"文件不存在：{state_path}"
    try:
        with open(state_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        nodes = data.get("nodes") or []
        title = data.get("title") or data.get("projectId") or "未命名画布"
        models = sorted({
            (n.get("metadata") or {}).get("model")
            for n in nodes
            if (n.get("metadata") or {}).get("model")
        })
        model_info = f"，已用模型：{', '.join(models)}" if models else ""
        return "OK", f'画布 "{title}"，{len(nodes)} 节点{model_info}'
    except Exception as exc:
        return "FAIL", f"解析失败：{exc}"


def check_blob_dir(explicit: str, origin: str, config: dict, state_path: str):
    """探测 IndexedDB blob 目录并统计文件数。"""
    inferred_origin = origin
    if not inferred_origin and state_path and os.path.isfile(state_path):
        try:
            with open(state_path, "r", encoding="utf-8") as fh:
                inferred_origin = collect_blobs.infer_origin_from_state(json.load(fh))
        except Exception:
            pass
    blob_dir = collect_blobs.resolve_blob_dir(explicit, inferred_origin, config)
    if not blob_dir or not os.path.isdir(blob_dir):
        return "FAIL", f"未找到 IndexedDB blob 目录（origin={inferred_origin or '未指定'}）"
    total = 0
    recent = 0
    cutoff = time.time() - 3600
    for dirpath, _dirs, files in os.walk(blob_dir):
        for name in files:
            total += 1
            try:
                if os.path.getmtime(os.path.join(dirpath, name)) >= cutoff:
                    recent += 1
            except OSError:
                pass
    return "OK", f"{blob_dir}（共 {total} 项，近 60min {recent} 项）"


def check_ffmpeg():
    """检查 ffmpeg / ffprobe 与核心滤镜可用性，并判定字幕渲染路线。"""
    ffmpeg_bin = shutil.which("ffmpeg")
    ffprobe_bin = shutil.which("ffprobe")
    if not ffmpeg_bin or not ffprobe_bin:
        return "FAIL", f"缺少可执行文件（ffmpeg={ffmpeg_bin}, ffprobe={ffprobe_bin}）"
    proc = sp.run([ffmpeg_bin, "-hide_banner", "-filters"], capture_output=True, text=True)
    if proc.returncode != 0:
        return "FAIL", f"ffmpeg -filters 执行失败：{proc.stderr.strip()}"
    filters_out = proc.stdout
    required = ["select", "silencedetect", "volumedetect", "volume", "atempo", "setpts", "alimiter"]
    missing = [f for f in required if f" {f} " not in filters_out]
    if missing:
        return "FAIL", f"ffmpeg 缺少核心滤镜：{', '.join(missing)}"
    has_libass = " subtitles " in filters_out
    has_drawtext = " drawtext " in filters_out
    sub_route = "可用 libass（subtitles= 滤镜优先）" if has_libass else "无 libass → 降级 PIL 透明 PNG overlay"
    return "OK", f"核心滤镜齐全；libass={'有' if has_libass else '无'}，drawtext={'有' if has_drawtext else '无'} → {sub_route}"


def check_python_deps():
    """检查 numpy 与 Pillow 依赖。"""
    missing = []
    versions = []
    for mod_name, pkg_name in (("numpy", "numpy"), ("PIL", "Pillow")):
        try:
            mod = __import__(mod_name)
            versions.append(f"{pkg_name} {getattr(mod, '__version__', 'OK')}")
        except ImportError:
            missing.append(pkg_name)
    if missing:
        return "FAIL", f"缺少 Python 依赖：{', '.join(missing)}（运行 pip install -r requirements.txt）"
    return "OK", " / ".join(versions)


def check_config_and_font(config_path: str):
    """检查 config.json 与可用中文字体。"""
    cfg_note = "未提供 config.json（将使用命令行/环境变量/自动探测）"
    if config_path and os.path.isfile(config_path):
        cfg_note = f"已加载 {config_path}"
    else:
        for cand in (
            os.path.join(os.getcwd(), "config.json"),
            os.path.join(os.path.dirname(SCRIPT_DIR), "config.json"),
        ):
            if os.path.isfile(cand):
                cfg_note = f"已加载 {cand}"
                break

    found_font = next((p for p in FONT_CANDIDATES if os.path.isfile(p)), "")
    if found_font:
        return "OK", f"{cfg_note}；中文字体：{found_font}"
    return "WARN", f"{cfg_note}；未探测到常见中文字体（contact_sheet.py 请显式传 --font）"


def main():
    ap = argparse.ArgumentParser(description="短剧流水线开工前环境自检")
    ap.add_argument("--config", default="", help="可选 config.json 路径")
    ap.add_argument("--blob-dir", default="", help="可选显式 blob 目录")
    ap.add_argument("--origin", default="", help="可选画布域名过滤词")
    ap.add_argument("--state", default="", help="可选 canvas_get_state 落盘 JSON 路径")
    args = ap.parse_args()

    config = collect_blobs.load_config(args.config)
    checks = [
        ("1/6", "MCP 配置", check_mcp_config()),
        ("2/6", "画布快照", check_canvas_state(args.state)),
        ("3/6", "blob 目录", check_blob_dir(args.blob_dir, args.origin, config, args.state)),
        ("4/6", "ffmpeg 能力", check_ffmpeg()),
        ("5/6", "Python 依赖", check_python_deps()),
        ("6/6", "配置与字体", check_config_and_font(args.config)),
    ]

    failed = 0
    for idx, label, (status, detail) in checks:
        print(f"[{idx}] {pad_display(label, 12)}  {status:<4}  {detail}")
        if status == "FAIL":
            failed += 1

    if failed:
        print(f"\n自检未通过：{failed} 项失败，请先修复后再开工。", file=sys.stderr)
        sys.exit(1)
    print("\n自检通过：本地环境就绪。")


if __name__ == "__main__":
    main()
