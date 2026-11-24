# Stage 6：收片装配与验收

## 装配前硬断言（尺寸一致性）

不同通道默认分辨率不同（例如 `fl2va` 直连默认 `1344×768`，而画布出片常见 `1248×704` 或 `704×1248`）。装配脚本入口必须先用 `ffprobe` 校验全部分镜分辨率一致，不一致立刻报错或先显式归一化，禁止直接拼接：

```python
import subprocess as sp

def ffprobe_size(path: str) -> str:
    return sp.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", path],
        text=True,
    ).strip()

sizes = {ffprobe_size(p) for p in shots}
assert len(sizes) == 1, f"分镜尺寸不一致，请先归一化：{sizes}"
```

## 装配流水（ffmpeg + 自适应字幕路线）

根据 `scripts/preflight.py` 的 `[4/6] ffmpeg 能力` 探测结果选择字幕路线：**环境有 `libass` 时优先走 `subtitles=` 滤镜（更快更准），无 `libass` 时降级为 PIL 渲染透明 PNG → `overlay`**。

1. **量停顿点**：`ffmpeg -i shot.mp4 -af "silencedetect=noise=-32dB:d=0.2" -f null -` 提取每镜台词间静默，字幕按实测停顿落位（不是按比例估）。有台词的镜头先语音转写校对文本与时间。
2. **字幕渲染**：
   - 有 `libass`：生成 ASS/SRT 字幕，走 ffmpeg `subtitles=` 滤镜。
   - 无 `libass`：PIL 画白字黑边（`stroke_width`），底部安全区；`overlay` 用 `enable='between(t,a,b)'`。
3. **逐镜电平补正**：H3 各镜自带音量不齐（实测差 5–6dB）。`volumedetect` 逐镜量均值，按差值设 `GAINS` 字典逐镜 `volume=XdB`，再全局 `volume=12dB,alimiter=0.95`。目标：全片均值对齐参考片（`volumedetect` 对照），分段差 ≤1dB。
4. **时长压缩**（H3 17k+5 帧网格取整导致每镜多 0.2–1s）：两步——切每镜首尾死气口（留 0.1–0.15s 呼吸）+ 全片匀速提速（`setpts=0.9*PTS` + `atempo=1.1`，音高不变）。提速比例由「逐镜时长 vs 参考片逐镜时长」回归得出。字幕时间轴跟着提速重排。
5. **切镜**（可选）：`哔声 + 彩色无信号`（7 帧）用于主切点、白闪（3 帧）用于字卡前后；插帧段雪花声用带通噪声 + 20ms 淡入出，电平压到 −25dB 左右防削波。

## 监控体裁专用规格（古早监控）

- 30 秒上下、单机位、6–7 镜、四幕（待机-异常-高潮-收档）、**零旁白**；台词用字幕卡不做配音（口型是最大破绽）。
- 时间戳故意荒诞（前 227 年 / 公元 1026 年），机位名具体到地名（`CAM-01 景阳冈南侧`）。
- 结尾定格 + 档案卡（「该影像已移交 XX 府」）。
- 后期链：`hue=s=0 → eq → gblur → noise → vignette`（「脏」交给后期，模型只出结构）。

## 验收清单（全部通过才算交付）

- [ ] `ffprobe`：时长 = 参考片 ±0.5s；全部分镜分辨率/帧率一致；流含视频+音频
- [ ] 响度：全片均值对齐参考片；分段（每镜）差 ≤1dB；峰值不削波（max ≤ −0.1dB）
- [ ] 声画同步：`silencedetect` 反查静默区间与推算位置偏差 ≤0.2s
- [ ] 联系表（`contact_sheet.py`，每 2–2.5s 一帧）：无黑帧/花屏/畸变；镜头顺序正确
- [ ] 逐镜抽帧检查：角色一致性、双袖/道具入画、无字幕遮挡面部
- [ ] 字卡在片（联系表采样可能跳过短字卡，单独抽帧确认）
- [ ] 每镜声线：`python3 scripts/f0_check.py <shot.mp4> --characters characters.json --role <角色>` 对照 `voice_ref_hz`（H3 浮动 ±30Hz 内算同声线；偏高先量参考片再判）
- [ ] `spec.md`、`characters.json`、`state.json` 完整归档

## 交付

- 成片放 `<项目>/out/`，命名不带版本周期标签（无「最终版/定稿」字样）
- 工程脚本（装配 `build_*.py`）随片保留在 `<项目>/tools/`，可重跑
- 已知软肋（音色偏差、单镜瑕疵）如实写进交付说明，不靠修辞兜
