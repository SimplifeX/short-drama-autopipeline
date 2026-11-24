#!/usr/bin/env python3
"""角色资产表（characters.json）最小硬校验脚本。

当运行环境未安装外部技能 `baige-duanju-juese` 时，作为 Stage 1 验收门的内置校验工具：
  1. 校验角色八项字段齐全（支持英文 key 或中文 key）
  2. 校验姓名非空且不重名
  3. 校验 consistency_locks（一致性锁定项）数量为 2-4 条，每条独立成句
  4. 可选校验结构化声线字段 voice_anchor（非空字符串）与 voice_ref_hz（[min, max] 区间）

用法:
  python3 character_check.py characters.json
  python3 character_check.py characters.json --require-voice
"""
import argparse
import json
import sys

# 八项必填字段及兼容别名（支持标准英文键或中文键）
REQUIRED_FIELDS = [
    ("name", ("name", "姓名")),
    ("identity", ("identity", "role", "身份")),
    ("appearance", ("appearance", "外貌")),
    ("costume", ("costume", "clothing", "outfit", "服装")),
    ("signature_items", ("signature_items", "props", "标志性物品")),
    ("personality", ("personality", "性格")),
    ("variants", ("variants", "变体")),
    ("consistency_locks", ("consistency_locks", "locks", "一致性锁定项")),
]


def get_field(char: dict, aliases: tuple):
    """按别名顺序读取字段值。"""
    for key in aliases:
        if key in char:
            return char[key]
    return None


def is_empty(val) -> bool:
    """判断字段值是否为空。"""
    if val is None:
        return True
    if isinstance(val, str):
        return len(val.strip()) == 0
    if isinstance(val, (list, dict)):
        return len(val) == 0
    return False


def validate_characters(data, require_voice: bool = False):
    """执行角色资产表硬校验，返回 (errors, warnings)。"""
    errors = []
    warnings = []

    if isinstance(data, dict):
        chars = data.get("characters")
        if not isinstance(chars, list):
            return ["顶层对象必须包含列表字段 'characters'（或顶层直接为角色数组）"], []
    elif isinstance(data, list):
        chars = data
    else:
        return ["characters.json 顶层必须为角色数组或含 'characters' 数组的对象"], []

    if not chars:
        return ["角色列表为空，至少需要 1 个角色"], []

    seen_names = set()
    for i, char in enumerate(chars):
        tag = f"角色#{i + 1}"
        if not isinstance(char, dict):
            errors.append(f"{tag} 不是有效的 JSON 对象")
            continue

        # 1. 姓名唯一与非空
        name = get_field(char, ("name", "姓名"))
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{tag} 缺少有效的姓名（name / 姓名）")
        else:
            clean_name = name.strip()
            tag = f"角色[{clean_name}]"
            if clean_name in seen_names:
                errors.append(f"{tag} 重名")
            seen_names.add(clean_name)

        # 2. 八项字段齐全（variants 允许显式写 "无" 或 []，但字段本身必须存在）
        for canonical, aliases in REQUIRED_FIELDS:
            val = get_field(char, aliases)
            if val is None:
                errors.append(f"{tag} 缺少必填字段 {canonical}（可用键：{', '.join(aliases)}）")
            elif canonical != "variants" and is_empty(val):
                errors.append(f"{tag} 字段 {canonical} 不能为空")

        # 3. 一致性锁定项（2-4 条，独立成句）
        locks = get_field(char, ("consistency_locks", "locks", "一致性锁定项"))
        if isinstance(locks, list):
            if not (2 <= len(locks) <= 4):
                errors.append(f"{tag} consistency_locks 数量应为 2–4 条，当前为 {len(locks)} 条")
            for idx_l, lock in enumerate(locks, start=1):
                if not isinstance(lock, str) or not lock.strip():
                    errors.append(f"{tag} 第 {idx_l} 条锁定项为空")
                    continue
                s = lock.strip()
                if len(s) <= 6 or s.endswith((",", "，")):
                    warnings.append(
                        f"{tag} 第 {idx_l} 条锁定项建议独立成句（当前长度 {len(s)}：'{s}'）"
                    )
        elif locks is not None:
            errors.append(f"{tag} consistency_locks 必须为字符串数组")

        # 4. 结构化声线锚校验（P3-1：防止跨镜手写漂移）
        voice_anchor = char.get("voice_anchor")
        voice_ref_hz = char.get("voice_ref_hz")
        if require_voice and (not isinstance(voice_anchor, str) or not voice_anchor.strip()):
            errors.append(f"{tag} 启用 --require-voice 时必须提供非空 voice_anchor")
        if voice_anchor is not None and (not isinstance(voice_anchor, str) or not voice_anchor.strip()):
            errors.append(f"{tag} voice_anchor 必须为非空字符串")
        if voice_ref_hz is not None:
            if (
                not isinstance(voice_ref_hz, list)
                or len(voice_ref_hz) != 2
                or not all(isinstance(v, (int, float)) for v in voice_ref_hz)
                or voice_ref_hz[0] <= 0
                or voice_ref_hz[0] >= voice_ref_hz[1]
            ):
                errors.append(f"{tag} voice_ref_hz 格式无效，应为 [min_hz, max_hz] 且 0 < min < max")

    return errors, warnings


def main():
    ap = argparse.ArgumentParser(description="Stage 1 characters.json 最小硬校验工具")
    ap.add_argument("path", help="characters.json 路径")
    ap.add_argument("--require-voice", action="store_true", help="强制校验每个角色都配置了 voice_anchor")
    args = ap.parse_args()

    try:
        with open(args.path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:
        raise SystemExit(f"读取 JSON 失败：{exc}")

    errors, warnings = validate_characters(data, require_voice=args.require_voice)
    for w in warnings:
        print(f"[WARN] {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"[FAIL] {e}", file=sys.stderr)
        sys.exit(1)

    count = len(data["characters"]) if isinstance(data, dict) else len(data)
    print(f"[OK] 角色校验通过（共 {count} 名角色，{len(warnings)} 条提示）")


if __name__ == "__main__":
    main()
