---
author: admin@pldz1.com
category: others
csdn: ''
date: '2025-08-04'
gitee: ''
github: ''
juejin: ''
serialNo: 3
status: publish
summary: 在每个整点（00 分）检查一次服务是不是活着，如果挂了就自动重启
tags:
- WSL2
thumbnail: /api/v1/website/image/others/wsl-service-heartbeat-thumbnail.png
title: wsl2-service守护脚本
---

# 🛠️ WSL2 服务整点健康守护脚本

> 你有在 WSL2 里跑的某个长期服务，担心它挂了但又不想每小时盯着？
> 这个脚本的目标很简单：在每个整点（00 分）检查一次服务是不是活着，如果挂了就自动重启，尽量不 drift（时间漂移），日志也清晰好排查。

---

## 为什么这么写？

常见的“每隔一小时睡 3600 秒再检查一次”会慢慢错开整点（比如启动在 10:05，就变成 11:05、12:05……），不利于对齐排查窗口。
这个脚本把重心放在\*\*“整点”\*\*：不管你什么时候启动，每一轮检查都在下一个完整的小时（比如 11:00、12:00）发生。
另外加了点小心思：唤醒 WSL（防止冷启动 delay）、检查进程、失败就重启、再确认，日志都打出来，方便你把它丢后台用 `nohup` / 计划任务挂着。

---

## 🔧 脚本源码（`wsl2-service-watchdog.py`）

```python
import subprocess
import time
import datetime

# ========== 配置区（改这两项） ==========
SERVICE_NAME = "your_service_process_name"
SERVICE_START_CMD = "/path/to/your/service/start-command --with-flags"
# ========================================


def run_wsl_command(command, shell=False):
    """在 Windows 上通过 WSL 执行命令，返回执行结果对象"""
    try:
        if shell:
            cmd = ["wsl", "bash", "-c", command]
        else:
            cmd = ["wsl"] + command
        return subprocess.run(cmd, capture_output=True, text=True)
    except Exception as e:
        print(f"🚨 执行命令时出错: {e}")
        return None


def warmup_wsl():
    """轻量唤醒 WSL，避免冷启动导致首次命令失败"""
    print("🧊 唤醒 WSL 子系统...")
    run_wsl_command(["echo", "WSL Ready"])
    time.sleep(2)


def check_service_process():
    """看目标服务进程在不在"""
    result = run_wsl_command(["pgrep", "-x", SERVICE_NAME])
    if result and result.returncode == 0 and result.stdout.strip():
        print(f"✅ 服务 '{SERVICE_NAME}' 还在运行 (PID: {result.stdout.strip()})")
        return True
    print(f"❌ 服务 '{SERVICE_NAME}' 没找到进程")
    return False


def start_service():
    """尝试用你配置的命令把服务启动起来"""
    print(f"🚀 尝试启动服务: {SERVICE_NAME}")
    run_wsl_command(SERVICE_START_CMD, shell=True)


def sleep_until_next_hour():
    """睡到下一个整点，保证下一次检查是 xx:00:00"""
    now = datetime.datetime.now()
    next_hour = (now.replace(minute=0, second=0, microsecond=0)
                 + datetime.timedelta(hours=1))
    delta = (next_hour - now).total_seconds()
    print(f"💤 当前时间 {now.strftime('%Y-%m-%d %H:%M:%S')}，睡 {int(delta)} 秒等到 {next_hour.strftime('%Y-%m-%d %H:%M:%S')} 继续检查")
    time.sleep(delta)


def main():
    while True:
        warmup_wsl()

        if check_service_process():
            print("🎉 服务状态正常")
        else:
            print("🔁 服务不在了，准备重启...")
            start_service()

            if check_service_process():
                print("✅ 重启成功")
            else:
                print("🔥 重启失败，需要人工干预")

        sleep_until_next_hour()


if __name__ == "__main__":
    main()
```

---

## 📘 核心代码详解

### 1. 整点对齐睡眠

```python
now = datetime.datetime.now()
next_hour = (now.replace(minute=0, second=0, microsecond=0)
             + datetime.timedelta(hours=1))
delta = (next_hour - now).total_seconds()
time.sleep(delta)
```

- 不是固定睡 3600 秒，而是算到下一个整点还剩多少秒然后睡那个时间。
- 这样无论脚本几点启动，下一次检查都会在 XX:00:00，而不会逐渐错位。
- 和日志、报警、其他定时系统对齐，排查窗口一致性好。

---

### 2. 预热 WSL —— 保护性启动

```python
run_wsl_command(["echo", "WSL Ready"])
time.sleep(2)
```

- 跑一个轻量命令让 WSL 从可能的休眠/冷启动状态“醒来”，再等两秒。
- 第一次执行命令失败经常因为 WSL 尚未完全激活，尤其在 Windows 启动后马上触发脚本时。
- 显著减少“奇怪的第一次失败”噪声，让后续检查更稳。

---

### 3. 进程存在性检查

```python
result = run_wsl_command(["pgrep", "-x", SERVICE_NAME])
if result and result.returncode == 0 and result.stdout.strip():
    # 活着
```

- 通过 `pgrep -x` 精确匹配进程名，看服务是不是在跑。
- 进程存在本身是最简单、开销最低的“健康”指标。
- 如果某些服务是短命的 worker，可能要换成别的检查（比如端口、HTTP endpoint）。

---

### 4. 重启逻辑

```python
run_wsl_command(SERVICE_START_CMD, shell=True)
```

- 用你填的那个 shell 命令触发服务启动。
- 用 `shell=True` 允许你在启动字符串里写复杂命令（背景执行符 `&`、配置导出、管道等）。
- 启动命令本身最好能把服务守护到后台，脚本只负责触发和后续再验证是否真的跑起来了。

---