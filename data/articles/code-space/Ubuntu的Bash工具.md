---
author: admin@pldz1.com
category: code-space
date: '2025-01-09'
serialNo: 3
status: publish
summary: 简单的更新一点这个指令bash脚本.
tags:
- Ubuntu
thumbnail: /api/v1/website/image/code-space/ut_ubuntu_tool_thumbnail.png
title: Ubuntu的Bash工具
---

# 💻⚡ Ubuntu Bash 工具

`SSH` 了 `Ubuntu` 服务器 如果想查看电池电量、监控 `CPU` 和内存使用情况、设置代理、旋转屏幕等 其实都有指令 但是比较麻烦要去搜 这里简单的更新一点这个指令 `bash` 脚本

代码如下：

```bash
#!/bin/bash

# Function to display usage message
display_usage() {
    echo "Usage: $0 [-b] [-r] [-p <proxy_url>]"
    echo "Options:"
    echo "  -b    Display battery information"
    echo "  -m    Display CPU and memory usage"
    echo "  -p    Set HTTP and HTTPS proxy (format: host:port)"
    echo "  -r    Rotate the screen in the left direction"
    echo "  -s    Show screen if it is locked"
}

# Check if no options are provided
if [ "$#" -eq 0 ]; then
    display_usage
    exit 1
fi

# Ubuntu helper.
if [ "$1" = "-b" ]; then
    DEVICE_PATH=$(upower -e | grep 'BAT')
    upower -i "$DEVICE_PATH" | grep percentage | awk '{print "Battery =====> " $2}'

elif [ "$1" = "-m" ]; then
    top -b -n1 | grep "Cpu(s)" | awk '{print "CPU Usage =====> " $2 + $4 " %"}'
    free | awk '/Mem/{print "Mem Usage =====> " $3/$2 * 100.0 " %"}'

elif [ "$1" = "-r" ]; then
    xrandr -o left

elif [ "$1" = "-s" ]; then
        gnome-screensaver-command -d

elif [ "$1" = "-p" ]; then
    if [ "$#" -ne 2 ]; then
        echo "[ ERROR ] Invalid number of -p. Usage: -p <proxy_url>"
        exit 1
    fi
    echo -e "[ INFO ] To diable proxy, You should close the terminal. \n"

    echo "export http_proxy="http://$2/""
    echo "export https_proxy="http://$2/""
    echo "export ftp_proxy="http://$2/""
    echo "export no_proxy="127.0.0.1,localhost""
    # For curl
    echo "export HTTP_PROXY="http://$2/""
    echo "export HTTPS_PROXY="http://$2/""
    echo "export FTP_PROXY="http://$2/""
    echo "export NO_PROXY="127.0.0.1,localhost""

    echo -e "\n[ INFO ] Copy the follow message to set the proxy."


else
    echo "[ ERROR ] Invalid option: $1"
    display_usage
    exit 1
fi
```

---

## 🔨 指令列表

### 1. 🔋 查看电池信息 (`-b`)

**如何使用：**

```bash
./script.sh -b
```

**脚本实现：**

```bash
DEVICE_PATH=$(upower -e | grep 'BAT')
upower -i "$DEVICE_PATH" | grep percentage | awk '{print "Battery =====> " $2}'
```

**输出示例：**

```
Battery =====> 85% 🔋
```

---

### 2. 💻 查看 CPU 和内存使用情况 (`-m`)

**如何使用：**

```bash
./script.sh -m
```

**脚本实现：**

```bash
top -b -n1 | grep "Cpu(s)" | awk '{print "CPU Usage =====> " $2 + $4 " %"}'
free | awk '/Mem/{print "Mem Usage =====> " $3/$2 * 100.0 " %"}'
```

**输出示例：**

```
CPU Usage =====> 15.3% 🧑‍💻
Mem Usage =====> 60.2% 💾
```

---

### 3. 🔄 旋转屏幕 (`-r`)

**如何使用：**

```bash
./script.sh -r
```

**脚本实现：**

```bash
xrandr -o left
```

**输出示例：**

```
Screen rotated to the left direction.
```

---

### 4. 🔓 解锁屏幕 (`-s`)

**如何使用：**

```bash
./script.sh -s
```

**脚本实现：**

```bash
gnome-screensaver-command -d
```

**输出示例：**

```
Screen unlocked.
```

---

### 5. 🌐 设置代理 (`-p <proxy_url>`)

**如何使用：**

```bash
./script.sh -p <proxy_url>
```

**脚本实现：**

```bash
echo "export http_proxy="http://$2/""
echo "export https_proxy="http://$2/""
echo "export ftp_proxy="http://$2/""
echo "export no_proxy="127.0.0.1,localhost""
# For curl
echo "export HTTP_PROXY="http://$2/""
echo "export HTTPS_PROXY="http://$2/""
echo "export FTP_PROXY="http://$2/""
echo "export NO_PROXY="127.0.0.1,localhost""
```

**输出示例：**

```
[ INFO ] To disable proxy, You should close the terminal.

export http_proxy="http://proxy.example.com:8080/"
export https_proxy="http://proxy.example.com:8080/"
export ftp_proxy="http://proxy.example.com:8080/"
export no_proxy="127.0.0.1,localhost"
```

---

## 🚀 推荐使用符号链接（`ln -s`）调用

为了让这个脚本更加便捷，我推荐通过创建符号链接（symlink）将其加入到系统路径。这样，我就可以直接通过简短的命令来执行脚本，而无需每次都输入完整路径。

### 步骤 1: 给脚本增加执行权限

首先，我需要确保脚本具有执行权限：

```bash
chmod +x /path/to/your/script.sh
```

### 步骤 2: 创建符号链接

接下来，我可以使用 `ln -s` 命令在 `/usr/bin` 目录下创建符号链接，这样我可以直接通过命令来调用脚本：

```bash
sudo ln -s /path/to/your/script.sh /usr/bin/xxx
```

例如，如果我将脚本命名为 `pldzlt.sh`，可以这样做：

```bash
sudo ln -s /home/user/scripts/pldzlt.sh /usr/bin/pldzlt
```

### 步骤 3: 直接使用命令

```bash
pldzlt -b
```

结果如下图

![软连接结果](/api/v1/website/image/code-space/ut_ubuntu_tool_thumbnail.png)