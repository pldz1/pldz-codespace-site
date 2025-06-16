import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


from core import ProjectConfig

TEMPLATE_PATH = ProjectConfig.get_templates_path()


# 挂载一个AIGC Playground V1 的应用
AIGC_PLAYGROUND_V1_APP = FastAPI()
AIGC_PLAYGROUND_V1_TEMPLATE_PATH = os.path.join(TEMPLATE_PATH, "aigc_playground_v1")
AIGC_PLAYGROUND_V1_TEMPLATE = Jinja2Templates(directory=AIGC_PLAYGROUND_V1_TEMPLATE_PATH)
AIGC_PLAYGROUND_V1_APP.mount("/assets", StaticFiles(directory=os.path.join(AIGC_PLAYGROUND_V1_TEMPLATE_PATH, "assets")), name="assets")


@AIGC_PLAYGROUND_V1_APP.get("/", response_class=HTMLResponse)
async def aigc_v1_home(request: Request):
    return AIGC_PLAYGROUND_V1_TEMPLATE.TemplateResponse("index.html", {"request": request})


# 挂载一个 Markdown SSE 的应用
MD_SSE_APP = FastAPI()
MD_SSE_TEMPLATE_PATH = os.path.join(TEMPLATE_PATH, "sse_markdown")
MD_SSE_TEMPLATE = Jinja2Templates(directory=MD_SSE_TEMPLATE_PATH)
MD_SSE_APP.mount("/assets", StaticFiles(directory=os.path.join(MD_SSE_TEMPLATE_PATH, "assets")), name="assets")


@MD_SSE_APP.get("/", response_class=HTMLResponse)
async def sse_md_home(request: Request):
    return MD_SSE_TEMPLATE.TemplateResponse("index.html", {"request": request})
