import os
from fastapi import FastAPI, Request
from fastapi.routing import Mount, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


from core import ProjectConfig, Logger
from scripts.codespace.load_codespace import CodeSpaceHandler

TEMPLATE_PATH = ProjectConfig.get_templates_path()
CODE_SPACE_ROUTER = APIRouter(prefix="/api/v1/codespace", tags=["codespace"])

# 实例化 Codespace 处理器
codespace_handler = CodeSpaceHandler()


def mount_codespace_app(main_app: FastAPI):
    """
    加载 Codespace 应用
    """
    items = codespace_handler.get_codespace_items()

    for item in items:
        try:
            template_dir = os.path.join(TEMPLATE_PATH, item['folder'])
            if not os.path.exists(template_dir):
                raise FileNotFoundError(f"Template folder '{template_dir}' does not exist.")

            app = FastAPI()
            templates = Jinja2Templates(directory=template_dir)
            app.mount("/assets", StaticFiles(directory=os.path.join(template_dir, "assets")), name="assets")

            # 这里通过默认参数把 templates 绑定进来, 避免闭包
            @app.get("/", response_class=HTMLResponse)
            async def index(request: Request, templates=templates):
                return templates.TemplateResponse("index.html", {"request": request})

            main_app.mount(f"/io/{item['url']}/", app, name=item['title'])
        except FileNotFoundError as e:
            Logger.error(f"Error mounting codespace app '{item['title']}': {e}")
            continue


def unmount_codespace_app(main_app: FastAPI):
    """
    卸载 Codespace 应用
    """
    items = codespace_handler.get_codespace_items()
    try:
        for item in items:
            prefix = f"/io/{item['folder']}"

            # 1. 从 routes 里移除对应的 Mount
            main_app.router.routes = [
                route
                for route in main_app.router.routes
                if not (isinstance(route, Mount) and route.path.startswith(prefix))
            ]

            # 2. （可选）从 user_mounts 里也删掉同名挂载
            if item['title'] in main_app.user_mounts:
                main_app.user_mounts.pop(item['title'])
    except Exception as e:
        Logger.error(f"Error unmounting codespace app '{item['title']}': {e}")
        return False


@CODE_SPACE_ROUTER.get("/all")
async def get_all_codespace_items():
    """
    获取所有 Codespace 项目
    """
    items = codespace_handler.get_codespace_items()
    return {"data": items}
