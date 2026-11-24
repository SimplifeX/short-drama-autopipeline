#!/usr/bin/env python3
"""拼验收联系表：把一组帧图拼成网格 + 标签。

用法:
  python3 contact_sheet.py --dir build/shots --pattern "*.png" --cols 4 --out sheet.jpg
  python3 contact_sheet.py --files "a.png,b.png" --labels "A,B" --cols 3 --out cmp.png --font /path/to/font.ttc

特性:
  - 自动探测跨平台中文字体（也可通过 --font 指定），避免中文标签乱码/方块
  - 使用 Pillow textlength 实测标签宽度，按格宽自动截断加省略号，底框贴合不裁字
  - 根据输出文件扩展名决定是否传入 quality 参数（JPEG/WEBP 生效，PNG 不传无效参数）
"""
import argparse
import glob
import os
import sys

from PIL import Image, ImageDraw, ImageFont

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


def load_font(font_path: str, size: int):
    """加载指定或自动探测的中文字体，失败时回退 Pillow 默认字体。"""
    candidates = [font_path] if font_path else FONT_CANDIDATES
    for path in candidates:
        if path and os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def fit_label(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> str:
    """按像素宽度截断标签，超出时追加省略号。"""
    if draw.textlength(text, font=font) <= max_width:
        return text
    ellipsis = "…"
    ell_w = draw.textlength(ellipsis, font=font)
    out = ""
    for ch in text:
        if draw.textlength(out + ch, font=font) + ell_w > max_width:
            break
        out += ch
    return (out or text[:1]) + ellipsis


def main():
    ap = argparse.ArgumentParser(description="拼接分镜验收联系表")
    ap.add_argument("--dir", help="图片目录")
    ap.add_argument("--pattern", default="*.png", help="目录匹配模式（默认 *.png）")
    ap.add_argument("--files", help="逗号分隔的显式文件列表（优先于 --dir）")
    ap.add_argument("--labels", help="逗号分隔标签，与 --files 对应；缺省用文件名")
    ap.add_argument("--cols", type=int, default=4, help="每行列数")
    ap.add_argument("--cell-w", type=int, default=320, help="单格宽度（像素）")
    ap.add_argument("--font", default="", help="自定义字体文件路径（支持中文 ttf/ttc/otf）")
    ap.add_argument("--font-size", type=int, default=14, help="标签字号（像素）")
    ap.add_argument("--out", required=True, help="输出图片路径")
    ap.add_argument("--quality", type=int, default=85, help="JPEG/WEBP 压缩质量（PNG 忽略）")
    args = ap.parse_args()

    if args.cols < 1:
        raise SystemExit(f"错误：--cols 必须 >= 1（当前：{args.cols}）")
    if args.cell_w < 32:
        raise SystemExit(f"错误：--cell-w 必须 >= 32（当前：{args.cell_w}）")

    if args.files:
        files = [f.strip() for f in args.files.split(",") if f.strip()]
        labels = [l.strip() for l in (args.labels or "").split(",") if l.strip()]
        if len(labels) > len(files):
            print(
                f"警告：--labels 提供了 {len(labels)} 项，多于 --files 的 {len(files)} 项，多余标签将被忽略。",
                file=sys.stderr,
            )
            labels = labels[:len(files)]
        while len(labels) < len(files):
            labels.append(os.path.splitext(os.path.basename(files[len(labels)]))[0])
    else:
        d = args.dir or "."
        files = sorted(glob.glob(os.path.join(d, args.pattern)))
        labels = [os.path.splitext(os.path.basename(f))[0] for f in files]

    if not files:
        raise SystemExit("没有匹配到文件")

    total_w = args.cell_w * args.cols
    if total_w > 4096:
        print(
            f"警告：输出画布宽度较大（{total_w}px = {args.cols} 列 × {args.cell_w}px），"
            "如需降低内存/体积请调小 --cols 或 --cell-w。",
            file=sys.stderr,
        )

    cells = []
    for f, lab in zip(files, labels):
        im = Image.open(f).convert("RGB")
        w = args.cell_w
        h = max(1, int(args.cell_w * im.height / im.width))
        cells.append((im.resize((w, h), Image.Resampling.LANCZOS), lab, w, h))

    ch = max(c[3] for c in cells)
    rows = (len(cells) + args.cols - 1) // args.cols
    sheet = Image.new("RGB", (args.cell_w * args.cols, ch * rows), "black")
    draw = ImageDraw.Draw(sheet)
    font = load_font(args.font, args.font_size)
    pad_x, pad_y = 6, 4

    for i, (im, lab, w, h) in enumerate(cells):
        r, c = divmod(i, args.cols)
        x0, y0 = c * w, r * ch
        sheet.paste(im, (x0, y0))
        fitted = fit_label(draw, lab, font, max_width=max(20, w - pad_x * 2))
        bbox = draw.textbbox((0, 0), fitted, font=font)
        tw = int(bbox[2] - bbox[0])
        th = int(bbox[3] - bbox[1])
        box_w = min(w, tw + pad_x * 2)
        box_h = th + pad_y * 2 + 2
        draw.rectangle([x0, y0, x0 + box_w, y0 + box_h], fill="black")
        draw.text((x0 + pad_x, y0 + pad_y - bbox[1]), fitted, fill="yellow", font=font)

    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    ext = os.path.splitext(args.out)[1].lower()
    if ext in (".jpg", ".jpeg", ".webp"):
        sheet.save(args.out, quality=args.quality)
    else:
        sheet.save(args.out)
    print(f"{len(cells)} 格 -> {args.out}")


if __name__ == "__main__":
    main()
