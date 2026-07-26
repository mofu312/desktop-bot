[English](README_EN.md) | [中文](README.md)

> **🚀 想要制作自己的桌宠角色？**
> 查看最新发布的 **[🎨 小白资源包创作/修改保姆级指南](docs/CUSTOM_PACK_GUIDE_FOR_BEGINNERS.md)**，从零开始打造你的专属伴侣！

# Resona Desktop Pet（雷索纳桌面宠物）

基于 AI 多模态技术的 Windows 桌面虚拟宠物，集成大语言模型 (LLM)、语音合成 (TTS)、语音识别 (STT)、物理引擎与 MCP 扩展能力。

## 项目结构

```
Resona-Desktop-Pet/
├── main.py                              # 程序入口
├── config.cfg                           # 主配置文件
├── run.bat / run.sh                     # 启动脚本
├── setup.ps1 / setup.sh                 # 环境安装脚本
├── requirements.txt                     # Python 依赖清单
│
├── resona_desktop_pet/                  # 核心源码包
│   ├── backend/                         # 后端服务（LLM/TTS/STT/MCP）
│   ├── config/                          # 配置与资源包管理
│   ├── ui/                              # 用户界面（窗口/立绘/托盘/设置）
│   ├── physics/                         # 物理引擎（实验性）
│   ├── web_server/                      # FastAPI + WebSocket 远程服务
│   ├── utils/                           # 工具函数
│   ├── behavior_monitor.py              # 系统监控与触发逻辑核心
│   └── cleanup_manager.py               # 进程清理
│
├── packs/                               # 角色资源包
│   └── Example_Pack/                    #   示例包（可据此创建自定义角色）
│
├── mcpserver/                           # MCP 工具脚本
│
├── memory/                              # 长期记忆模块（SQLite + 向量检索）
│
├── tools/                               # 开发辅助工具（触发器编辑器/模拟器等）
│
├── docs/                                # 中英文双语文档
│
└── GPT-SoVITS/                          # GPT-SoVITS 整合包（自行获取）
```

## 快速开始

### 1. 环境要求

- **操作系统**：Windows 10/11 x64
- **运行时**：Microsoft Visual C++ Redistributable 2015-2022（[下载](https://aka.ms/vs/17/release/vc_redist.x64.exe)）
- **Python**：3.10+

### 2. 安装

**一键安装（推荐新手）**：

右键 `if_you_really_dont_know_what_is_python.ps1` → **"使用 PowerShell 运行"**，等待约 20 分钟即可完成全部环境配置。

**手动安装**：

```powershell
# 克隆仓库
git clone https://github.com/<your-org>/Resona-Desktop-Pet.git
cd Resona-Desktop-Pet

# 运行安装脚本
.\setup.ps1

# 配置 API Key —— 编辑 config.cfg，填入 LLM API Key
# 获取 GPT-SoVITS 整合包，解压到 GPT-SoVITS/ 目录
```

> 注意：项目路径中不要包含非英文字符。

### 3. 启动

```powershell
.\run.bat
```

## 核心特性

| 特性 | 说明 |
|------|------|
| 深度对话 | litellm 统一调用 100+ 种大模型，支持持久化记忆与环境感知 |
| 语音交互 | GPT-SoVITS v2pro 引擎，9 种情感 TTS；SenseVoice 离线 STT |
| 智能触发 | 20+ 种条件（CPU/GPU/进程/鼠标/物理/时间），支持 AND/OR 组合 |
| 资源包系统 | 角色立绘、语音、提示词、触发逻辑独立封装，一键切换 |
| 长期记忆 | SQLite 持久化 + ONNX 向量语义检索，跨会话延续上下文 |
| MCP 扩展 | LLM 可调用系统命令、文件管理、定时任务等工具 |
| Web 服务 | FastAPI REST API + WebSocket 实时双向通信 |
| 物理引擎 | Verlet 积分粒子模拟，重力/碰撞/拖拽惯性（实验性） |

## 交互流程

```
主动交互：点击/语音 → STT → LLM → TTS → UI
被动触发：BehaviorMonitor → 匹配条件 → 执行动作序列
远程控制：WebSocket → 接收指令 → 执行动作
```

支持的动作类型：

| 动作 | 说明 |
|------|------|
| `speak` | 播放指定情感和文本的语音台词 |
| `move_to` | 移动宠物到指定屏幕坐标 |
| `fade_out` | 改变透明度 / 虚化效果 |
| `lock_interaction` | 锁定交互若干秒 |
| `random_group` | 从多个动作中随机抽选执行 |
| `delay` | 动作之间的延迟等待 |
| `physics_*` | 物理推力、临时禁用、力场倍率 |
| `exit_app` | 退出程序 |

## 资源包结构

每个角色 = 一个资源包文件夹：

```
packs/Your_Pack/
├── pack.json              # 角色清单
├── assets/sprites/        # 立绘素材（建议 16:9）
├── assets/audio/          # 语音文件（.wav/.mp3）
├── logic/                 # 表情/触发/错误配置
├── prompts/               # 角色系统提示词
└── plugins/               # 自定义 Python 插件（可选）
```

支持的 9 种情绪：`smile` `serious` `angry` `sad` `thinking` `surprised` `dislike` `smirk` `embarrassed`

## 配置说明

主配置文件 `config.cfg` 采用标准 INI 格式：

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

> 90% 的功能默认关闭，请按需开启。

## Web 服务接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/status` | 获取宠物当前状态 |
| POST | `/api/action` | 发送控制指令 |
| GET | `/ws` | WebSocket 实时通信（推送状态/接收指令） |

### SoVITS 远程模式

将 SoVITS 推理服务器独立部署，客户端通过 WebSocket 远程调用：

```ini
[SoVITS]
mode = server
server_auto_discover = true
server_host = 127.0.0.1
server_port = 9876
```

## MCP 工具

基于 Model Context Protocol，LLM 可调用本地工具实现 Agent 行为：

| 工具 | 功能 | 风险等级 |
|------|------|---------|
| `command_proxy` | 执行系统 Shell 命令 | 高 |
| `filesystem_tools` | 文件读写、搜索、编辑 | 高 |
| `timer_inbox` | 创建定时任务与提醒 | 中 |
| `ocr_tools` | 屏幕截图 + OCR 识别 | 中 |
| `random_tools` | 随机数/随机选择 | 低 |

> ⚠️ MCP 默认关闭，开启即代表您已充分了解并自愿承担风险。

## 开发辅助工具

| 工具 | 命令 | 说明 |
|------|------|------|
| 触发编辑器 | `python tools/trigger_editor.py` | 图形化编辑触发器条件与动作 |
| 传感器模拟器 | `python tools/sensor_mocker.py` | 模拟系统状态，调试触发逻辑 |
| 立绘处理器 | `python tools/image_processor.py` | 批量处理 PNG 居中下对齐 |
| 素材整理器 | `python tools/sprite_organizer.py` | 批量重命名 + 生成素材清单 |

## 技术栈

| 层级 | 技术 |
|------|------|
| UI 框架 | PySide6 (Qt) — 透明无边框桌面叠加窗口 |
| 大语言模型 | litellm 统一调用层 — OpenAI / DeepSeek / Gemini / Claude |
| 语音合成 (TTS) | GPT-SoVITS v2pro — 本地 HTTP API 推理 |
| 语音识别 (STT) | SenseVoice + sherpa-onnx — 离线识别 + VAD 静音检测 |
| Web 服务 | FastAPI + WebSocket |
| 物理引擎 | 自研 Verlet 积分 — 粒子系统 + 碰撞检测 |
| 记忆系统 | SQLite + ONNX 向量嵌入 |
| 图像处理 | Pillow |
| 系统监控 | psutil + pynvml + GPUtil |

## 安全与免责

- **MCP 权限风险**：`command_proxy` 和 `filesystem_tools` 具有极高系统权限，请勿在不可信 LLM 上启用
- **OCR 隐私风险**：启用 OCR 会将屏幕内容发送至第三方服务商，可能包含敏感信息
- **源代码**：采用 [MIT](LICENSE) 许可证
- 使用前请阅读 [LEGAL.md](docs/LEGAL.md)

## 鸣谢

- **灵感来源**：[luna-sama](https://github.com/annali07/luna-sama)
- **语音合成**：[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)（v2pro-20250604）
- **语音识别**：阿里 FunASR SenseVoiceSmall + [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx)

## 许可证

本项目源代码采用 [MIT](LICENSE) 许可证。

---

*本文档部分使用大语言模型辅助生成*
