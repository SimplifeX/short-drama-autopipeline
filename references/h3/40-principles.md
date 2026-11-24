## 14. Prompt 的底层原理

## 14.1 Prompt 是条件图，不是关键词袋

可以把 H3 Prompt 抽象为一个有向图：

```text
节点：人物、物体、场景、镜头、声音、关键帧
边：出现于、来自、保持、移动到、说出、复制、参考、结束于
时间：每条边在何时生效
```

高质量 Prompt 的关键不是节点多，而是边清晰。

例如：

```text
“参考图中的女孩在咖啡馆说话”
```

关系不清晰：参考图提供脸还是构图？咖啡馆来自哪里？谁说话？音色是否参考？

结构化后：

```text
<Subject 1>：女孩身份来自 Picture 1
<Subject 2>：咖啡馆场景来自 Picture 2
<Audio 1>：只参考女孩音色
Shot 1：Subject 1 位于 Subject 2 中并发声
```

## 14.2 时间约束比形容词更重要

视频模型必须预测连续 latent。若 Prompt 只写“史诗、震撼、电影感”，模型知道风格，却不知道变化路径。

可执行描述应包含：

```text
谁
在何处
从什么状态
通过什么动作
变成什么状态
摄影机如何观察
声音何时发生
```

## 14.3 状态守恒

每个镜头结束时都形成下一镜头的初始状态：

```text
State(N, end) ≈ State(N+1, start)
```

需要连续的项目应显式守恒：

- 人物身份
- 衣着和发型
- 道具数量
- 左右位置
- 光线方向
- 情绪发展
- 音频环境

若某项要改变，应写出触发动作，而不是让它凭空变化。

## 14.4 约束竞争

模型容量和时间有限。以下要求会竞争：

- 多角色身份
- 多地点
- 高速动作
- 长对白
- 复杂运镜
- 精准文字
- 多参考素材
- 首尾帧强约束

当结果不稳定时，优先减少同时竞争的目标，而不是继续堆更多形容词。

## 14.5 参考素材的信息污染

参考素材不仅携带你想要的内容，也携带背景、姿势、文字、光线、压缩噪声和平台水印。

Ref2VA 的职责分配就是在回答：

```text
这个素材的哪些信息应该进入目标？
哪些只属于来源，不应扩散？
```

职责越窄，控制越强；职责越模糊，素材混合越随机。

## 14.6 为什么 2K 再生成不同于普通超分

普通超分主要从现有像素推测高频细节；官方 H3-Regenerate-2K 会再次使用原始上下文，因此理论上能结合人物、文字、场景和多模态条件恢复细节。

但开源 Base 与官方完整 2K 系统并不等价。使用 FlashVSR、SeedVR2、Real-ESRGAN 等外部工具时，应称为后处理超分，不应混称为官方 H3-Regenerate-2K。

---

## 15. 生产模板

## 15.1 T2VA 模板

```text
integrated_multimodal_description: [Shot 1] [Style], [initial composition]. [Subject identity, position, environment, lighting]. [Primary action]. [Speaker description] (S1) says: <d>[Language] Exact dialogue.</d> [Reaction and state change].
[Shot 2] At 00:SS.mmm, the camera cuts to [new information]. [Action, camera, synchronized sound, result].

overall_soundscape: [Ambient baseline]. [Physical and non-verbal sounds across the video].

non_diegetic_music: [Instrumentation, tempo, rhythm, dynamic development] / N/A
```

## 15.2 I2VA 模板

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] [Style], the subject shown in <Picture 1> remains in the same opening composition, preserving [identity, clothing, pose, objects, spatial layout]. [Observable motion begins]. [Continuous development]. [Result or reaction].

overall_soundscape: ...

non_diegetic_music: ...
```

## 15.3 FL2VA 模板

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the SS.SS-second mark of the target video.

integrated_multimodal_description: [Shot 1] [Style], the shot begins in the exact state and composition established by Picture 1. [Step-by-step physical path]. [Intermediate visible changes]. The motion gradually settles into the pose, object state, lighting, spacing, and final composition established by Picture 2.

overall_soundscape: ...

non_diegetic_music: ...
```

## 15.4 L2VA 模板

```text
How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the SS.SS-second mark of the target video.

integrated_multimodal_description: [Shot 1] [Style], [plausible earlier state compatible with Picture 1]. [Action path]. [Shot N] At 00:SS.mmm, [final convergence]. The subject and scene settle into the exact final pose, geometry, lighting, and composition established by <Picture 1>.

overall_soundscape: ...

non_diegetic_music: ...
```

## 15.5 Ref2VA 骨架

```text
subject_definitions:
<Subject 1> is ... from <Picture 1>, providing ...
<Subject 2> is ... from <Video 1>, providing ...
<Audio 1> is the voice-timbre reference for <Subject 1> (S1).

summary:
[reference generation + audio reference] The target video ...

retention_analysis:
<Subject 1> (appears in [Shot 1], [Shot 2]): fully_preserved - ...
<Subject 2> (appears in [Shot 1]): weak_reference - ...
<Audio 1>: reference - ...

detailed_description:
The target video uses ...
[Shot 1] ...
[Shot 2] At 00:SS.mmm, ...

overall_soundscape:
...

non_diegetic_music:
...
```

## 15.6 中文对白示例

```text
A calm adult Mandarin narrator with a warm, measured delivery (S1) says in an off-screen voiceover: <d>[Chinese] 今天，我们从这里出发。</d> while the on-screen character's lips remain completely closed.
```

---

