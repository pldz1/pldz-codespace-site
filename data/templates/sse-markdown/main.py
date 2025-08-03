# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

app = FastAPI()

# 当前路径
current_path = os.path.dirname(os.path.abspath(__file__))

# 挂载 statics 目录，html=True 会让 / 或找不到的路径自动返回 index.html
app.mount(
    "/io/sse-markdown",
    StaticFiles(directory=os.path.join(current_path, 'statics'), html=True),
    name="static"
)

if __name__ == "__main__":
    # 启动 Uvicorn 服务，绑定到 0.0.0.0:10078
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=10078,
    )
