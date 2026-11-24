#!/usr/bin/env python3
"""音高（F0）检测：角色跨镜声线一致性验收。

自相关法测中位 F0，跳过静音段，并加入半频错判修正（octave error correction）与多说话人离散度判别。
H3 同一角色跨镜浮动 ±30Hz 内算同声线；判偏高/偏低前先量参考片原声。

局限说明:
  - 离散度判别可有效识别「双人交替说话」或大幅音高跳变；
  - 若两人「同时叠加说话」，自相关会锁定能量强势的一方，离散度判别可能失效，需配合人工抽听或分轨校验。

用法:
  python3 f0_check.py a_s1.wav                              # 整段
  python3 f0_check.py shot.mp4 --start 3.5 --end 8          # 视频自动抽音轨并精确截取
  python3 f0_check.py shot.mp4 --characters characters.json --role 老周  # 自动对照 voice_ref_hz

退出码:
  0: 检测成功（若指定角色区间且命中区间）
  1: 声线超出目标 voice_ref_hz 区间或参数错误
  2: 无法测出有效基频（静音或纯噪声）
"""
import argparse
import json
import subprocess as sp
import sys

import numpy as np


def _load_wav_native(path: str, start=None, end=None, sr: int = 16000):
    """标准库直读 WAV（8/16/32bit PCM），样本级 seek 并重采样到 16kHz 单声道。

    返回 float64 数组；不是 WAV 或格式不受支持时返回 None，交由 ffmpeg 处理。
    """
    import wave

    if not path.lower().endswith((".wav", ".wave")):
        return None
    try:
        with wave.open(path, "rb") as wf:
            nch = wf.getnchannels()
            sw = wf.getsampwidth()
            fr = wf.getframerate()
            total = wf.getnframes()
            i0 = max(0, int((start or 0.0) * fr))
            i1 = total if end is None else min(total, int(end * fr))
            if i1 <= i0:
                return None
            wf.setpos(i0)
            raw = wf.readframes(i1 - i0)
    except Exception:
        return None
    if not raw:
        return None

    if sw == 1:
        data = (np.frombuffer(raw, dtype=np.uint8).astype(np.float64) - 128.0) / 128.0
    elif sw == 2:
        data = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    elif sw == 4:
        data = np.frombuffer(raw, dtype=np.int32).astype(np.float64) / 2147483648.0
    else:
        return None

    if nch > 1:
        data = data.reshape(-1, nch).mean(axis=1)

    if fr != sr and len(data) > 1:
        n_out = int(round(len(data) * sr / fr))
        data = np.interp(
            np.linspace(0, len(data) - 1, n_out, dtype=np.float64),
            np.arange(len(data), dtype=np.float64),
            data,
        )
    return data.astype(np.float64)


def load_audio(path: str, start=None, end=None) -> np.ndarray:
    """抽取 16kHz 单声道 PCM 浮点数组：WAV 走标准库，其余格式交给 ffmpeg。"""
    if start is not None and end is not None and end <= start:
        raise SystemExit(f"错误：--end ({end}) 必须大于 --start ({start})")

    if path.lower().endswith((".wav", ".wave")):
        native = _load_wav_native(path, start, end)
        if native is not None and len(native) > 0:
            return native

    cmd = ["ffmpeg", "-v", "error"]
    if start is not None:
        # -ss 置于 -i 前执行快速输入端 seek；此时输出时间戳归零，end 需换算为持续时长 -t
        cmd += ["-ss", str(start)]
    cmd += ["-i", path]
    if end is not None:
        if start is not None:
            cmd += ["-t", str(end - start)]
        else:
            cmd += ["-to", str(end)]
    cmd += ["-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"]

    try:
        proc = sp.run(cmd, capture_output=True)
    except FileNotFoundError:
        raise SystemExit(
            "错误：未找到 ffmpeg。仅 .wav 输入可在无 ffmpeg 环境运行；"
            "视频/其他音频请先安装 ffmpeg（preflight.py 会提前检测）。"
        )
    if proc.returncode != 0:
        raise SystemExit(f"ffmpeg 抽音轨失败：{proc.stderr.decode('utf-8', errors='ignore').strip()}")
    return np.frombuffer(proc.stdout, dtype=np.int16).astype(np.float64) / 32768.0


def estimate_f0(x: np.ndarray, min_hz: float = 60.0, max_hz: float = 1000.0):
    """计算中位基频（Hz）以及有声帧中的有效基频帧占比。"""
    n, hop, sr = 1024, 256, 16000
    lo = max(1, int(sr / max_hz))
    hi = min(n - 1, int(sr / min_hz))
    voiced_frames = 0
    res = []

    for i in range(0, max(1, len(x) - n), hop):
        f = x[i:i + n]
        if len(f) < n:
            break
        if np.sqrt((f ** 2).mean()) < 0.012:  # 跳过静音帧
            continue
        voiced_frames += 1
        f = f - f.mean()
        ac = np.correlate(f, f, "full")[n - 1:]
        ac /= (ac[0] + 1e-9)

        k = int(np.argmax(ac[lo:hi])) + lo
        if ac[k] <= 0.3:
            continue

        # 半频错判（octave error）修正：若滞后 k/2（即 2 倍频）处局部峰值接近 ac[k]，取真实基频
        half_k = k // 2
        if half_k >= lo:
            win_lo = max(lo, half_k - 2)
            win_hi = min(hi, half_k + 3)
            k2 = int(np.argmax(ac[win_lo:win_hi])) + win_lo
            if ac[k2] >= 0.85 * ac[k]:
                k = k2

        res.append(sr / k)

    valid_ratio = (len(res) / voiced_frames) if voiced_frames > 0 else 0.0
    if res:
        med = float(np.median(res))
        median_hz = round(med, 1)
        outlier_ratio = sum(1 for v in res if abs(v - med) / med > 0.15) / len(res)
    else:
        median_hz = 0.0
        outlier_ratio = 0.0
    return median_hz, valid_ratio, len(res), voiced_frames, outlier_ratio


def lookup_role_range(characters_path: str, role_name: str):
    """从 characters.json 读取指定角色的 voice_ref_hz 区间。"""
    with open(characters_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    chars = data.get("characters", []) if isinstance(data, dict) else data
    for c in chars:
        cname = c.get("name") or c.get("姓名") or ""
        if cname == role_name:
            ref = c.get("voice_ref_hz")
            if isinstance(ref, list) and len(ref) == 2:
                return float(ref[0]), float(ref[1])
            raise SystemExit(f"错误：角色 [{role_name}] 未配置 voice_ref_hz")
    raise SystemExit(f"错误：在 {characters_path} 中未找到角色 [{role_name}]")


def main():
    ap = argparse.ArgumentParser(description="人声基频（F0）检测与角色声线区间验收")
    ap.add_argument("path", help="音频或视频文件路径")
    ap.add_argument("--start", type=float, help="起始时间（秒）")
    ap.add_argument("--end", type=float, help="结束时间（秒）")
    ap.add_argument("--min-hz", type=float, default=60.0, help="最低检测频率（默认 60Hz）")
    ap.add_argument("--max-hz", type=float, default=1000.0, help="最高检测频率（默认 1000Hz，覆盖高女声/童声）")
    ap.add_argument("--characters", help="可选 characters.json 路径，配合 --role 自动校验 voice_ref_hz")
    ap.add_argument("--role", help="角色名称（与 --characters 搭配）")
    args = ap.parse_args()

    x = load_audio(args.path, args.start, args.end)
    hz, valid_ratio, valid_n, voiced_n, outlier_ratio = estimate_f0(x, min_hz=args.min_hz, max_hz=args.max_hz)

    print(hz)
    if hz <= 0.0:
        print("错误：未检测到有效人声基频（全静音或强噪声）。", file=sys.stderr)
        sys.exit(2)

    if voiced_n > 0 and valid_ratio < 0.30:
        print(
            f"提示：有效基频帧占比偏低（{valid_ratio:.0%}，{valid_n}/{voiced_n}），"
            "该镜可能存在背景噪声或音乐干扰，结果仅供参考。",
            file=sys.stderr,
        )

    if outlier_ratio > 0.30:
        print(
            f"提示：{outlier_ratio:.0%} 的有效帧偏离中位基频 >15%，"
            "疑似多说话人交替串音或音高剧烈跳变，单角色判定不可信。",
            file=sys.stderr,
        )

    if args.characters and args.role:
        lo_hz, hi_hz = lookup_role_range(args.characters, args.role)
        if not (lo_hz <= hz <= hi_hz):
            print(
                f"警告：角色 [{args.role}] 实测 {hz}Hz 超出基准区间 [{lo_hz}, {hi_hz}]Hz。",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"[OK] 角色 [{args.role}] 实测 {hz}Hz 位于基准区间 [{lo_hz}, {hi_hz}]Hz 内。", file=sys.stderr)


if __name__ == "__main__":
    main()
