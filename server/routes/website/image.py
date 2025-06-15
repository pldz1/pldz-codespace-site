import mimetypes
from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Depends, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core import Logger
from scripts.mongodb import AuthorizedHandler
from scripts.filesystem import ImageCrudHandler

IMAGES_ROUTE = APIRouter(prefix="/website/image", tags=["website-image"])


@IMAGES_ROUTE.get("/{category}/{image}")
async def api_get_image(category: str, image: str):
    """
    获取指定分类下的图片
    :param category: 图片分类
    :param image: 图片文件名
    """
    try:
        path = ImageCrudHandler.get_image_path(category, image)
        media_type, _ = mimetypes.guess_type(path)
    except Exception as e:
        Logger.error(f"获取图片失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

    return FileResponse(path, media_type=media_type or "application/octet-stream")


class ImageCategoryData(BaseModel):
    category: str


@IMAGES_ROUTE.post("/category/all")
async def api_post_all_images(category: ImageCategoryData, user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    获取指定分类下的所有图片
    :param category: 图片分类
    """
    # 验证用户是否已登录
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to sync articles."
        )

    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to sync articles."
        )

    try:
        images = ImageCrudHandler.get_all_images(category.category)
    except Exception as e:
        Logger.error(f"获取所有图片失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

    return {"data": images}


class ImageRenameData(BaseModel):
    category: str
    oldName: str
    newName: str


@IMAGES_ROUTE.post("/rename")
async def api_rename_image(
    payload: ImageRenameData,
    user: dict = Depends(AuthorizedHandler.get_current_user)
):
    """
    重命名指定分类下的图片
    :param payload: 包含分类和新旧图片名的请求体
    :param user: 当前用户
    """
    # 验证用户是否已登录
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to sync articles."
        )

    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to sync articles."
        )

    if any(sep in payload.newName for sep in ("..", "/", "\\")):
        raise HTTPException(400, "非法文件名")

    try:
        new_name = ImageCrudHandler.rename_image(payload.category, payload.oldName, payload.newName)
    except HTTPException:
        # 如果 handler 已经抛了 HTTPException，就直接 re-raise
        raise
    except Exception as e:
        Logger.error(f"重命名图片失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误，重命名失败")

    return {"data": {"flag": True, "new_name": new_name}}


class ImageData(BaseModel):
    category: str
    name: str


@IMAGES_ROUTE.post("/delete")
async def api_delete_image(
    payload: ImageData,
    user: dict = Depends(AuthorizedHandler.get_current_user)
):
    """
    删除指定分类下的图片
    :param payload: 包含分类和图片名的请求体
    :param user: 当前用户
    """
    # 验证用户是否已登录
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to sync articles."
        )

    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to sync articles."
        )

    try:
        success = ImageCrudHandler.delete_image(payload.category, payload.name)
        if not success:
            raise HTTPException(status_code=404, detail="图片未找到")
    except HTTPException:
        # 如果 handler 已经抛了 HTTPException，就直接 re-raise
        raise
    except Exception as e:
        Logger.error(f"删除图片失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误，删除失败")

    return {"data": {"flag": True}}


@IMAGES_ROUTE.post("/upload/avatar")
async def api_upload_avatar(
    file: UploadFile = File(...),
    name: str = Form(...),
    user: dict = Depends(AuthorizedHandler.get_current_user)
):
    """
    上传用户头像
    :param file: 上传的文件
    :param name: 文件名
    :param user: 当前用户
    """
    # 验证用户是否已登录

    if not user:
        raise HTTPException(403, "未授权的用户")
    if any(sep in name for sep in ("..", "/", "\\")):
        raise HTTPException(400, "非法文件名")

    data = await file.read()
    try:
        saved_name = ImageCrudHandler.save_avatar(data, file.filename, user.get("username", "unknown"))
    except HTTPException:
        # 如果 handler 已经抛了 HTTPException，就直接 re-raise
        raise
    except Exception as e:
        Logger.error(f"保存头像失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误，头像保存失败")

    url = f"/api/v1/image/avatar/{saved_name}"
    return {"data": {"flag": True, "url": url}}


@IMAGES_ROUTE.post("/upload/article")
async def api_upload_article_image(
    file: UploadFile = File(...),
    category: str = Form(...),
    name: str = Form(...),
    user: dict = Depends(AuthorizedHandler.get_current_user)
):
    """
    上传文章图片
    :param file: 上传的文件
    :param category: 图片分类
    :param name: 文件名
    :param user: 当前用户
    """
    # 验证用户是否已登录
    if not user:
        raise HTTPException(403, "未授权的用户")
    if any(sep in name for sep in ("..", "/", "\\")):
        raise HTTPException(400, "非法文件名")

    data = await file.read()
    try:
        saved_name = ImageCrudHandler.save_article_image(data, category, name, file.filename)
    except Exception as e:
        Logger.error(f"保存文章图片失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误，图片保存失败")

    url = f"/api/v1/image/{category}/{saved_name}"
    return {"data": {"flag": True, "url": url}}


class ImageCheck(BaseModel):
    category: str
    name: str


@IMAGES_ROUTE.post("/upload/check")
async def api_check_image_exist(
    payload: ImageCheck,
    user: dict = Depends(AuthorizedHandler.get_current_user)
):
    """
    检查指定分类下的图片是否已存在
    :param payload: 包含分类和图片名的请求体
    :param user: 当前用户
    """
    # 验证用户是否已登录
    if not user:
        raise HTTPException(403, "未授权的用户")
    exists = ImageCrudHandler.check_exists(payload.category, payload.name)
    return {"data": not exists}
