import hashlib
import mimetypes
import re
from pathlib import Path

from fastapi import (
    APIRouter,
    HTTPException,
    File,
    UploadFile,
    Form,
    Depends,
    status,
    Query,
    Request,
)
from fastapi.responses import FileResponse
from PIL import Image, ImageSequence, ImageOps, UnidentifiedImageError
from pydantic import BaseModel

from core import Logger, ProjectConfig
from scripts.db import AuthorizedHandler
from scripts.filesystem import ImageCrudHandler

IMAGES_ROUTE = APIRouter(prefix="/website/image", tags=["website-image"])

MAX_IMAGE_SIZE = 2000
DEFAULT_IMAGE_WIDTH = 512
DEFAULT_IMAGE_HEIGHT = 512
DEFAULT_IMAGE_QUALITY = 80
CACHE_CONTROL_HEADER = {"Cache-Control": "public, max-age=86400"}
SUPPORTED_OUTPUT_FORMATS = {"webp", "jpeg"}


def _validate_image_request(category: str, image: str) -> None:
    if any(sep in category for sep in ("..", "/", "\\")):
        raise HTTPException(status_code=400, detail="非法的图片分类")
    if any(sep in image for sep in ("..", "/", "\\")):
        raise HTTPException(status_code=400, detail="非法的图片文件名")


def _validate_dimensions(width: int, height: int) -> None:
    if width <= 0 or height <= 0 or width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail=f"非法图片尺寸，宽高必须在 1-{MAX_IMAGE_SIZE} 之间")


def _parse_dimension(value: str) -> int:
    if not re.fullmatch(r"\d{1,4}", value):
        raise HTTPException(status_code=400, detail="非法图片尺寸格式，示例：128x128")
    return int(value)


def _parse_quality(quality: str) -> int:
    if not re.fullmatch(r"\d{1,2}", quality):
        raise HTTPException(status_code=400, detail="非法图片质量，quality 必须在 1-95 之间")
    return int(quality)


def _validate_quality(quality: str) -> int:
    quality_value = _parse_quality(quality)
    if quality_value < 1 or quality_value > 95:
        raise HTTPException(status_code=400, detail="非法图片质量，quality 必须在 1-95 之间")
    return quality_value


def _select_output_format(request: Request, output_format: str | None) -> str:
    if output_format:
        normalized_format = output_format.lower()
        if normalized_format not in SUPPORTED_OUTPUT_FORMATS:
            raise HTTPException(status_code=400, detail="非法图片格式，仅支持 webp/jpeg")
        return normalized_format

    accept = request.headers.get("accept", "")
    if "image/webp" in accept or "*/*" in accept or not accept:
        return "webp"
    return "jpeg"


def _cache_file_path(category: str, image: str, width: int, height: int, quality: int, output_format: str) -> Path:
    cache_dir = Path(ProjectConfig.get_webp_cache_path())
    cache_dir.mkdir(parents=True, exist_ok=True)

    image_key = f"{category}/{image}"
    digest = hashlib.sha256(image_key.encode("utf-8")).hexdigest()[:12]
    safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", Path(image).stem).strip("._") or "image"
    base_name = f"{safe_stem}_{digest}_{width}x{height}"
    if output_format == "webp" and quality == DEFAULT_IMAGE_QUALITY:
        return cache_dir / f"{base_name}.webp"
    return cache_dir / f"{base_name}_q{quality}.{output_format}"


def _resize_keep_ratio(image: Image.Image, width: int, height: int) -> Image.Image:
    frame = ImageOps.exif_transpose(image)
    return ImageOps.contain(frame, (width, height), Image.Resampling.LANCZOS)


def _jpeg_ready(image: Image.Image) -> Image.Image:
    if image.mode in ("RGBA", "LA", "P"):
        image = image.convert("RGBA")
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.getchannel("A"))
        return background
    return image.convert("RGB")


def _save_static_image(source: Image.Image, target: Path, width: int, height: int, quality: int, output_format: str) -> None:
    resized = _resize_keep_ratio(source, width, height)
    if output_format == "jpeg":
        resized = _jpeg_ready(resized)
        resized.save(target, format="JPEG", quality=quality, optimize=True, progressive=True)
        return

    resized.save(target, format="WEBP", quality=quality, method=6)


def _save_animated_webp(source: Image.Image, target: Path, width: int, height: int, quality: int) -> None:
    frames = []
    durations = []
    for frame in ImageSequence.Iterator(source):
        durations.append(frame.info.get("duration", source.info.get("duration", 100)))
        resized = _resize_keep_ratio(frame.convert("RGBA"), width, height)
        frames.append(resized)

    if not frames:
        raise HTTPException(status_code=400, detail="无效的 GIF 图片")

    frames[0].save(
        target,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=source.info.get("loop", 0),
        quality=quality,
        method=6,
    )


def _build_image_response(
    category: str,
    image: str,
    width: int | None,
    height: int | None,
    request: Request,
    quality: str,
    output_format: str | None,
) -> FileResponse:
    _validate_image_request(category, image)
    quality = _validate_quality(quality)
    path = ImageCrudHandler.get_image_path(category, image)

    try:
        with Image.open(path) as source:
            if width is None or height is None:
                width = DEFAULT_IMAGE_WIDTH
                height = DEFAULT_IMAGE_HEIGHT
            _validate_dimensions(width, height)

            selected_format = _select_output_format(request, output_format)
            is_animated = getattr(source, "is_animated", False)
            if is_animated:
                selected_format = "webp"

            cache_path = _cache_file_path(category, image, width, height, quality, selected_format)
            if not cache_path.exists():
                if is_animated:
                    _save_animated_webp(source, cache_path, width, height, quality)
                else:
                    _save_static_image(source, cache_path, width, height, quality, selected_format)
    except HTTPException:
        raise
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="无效的图片文件")
    except Exception as e:
        Logger.error(f"处理图片失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误，图片处理失败")

    media_type = "image/jpeg" if selected_format == "jpeg" else "image/webp"
    return FileResponse(cache_path, media_type=media_type, headers=CACHE_CONTROL_HEADER)


def _build_original_image_response(category: str, image: str) -> FileResponse:
    _validate_image_request(category, image)
    path = ImageCrudHandler.get_image_path(category, image)
    media_type, _ = mimetypes.guess_type(path)
    return FileResponse(
        path,
        media_type=media_type or "application/octet-stream",
        headers=CACHE_CONTROL_HEADER,
    )


@IMAGES_ROUTE.get("/{category}/{image}@{width}x{height}")
async def api_get_resized_image(
    category: str,
    image: str,
    width: str,
    height: str,
    request: Request,
    quality: str = Query(str(DEFAULT_IMAGE_QUALITY)),
    format: str | None = Query(None),
):
    """
    获取指定分类下的压缩图片，按请求尺寸等比缩放并输出 WebP/JPEG。
    :param category: 图片分类
    :param image: 图片文件名
    :param width: 目标宽度
    :param height: 目标高度
    """
    return _build_image_response(
        category,
        image,
        _parse_dimension(width),
        _parse_dimension(height),
        request,
        quality,
        format,
    )


@IMAGES_ROUTE.get("/{category}/{image}@original")
@IMAGES_ROUTE.get("/{category}/{image}@raw")
async def api_get_original_image(category: str, image: str):
    """
    获取指定分类下的原始图片文件，不进行缩放和格式转换。
    :param category: 图片分类
    :param image: 图片文件名
    """
    return _build_original_image_response(category, image)


@IMAGES_ROUTE.get("/{category}/{image}@{size}")
async def api_get_square_resized_image(
    category: str,
    image: str,
    size: str,
    request: Request,
    quality: str = Query(str(DEFAULT_IMAGE_QUALITY)),
    format: str | None = Query(None),
):
    """
    获取指定分类下的压缩图片，单个尺寸参数表示宽高相同。
    :param category: 图片分类
    :param image: 图片文件名
    :param size: 目标宽高
    """
    parsed_size = _parse_dimension(size)
    return _build_image_response(
        category,
        image,
        parsed_size,
        parsed_size,
        request,
        quality,
        format,
    )


@IMAGES_ROUTE.get("/{category}/{image}")
async def api_get_image(
    category: str,
    image: str,
    request: Request,
    quality: str = Query(str(DEFAULT_IMAGE_QUALITY)),
    format: str | None = Query(None),
):
    """
    获取指定分类下的压缩图片
    :param category: 图片分类
    :param image: 图片文件名
    """
    return _build_image_response(category, image, None, None, request, quality, format)


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

    url = f"/api/v1/website/image/avatar/{saved_name}"
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

    url = f"/api/v1/website/image/{category}/{saved_name}"
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
