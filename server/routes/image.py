import os
import mimetypes
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from core import Logger, ProjectConfig

IMAGES_ROUTE = APIRouter()


@IMAGES_ROUTE.get("/images/{category}/{image}")
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
