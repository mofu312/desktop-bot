# TTS 语音优化建议

## 1. SoVITS 参数调优

在 `tts_backend.py` 的 `_synthesize_local()` 方法中调整以下参数（`payload` 字典）：

| 参数 | 当前值 | 建议范围 | 说明 |
|------|--------|----------|------|
| `speed_factor` | 1.0 | **0.8 ~ 1.0** | 语速。1.0 偏慢，调太大会变唐老鸭 |
| `top_k` | 见 config | **6** | 采样候选数。越小越稳定，越大越随机 |
| `top_p` | 见 config | **0.6** | 核采样。配合 top_k 使用 |
| `temperature` | 见 config | **0.5 ~ 0.8** | 温度。越低越稳定，越高越有情感波动 |
| `fragment_interval` | 见 config | **0.3 ~ 0.5** | 片段间停顿秒数。越大越自然但有延迟 |
| `text_split_method` | 见 config | **cut5** | 按标点切分，效果较均衡 |
| `repetition_penalty` | 1.35 | **1.3 ~ 1.5** | 重复惩罚。防止 GPT 部分循环 |

**配置文件位置**: `config.cfg` 中 `[SoVITS]` 段落。

---

## 2. 参考音频（最关键的改进点）

### 质量要求
- **格式**: 24kHz / 16bit / 单声道 / WAV
- **时长**: 3 ~ 10 秒
- **内容**: 与目标情感匹配、发音清晰、无背景噪音
- **文本**: `ref_text` 必须与音频内容**完全一致**（标点符号也不能错），否则 GPT 部分会崩

### 音频存放位置
`packs/<pack_id>/assets/audio/extracted_ogg/`（或其他路径，在 `emotions.json` 中指定）

### 多参考音频（已实现）

项目已支持每个情感配置多条参考音频，随机挑选。

**格式对比**:

```json
// 旧格式（单条）
"<E:smile>": {
    "ref_wav": "smile_001.wav",
    "ref_text": "はい、わかりました。",
    "ref_lang": "ja"
}

// 新格式（多条，推荐）
"<E:smile>": {
    "ref_wavs": [
        {"ref_wav": "smile_001.wav", "ref_text": "はい、わかりました。", "ref_lang": "ja"},
        {"ref_wav": "smile_002.wav", "ref_text": "そうですね！", "ref_lang": "ja"},
        {"ref_wav": "smile_003.wav", "ref_text": "喜んで！", "ref_lang": "ja"}
    ]
}
```

**建议**: 每个情感至少配置 3 ~ 5 条不同语气/音高的参考音频，`_pick_ref_audio()` 方法会随机选取，让语音自然变化。

### 情感列表（`emotions.json`）
| 情感 Key | 建议音频方向 |
|----------|-------------|
| `<E:smile>` | 温和、开心、友好语气 |
| `<E:angry>` | 生气、不耐烦、语速偏快 |
| `<E:sad>` | 低落、语速偏慢 |
| `<E:serious>` | 认真、平稳、低频 |
| `<E:thinking>` | 犹豫、拖长音 |
| `<E:surprised>` | 惊讶、语调上扬 |
| `<E:dislike>` | 嫌弃、冷淡 |
| `<E:smirk>` | 得意、戏谑 |
| `<E:embarrassed>` | 害羞、语速快渐弱 |

### 参考音频处理流
1. 从原声提取 → `extracted_ogg/`
2. 脚本批量转为标准格式（24kHz/16bit/mono WAV）
3. 手动标注 `ref_text`
4. 在 `emotions.json` 中配置

---

## 3. 通过 LLM Prompt 控制语音

在 `prompt.txt`（或 Character Card）中加入语音控制指令，让大模型输出额外参数：

### 方法一：通过情感标签控制
```
回复格式：
{
    "text_tts": "实际语音文本",
    "emotion": "<E:smile>"
}
```

可用情感标签：
- `<E:smile>` — 微笑、温和
- `<E:angry>` — 生气
- `<E:sad>` — 悲伤
- `<E:serious>` — 认真
- `<E:thinking>` — 思考、犹豫
- `<E:surprised>` — 惊讶
- `<E:dislike>` — 嫌弃
- `<E:smirk>` — 得意
- `<E:embarrassed>` — 害羞
```

### 方法二：通过语速控制
在 prompt 中加入：
```
说话习惯：
- 根据情境切换情感标签
- 生气时语速略快（语气词增多）
- 悲伤时语速放慢、带停顿
- 思考时拖长音、加省略感
```

### 方法三：扩展 tts_params（进阶）
让 LLM 输出额外参数直接覆盖 SoVITS 参数：

```json
{
    "text_tts": "语音文本",
    "emotion": "<E:smile>",
    "tts_params": {
        "speed_factor": 0.9,
        "temperature": 0.7
    }
}
```

需要在 `ApplicationController` 中解析 `tts_params` 并传递到 `TTSBackend.synthesize()`。

---

## 4. 其他 TTS 引擎对比

| 引擎 | 优势 | 劣势 | 集成难度 |
|------|------|------|----------|
| **GPT-SoVITS（当前）** | 情感细腻，可自定义参考音频 | 音质依赖参考音频，部署复杂 | - |
| **CosyVoice 2** | 阿里出品，中文极好，情感丰富 | 需要 GPU，社区生态不如 SoVITS | 中 |
| **ChatTTS** | 开源 controllable，中文优秀 | 情感控制不如 SoVITS 细粒度 | 中低 |
| **Fish Speech** | 多语言、速度快 | 情感表现力一般 | 低 |
| **火山引擎 TTS** | 商用级音质，延迟低 | 付费，无自定义情感 | 低（API） |
| **Edge TTS** | 免费、延迟低 | 情感平淡、声音有限 | 极低 |

### 建议路线
1. **短期**: 优化 SoVITS 参考音频质量 + 多 ref 配置
2. **中期**: 接入 ChatTTS 或 CosyVoice 2 作为备选引擎
3. **长期**: 若预算充足，部分场景可切商用 API

---

## 5. 已修改的相关文件

- **`resona_desktop_pet/backend/tts_backend.py`** — 添加 `_pick_ref_audio()` 支持多参考音频随机选取
- **`packs/<pack_id>/logic/emotions.json`** — `ref_wavs` 数组格式配置
- **`config.cfg`** — SoVITS 参数配置

---

## 6. 修改后需要重启程序

Python 无热重载机制，所有源码更改后必须重启程序才能生效。
