# --------- 1：构建前端 ----------
FROM node:22 AS frontend-builder
WORKDIR /usr/src/app/web

# 拷贝 package.json 文件并安装依赖
COPY web/package*.json ./
RUN npm install


# --------- 2：构建后端 ----------
FROM python:3.11-slim AS backend
WORKDIR /usr/src/app

# 拷贝并安装后端依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
