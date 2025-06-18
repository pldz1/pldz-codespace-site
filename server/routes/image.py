import os
import mimetypes
from uuid import uuid4
from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from core import Logger, ProjectConfig
from pathlib import Path

from scripts.mongodb import AuthorizedHandler

IMAGES_ROUTE = APIRouter(prefix="/api/v1/image", tags=["image"])


@IMAGES_ROUTE.get("/{category}/{image}")
async def api_get_image(category: str, image: str):
    """
    获取指定分类下的图片文件
    Args:
        category (str): 图片分类
        image (str): 图片文件名
    Returns:
        FileResponse: 图片文件
    """
    # 根图片目录
    image_folder = ProjectConfig.get_images_path()
    image_path = os.path.join(image_folder, category, image)

    # 防止路径遍历
    abs_image_path = os.path.abspath(image_path)
    base_path = os.path.abspath(image_folder) + os.sep
    if not abs_image_path.startswith(base_path):
        Logger.error(f"非法路径访问: {abs_image_path}")
        raise HTTPException(status_code=400, detail="非法的图片路径")

    # 检查文件是否存在
    if not os.path.isfile(abs_image_path):
        Logger.error(f"图片未找到: {abs_image_path}")
        raise HTTPException(status_code=404, detail="图片未找到")

    # 自动推断 Content-Type
    media_type, _ = mimetypes.guess_type(abs_image_path)
    return FileResponse(abs_image_path, media_type=media_type or "application/octet-stream")


@IMAGES_ROUTE.post("/upload/avatar")
async def api_upload_image_avatar(file: UploadFile = File(...), name: str = Form(...), user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    """
    # 受保护的请求 需要判断身份
    if not user:
        raise HTTPException(status_code=403, detail="未授权的用户")

    # 安全检查：避免文件名穿越攻击
    if any(sep in name for sep in ("..", "/", "\\")):
        raise HTTPException(status_code=400, detail="非法文件名")

    # 提取后缀，如 ".jpg"
    suffix = Path(file.filename).suffix or ""

    # 生成存储目录
    images_dir = Path(ProjectConfig.get_images_path())
    avatar_dir = images_dir / "avatar"

    # 清理并校验 name
    valid_name = name.strip().replace(".", "_") + "_" + uuid4().hex[:8]
    target_path = avatar_dir / f"{valid_name}{suffix}"

    try:
        # 创建目录（如果不存在）
        avatar_dir.mkdir(parents=True, exist_ok=True)

        # 保存文件内容
        contents = await file.read()
        target_path.write_bytes(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {e}")

    return {"data": True, "url": f"/api/v1/image/avatar/{valid_name}{suffix}"}


@IMAGES_ROUTE.post("/upload/article")
async def api_upload_image_article(
        file: UploadFile = File(...),
        category: str = Form(...),
        name: str = Form(...),
        user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    获取指定分类下的文章图片
    Args:
        file (UploadFile): 上传的文件
        category (str): 图片分类
        name (str): 图片文件名
        user (dict): 当前用户信息
    Returns:
        dict: 包含上传结果和图片 URL
    """
    # 受保护的请求 需要判断身份
    if not user:
        raise HTTPException(status_code=403, detail="未授权的用户")
    # 安全检查：避免文件名穿越攻击
    if any(sep in name for sep in ("..", "/", "\\")):
        raise HTTPException(status_code=400, detail="非法文件名")

    # 提取后缀，如 ".jpg"
    suffix = Path(file.filename).suffix or ""

    # 生成存储目录
    images_dir = Path(ProjectConfig.get_images_path())
    category_dir = images_dir / category

    # 清理并校验 name
    valid_name = name.strip().replace(".", "_")
    target_path = category_dir / f"{valid_name}{suffix}"

    try:
        # 创建目录（如果不存在）
        category_dir.mkdir(parents=True, exist_ok=True)

        # 保存文件内容
        contents = await file.read()
        target_path.write_bytes(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {e}")

    return {"data": True, "url": f"/api/v1/image/{category}/{valid_name}{suffix}"}


class ImageCheck(BaseModel):
    category: str
    name: str


@IMAGES_ROUTE.post("/upload/check")
async def api_check_image_exit(
        payload: ImageCheck,
        user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    """
    if not user:
        raise HTTPException(status_code=403, detail="未授权的用户")

    category, name = payload.category, payload.name
    images_dir = Path(ProjectConfig.get_images_path())
    category_dir = images_dir / category

    # 读取 category_dir 的全部文件的去掉后缀的文件名称, 如果和 name 一样返回false
    category_dir.mkdir(parents=True, exist_ok=True)

    existing_stems = {p.stem for p in category_dir.iterdir() if p.is_file()}
    if name in existing_stems:
        # Name already taken
        return {"data": False}

    return {"data": True}
