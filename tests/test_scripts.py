#!/usr/bin/env python3
"""short-drama-autopipeline 脚本自动化回归测试套件。

兼容标准库 unittest 与 pytest：
  python3 -m unittest discover -s tests -v
  pytest -v
"""
import hashlib
import json
import os
import shutil
import subprocess as sp
import sys
import tempfile
import time
import unittest
import wave

import numpy as np
from PIL import Image

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_ROOT, "scripts")


def md5_file(path: str) -> str:
    """计算文件 MD5 哈希。"""
    h = hashlib.md5()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def run_script(name: str, args: list) -> sp.CompletedProcess:
    """调用 scripts 目录下的指定 Python 脚本。"""
    cmd = [sys.executable, os.path.join(SCRIPTS_DIR, name)] + args
    return sp.run(cmd, capture_output=True, text=True)


def write_wav(path: str, segments: list, sr: int = 16000):
    """合成测试用 16kHz 单声道 WAV（含二次/三次谐波模拟真实人声）。"""
    chunks = []
    for dur, freq in segments:
        t = np.arange(int(sr * dur)) / sr
        if freq <= 0:
            sig = np.zeros_like(t)
        else:
            sig = (
                0.50 * np.sin(2 * np.pi * freq * t)
                + 0.25 * np.sin(2 * np.pi * 2 * freq * t)
                + 0.10 * np.sin(2 * np.pi * 3 * freq * t)
            )
        chunks.append(sig)
    y = np.concatenate(chunks)
    pcm = np.clip(y * 32767, -32768, 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


class TestCollectBlobs(unittest.TestCase):
    """覆盖 N1（共享 storageKey 副本防串图）与 N7 / P0 回归测试。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="sd_collect_")
        self.blob_dir = os.path.join(self.tmp, "blobs")
        os.makedirs(os.path.join(self.blob_dir, "nested", "1"), exist_ok=True)
        self.png_head = b"\x89PNG\r\n\x1a\n"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_blob(self, rel_name: str, fill_byte: bytes, body_len: int, mtime_offset: float = 0.0) -> str:
        path = os.path.join(self.blob_dir, "nested", "1", rel_name)
        with open(path, "wb") as fh:
            fh.write(self.png_head + fill_byte * body_len)
        if mtime_offset:
            t = time.time() + mtime_offset
            os.utime(path, (t, t))
        return path

    def test_shared_storage_key_single_blob(self):
        """回归 1：画布扇出副本共享同一 storageKey 且本地仅一份 blob，应全部收回且 md5 一致。"""
        b1 = self._write_blob("only_one", b"R", 1000)
        sz = os.path.getsize(b1)
        state = os.path.join(self.tmp, "state.json")
        with open(state, "w", encoding="utf-8") as fh:
            json.dump({
                "nodes": [
                    {"id": "n1", "type": "image", "title": "A_原图", "metadata": {"images": [{"storageKey": "image:k1", "bytes": sz}]}},
                    {"id": "n2", "type": "image", "title": "A_副本", "metadata": {"images": [{"storageKey": "image:k1", "bytes": sz}]}},
                ],
                "connections": [],
            }, fh)
        out = os.path.join(self.tmp, "out")
        res = run_script("collect_blobs.py", ["--state", state, "--out", out, "--blob-dir", self.blob_dir])
        self.assertEqual(res.returncode, 0, res.stderr)
        with open(os.path.join(out, "manifest.json"), encoding="utf-8") as fh:
            manifest = json.load(fh)
        self.assertEqual(len(manifest), 2)
        self.assertEqual(md5_file(manifest[0]["file"]), md5_file(manifest[1]["file"]))

    def test_shared_key_plus_same_size_distinct_key(self):
        """回归 2（N1 复现场景）：同尺寸红/绿两份 blob，n1/n2 共享 k1，n3 用 k3，不串图且全收。"""
        red = self._write_blob("red", b"R", 1000, mtime_offset=-10)
        green = self._write_blob("green", b"G", 1000, mtime_offset=-20)
        sz = os.path.getsize(red)
        self.assertEqual(sz, os.path.getsize(green))

        state = os.path.join(self.tmp, "state.json")
        with open(state, "w", encoding="utf-8") as fh:
            json.dump({
                "nodes": [
                    {"id": "n1", "type": "image", "title": "A_原图", "metadata": {"images": [{"storageKey": "image:k1", "bytes": sz}]}},
                    {"id": "n2", "type": "image", "title": "A_副本", "metadata": {"images": [{"storageKey": "image:k1", "bytes": sz}]}},
                    {"id": "n3", "type": "image", "title": "B_另一张", "metadata": {"images": [{"storageKey": "image:k3", "bytes": sz}]}},
                ],
                "connections": [],
            }, fh)
        out = os.path.join(self.tmp, "out")
        res = run_script("collect_blobs.py", ["--state", state, "--out", out, "--blob-dir", self.blob_dir])
        self.assertEqual(res.returncode, 0, res.stderr)
        with open(os.path.join(out, "manifest.json"), encoding="utf-8") as fh:
            manifest = json.load(fh)
        self.assertEqual(len(manifest), 3)
        by_node = {m["node"]: md5_file(m["file"]) for m in manifest}
        self.assertEqual(by_node["n1"], by_node["n2"])
        self.assertNotEqual(by_node["n1"], by_node["n3"])

    def test_missing_blob_and_minutes_diagnosis(self):
        """回归 3：真缺片返回 exit 1；时间窗漏收输出窗外诊断；--min-bytes 显式打印过滤提示且 exit 0。"""
        old_big = self._write_blob("old_big", b"X", 250000, mtime_offset=-7200)
        small = self._write_blob("small", b"S", 1000, mtime_offset=-10)
        big_sz = os.path.getsize(old_big)
        small_sz = os.path.getsize(small)

        # 3a. 时间窗漏收诊断
        state_time = os.path.join(self.tmp, "state_time.json")
        with open(state_time, "w", encoding="utf-8") as fh:
            json.dump({
                "nodes": [{"id": "n1", "type": "image", "title": "旧图", "metadata": {"images": [{"storageKey": "image:old", "bytes": big_sz}]}}],
                "connections": [],
            }, fh)
        res = run_script("collect_blobs.py", ["--state", state_time, "--out", os.path.join(self.tmp, "out_t"), "--blob-dir", self.blob_dir, "--minutes", "60"])
        self.assertEqual(res.returncode, 1)
        self.assertIn("时间窗", res.stderr)

        # 3b. --min-bytes 过滤小图并显式提示
        state_min = os.path.join(self.tmp, "state_min.json")
        with open(state_min, "w", encoding="utf-8") as fh:
            json.dump({
                "nodes": [
                    {"id": "n1", "type": "image", "title": "大图", "metadata": {"images": [{"storageKey": "image:big", "bytes": big_sz}]}},
                    {"id": "n2", "type": "image", "title": "小图", "metadata": {"images": [{"storageKey": "image:sml", "bytes": small_sz}]}},
                ],
                "connections": [],
            }, fh)
        res = run_script("collect_blobs.py", ["--state", state_min, "--out", os.path.join(self.tmp, "out_m"), "--blob-dir", self.blob_dir, "--min-bytes", "200000"])
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("过滤跳过 1 项", res.stderr)

        # 3c. 真缺片返回 exit 1
        state_miss = os.path.join(self.tmp, "state_miss.json")
        with open(state_miss, "w", encoding="utf-8") as fh:
            json.dump({
                "nodes": [{"id": "n1", "type": "image", "title": "不存在", "metadata": {"images": [{"storageKey": "image:miss", "bytes": 999999}]}}],
                "connections": [],
            }, fh)
        res = run_script("collect_blobs.py", ["--state", state_miss, "--out", os.path.join(self.tmp, "out_x"), "--blob-dir", self.blob_dir])
        self.assertEqual(res.returncode, 1)


class TestF0Check(unittest.TestCase):
    """覆盖 P3-3 精度、输入端 seek、N6 多说话人离散度判别与角色闭环验收。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="sd_f0_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_single_speaker_precision_and_no_false_alarm(self):
        for freq in (120.0, 254.0, 380.0, 520.0):
            wp = os.path.join(self.tmp, f"s_{int(freq)}.wav")
            write_wav(wp, [(1.0, freq)])
            res = run_script("f0_check.py", [wp])
            self.assertEqual(res.returncode, 0, res.stderr)
            val = float(res.stdout.strip())
            self.assertLessEqual(abs(val - freq), 5.0, f"freq={freq}, got={val}")
            self.assertNotIn("疑似多说话人", res.stderr)

    def test_natural_intonation_not_flagged(self):
        """单人正常语调起伏（110/130/115Hz）不应误触发多说话人警告。"""
        wp = os.path.join(self.tmp, "intonation.wav")
        write_wav(wp, [(0.4, 110.0), (0.4, 130.0), (0.4, 115.0)])
        res = run_script("f0_check.py", [wp])
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertNotIn("疑似多说话人", res.stderr)

    def test_dual_speaker_alternating_flagged(self):
        """N6：双人交替（120Hz / 380Hz）应触发多说话人离散度警告。"""
        wp = os.path.join(self.tmp, "dual.wav")
        write_wav(wp, [(0.6, 120.0), (0.6, 380.0)])
        res = run_script("f0_check.py", [wp])
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("疑似多说话人", res.stderr)

    def test_seek_and_silence_exit_2(self):
        wp = os.path.join(self.tmp, "mix.wav")
        write_wav(wp, [(1.0, 120.0), (1.0, 254.0), (1.0, 120.0)])
        res = run_script("f0_check.py", [wp, "--start", "1.1", "--end", "1.9"])
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertLessEqual(abs(float(res.stdout.strip()) - 254.0), 5.0)

        sil = os.path.join(self.tmp, "sil.wav")
        write_wav(sil, [(1.0, 0.0)])
        res_sil = run_script("f0_check.py", [sil])
        self.assertEqual(res_sil.returncode, 2)
        self.assertEqual(res_sil.stdout.strip(), "0.0")


class TestCharacterAndContactSheet(unittest.TestCase):
    """覆盖 character_check.py 与 contact_sheet.py（含 N9 边界校验）。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="sd_misc_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_character_check(self):
        good = os.path.join(self.tmp, "good.json")
        with open(good, "w", encoding="utf-8") as fh:
            json.dump({"characters": [{
                "name": "老周", "identity": "网约车司机", "appearance": "四十多岁蓄黑短胡",
                "costume": "深蓝工装夹克", "signature_items": ["黑色对讲机"], "personality": "嘴碎热心",
                "variants": [], "consistency_locks": ["四十岁出头偏瘦脸型蓄短黑胡茬。", "深蓝褪色工装夹克左胸带反光条。"],
                "voice_anchor": "deep resonant chest voice", "voice_ref_hz": [110, 140],
            }]}, fh, ensure_ascii=False)
        self.assertEqual(run_script("character_check.py", [good, "--require-voice"]).returncode, 0)

        bad = os.path.join(self.tmp, "bad.json")
        with open(bad, "w", encoding="utf-8") as fh:
            json.dump({"characters": [{"name": "缺字段", "voice_ref_hz": [200, 100]}]}, fh, ensure_ascii=False)
        self.assertEqual(run_script("character_check.py", [bad]).returncode, 1)

    def test_contact_sheet_labels_and_cols_guard(self):
        img = os.path.join(self.tmp, "镜01_监控体.png")
        Image.new("RGB", (320, 180), (30, 60, 90)).save(img)
        out = os.path.join(self.tmp, "sheet.png")
        res = run_script("contact_sheet.py", ["--files", img, "--labels", "标签一,多余标签", "--cols", "1", "--out", out])
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("多余标签将被忽略", res.stderr)
        self.assertTrue(os.path.isfile(out))

        res_bad = run_script("contact_sheet.py", ["--files", img, "--cols", "0", "--out", out])
        self.assertNotEqual(res_bad.returncode, 0)


if __name__ == "__main__":
    unittest.main()
