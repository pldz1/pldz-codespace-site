import os
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from core import ProjectConfig

from .article import ARTICLES_ROUTE
from .image import IMAGES_ROUTE
from .authorization import AUTH_ROUTER
from .codespace import CODE_SPACE_ROUTER, mount_codespace_app
from .resource import RESOURCE_ROUTE


# 生命周期具体执行的内容
@asynccontextmanager
async def lifespan(app=FastAPI):
    yield

# 设置生命周期的行为
app = FastAPI(lifespan=lifespan)
# 挂载路由
app.include_router(ARTICLES_ROUTE)
app.include_router(IMAGES_ROUTE)
app.include_router(AUTH_ROUTER)
app.include_router(CODE_SPACE_ROUTER)
app.include_router(RESOURCE_ROUTE)

# 挂载其他的应用
# 用法: app.mount("/path", other_app)
mount_codespace_app(app)


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

    host = os.environ.get('HOST', "127.0.0.1")
    port = int(os.environ.get('PORT', 10058))

    uvicorn.run(app, host=host, port=port)


def run_main():
    '''
    运行服务时候挂载静态资源, 注意这个内容现在都被加入到一个进程来运行
    '''
    statics_path = ProjectConfig.get_statics_path()

    # 挂载静态资源目录
    @app.get("/{full_path:path}")
    async def _(full_path: str):
        # 构造静态文件的真实路径
        file_path = os.path.join(statics_path, full_path)
        # 若静态文件存在，则直接返回
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # 否则返回 index.html，由前端路由接管
        index_path = os.path.join(statics_path, "index.html")
        return FileResponse(index_path)

    # 挂载静态资源

    host = os.environ.get('HOST', "127.0.0.1")
    port = int(os.environ.get('PORT', 10058))

    uvicorn.run(app,
                host=host,
                port=port)
