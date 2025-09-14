---
author: admin@pldz1.com
category: docker
csdn: ''
date: '2025-08-05'
gitee: ''
github: ''
juejin: ''
serialNo: 1
status: publish
summary: 本章整合常见的 Dockerfile 使用与容器管理实战经验, 重点涵盖Dockerfile 基础与关键指令, docker build 与常用选项,docker
  run 与容器运行选项
tags:
- docker
- dockerfile
thumbnail: /api/v1/website/image/docker/dockerfile-blog-thumbnail.png
title: dockerfile创建自己的镜像
---

# Dockerfile 随笔

本章整合常见的 Dockerfile 使用与容器管理实战经验，重点涵盖

* **基本概念**：镜像、容器、标签、容器状态保存
* **Dockerfile 基础与关键指令**
* **`docker build` 与常用选项**
* **`docker run` 与容器运行选项**

---

## 0. 先直接体验

1. 创建一个 `Dockerfile` 文件
2. 文件的内容如下

```dockerfile
# 使用官方 Nginx 镜像
FROM nginx

# 直接写入一个简单的 HTML 文件
RUN echo "<h1>Hello world from Docker!</h1>" \
    > /usr/share/nginx/html/index.html
```

3. 执行指令 `docker build -t my-nginx-html .`
4. 执行 `docker run -d -p 8080:80 my-nginx-html`
5. 打开 `http://localhost:8080`

![dockerfile-demo-logs](/api/v1/website/image/docker/dockerfile-demo-logs.png)

![dockerfile-demo-html-preview](/api/v1/website/image/docker/dockerfile-demo-html-preview.png)



## 1. Dockerfile 是定义镜像构建流程的脚本 

🐳 Dockerfile 是一份文本脚本，按序定义镜像构建流程。

### 几个常用的指令


| 指令            | 作用                                   |
| ------------- | ------------------------------------ |
| `FROM`        | 指定基础镜像，必需。                           |
| `WORKDIR`     | 切换/创建工作目录；后续指令在此执行。                  |
| `COPY`/`ADD`  | 拷贝文件到镜像；`ADD` 支持 URL 和自动解压 tar 包。    |
| `RUN`         | 执行命令（安装依赖、编译等），生成新镜像层。               |
| `ENV`         | 设置环境变量，影响后续构建和运行时环境。                 |
| `ARG`         | 构建参数，仅在 build 阶段可用，不会保留到最终镜像。        |
| `EXPOSE`      | 声明容器运行时监听的端口（文档化作用，需配合端口映射）。         |
| `VOLUME`      | 定义数据卷挂载点，用于持久化或共享数据。                 |
| `ENTRYPOINT`  | 设置容器入口点，可配合 `CMD` 传递参数，不易被覆盖。        |
| `CMD`         | 默认启动命令，可被 `docker run` 或 Compose 覆盖。 |
| `HEALTHCHECK` | 定义健康检查命令，Docker 定期运行判断服务状态。          |

**刚刚的示例就是一个最小的指定要构建什么样的docker镜像的流程**：

```dockerfile
# 使用官方 Nginx 镜像
FROM nginx

# 直接写入一个简单的 HTML 文件
RUN echo "<h1>Hello world from Docker!</h1>" \
    > /usr/share/nginx/html/index.html
```

### 再看下其他的内容 

如果能成功的打开了刚刚体验的网页 那么我们输入下面指令看看

1. 执行 `docker images` 看看

```bash
pldz:~/local/docker-demo$ docker images
REPOSITORY                                        TAG       IMAGE ID       CREATED         SIZE
my-nginx-html                                     latest    7b2a8ce8091b   3 minutes ago   192MB
```

2. 执行 `docker ps -a` 看看

```bash
pldz:~/local/docker-demo$ docker ps -a
CONTAINER ID   NAMES               STATUS
fe34ca2893c0   blissful_roentgen   Up 5 minutes
```

好了 如果能成功看见这些信息 那我们进入下一步 看看这些都是什么意思.


### 什么是镜像/容器/标签

* **镜像（Image）**：只读模板，包含操作系统层、依赖和应用代码，用于创建容器。
* **容器（Container）**：镜像的可运行实体，拥有独立的文件系统、网络和进程空间。
* **标签（Tag）**：镜像的可读名称后缀，格式为 `name:tag`，用于区分不同版本或变体。
---


## 2. 构建 docker 镜像


### 概念背书 😵‍💫 

在 Docker 里，可以用 `docker build`（或同义的 `docker image build`）基于 Dockerfile 做可重现的单平台构建；用 `docker buildx build` 利用 BuildKit 做多平台、高级缓存的构建；用 `docker commit` 将运行中容器快照成镜像（不可重现，仅用于快速实验）；用 `docker load`／`docker import` 从 tar 包恢复或导入镜像。下表对比了各命令的来源、可重现性和典型场景：

| 命令                                    | 构建来源                    | 可重现性      | 典型场景              |
| ------------------------------------- | ----------------------- | --------- | ----------------- |
| `docker build` / `docker image build` | Dockerfile + 上下文        | 高         | 本地常规单平台构建         |
| `docker buildx build`                 | Dockerfile + 上下文        | 更高（支持多平台） | 多架构镜像构建，CI/CD 流水线 |
| `docker commit`                       | 运行中容器                   | 低         | 实验调试、快速快照         |
| `docker load`                         | `docker save` 导出的 tar 包 | 与导出时一致    | 恢复或迁移镜像           |
| `docker import`                       | 任意格式的 tar 包             | 取决于来源     | 从非标准 tar 导入镜像     |



### `docker build` 与常用选项

```bash
docker build [OPTIONS] -t <image_name>:<tag> <context_dir>
```

* `-t name:tag`：为镜像命名并打标签。
* `-f Dockerfile`：指定 Dockerfile 文件。
* `--target stage`：在多阶段构建中仅构建指定阶段。
* `--build-arg KEY=VALUE`：传递构建参数。

**示例**：

```bash
docker build -t my-nginx-html .
```

---

## 3. 运行 docker 镜像


### 概念背书 😵‍💫 

把镜像“跑起来”主要可以分为四大类方式：

* **单机命令**：直接在本地创建并启动容器；
* **Compose 编排**：使用 `docker-compose` 管理多容器应用；
* **Swarm/集群**：在 Docker Swarm 模式下部署服务；
* **云原生/Kubernetes**：通过 Kubernetes 或 Helm 在集群中调度。

| 类别             | 命令／工具                             | 说明                                   |
| -------------- | --------------------------------- | ------------------------------------ |
| **单机命令**       | `docker run`                      | 一步到位，创建并启动新容器                        |
|                | `docker create` + `docker start`  | 分步：先建容器（不启动）、再启动；更灵活地分离创建与运行         |
|                | `docker exec`                     | 在已运行容器内执行命令（常用 `-it sh` 进入交互式 Shell） |
|                | `docker Desktop`（GUI）             | 通过图形界面点击启动                           |
| **Compose 编排** | `docker-compose up`               | 基于 `docker-compose.yml` 一键启动/重建多容器服务 |
|                | `docker compose up`               | Docker 官方新版 CLI 插件形式                 |
| **Swarm/集群**   | `docker swarm init`               | 初始化 Swarm 集群                         |
|                | `docker service create`           | 在 Swarm 上部署单个服务                      |
|                | `docker stack deploy`             | 根据 Compose 文件部署完整应用栈                 |
| **云原生/K8s**    | `kubectl run`                     | 最基本的单 Pod 运行命令                       |
|                | `kubectl apply -f deployment.yml` | 用 Deployment/YAML 描述启动容器组            |
|                | `helm install`                    | 通过 Helm Chart 安装、升级复杂应用              |
|                | `k3s` / `minikube`                | 本地 Kubernetes 发行版，可用同样命令跑起镜像         |

每种方式都有自己适用的场景：

1. **快速测试或开发**：用 `docker run`／`docker exec`；
2. **本地多容器依赖**：用 Compose；
3. **多主机高可用**：用 Swarm；
4. **生产级云原生**：用 Kubernetes 或 Helm。



### `docker run` 与容器运行选项 

```bash
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```

* `-d`：后台运行。
* `-p hostPort:containerPort`：端口映射。
* `--name NAME`：指定容器名称。
* `-v hostPath:containerPath[:ro|rw]`：挂载卷或主机目录。
* `--env KEY=VALUE`：设置环境变量。
* `--env-file path`：从文件加载环境变量。
* `--rm`：容器停止后自动删除。
* `--network NETWORK`：指定网络模式。

**示例**：

```bash
docker run -d -p 8080:80 my-nginx-html
```

---