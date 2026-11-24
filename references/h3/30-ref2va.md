## 13. Ref2VA：全参考模式

Ref2VA 不使用 Base 三段式，而使用六段式：

```text
subject_definitions:
...

summary:
...

retention_analysis:
...

detailed_description:
...

overall_soundscape:
...

non_diegetic_music:
...
```

所有重写字段使用英文；仅对白、歌词和真正可见的文字保留原语言。

## 13.1 四类标签

### `<Subject N>`

代表可复用的可见内容：

- 人物、动物、物体
- 场景和环境
- 服装、道具、界面、特效
- 风格、动作、表情或姿势

它描述“要追踪的内容单元”，不等同于源文件。

```text
<Subject 1> is the young woman in <Picture 1>, with long dark hair, a blue cardigan, and a thin silver necklace.
```

### `<Picture N>`

只有当图片本身承担具体帧锚点、构图锚点或分镜参考时，才单独定义 `<Picture N>`。

若图片只提供人物身份，不要多建 Picture 条目；在对应 `<Subject N>` 中引用图片即可。

### `<Video N>`

用于整个视频级关系：

- 编辑原视频
- 从原视频结尾继续
- 参考运镜、切点、节奏或时间结构

视频中的人物、道具和场景仍然应抽象为 `<Subject N>`，不能让 `<Video N>` 代替主体标签。

### `<Audio N>`

用于独立音频或启用的参考视频音轨：

- 完整或部分复制音频
- 参考音乐风格
- 参考音色和演绎
- 参考台词、歌词、音效
- 参考节拍、韵律或音频连续性

图片、视频和音频的编号分别独立，不表示彼此天然配对。

## 13.2 `subject_definitions`

每个需要追踪的主体单独一行，说明：

- 它是什么；
- 来自哪个素材；
- 该素材承担什么角色；
- 哪些特征需要保留。

不要在这里写剧情时间轴。

## 13.3 `summary`

用一个短英文段落总结目标视频和参考关系，并以任务类型开头：

```text
[reference generation] ...
[video continuation + keyframe completion] ...
[video editing + audio reuse] ...
```

官方任务关系包括：

| 类型 | 含义 |
|---|---|
| `keyframe completion` | 图片是首帧、关键帧、尾帧或编辑帧锚点 |
| `reference generation` | 素材只提供角色、场景、风格、动作、镜头等指导 |
| `video editing` | 直接编辑现有视频 |
| `video continuation` | 从现有视频继续、延长或衔接 |
| `audio reuse` | 直接复用全部或部分音频信号 |
| `audio reference` | 只参考音色、节奏、风格、内容或质感，不复制原信号 |

素材存在不等于自动产生任务类型。参考视频只提供运镜时，通常属于 `reference generation`，不是 `video editing`。

## 13.4 `retention_analysis`

### 视觉关系标记

| 标记 | 含义 |
|---|---|
| `fully_preserved` | 定义的参考角色完全保留 |
| `partially_preserved` | 仍使用参考，但部分特征改变或仅部分保留 |
| `attribute_transfer` | 把参考属性转移给另一个可识别主体 |
| `weak_reference` | 只保留宽泛风格、类别、构图或气氛 |

### 音频关系标记

| 标记 | 含义 |
|---|---|
| `fully_copy` | 源音频完整成为目标最终音轨 |
| `partially_copy` | 只复制部分时间或部分声音层，或复制后发生增删改 |
| `reference` | 只参考音色、节奏、音乐风格、台词内容或声音质感 |
| `weak_reference` | 只保留宽泛类别或气氛 |

每个标签一行，不要改变其在 `subject_definitions` 中已经定义的含义。

## 13.5 `detailed_description`

这是 Ref2VA 的主时间轴。与 Base 的差异：

- Base 主字段是 `integrated_multimodal_description`；Ref2VA 是 `detailed_description`。
- Ref2VA 先用 1–2 句英文定义总体风格，再进入 `[Shot 1]`。
- 每个参考主体首次清晰出现时，说明其位置、外观和当前动作。
- 在参考关系实际生效的时间段自然引用 `<Picture N>`、`<Video N>`、`<Audio N>`。

生成类任务通常可写约 350–500 个英文单词；对白密集任务优先满足完整时间轴，不必机械凑字数。这个范围来自官方 Ref Guide，不是所有简单编辑任务的硬要求。

## 13.6 参考关系冲突处理

当多张图或视频相互冲突时，先指定职责：

```text
<Picture 1> defines face and hairstyle.
<Picture 2> defines wardrobe and body proportions.
<Video 1> provides walking motion and camera rhythm only.
```

不要写“综合所有参考”后让模型自行决定，因为模型可能平均化脸型、混合服装或复制错误背景。

---

