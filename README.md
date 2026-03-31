# pldz-codespace-site — pldz1.com

支撑 https://pldz1.com 的源码仓, 同时适配 Codespaces / Docker 作为部署.

## 核心

- 🐍 后端用 Python
- 🧰 前端按需混合（静态 + JS）
- 🐳 Docker + Compose 搞定开发环境
- ⚙️ 推荐用 VS Code（`.vscode/` 配置在仓里）
- 🔒 环境变量通过 `.env` 管理
- 🔁 可复现：Dockerfile + compose 保证本地/线上一致

## Build & Debug

```bash
git clone https://github.com/pldz1/pldz-codespace-site.git
cd pldz-codespace-site
cp .env.example .env          # 改你自己的配置
docker compose up --build     # 构建并启动
```

## 分离式部署

Build 和 Debug 无误之后，可以考虑将各个服务分离到不同的容器中，具体步骤如下：

1. 使用 `docker-compose up -d` 启动所有服务。
2. 通过 `docker-compose logs -f` 查看各个服务的日志。

## 常见错误

### 镜像拉失败

直接运行 `docker compose up --build` 发现 `mongo:7` 或者 `nginx:1.25-alpine` 拉取失败, 可以分别拉取

这里给出只是参考例子

1. 通过代理拉 `mongod:7` : `docker pull docker.m.daocloud.io/library/mongo:7`
2. 重命名 `tag` : `docker tag docker.m.daocloud.io/library/mongo:7 mongo:7`
3. 删除无用的资源: `docker rmi docker.m.daocloud.io/library/mongo:7`
