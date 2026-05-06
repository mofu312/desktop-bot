#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SoVITS 看门狗脚本
==================
作用：监控 SoVITS TTS 引擎的运行状态，当检测到 TTS 失败错误时自动重启 SoVITS 进程。
用法：在 Resona Desktop Pet 运行期间，在另一个终端执行 python sovits_watchdog.py
原理：每隔一段时间检查 SoVITS API 是否存活，并扫描日志中的错误关键字，
      发现异常时杀掉旧进程并重新启动。
"""

import os
import sys
import time
import subprocess
import requests
import re
import glob
import signal
import psutil
from pathlib import Path

# ===================== 配置区（按需修改） =====================
PROJECT_ROOT = Path(__file__).resolve().parent       # 项目根目录
SOVITS_PORT = 9880                                    # SoVITS API 端口
CHECK_INTERVAL = 10                                   # 每次检查的间隔（秒）
ERROR_PATTERNS = [                                    # 需要触发的错误关键词
    "File is not a zip file",
    "tts failed",
    "TTS API error: 400",
    "POST /tts HTTP/1.1\" 400",
]
# ============================================================

# 日志目录
LOG_DIR = PROJECT_ROOT / "logs"
# SoVITS 工作目录（api_v2.py 所在目录）
SOVITS_WORK_DIR = PROJECT_ROOT / "GPT-SoVITS"
# SoVITS API 地址
SOVITS_URL = f"http://127.0.0.1:{SOVITS_PORT}"
# Python 解释器路径
PYTHON_EXE = sys.executable
# 临时 override 配置模板路径
TEMP_CONFIG_DIR = PROJECT_ROOT / "TEMP"
# 默认角色包 ID（从 config.cfg 中读取）
PACK_ID = "Resona_Default"


def log(msg: str):
    """打印带时间戳的日志"""
    print(f"[{time.strftime('%H:%M:%S')}] [Watchdog] {msg}")


def load_pack_id() -> str:
    """
    从 config.cfg 读取当前激活的角色包 ID
    如果读取失败，返回默认值 "Resona_Default"
    """
    try:
        import configparser
        cfg = configparser.ConfigParser()
        cfg.read(PROJECT_ROOT / "config.cfg", encoding="utf-8")
        return cfg.get("General", "active_pack", fallback="Resona_Default")
    except Exception:
        return "Resona_Default"


def find_latest_log_dir() -> Path:
    """
    找到 logs/ 目录下最新的日志文件夹（按名称排序，名称是时间戳）
    返回 Path 对象；如果找不到则返回 None
    """
    if not LOG_DIR.exists():
        return None
    dirs = sorted([d for d in LOG_DIR.iterdir() if d.is_dir()], reverse=True)
    return dirs[0] if dirs else None


def check_api_health() -> bool:
    """
    向 SoVITS API 发送 GET 请求检查是否存活
    返回 True 表示正常，False 表示异常
    """
    try:
        resp = requests.get(f"{SOVITS_URL}/", timeout=3)
        # SoVITS 返回 200 或 404 都算活着（404 说明服务器在运行但没有根路由）
        return resp.status_code in (200, 404)
    except requests.ConnectionError:
        return False
    except requests.Timeout:
        return False
    except Exception:
        return False


# 已处理过的错误行指纹集合 — 防止重复触发重启
_seen_error_lines: set = set()


def _line_fingerprint(line: str, pattern: str) -> str:
    """生成错误行指纹，用于去重"""
    return f"{pattern}|{line.strip()}"


def scan_logs_for_errors(log_dir: Path = None) -> bool:
    """
    扫描日志文件中的错误关键词。
    每次只读取最新日志目录的最后 200 行，检测 ERROR_PATTERNS 中的关键词。
    内部维护已处理过的错误行指纹，避免同一行重复触发重启。
    如果传入 log_dir 则使用指定目录，否则自动查找最新目录。
    """
    if log_dir is None:
        log_dir = find_latest_log_dir()
    if not log_dir:
        return False

    # 检查 app.log / sovits.log / tts.log 这三个关键日志
    log_files = [
        log_dir / "app.log",
        log_dir / "sovits.log",
        log_dir / "tts.log",
    ]

    found_new_error = False
    for log_file in log_files:
        if not log_file.exists():
            continue
        try:
            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()[-200:]
            for line in lines:
                for pattern in ERROR_PATTERNS:
                    if pattern in line:
                        fp = _line_fingerprint(line, pattern)
                        if fp in _seen_error_lines:
                            continue  # 已处理过的旧错误，跳过
                        _seen_error_lines.add(fp)
                        log(f"[检测到新错误] {log_file.name}: {pattern}")
                        found_new_error = True
        except Exception:
            continue

    return found_new_error


def kill_process_on_port(port: int):
    """
    杀掉占用指定端口的进程
    使用 psutil 遍历所有进程的网络连接，找到匹配端口的进程后杀死
    """
    killed = False
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            for conn in proc.connections(kind="inet"):
                if conn.laddr.port == port:
                    log(f"杀掉进程 PID={proc.info['pid']} ({proc.info['name']}), 占用端口 {port}")
                    proc.kill()
                    killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return killed


def wait_port_free(port: int, timeout: float = 15.0) -> bool:
    """
    等待指定端口被释放
    每隔 0.5 秒检查一次，直到超时
    返回 True 表示端口已释放，False 表示超时
    """
    start = time.time()
    while time.time() - start < timeout:
        try:
            # 尝试连接端口，如果被拒绝或超时说明端口已释放
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex(("127.0.0.1", port))
            s.close()
            if result != 0:
                return True
        except Exception:
            return True
        time.sleep(0.5)
    return False


def start_sovits() -> bool:
    """
    启动 SoVITS 子进程
    读取 TEMP/tts_infer_override_Resona_Default.yaml 作为配置
    启动后等待 API 就绪，最多等 60 秒
    """
    global PACK_ID
    PACK_ID = load_pack_id()

    # override 配置文件路径
    config_file = TEMP_CONFIG_DIR / f"tts_infer_override_{PACK_ID}.yaml"
    if not config_file.exists():
        log(f"错误: 配置文件不存在 {config_file}")
        return False

    # 启动命令
    cmd = [
        str(PYTHON_EXE),
        "api_v2.py",
        "-a", "127.0.0.1",
        "-p", str(SOVITS_PORT),
        "-c", str(config_file),
    ]

    log(f"启动命令: {' '.join(cmd)}")
    log(f"工作目录: {SOVITS_WORK_DIR}")

    try:
        # 启动子进程，隐藏窗口
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        proc = subprocess.Popen(
            cmd,
            cwd=str(SOVITS_WORK_DIR),
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        # 等待 API 就绪，最多 60 秒
        start_time = time.time()
        while time.time() - start_time < 60:
            if check_api_health():
                elapsed = time.time() - start_time
                log(f"SoVITS 启动成功，API 就绪（耗时 {elapsed:.1f} 秒）")
                return True
            # 检查进程是否意外退出
            if proc.poll() is not None:
                log(f"错误: SoVITS 进程异常退出，退出码={proc.returncode}")
                return False
            time.sleep(1)

        log("错误: SoVITS 启动超时（60 秒）")
        return False

    except Exception as e:
        log(f"错误: 启动 SoVITS 时发生异常: {e}")
        return False


def restart_sovits():
    """
    重启 SoVITS 的完整流程：
    1. 杀掉占用端口的旧进程
    2. 等待端口释放
    3. 启动新进程
    4. 清空已处理错误记录，避免新旧混淆
    """
    global _seen_error_lines
    log("===== 开始重启 SoVITS =====")
    kill_process_on_port(SOVITS_PORT)

    if wait_port_free(SOVITS_PORT, timeout=15):
        log("端口已释放，开始启动...")
    else:
        log("警告: 端口未完全释放，强制继续启动...")

    if start_sovits():
        log("===== SoVITS 重启成功 =====")
        _seen_error_lines.clear()
        log("已清空历史错误记录指纹")
    else:
        log("===== SoVITS 重启失败 =====")


def main():
    """
    主循环：
    1. 先检查 SoVITS 是否在运行，如果没有则启动
    2. 每隔 CHECK_INTERVAL 秒做一次检查和日志扫描
    3. 发现异常则重启

    注意：看门狗的输出不会写入主程序的日志文件。
    如果需要查看看门狗的运行状态，可以在启动它的终端中看到输出。
    如果看不到输出，可以重定向到文件：
      python sovits_watchdog.py > watchdog.log 2>&1
    """
    log("SoVITS 看门狗启动")
    log(f"项目路径: {PROJECT_ROOT}")
    log(f"检查间隔: {CHECK_INTERVAL}s")

    # 缓存当前日志目录，避免每次都重新查找
    current_log_dir = find_latest_log_dir()
    if current_log_dir:
        log(f"监控日志目录: {current_log_dir.name}")

    # 启动时先检查 SoVITS 是否活着，没活着就启动
    if not check_api_health():
        log("检测到 SoVITS 未运行，正在启动...")
        start_sovits()

    # 循环监控 —— 每次循环都同时做健康检查和日志扫描
    while True:
        # ---- 健康检查 ----
        api_ok = check_api_health()
        if not api_ok:
            log("健康检查失败: SoVITS API 无响应")
            restart_sovits()
            time.sleep(CHECK_INTERVAL)
            continue

        # ---- 日志扫描（每次循环都扫） ----
        # 更新最新日志目录（程序重启后日志目录会变）
        current_log_dir = find_latest_log_dir()
        if scan_logs_for_errors(current_log_dir):
            log("日志中检测到 TTS 错误，触发重启")
            restart_sovits()
            time.sleep(CHECK_INTERVAL)
            continue

        # ---- 一切正常，等待下一轮 ----
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("看门狗已停止")
        sys.exit(0)
