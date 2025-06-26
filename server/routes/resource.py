import os
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Depends, status
from fastapi.responses import HTMLResponse, FileResponse

from core import ProjectConfig, Logger
from scripts.filesystem import CacheCurdHandle
from scripts.mongodb import AuthorizedHandler


RESOURCE_ROUTE = APIRouter(prefix="/resource", tags=["resource"])


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
async def api_get_privacy_policy():
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
async def api_get_user_agreement():
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


@RESOURCE_ROUTE.get('/cache/all')
async def api_get_all_cache_files(user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    获取所有缓存文件
    :param user: 当前用户信息
    :return: 缓存文件列表
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to access cache files."
        )

    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access cache files."
        )

    cache_files = CacheCurdHandle.get_all_cache_files()
    return {"data": cache_files}


class CacheDataRequest(BaseModel):
    filename: str


@RESOURCE_ROUTE.post('/cache/download')
async def api_download_cache_file(request: CacheDataRequest, user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    下载指定的缓存文件
    :param request: 请求体，包含要下载的文件名
    :param request.filename: 要下载的缓存文件名
    :param user: 当前用户信息
    :return: 缓存文件内容
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to download cache files."
        )

    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to download cache files."
        )

    filename = request.filename.strip()
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename must be provided."
        )

    file_path = CacheCurdHandle.get_cache_file(filename)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cache file '{filename}' not found."
        )

    return FileResponse(file_path, media_type='application/octet-stream', filename=filename)


@RESOURCE_ROUTE.post('/cache/delete')
async def api_delete_cache_file(request: CacheDataRequest, user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    删除指定的缓存文件
    :param request: 请求体，包含要删除的文件名
    :param request.filename: 要删除的缓存文件名
    :param user: 当前用户信息
    :return: 删除结果
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to delete cache files."
        )

    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete cache files."
        )

    filename = request.filename.strip()
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename must be provided."
        )

    success = CacheCurdHandle.delete_cache_file(filename)
    return {"data": success}


@RESOURCE_ROUTE.post('/cache/upload')
async def api_upload_cache_file(
    file: UploadFile = File(...),
    user: dict = Depends(AuthorizedHandler.get_current_user)
):
    """
    上传缓存文件
    :param file: 要上传的文件
    :param user: 当前用户信息
    :return: 上传结果
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to upload cache files."
        )

    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to upload cache files."
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename must be provided."
        )

    try:
        flag = CacheCurdHandle.save_cache_file(file.filename, await file.read())
        return {"data": flag}
    except Exception as e:
        Logger.error(f"上传缓存文件失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")
