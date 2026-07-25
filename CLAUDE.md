# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指导。

## 项目概述
Windows 桌面宠物 + LLM Agent，角色为大藏里想奈。支持 LLM 对话、GPT-SoVITS 本地语音合成、SenseVoice 离线语音识别、系统触发器（CPU/GPU 温度、活动窗口、剪贴板、浏览器 URL 等）、物理引擎、Web 远程控制、MCP 工具调用。

## 常用命令

### 环境搭建
```bash
# Windows（建议用管理员权限运行 PowerShell）
.\setup.ps1            # 交互式安装：选择 venv/runtime/global，自动下载 SoVITS + STT + 资源包

# Linux/Mac
bash setup.sh
```

### 启动
```bash
# Windows — 自动检测 venv、runtime 或系统 Python
.\run.bat

# Linux/Mac
bash run.sh

# 直接启动（如果已激活 venv）
python main.py

# 用 pythonw.exe 启动可隐藏控制台窗口
```

### 独立启动 SoVITS 服务器
```bash
python run_sovits_server.py
```

### 开发工具
```bash
python tools/trigger_editor.py     # 触发器图形编辑器（编辑 triggers.json）
python tools/sensor_mocker.py      # 传感器模拟器（伪造 CPU/GPU 温度等用于调试触发器）
python tools/image_processor.py    # 立绘预处理器（缩放/对齐到 1280×720 画布）
python tools/sprite_organizer.py   # 立绘整理器（批量重命名 + 自动生成 sum.json）
```

### 依赖安装
```bash
pip install -r requirements.txt    # PySide6, litellm, sherpa-onnx, pyaudio, fastapi 等
```

本项目没有配置测试套件、代码检查或类型检查工具。

## 架构总览

### 入口文件：`main.py`
`ApplicationController`（约 1700 行）是整个程序的"上帝对象"，负责连接所有子系统。它拥有并初始化所有模块，通过 Qt 信号/槽机制连接各组件。异步事件循环运行在独立的守护线程（`_loop_thread`）上，与 Qt 主线程分离。

主要内嵌类：
- `AudioPlayer`：封装 QMediaPlayer，管理音频播放
- `TimerScheduler`：轮询定时任务收件箱，支持预合成语音

### 核心交互流程
```
用户输入（IOOverlay.edit → submitted 信号，或 STT 快捷键，或 WebSocket）
  → ApplicationController._handle_user_query
    → main_window.start_thinking() → 显示随机"思考中"文本 + 立绘
    → LLMBackend.query() [异步] → litellm → LLM API
  → _handle_llm_response → _trigger_voice_response
    → TTSBackend.synthesize() [异步] → SoVITS HTTP API
  → _handle_tts_ready → main_window.show_response(text, emotion)
    → AudioPlayer.play() → on_audio_finished → finish_processing()
```

### 各子系统说明

**`config/config_manager.py`** — ConfigParser 封装。读取 `config.cfg`，包含 10+ 个模型配置节（`[Model_1_OpenAI]` 到 `[Model_10_*]`、`[Model_Vision]`、`[Model_Local]`），由 `[General]` 中的 `model_select` 决定当前使用哪个模型。同时管理 `[SoVITS]`、`[STT]`、`[MCP]`、`[Behavior]`、`[Physics]`、`[Memory]`、`[HTML]`、`[Timer]`、`[IdleTrigger]`、`[ScreenWatch]` 等所有配置节。

**`config/pack_manager.py`** — 资源包加载器。读取 `packs/<id>/pack.json`，管理立绘路径解析（服装 + 情感标签 → PNG 文件路径，通过 `sum.json`）、插件加载（从 `plugins/` 目录）、以及每个资源包的 `override_config.cfg` 配置覆盖。资源包是角色身份的完整单位——切换资源包会同时切换立绘、SoVITS 模型、提示词、触发器和插件。

**`backend/llm_backend.py`** — 统一 LLM 调用接口，基于 `litellm` 库。返回结构化 `LLMResponse` 对象（情感标签、显示文本、TTS 文本）。管理对话历史（`ConversationHistory`），支持思考过程提取（`<think>` 标签）、OCR/VLM 截图上下文注入、IP 地理位置上下文人。

**`backend/tts_backend.py`** — GPT-SoVITS HTTP 客户端。将情感标签（如 `<E:smile>`）映射到资源包 `emotions.json` 中定义的参考音频。支持本地模式（HTTP 连接 `localhost:9880`）和远程服务器模式（WebSocket + UDP 广播自动发现，端口 19876）。

**`backend/stt_backend.py`** — 离线语音识别，基于 `sherpa-onnx` + SenseVoice 模型。在独立线程中通过 `pyaudio` 采集音频。VAD 静音检测自动停止录音。全局快捷键（默认 `Ctrl+Shift+I`）切换录音状态。

**`backend/sovits_manager.py`** — 管理 GPT-SoVITS 子进程生命周期。自动查找 SoVITS 安装目录中的 `api_v2.py`，通过子进程启动并等待 API 就绪，退出时自动清理。支持 GPU 检测（NVIDIA 50 系列使用专用优化版本）。

**`backend/mcp_manager.py`** — Model Context Protocol 集成。自动扫描 `mcpserver/` 目录中的 `.mcp.json/py/js` 文件，以子进程方式启动 MCP 服务器，将其工具 Schema 注入 LLM 系统提示词。内置工具包括：`filesystem_tools`（文件操作）、`command_proxy`（执行 Shell 命令）、`timer_inbox`（定时任务）、`ocr_tools`（屏幕 OCR）。

**`behavior_monitor.py`** — 基于轮询的触发器引擎。每隔 N 秒（可配置）扫描传感器数据（CPU/GPU 温度、活动窗口标题、浏览器 URL、剪贴板、音乐播放状态），对当前资源包的 `triggers.json` 中定义的规则进行匹配。条件满足时发射 `trigger_matched` 信号并携带动作列表。

**`memory/`** — 长期记忆系统。
- `memory_manager.py`：将对话历史存入 SQLite，支持按资源包隔离
- `vector_store.py`：通过 ONNX 句嵌入模型提供语义搜索（可选启用）
- `startup_processor.py`：使用独立 LLM 配置对上次会话进行摘要总结

**`web_server/`** — FastAPI + WebSocket 远程控制服务。
- `server.py`：托管 HTTP API 和 WebSocket 端点
- `session_manager.py`：跟踪已连接客户端，支持每个会话独立的资源包/服装状态
- 支持远程 STT（音频上传 → 转录 → LLM 查询 → TTS 响应）、资源包切换、配置更新

**`physics/`** — 实验性 Verlet 积分物理引擎。
- `engine.py`：模拟粒子运动，支持重力、摩擦力、弹跳、碰撞（屏幕边缘 + 其他窗口，通过 `env_scanner.py` 检测）
- `bridge.py`：将物理状态桥接到 UI（MainWindow 移动）

**`ui/luna/`** — Qt 控件树。
- `main_window.py`：无边框透明窗口，包含 `CharacterView`（立绘渲染）和 `IOOverlay`（文本输入/输出对话框）
- `character_view.py`：角色立绘显示，支持多服装切换、表情随机选取
- `io_overlay.py`：对话 UI 组件，支持打字机动画、思考中/录音中状态显示、手动布局

### 资源包目录结构
```
packs/<资源包名>/
├── pack.json              # id, name, version, character, models 路径
├── icon.ico               # 托盘图标（可选）
├── override_config.cfg    # 按资源包覆盖配置（可选）
├── assets/sprites/<服装名>/
│   ├── sum.json           # 情感标签 → [文件名列表] 映射
│   └── *.png              # 立绘图片（1280×720 画布）
├── assets/audio/          # TTS 情感参考音频和事件音频
├── logic/
│   ├── emotions.json      # TTS 情感 → ref_wav + ref_text 配置
│   ├── triggers.json      # 触发器规则（条件 + 动作）
│   ├── thinking.json      # 随机"思考中..."文本
│   ├── listening.json     # 随机"录音中..."文本
│   └── error_config.json  # 按错误类型的错误响应（可选）
├── models/sovits/         # GPT-SoVITS 模型权重 (.pth / .ckpt)
├── prompts/
│   └── character_prompt.txt  # LLM 系统提示词（角色人格）
└── plugins/               # Python 插件脚本（可选）
```

### 配置系统要点
- `config.cfg` 采用 INI 格式，但有多模型切换机制：`[General]` 中的 `model_select` 决定当前使用 `[Model_N_*]` 中的哪个模型
- 资源包可通过 `override_config.cfg` 覆盖配置（优先级：资源包 > 主配置 > 默认值）
- 切换资源包会触发 SoVITS 重启和 UI 完整刷新

## 已知问题
- `ApplicationController` 状态机脆弱——多个布尔标志（`is_processing`、`is_speaking`、`is_listening`、`is_displaying_text`、`_is_chain_executing`、`interaction_locked`）以不明显的方式相互耦合
- 多处裸 `except: pass` 可能隐藏错误
- `DialogueAdapter.set_text()` 在 main_window.py 中是死代码
- `_force_unlock` 看门狗定时器是暴力防卡死机制，治标不治本
- 无自动化测试

## Windows 专属注意事项
- 使用 `pythonw.exe` 可隐藏控制台窗口；`run.bat` 自动选择最佳 Python 环境
- 所有子进程调用均使用 `CREATE_NO_WINDOW` + `STARTF_USESHOWWINDOW | SW_HIDE` 抑制弹窗
- SoVITS 子进程使用相同的窗口隐藏标志
- GPU 检测通过 `pnputil` 实现——NVIDIA 独显启用 GPU 监控；AMD/Intel 则禁用
- 开机自启写入 `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- 需要安装 Visual C++ Redistributable 2015–2022 才能运行 PySide6/NumPy
