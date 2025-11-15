---
author: admin@pldz1.com
category: others
csdn: ''
date: '2025-11-03'
gitee: ''
github: ''
juejin: ''
serialNo: 4
status: publish
summary: Windows 环境下使用codex踩了不少坑。这里记录一下整个过程，主要是安装、配置、模型切换，还有一些注意事项。
tags: []
thumbnail: /api/v1/website/image/others/codex-start-001-thumbnail.png
title: Codex简单使用
---

# 在 Windows 上折腾 Codex CLI：环境、配置与一些小坑


## 一、准备环境

我是在 **Windows 11** 上操作的。Codex CLI 对 Windows 的原生支持目前还不算完美，强烈建议用 **WSL2（Windows Subsystem for Linux）** 跑环境。

### 1. 安装 WSL2
在 PowerShell（管理员模式）执行：
```bash
wsl --install -d Ubuntu
````

装完之后重启一下系统，打开 Ubuntu 终端，基本环境就有了。

### 2. 安装 Node.js 和 Git

Codex CLI 是个 npm 包，先把 Node 环境装好：

```bash
sudo apt update && sudo apt upgrade -y
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs git
```

检查版本：

```bash
node -v
npm -v
git --version
```

我用的是 Node.js v22。低版本有时候会装不上。

---

## 二、安装 Codex CLI

在 WSL 终端里执行：

```bash
npm install -g @openai/codex
```

装完可以用：

```bash
codex --version
```

确认工具能跑。

第一次运行时，CLI 可能会提示要登录或者使用 API key。我这里直接用环境变量配置了 key，不用网页登录。

---

## 三、配置环境变量

去 [OpenAI 控制台](https://platform.openai.com/account/api-keys) 创建一个新的 **Secret Key**。

在终端里导出这个 key：

```bash
export OPENAI_API_KEY="你的key"
```

如果你想永久生效，就把它加进 `~/.bashrc`：

```bash
echo 'export OPENAI_API_KEY="你的key"' >> ~/.bashrc
source ~/.bashrc
```

用 `echo $OPENAI_API_KEY` 检查是否生效。

---

## 四、配置文件（config.toml）

Codex CLI 的配置文件一般在：

```
~/.codex/config.toml
```

第一次运行 Codex 后，这个文件可能会自动生成。也可以手动新建。下面是一个我正在用的配置示例：

```toml
# ~/.codex/config.toml
model = "gpt-4.1"
provider = "openai"
approval-mode = "suggest"
reasoning-effort = "medium"

[providers.openai]
envKey = "OPENAI_API_KEY"
baseURL = "https://api.openai.com/v1"
```

### 说明

* `model`：设置使用的模型。默认是 `o4-mini`，我换成了 `gpt-4.1`，效果更好但消耗也更高。
* `provider`：指定使用哪个模型提供方。默认是 `openai`，但也可以自定义，比如 `gemini` 或本地兼容 API。
* `approval-mode`：Codex 执行操作的模式。

  * `suggest` 表示只给建议，不自动执行。
  * `auto` 表示自动执行命令（慎用）。
* `reasoning-effort`：推理强度。`low`、`medium`、`high` 可选。

---

## 五、切换模型和 provider

Codex 支持多个 provider 配置，比如我加了个 Gemini 的备用配置：

```toml
[providers.gemini]
envKey = "GEMINI_API_KEY"
baseURL = "https://generativelanguage.googleapis.com/v1beta"
```

然后在顶层换个 provider：

```toml
provider = "gemini"
model = "gemini-exp-1206"
```

或者临时在命令行覆盖配置：

```bash
codex --model gpt-4.1 --provider openai "帮我重构这段JS"
```

---

## 六、基本使用

进入一个代码项目目录，比如：

```bash
cd ~/projects/my-app
```

执行：

```bash
codex "Explain this project"
```

Codex 会读目录里的文件，然后生成总结。
如果配置了允许网络访问，可以让它直接装依赖或跑命令，比如：

```bash
codex --allow-internet "install missing dependencies"
```

这个功能要慎用，因为 Codex 真的会执行命令。

---

## 七、常见问题

### 1. Windows 原生 PowerShell 无法运行

我试过直接在 PowerShell 里装 npm 包，结果各种路径和权限问题。结论：用 WSL 省心。

### 2. API key 无效或超时

如果提示 “Invalid API key” 或 “Unauthorized”，重新检查环境变量。注意区分大小写。

### 3. 模型响应慢

可以切换到轻量模型：

```toml
model = "o4-mini"
```

速度快很多。

### 4. 文件权限问题

Codex CLI 可能拒绝修改某些目录下的文件，尤其是非 Git 管理的文件夹。解决办法：
初始化 Git 仓库：

```bash
git init
```

---

## 八、一些使用心得

* WSL 环境比原生 Windows 环境干净很多，命令行输出也更稳定。
* `approval-mode = "suggest"` 模式下最安全，可以看到 Codex 的建议再决定要不要执行。
* 模型和 provider 可以自由切换，但要小心 key 对应关系。
* 如果想做自动化，可以考虑用脚本包一下 Codex CLI，比如写个 `Makefile` 或 `bash` 脚本批量调用。

---