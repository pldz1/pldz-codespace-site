---
author: admin@pldz1.com
category: others
date: '2025-07-28'
serialNo: 2
summary: 体验code-server, 搭建在线的vscode开发环境.
tags: []
thumbnail: /api/v1/website/image/others/code-server-thumbnail.png
title: 体验code-server
---

# 体验code-server

## 1. 安装code-server

### 1.1 使用安装包

#### 1. 前置条件

- 已安装 Node.js (v12 及以上) 和 npm。  
- Linux 下需安装 C/C++ 编译环境（如 Debian/Ubuntu: `sudo apt install -y build-essential python3`），以编译原生模块。

#### 2. 安装命令


1. 设置版本, 可以在 [https://github.com/coder/code-server/releases](https://github.com/coder/code-server/releases) 查看最新的 release 版本号.

```bash
export VERSION=4.102.2
```

![code-server-release-number](/api/v1/website/image/others/code-server-release-number.png)


2. 下载解压

```bash
mkdir -p ~/.local/lib ~/.local/bin

curl -fL https://github.com/coder/code-server/releases/download/v$VERSION/code-server-$VERSION-linux-amd64.tar.gz \
  | tar -C ~/.local/lib -xz
```


3. 配置路径和快捷访问

```bash
mv ~/.local/lib/code-server-$VERSION-linux-amd64 ~/.local/lib/code-server-$VERSION

ln -s ~/.local/lib/code-server-$VERSION/bin/code-server ~/.local/bin/code-server

PATH="~/.local/bin:$PATH"
```

4. 测试

```bash
code-server

# Now visit http://127.0.0.1:8080. Your password is in ~/.config/code-server/config.yaml
```

### 2. 使用 Docker 安装

#### 1. 前置条件

* 已安装并启动 Docker

#### 2. 运行容器

```bash
mkdir -p ~/.config
docker run -it --name code-server \
  -p 127.0.0.1:8080:8080 \
  -v "$HOME/.local:/home/coder/.local" \
  -v "$HOME/.config:/home/coder/.config" \
  -v "$PWD:/home/coder/project" \
  -u "$(id -u):$(id -g)" \
  -e "DOCKER_USER=$USER" \
  codercom/code-server:latest
```



---

## 2. 配置