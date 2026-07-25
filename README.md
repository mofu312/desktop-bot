[English](README_EN.md) | [中文](README.md)

> **🚀 想要制作自己的桌宠角色？**
> 查看最新发布的 **[🎨 小白资源包创作/修改保姆级指南](docs/CUSTOM_PACK_GUIDE_FOR_BEGINNERS.md)**，从零开始打造你的专属伴侣！

# 🐾 Resona Desktop Pet（雷索纳桌面宠物）

一个基于 AI 多模态技术的 Windows 桌面虚拟宠物。集成大语言模型 (LLM)、语音合成 (TTS)、语音识别 (STT)、物理引擎与 MCP 扩展能力，提供深度情感化的人机交互体验。

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Python](https://img.shields.io/badge/python-3.10+-blue)

---

## 📖 目录

- [✨ 核心特性](#-核心特性)
- [🛠️ 技术栈](#️-技术栈)
- [📁 项目结构](#-项目结构)
- [🚀 快速开始](#-快速开始)
- [⚙️ 配置说明](#️-配置说明)
- [🎮 交互触发系统](#-交互触发系统)
- [🎨 资源包系统](#-资源包系统)
- [🔌 插件系统](#-插件系统)
- [🧠 记忆系统](#-记忆系统)
- [🤖 MCP 扩展能力](#-mcp-扩展能力)
- [🌐 Web 服务接口](#-web-服务接口)
- [⚡ 物理引擎（实验性）](#-物理引擎实验性)
- [🛠️ 开发辅助工具](#️-开发辅助工具)
- [📚 详细文档](#-详细文档)
- [⚠️ 安全与免责](#️-安全与免责)
- [🙏 鸣谢](#-鸣谢)
- [📄 许可证](#-许可证)

---

## ✨ 核心特性

### 🤖 深度对话交互
- **多模型支持**：通过 litellm 统一调用 OpenAI (DeepSeek/GPT-4)、Google Gemini、Anthropic Claude 等 100+ 种大模型
- **持久化记忆**：SQLite + 向量语义检索，跨会话保留对话上下文
- **环境感知**：LLM 可获取系统时间、天气、IP 位置等上下文信息
- **OCR 屏幕感知（可选）**：将屏幕文字注入对话，增强场景理解（启用即视为知情并自行承担风险）

### 🎙️ 全语音交互体验
- **高质量 TTS**：集成 GPT-SoVITS v2pro 推理引擎，支持 9 种情感表达（喜怒哀乐羞惊思厌嘲）
- **离线 STT**：基于阿里 SenseVoice + sherpa-onnx 的本地离线语音识别，保护隐私、响应迅速
- **快捷键唤起**：默认 `Ctrl+Shift+I` 呼出语音对话，支持 VAD 自动静音检测

### 🎯 智能触发系统
支持 **AND / OR / CUMULATIVE** 复杂逻辑组合，20+ 种触发条件：

| 类别 | 条件类型 |
|------|---------|
| 系统监控 | CPU/GPU 温度、占用率、电池电量 |
| 软件检测 | 前台/后台进程、进程存活时间、浏览器 URL、窗口标题 |
| 用户交互 | 鼠标悬停/离开时长、长按、连击、闲置时长与恢复 |
| 物理引擎 | 加速度阈值、反弹次数、下落距离、窗口碰撞次数 |
| 环境感知 | 全屏检测、剪贴板关键词、天气、音乐播放（网易云） |
| 时间日期 | 特定日期、时间段范围 |
| 拓展能力 | 插件注册的自定义条件 |

触发后可执行：播放语音台词、移动位置、透明度变化、物理推力、延迟等待、随机分支、锁定交互、退出程序等 10+ 种动作序列。

### 🎨 灵活资源包系统
- **一键切换角色**：立绘、语音模型、人格提示词、触发逻辑全部独立封装
- **多服装支持**：一个角色可配多套服装，运行时动态切换
- **高度可定制**：通过 JSON + PNG + WAV 即可定义完整角色行为

### 🧠 长期记忆系统
- **SQLite 持久化**：对话历史自动存档，支持按天保留策略
- **向量语义检索**：ONNX 嵌入模型，根据语义相似度检索历史记忆
- **跨会话延续**：启动时自动总结上次会话，提取关键记忆注入新对话
- **按角色隔离**：不同资源包拥有独立记忆空间

### 🤖 MCP 扩展能力
- **系统控制**：LLM 可执行 `cmd`/`powershell` 命令（需谨慎授权）
- **文件管理**：读取、搜索、编辑、写入文件系统
- **定时任务**：LLM 可设置未来提醒或事件 (timer_inbox)
- **可扩展**：开发者可编写 Python/Node.js MCP 工具脚本

### 🌐 Web 服务与 WebSocket
- **RESTful API**：内置 FastAPI 服务器
- **WebSocket 实时流**：实时推送宠物状态、语音数据，接收远程控制指令
- **远程 TTS 模式**：SoVITS 可作为独立服务器运行，支持多客户端连接

### ⚡ 物理引擎（实验性）
- Verlet 积分粒子模拟
- 重力、墙壁碰撞、地面反弹
- 鼠标拖拽惯性效果
- 多窗口碰撞检测（开发中）

---

## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **UI 框架** | PySide6 (Qt) | 透明无边框桌面叠加窗口 |
| **大语言模型** | litellm 统一调用层 | OpenAI / DeepSeek / Gemini / Claude |
| **语音合成 (TTS)** | GPT-SoVITS v2pro | 本地 HTTP API 推理服务器 |
| **语音识别 (STT)** | SenseVoice + sherpa-onnx | 离线识别，VAD 静音检测 |
| **Web 服务** | FastAPI + WebSocket | REST API + 实时双向通信 |
| **物理引擎** | 自研 Verlet 积分 | 粒子系统 + 碰撞检测 |
| **记忆系统** | SQLite + ONNX 向量嵌入 | 语义检索 + 持久化存档 |
| **图像处理** | Pillow | 立绘加载与透明通道处理 |
| **系统监控** | psutil + pynvml + GPUtil | 硬件状态轮询 |

---

## 📁 项目结构

```
Resona-Desktop-Pet/
├── main.py                              # 程序入口
├── config.cfg                           # 主配置文件
├── run.bat / run.sh                     # 启动脚本
├── setup.ps1 / setup.sh                 # 环境安装脚本
├── requirements.txt                     # Python 依赖清单
│
├── resona_desktop_pet/                  # 核心源码包
│   ├── backend/                         # 后端服务
│   │   ├── llm_backend.py               #   LLM 调用与对话历史管理
│   │   ├── tts_backend.py               #   语音合成接口
│   │   ├── tts_remote_handler.py        #   远程 TTS 客户端
│   │   ├── stt_backend.py               #   语音识别接口
│   │   ├── sovits_manager.py            #   SoVITS 进程管理
│   │   └── mcp_manager.py               #   MCP 工具调度
│   ├── config/                          # 配置管理
│   │   ├── config_manager.py            #   配置读写
│   │   └── pack_manager.py              #   资源包加载与插件管理
│   ├── ui/                              # 用户界面
│   │   ├── luna/                        #   主 UI 模块（窗口/立绘/对话框）
│   │   ├── tray_icon.py                 #   系统托盘
│   │   ├── settings_dialog.py           #   设置对话框
│   │   └── debug_panel.py               #   调试面板
│   ├── physics/                         # 物理引擎（实验性）
│   │   ├── engine.py                    #   Verlet 物理计算核心
│   │   ├── bridge.py                    #   物理与 UI 桥接
│   │   └── env_scanner.py              #   窗口检测与环境扫描
│   ├── web_server/                      # Web 远程服务
│   │   ├── server.py                    #   FastAPI 服务器
│   │   └── session_manager.py           #   WebSocket 会话管理
│   ├── utils/                           # 工具函数
│   ├── behavior_monitor.py              # 系统监控与触发逻辑核心
│   └── cleanup_manager.py               # 进程清理
│
├── packs/                               # 角色资源包
│   └── Example_Pack/                    #   示例包（可据此创建自定义角色）
│       ├── pack.json                    #     角色配置清单
│       ├── assets/sprites/              #     立绘素材
│       ├── assets/audio/                #     语音文件
│       ├── logic/                       #     逻辑配置（表情/触发/错误）
│       └── prompts/                     #     角色系统提示词
│
├── mcpserver/                           # MCP 工具脚本
│   ├── command_proxy.mcp.py             #   系统命令代理
│   ├── filesystem_tools.mcp.py          #   文件系统工具
│   ├── timer_inbox.mcp.py               #   定时任务收件箱
│   ├── ocr_tools.mcp.py                 #   OCR 识别工具
│   ├── random_tools.mcp.py              #   随机工具
│   ├── minecraft_mcp.mcp.py             #   我的世界集成
│   └── slay_the_spire_mcp.mcp.py        #   杀戮尖塔集成
│
├── memory/                              # 长期记忆模块
│   ├── memory_manager.py                #   记忆 CRUD + SQLite 存储
│   ├── vector_store.py                  #   ONNX 向量语义检索
│   ├── startup_processor.py             #   启动时记忆总结
│   └── soul.md                          #   宠物核心人设文件
│
├── tools/                               # 开发辅助工具
│   ├── trigger_editor.py                #   可视化触发器编辑器
│   ├── sensor_mocker.py                 #   传感器全量模拟器
│   ├── image_processor.py               #   立绘预处理（居中+填充）
│   └── sprite_organizer.py              #   素材批量管理与 sum.json 生成
│
├── docs/                                # 中英文双语文档（8篇）
│   ├── FEATURES.md                      #   核心特性详解
│   ├── ARCHITECTURE.md                  #   技术架构说明
│   ├── BACKEND.md                       #   后端服务详解
│   ├── UI_COMPONENTS.md                 #   UI 组件说明
│   ├── RESOURCE_PACKS.md                #   资源包制作指南
│   ├── TOOLS_GUIDE.md                   #   开发工具使用指南
│   ├── TRIGGER_EDITOR_GUIDE.md          #   触发器编辑器指南
│   └── CUSTOM_PACK_GUIDE_FOR_BEGINNERS.md  # 零基础角色包教程
│
└── GPT-SoVITS/                          # GPT-SoVITS 整合包（自行获取）
```

---

## 🚀 快速开始

### 环境要求

- **操作系统**：Windows 10/11 x64
- **运行时**：Microsoft Visual C++ Redistributable 2015-2022（[下载](https://aka.ms/vs/17/release/vc_redist.x64.exe)）
- **Python**：3.10+（安装脚本会自动配置）

### 一键安装（推荐新手）

右键 `if_you_really_dont_know_what_is_python.ps1` → **"使用 PowerShell 运行"**，等待约 20 分钟即可完成全部环境配置。

### 手动安装

```powershell
# 1. 克隆仓库
git clone https://github.com/<your-org>/Resona-Desktop-Pet.git
cd Resona-Desktop-Pet

# 2. 运行安装脚本（按提示选择安装模式）
.\setup.ps1

# 3. 配置 API Key —— 编辑 config.cfg，填入 LLM API Key
# 4. 获取 GPT-SoVITS 整合包，解压到 GPT-SoVITS/ 目录

# 5. 启动
.\run.bat
```

### 目录注意事项

- 项目路径中**不要包含非英文字符**
- 确保 `GPT-SoVITS/GPT-SoVITS-v2pro-*/api_v2.py` 存在且可正常调用

---

## ⚙️ 配置说明

主配置文件 `config.cfg` 采用标准 INI 格式，关键配置节：

| 配置节 | 说明 |
|--------|------|
| `[LLM]` | LLM 模型选择、API Key、Base URL、温度参数 |
| `[SoVITS]` | TTS 模式 (local/server)、端口、设备 (cuda/cpu) |
| `[STT]` | 语音识别开关、快捷键、VAD 灵敏度 |
| `[Memory]` | 记忆开关、向量检索、保留天数、按角色隔离 |
| `[Behavior]` | 行为监控开关、轮询间隔、全局冷却时间 |
| `[Physics]` | 物理引擎开关、重力系数、摩擦、弹性 |
| `[MCP]` | MCP 工具开关与权限控制 |
| `[WebServer]` | Web 服务开关与端口配置 |
| `[Timer]` | 定时任务配置 |

> **提示**：90% 的功能默认关闭，请按需开启。

---

## 🎮 交互触发系统

### 工作流程

```
主动交互：点击/语音 → STT → LLM → TTS → UI
被动触发：BehaviorMonitor → 匹配条件 → 执行动作序列
远程控制：WebSocket → 接收指令 → 执行动作
```

### 支持的动作类型

| 动作 | 说明 |
|------|------|
| `speak` | 播放指定情感和文本的语音台词 |
| `delay` | 动作之间的延迟等待 |
| `move_to` | 移动宠物到指定屏幕坐标 |
| `fade_out` | 改变透明度 / 虚化效果 |
| `lock_interaction` | 锁定交互若干秒 |
| `random_group` | 从多个动作中随机抽选执行 |
| `physics_*` | 物理推力、临时禁用、力场倍率 |
| `exit_app` | 退出程序 |
| 插件动作 | 通过插件注册的自定义动作 |

---

## 🎨 资源包系统

每个角色 = 一个资源包文件夹，包含：

```
packs/Your_Pack/
├── pack.json              # 角色清单（名称/模型/素材/逻辑路径）
├── override_config.cfg    # 覆盖主配置（可选）
├── assets/
│   ├── sprites/
│   │   └── outfit_id/     # 服装目录
│   │       ├── *.png       #   立绘图片（建议 16:9）
│   │       └── sum.json    #   表情 → 图片文件名映射
│   └── audio/             # 语音文件（.wav/.mp3）
├── logic/
│   ├── emotions.json      # 9 种表情 → TTS 参考音频映射
│   ├── triggers.json      # 触发条件与动作配置
│   ├── thinking.json      # 思考中动画配置
│   ├── listening.json     # 聆听中动画配置
│   └── error_config.json  # 错误状态反馈配置
├── prompts/
│   └── character_prompt.txt  # 角色人格提示词
└── plugins/               # 自定义 Python 插件（可选）
```

### 9 种支持的情绪

`<E:smile>` `<E:serious>` `<E:angry>` `<E:sad>` `<E:thinking>` `<E:surprised>` `<E:dislike>` `<E:smirk>` `<E:embarrassed>`

---

## 🔌 插件系统

资源包可从 `plugins/` 目录加载 Python 脚本，扩展自定义触发条件与响应动作。

每个插件须定义 `INFO` 字典：

```python
INFO = {
    "id": "my_plugin",
    "name": "我的插件",
    "triggers": [{"type": "my_custom_trigger"}],
    "actions": [{"type": "my_custom_action"}],
}

def check_status():
    """后台周期性调用，返回 (bool, str, float)"""
    return (True, "ok", 42.0)
```

> ⚠️ 只加载你信任的插件。

---

## 🧠 记忆系统

```
┌─────────────────────────────────────────┐
│  LLM 调用                                │
│  ├── 搜索相关记忆 → 注入 System Prompt    │
│  ├── 生成回复                             │
│  └── 存储新记忆 → SQLite + 向量索引       │
├─────────────────────────────────────────┤
│  启动时                                   │
│  ├── 读取上次会话 → LLM 总结              │
│  └── 将总结写入长期记忆                    │
└─────────────────────────────────────────┘
```

核心配置（`config.cfg` `[Memory]` 节）：

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `enabled` | 是否启用长期记忆 | `true` |
| `per_pack_memory` | 是否按角色隔离 | `true` |
| `vector_enabled` | 是否启用向量语义检索 | `false` |
| `conversation_retention_days` | 对话保留天数（0=永久） | `30` |
| `startup_processing` | 启动时是否总结上次会话 | `true` |

---

## 🤖 MCP 扩展能力

基于 Model Context Protocol，LLM 可调用本地工具实现 Agent 行为。

### 内置工具

| 工具 | 功能 | 风险等级 |
|------|------|---------|
| `filesystem_tools` | 文件读写、搜索、编辑 | 🔴 高 |
| `command_proxy` | 执行系统 Shell 命令 | 🔴 高 |
| `timer_inbox` | 创建定时任务与提醒 | 🟡 中 |
| `ocr_tools` | 屏幕截图 + OCR 识别 | 🟡 中 |
| `random_tools` | 随机数/随机选择 | 🟢 低 |

### ⚠️ 风险警告

- 开启 MCP 后，工具描述会注入 System Prompt，**Token 消耗将大幅增加**
- `command_proxy` 可执行任意系统命令，**严禁在不可信 LLM 上使用**
- MCP 默认关闭，开启即代表您已充分了解并自愿承担风险

---

## 🌐 Web 服务接口

### REST API

启动后在 `http://localhost:8000` 提供：
- `GET /api/status` — 获取宠物当前状态
- `POST /api/action` — 发送控制指令

### WebSocket

连接 `ws://localhost:8000/ws` 实现：
- 实时推送表情、动作、语音状态
- 双向通信，支持远程设备控制
- 多客户端会话管理

### SoVITS 远程模式

将 SoVITS 推理服务器独立部署，客户端通过 WebSocket 远程调用：

```ini
[SoVITS]
mode = server
server_auto_discover = true    # UDP 广播自动发现
server_host = 127.0.0.1
server_port = 9876
```

---

## ⚡ 物理引擎（实验性）

> ⚠️ 实验性功能，不保证稳定运行

基于 Verlet 积分的 2D 粒子物理模拟：

- **重力模拟** — 宠物自由落体并停在地面
- **碰撞反弹** — 与屏幕边缘和窗口矩形碰撞
- **拖拽惯性** — 鼠标拖拽后按惯性继续飞行
- **状态追踪** — 反弹次数、下落距离、窗口碰撞次数可被触发器使用

```ini
[Physics]
enabled = false          # 默认关闭
gravity = 980            # 重力加速度 (px/s²)
friction = 0.95          # 摩擦系数
elasticity = 0.6         # 弹性系数
```

---

## 🛠️ 开发辅助工具

双击 `tools_launcher.bat` 启动工具菜单，或单独运行：

| 工具 | 命令 | 说明 |
|------|------|------|
| 触发编辑器 | `python tools/trigger_editor.py` | 图形化编辑 `triggers.json`，可视化配置条件与动作 |
| 传感器模拟器 | `python tools/sensor_mocker.py` | 模拟 CPU/GPU 温度、进程、剪贴板等，调试触发逻辑 |
| 立绘处理器 | `python tools/image_processor.py` | 批量将 PNG 居中下对齐并填充到 1280×720 |
| 素材整理器 | `python tools/sprite_organizer.py` | 批量重命名 + 生成 `sum.json` |

---

## 📚 详细文档

| 文档 | 内容 |
|------|------|
| [核心特性](docs/FEATURES.md) | 全部功能详解 |
| [技术架构](docs/ARCHITECTURE.md) | 架构设计与工作流程 |
| [后端服务](docs/BACKEND.md) | LLM / TTS / STT / MCP / 记忆 实现细节 |
| [UI 组件](docs/UI_COMPONENTS.md) | 界面构成与交互逻辑 |
| [资源包系统](docs/RESOURCE_PACKS.md) | 角色包制作完整指南 |
| [开发工具](docs/TOOLS_GUIDE.md) | 内置工具使用方法 |
| [触发器编辑器](docs/TRIGGER_EDITOR_GUIDE.md) | 触发器可视化编辑教程 |
| [小白资源包指南](docs/CUSTOM_PACK_GUIDE_FOR_BEGINNERS.md) | 零基础角色定制保姆级教程 |

---

## ⚠️ 安全与免责

- **MCP 权限风险**：`command_proxy` 和 `filesystem_tools` 具有极高系统权限，请勿在不可信 LLM 上启用
- **OCR 隐私风险**：启用 OCR 会将屏幕内容发送至第三方服务商，可能包含敏感信息
- **代码授权**：源代码采用 [MIT](LICENSE) 许可证
- **法律条款**：使用前请阅读 [LEGAL.md](docs/LEGAL.md)

> 一旦开始使用本项目，即视为已完整阅读并同意 [LEGAL.md](docs/LEGAL.md) 中的所有条款。

---

## 🙏 鸣谢

- **灵感来源**：[luna-sama](https://github.com/annali07/luna-sama)
- **语音合成**：[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)（v2pro-20250604）
- **语音识别**：阿里 FunASR SenseVoiceSmall + [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx)

---

## 📄 许可证

本项目源代码采用 [MIT](LICENSE) 许可证。

---

*本文档部分使用大语言模型辅助生成*
