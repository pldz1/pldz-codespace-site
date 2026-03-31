# --------- 1: 构建后端 ----------
FROM python:3.11-slim AS backend
WORKDIR /usr/src/app

# 拷贝并安装后端依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple