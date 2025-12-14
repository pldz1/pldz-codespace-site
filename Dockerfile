# --------- 1: 构建后端 ----------
FROM python:3.11-slim AS backend
WORKDIR /usr/src/app

# 拷贝并安装后端依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


# --------- 2：安装 git ----------
RUN rm -f /etc/apt/sources.list.d/debian.sources \
 && echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ trixie main contrib non-free non-free-firmware\n\
deb https://mirrors.tuna.tsinghua.edu.cn/debian-security trixie-security main contrib non-free non-free-firmware\n\
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ trixie-updates main contrib non-free non-free-firmware" > /etc/apt/sources.list \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends git ca-certificates -o Dpkg::Progress-Fancy=1 \
 && rm -rf /var/lib/apt/lists/*

COPY .gitconfig /root/.gitconfig