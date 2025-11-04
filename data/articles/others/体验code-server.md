---
author: admin@pldz1.com
category: others
csdn: ''
date: '2025-07-28'
gitee: ''
github: ''
juejin: ''
serialNo: 2
status: publish
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

### 2.1 配置使用GitHub Copilot

> 参考内容
>
> [How to install Github Copilot on code-server](https://github.com/coder/code-server/discussions/5063)
> 
> [VsixHub - Best Extensions for VS Code](https://www.vsixhub.com)
>

1. 下载GitHub Copilot 的 vsix 文件: [https://marketplace.visualstudio.com/_apis/public/gallery/publishers/GitHub/vsextensions/copilot/1.348.1698/vspackage
](https://marketplace.visualstudio.com/_apis/public/gallery/publishers/GitHub/vsextensions/copilot/1.348.1698/vspackage)

![code-server-github-copliot-version](/api/v1/website/image/others/code-server-github-copliot-version.png)

2. 拖拽这个内容到 code-server 里

![code-server-github-copilot-installed](/api/v1/website/image/others/code-server-github-copilot-installed.png)

能看见日志:

```bash
[13:19:04] Installing extension: github.copilot {
  installGivenVersion: true,
  isApplicationScoped: false,
  profileLocation: yr {
    scheme: 'file',
    authority: '',
    path: '/home/pldz/.local/share/code-server/extensions/extensions.json',
    query: '',
    fragment: '',
    _formatted: 'file:///home/pldz/.local/share/code-server/extensions/extensions.json',
    _fsPath: '/home/pldz/.local/share/code-server/extensions/extensions.json'
  },
  productVersion: { version: '1.102.2', date: '2025-07-24T20:11:42.777Z' }
}
[13:19:07] Extracted extension to file:///home/pldz/.local/share/code-server/extensions/github.copilot-1.348.1698: github.copilot
[13:19:07] Renamed to /home/pldz/.local/share/code-server/extensions/github.copilot-1.348.1698
[13:19:07] Extension installed successfully: github.copilot file:///home/pldz/.local/share/code-server/extensions/extensions.json
```

3. 激活 Github Copilot: 点击 code-server 右下角的 Accounts, 选择 `Sign in to xxxxx`
登录来使用 `Github Copilot`.

![code-server-login-github-copilot](/api/v1/website/image/others/code-server-login-github-copilot.png)

![code-server-using-github-copilot](/api/v1/website/image/others/code-server-using-github-copilot.png)

注意 如果你使用的是 Token 登录的 记得给 token 分配 Github Copilot 的权限

![code-server-ghp-github-copilot-tips](/api/v1/website/image/others/code-server-ghp-github-copilot-tips.png)


## 2.2 轻量化

只提供基本的远程编辑 + 文件管理功能，不要插件、遥测、同步之类的负担，只占 200–300 MB 内存”的最小工作环境。

---

### 2.2.1 配置最小化启动的config.yaml

编辑配置文件：

```bash
nano ~/.config/code-server/config.yaml
```

把内容改成这样 👇：

```yaml
bind-addr: 0.0.0.0:8080
auth: password
password: "你的登录密码"
cert: false

# 极简化设置
disable-telemetry: true
disable-update-check: true
disable-getting-started-override: true
disable-workspace-trust: true

# 限制内存缓存等
app-name: "light-vscode"
```

这几项能去掉：

* **插件更新与遥测**（减少网络与内存）
* **欢迎页、提示页**（节省加载）
* **自动更新检查**

---

### 2.2.2 禁用插件与扩展商店

在设置里彻底禁用插件安装：

1. 打开 VS Code 设置（左下角齿轮 → 设置）。
2. 搜索 “Extensions: Auto Update”，取消勾选。
3. 在用户设置（JSON）中添加：

   ```json
   {
     "extensions.autoUpdate": false,
     "extensions.autoCheckUpdates": false,
     "workbench.startupEditor": "none",
     "update.mode": "none",
     "extensionsGallery": {
       "serviceUrl": ""
     }
   }
   ```

彻底关闭插件市场访问。

---

### 2.2.3 使用 systemd 启动的配置

创建 systemd 服务，方便开机自启：

```bash
sudo tee /etc/systemd/system/code-server.service <<'EOF'
[Unit]
Description=code-server minimal
After=network.target

[Service]
Type=simple
User=root
Environment=NODE_OPTIONS=--max-old-space-size=512
ExecStart=/usr/bin/code-server
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now code-server
```

`NODE_OPTIONS=--max-old-space-size=512` 会限制最大堆内存 512 MB，非常关键。


---