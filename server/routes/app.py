import os
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware


from .authorization import AUTH_ROUTER
from .resource import RESOURCE_ROUTE
from .website import (
    ARTICLES_ROUTE,
    IMAGES_ROUTE,
    COMMENTS_ROUTE,
    WHITEBOARD_ROUTE,
    LIVEDEMO_ROUTER,
)


# 生命周期具体执行的内容
@asynccontextmanager
async def lifespan(app=FastAPI):
    yield

# 设置生命周期的行为
app = FastAPI(lifespan=lifespan)
# 挂载路由

app.include_router(AUTH_ROUTER, prefix="/api/v1")
app.include_router(RESOURCE_ROUTE, prefix="/api/v1")

app.include_router(ARTICLES_ROUTE, prefix="/api/v1")
app.include_router(IMAGES_ROUTE, prefix="/api/v1")
app.include_router(COMMENTS_ROUTE, prefix="/api/v1")
app.include_router(WHITEBOARD_ROUTE, prefix="/api/v1")
app.include_router(LIVEDEMO_ROUTER, prefix="/api/v1")


def start_dev():
    '''
    设置开发模式下的一些web server的配置
    '''
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,   # 允许携带 Cookie
        allow_origin_regex=".*",  # 允许所有域名（解决 credentials 不能使用 "*" 的问题）
        allow_methods=["*"],      # 允许所有 HTTP 方法
        allow_headers=["*"],      # 允许所有 HTTP 头部
    )


def run_dev():
    '''
    启动fastapi webserver 服务
    '''
    start_dev()

    host = os.environ.get('SITE_HOST', "127.0.0.1")
    port = int(os.environ.get('SITE_PORT', 10058))

    uvicorn.run(app, host=host, port=port)
