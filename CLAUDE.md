# Resona Desktop Pet

## 项目概述
Windows 桌面宠物 + LLM Agent，角色为大藏里想奈。支持 LLM 对话、TTS 语音、STT 语音识别、VLM 屏幕识别、物理引擎、Web 远程控制、行为触发、MCP 工具调用。

## 目录结构
```
main.py                              # ApplicationController（上帝对象，~1700行）
config.cfg                           # 主配置
resona_desktop_pet/
├── config/
│   ├── config_manager.py            # ConfigParser 封装
│   └── pack_manager.py              # 角色包管理
├── backend/
│   ├── llm_backend.py               # litellm 封装（LLM 调用 + parser）
│   ├── tts_backend.py               # GPT-SoVITS API 调用
│   ├── sovits_manager.py            # SoVITS 子进程管理（已隐藏窗口）
│   ├── tts_remote_handler.py        # 远程 TTS
│   └── mcp_manager.py               # MCP 工具调用
├── ui/luna/
│   ├── main_window.py               # 透明桌面窗口 + 角色显示 + 对话框
│   ├── character_view.py            # 角色立绘渲染
│   └── io_overlay.py                # 输入(QTextEdit)/输出(QLabel)对话框
├── physics/                         # 物理引擎
└── utils/
    ├── audio_utils.py               # ffmpeg 转码
    └── logger.py
```

## 核心数据流
```
用户输入 → IOOverlay.edit → submitted Signal
  → ApplicationController._handle_user_query
    → start_thinking() → show_status(思考中...)
    → LLMBackend.query() → LLM API
  → _handle_llm_response → _trigger_voice_response
    → TTSBackend.synthesize() → SoVITS
  → _handle_tts_ready → show_response(text)
    → audio_player.play() → finish_processing()
```

## 关键文件及职责

### io_overlay.py
- `self.edit` (QTextEdit): 用户输入框，已设 `documentMargin(0)` + `padding: 0px`
- `self.body` (QLabel): 输出显示，已设 `setContentsMargins(0,0,0,0)` + `setIndent(0)`
- `show_status(text)`: 思考中/录音中状态 → 居中显示，无动画
- `show_output(text)`: LLM 回复 → 左上顶格 + 打字机动画
- `to_input()`: 切换为输入模式（隐藏 body，显示 edit）
- `to_output()`: 切换为输出模式（隐藏 edit，显示 body）
- `layout_children()`: 手动布局 header + content（edit/body）
- `_adjust_height_for_text()`: 自适应内容高度

### main_window.py
- `MainWindow`: 透明置顶窗口，包含 CharacterView + IOOverlay
- `DialogueAdapter`: 桥接类，目前只用了 `show_name()`，`set_text()` 是死代码
- 状态字段: `is_processing`, `is_speaking`, `is_listening`, `is_displaying_text`
- `show_response()`, `show_response_with_timeout()`, `show_behavior_response_with_timeout()`
- `update_io_geometry()`: 根据角色图片位置计算对话框位置

### main.py - ApplicationController
- 上帝对象，~1700 行，承载所有编排逻辑
- 信号连接散落在 `__init__` 中
- watchdog timer 暴力解锁（`_force_unlock`）

## 已修复问题记录
1. **文本框定位**：QTextEdit 默认 documentMargin=4px + QLabel 默认 indent，导致输入/输出文本位置不一致 → 已清零
2. **输出文本顶格**：`setContentsMargins(0,0,0,0)` + `setIndent(0)`
3. **思考文本居中**：`show_status` 居中显示不带动画，`show_output` 左上顶格 + 打字机动画
4. **弹窗隐藏**：所有 `subprocess.run/Popen` 加了 `CREATE_NO_WINDOW`（ffmpeg、netstat、pnputil 等）

## 已知问题
- `ApplicationController` 状态机脆弱，多个布尔 flag 耦合
- `except: pass` 多处存在，可能隐藏 bug
- `DialogueAdapter.input_field` / `set_text()` 死代码

## Windows 部署注意
- 启动用 pythonw.exe 可隐藏控制台
- SoVITS 子进程用 `CREATE_NO_WINDOW` + `STARTF_USESHOWWINDOW | SW_HIDE` 已隐藏
- ffmpeg 调用已加 `CREATE_NO_WINDOW`
