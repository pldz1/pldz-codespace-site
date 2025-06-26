import os
import uvicorn

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from .user import USER_ROUTE
from .chat import CHAT_ROUTE
from .image import IMAGE_ROUTE

from scripts.libs import CONF
from scripts.database import USER_DATABASE, CHAT_DATABASE, IMAGE_DATABASE


@asynccontextmanager
async def lifespan(app=FastAPI):
    # startup: initialize resources
    await USER_DATABASE.initialize()
    await CHAT_DATABASE.initialize()
    await IMAGE_DATABASE.initialize()
    yield
    # shutdown: clean up resources
    await USER_DATABASE.destroy()
    await CHAT_DATABASE.destroy()
    await IMAGE_DATABASE.destroy()

# 设置生命周期的行为
app = FastAPI(lifespan=lifespan)
# 挂载路由
app.include_router(USER_ROUTE, prefix="/io/chat-playground-v1", tags=["user"])
app.include_router(CHAT_ROUTE, prefix="/io/chat-playground-v1", tags=["chat"])
app.include_router(IMAGE_ROUTE, prefix="/io/chat-playground-v1", tags=["image"])


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
    uvicorn.run(app, host=CONF.host, port=CONF.port)


def run_main():
    '''
    运行服务时候挂载静态资源, 注意这个内容现在都被加入到一个进程来运行
    '''
    statics_path = CONF.get_statics_path()
    if not os.path.exists(statics_path):
        errorMsg = f"Failed to start the server with static files: no static resources found {statics_path}"
        raise FileNotFoundError(errorMsg)

    # 挂载静态资源
    from fastapi.staticfiles import StaticFiles
    app.mount("/io/chat-playground-v1", StaticFiles(directory=CONF.get_statics_path(),
              html=True), name="static")
    uvicorn.run(app, host=CONF.host, port=CONF.port)
