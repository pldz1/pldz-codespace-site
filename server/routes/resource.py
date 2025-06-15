import os
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from core import ProjectConfig, Logger
from scripts.filesystem import NavInfoHandler

RESOURCE_ROUTE = APIRouter(prefix="/resource", tags=["resource"])
# 实例化 Codespace 处理器
NAV_INFO_HANDLE = NavInfoHandler()


def get_html_template(html_content: str) -> str:
    """
    获取 HTML 模板内容
    :param html_content: 要显示的 HTML 内容
    :return: 完整的 HTML 模板字符串
    """
    html = f"""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
        <title>爬楼的猪 CodeSpace 条款</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2rem; line-height: 1.6; }}
            pre {{ white-space: pre-wrap; }}
        </style>
    </head>
    <body>
        <pre>{html_content}</pre>
    </body>
    </html>
    """
    return html


@RESOURCE_ROUTE.get('/privacy_policy')
async def get_privacy_policy():
    """
    获取隐私政策
    :return: 隐私政策内容
    """
    # HTML 模板内容

    resource_path = ProjectConfig.get_resource_path()
    file_path = os.path.join(resource_path, 'privacy_policy.txt')
    if not os.path.exists(file_path):
        Logger.error(f"隐私政策文件未找到: {file_path}")
        html_response = get_html_template("隐私政策文件未找到")
        return HTMLResponse(content=html_response, status_code=404)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content:
        Logger.error(f"隐私政策文件内容为空: {file_path}")
        html_response = get_html_template("隐私政策文件内容为空")
        return HTMLResponse(content=html_response, status_code=404)

    # 将内容转换为 HTML 格式
    html_content = content.replace("\n", "<br>")
    html_response = get_html_template(html_content)

    return HTMLResponse(content=html_response, status_code=200)


@RESOURCE_ROUTE.get('/user_agreement')
async def get_user_agreement():
    """
    获取用户协议
    :return: 用户协议内容
    """
    # HTML 模板内容

    resource_path = ProjectConfig.get_resource_path()
    file_path = os.path.join(resource_path, 'user_agreement.txt')
    if not os.path.exists(file_path):
        Logger.error(f"用户协议文件未找到: {file_path}")
        html_response = get_html_template("用户协议文件未找到")
        return HTMLResponse(content=html_response, status_code=404)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content:
        Logger.error(f"用户协议文件内容为空: {file_path}")
        html_response = get_html_template("用户协议文件内容为空")
        return HTMLResponse(content=html_response, status_code=404)

    # 将内容转换为 HTML 格式
    html_content = content.replace("\n", "<br>")
    html_response = get_html_template(html_content)

    return HTMLResponse(content=html_response, status_code=200)
