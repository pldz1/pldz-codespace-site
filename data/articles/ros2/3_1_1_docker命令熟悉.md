---
author: admin@pldz1.com
category: ros2
date: '2025-01-01'
serialNo: 201
status: publish
summary: Docker搭建ROS2环境, 和Docker指令的熟悉.
tags:
- ROS2智能车
thumbnail: /api/v1/website/image/ros2/1_ros2_docker_basic_thumbnail.jpg
title: Docker 搭建 ROS2 嵌入式运行环境
---

# 1.1 安装 docker

# 1.2 docker 安装并配置 ubuntu20

1. 拉取 docker 镜像：`sudo docker pull ubuntu:20.04`

2. 启动镜像： `docker run --rm -it --network=host ubuntu:20.04`

> - `docker run` 是用于运行容器的 Docker 命令。
> - `--rm` 标志用于在容器停止后自动删除容器。这可以确保每次运行容器时都会清理掉容器，以避免产生无用的容器。
> - `-it` 是两个标志的结合。`-i` 标志表示保持标准输入(stdin)打开，使得你可以与容器进行交互。`-t` 标志表示为容器分配一个伪终端(pseudo-TTY)，以便你可以在命令行中与容器进行交互。
> - `--network=host` 标志用于将容器与主机共享网络命名空间。这意味着容器将与主机共享网络接口，可以访问主机上的网络资源。
> - `ubuntu:20.04` 是指定要运行的容器镜像。在这个例子中，使用的是基于 Ubuntu 20.04 的镜像

3. docker 内更新这样才能使用 apt-get 安装软件:`apt-get update`

```shell
jeston@jeston-desktop:~$ sudo docker run --rm -it --network=host ubuntu:20.04
root@jeston-desktop:/# uname -a
Linux jeston-desktop 4.9.253-tegra #1 SMP PREEMPT Sat Feb 19 08:59:22 PST 2022 aarch64 aarch64 aarch64 GNU/Linux
root@jeston-desktop:/# apt-get update
```

4. 安装基本软件：`apt-get install vim net-tools iputils-ping lsof`

5. 学会保存 docker 的状态：[保存对容器的修改](https://www.docker.org.cn/book/docker/docer-save-changes-10.html)

- 新开一个终端获取 docker 的 id:

```shell
sudo docker ps -l
```

![1_查看docker容器的id](/api/v1/website/image/ros2/1_get_docker_container_id.png)

- 根据 id 进行 commit, 如果 commit 的内容和原来的 docker 的 tag 一致，那么会替换掉之前 docker 的内容，达到保存的效果

```shell
sudo docker commit <commit id> <tag>
```

![1_保存docker镜像](/api/v1/website/image/ros2/1_save_docker_image.png)

# 1.3 docker 内 Ubuntu20.04 安装 ros2-foxy

1. 启动 docker 内的 Ubuntu20.04:

```shell
docker run --rm -it --network=host ubuntu:20.04
```

2. 输入 locale 查看是否支持 utf-8, 如果不支持要安装:

```shell
apt update && apt install locales && locale-gen en_US en_US.UTF-8 && update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 && export LANG=en_US.UTF-8
```

3. 添加 ROS2 GPG 密钥：如果出现 403 问题 查看[1 ROS2 介绍安装与快速体验](https://blog.csdn.net/qq_42727752/article/details/130277029)

```shell
apt update && apt install curl -y && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
```

4. 添加 ros 源：

```shell
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

5. 开始安装 ros2-foxy:

```shell
apt-get update && apt-get upgrade && apt-get install ros-foxy-desktop
```

6. 安装完成之后, 新建一个终端，找到当前 docker 的 id 之后，保存 docker 镜像状态

```shell

```