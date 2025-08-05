# --------- 1: 构建后端 ----------
FROM python:3.11-slim AS backend
WORKDIR /usr/src/app

# 拷贝并安装后端依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


# --------- 2：安装 git ----------
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends git ca-certificates \
  && rm -rf /var/lib/apt/lists/*

COPY .gitconfig /root/.gitconfig