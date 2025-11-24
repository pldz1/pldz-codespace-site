import os
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from core import Logger
from scripts.filesystem import CloudDriveStorage
from scripts.mongodb import AuthorizedHandler
from scripts.clouddriver import CloudDriveTokenHandler


CLOUD_DRIVE_ROUTER = APIRouter(prefix="/website/cloud-drive", tags=["website-cloud-drive"])

MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB


class GenerateTokenRequest(BaseModel):
    allow_upload: bool = Field(default=True, description="是否允许上传")
    allow_download: bool = Field(default=False, description="是否允许下载")
    filename: Optional[str] = Field(default=None, description="下载文件名（相对 data/cache）")
    description: Optional[str] = Field(default=None, description="备注信息")


class VerifyTokenRequest(BaseModel):
    token: str = Field(..., description="云盘令牌")


class DownloadTokenRequest(BaseModel):
    token: str = Field(..., description="云盘令牌")


class DeleteTokenRequest(BaseModel):
    token: str = Field(..., description="云盘令牌")


def _serialize_token(token_entry):
    filename = token_entry.get("filename")
    has_file = bool(filename and CloudDriveStorage.file_exists(filename))
    info = CloudDriveStorage.file_info(filename) if has_file else None
    size = info["size"] if info else int(token_entry.get("size") or 0)

    return {
        "token": token_entry["token"],
        "allow_upload": bool(token_entry.get("allow_upload")),
        "allow_download": bool(token_entry.get("allow_download")),
        "created": token_entry.get("created"),
        "expires_at": token_entry.get("expires_at"),
        "filename": filename,
        "original_filename": token_entry.get("original_filename"),
        "description": token_entry.get("description"),
        "size": size,
        "has_file": has_file,
        "last_updated": token_entry.get("last_updated"),
    }


@CLOUD_DRIVE_ROUTER.post("/token")
async def api_generate_drive_token(
    request: GenerateTokenRequest,
    user: dict = Depends(AuthorizedHandler.get_current_user),
):
    """
    管理员生成云盘令牌。
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    username = user.get("username")
    if not AuthorizedHandler.check_admin(username):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator privileges required.")

    if not request.allow_upload and not request.allow_download:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="令牌需要至少开启上传或下载权限。")

    relative_filename: Optional[str] = None
    size = 0

    if request.filename:
        sanitized = CloudDriveStorage.sanitize_filename(request.filename)
        relative_filename = sanitized
        info = CloudDriveStorage.file_info(relative_filename)
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"文件 {sanitized} 不存在，请确认后再试。",
            )
        size = info["size"]

    token_entry = CloudDriveTokenHandler.generate_token(
        allow_upload=request.allow_upload,
        allow_download=request.allow_download,
        filename=relative_filename,
        original_filename=relative_filename,
        description=request.description,
        size=size,
    )
    Logger.info(f"管理员 {username} 生成云盘令牌: {token_entry['token']}")
    return {"data": _serialize_token(token_entry)}


@CLOUD_DRIVE_ROUTER.get("/tokens")
async def api_list_drive_tokens(user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    管理员获取所有令牌列表。
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    username = user.get("username")
    if not AuthorizedHandler.check_admin(username):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator privileges required.")

    tokens = CloudDriveTokenHandler.list_tokens()
    return {"data": [_serialize_token(item) for item in tokens]}


@CLOUD_DRIVE_ROUTER.post("/verify")
async def api_verify_drive_token(request: VerifyTokenRequest):
    """
    校验令牌是否可用。
    """
    token_entry = CloudDriveTokenHandler.get_token(request.token.strip())
    if not token_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="令牌不存在或已过期。")

    # 更新文件信息
    filename = token_entry.get("filename")
    if filename and CloudDriveStorage.file_exists(filename):
        info = CloudDriveStorage.file_info(filename)
        CloudDriveTokenHandler.update_file_info(
            token_entry["token"],
            filename=filename,
            original_filename=token_entry.get("original_filename") or os.path.basename(filename),
            size=info["size"] if info else 0,
        )
        token_entry = CloudDriveTokenHandler.get_token(token_entry["token"]) or token_entry

    CloudDriveTokenHandler.touch(token_entry["token"])
    return {"data": _serialize_token(token_entry)}


@CLOUD_DRIVE_ROUTER.post("/upload")
async def api_drive_upload(
    token: str = Form(...),
    file: UploadFile = File(...),
):
    """
    使用令牌上传文件。
    """
    token_value = (token or "").strip()
    token_entry = CloudDriveTokenHandler.get_token(token_value)
    if not token_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="令牌不存在或已过期。")

    if not token_entry.get("allow_upload"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="该令牌不允许上传文件。")

    if not file or not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请选择要上传的文件。")

    original_filename = file.filename
    sanitized_name = CloudDriveStorage.sanitize_filename(original_filename)

    # 读取文件并限制大小
    buffer = bytearray()
    total = 0
    chunk_size = 4 * 1024 * 1024
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_FILE_SIZE:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="文件大小超过 200MB 限制。")
        buffer.extend(chunk)

    if total == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件内容为空。")

    # 确认保存路径
    existing_filename = token_entry.get("filename")
    if existing_filename:
        relative_path = existing_filename
    else:
        relative_path = CloudDriveStorage.build_token_relative_path(token_entry["token"], sanitized_name)

    CloudDriveStorage.save_bytes(relative_path, bytes(buffer))

    updated_entry = CloudDriveTokenHandler.update_file_info(
        token_entry["token"],
        filename=relative_path,
        original_filename=sanitized_name,
        size=total,
    ) or token_entry

    Logger.info(f"云盘令牌 {token_entry['token']} 上传文件成功: {relative_path}")
    return {
        "data": {
            "token": token_entry["token"],
            "filename": updated_entry.get("filename"),
            "original_filename": updated_entry.get("original_filename"),
            "size": updated_entry.get("size"),
            "has_file": True,
        }
    }


@CLOUD_DRIVE_ROUTER.post("/download")
async def api_drive_download(request: DownloadTokenRequest):
    """
    使用令牌下载文件。
    """
    token_value = request.token.strip()
    token_entry = CloudDriveTokenHandler.get_token(token_value)
    if not token_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="令牌不存在或已过期。")

    if not token_entry.get("allow_download"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="该令牌不允许下载文件。")

    filename = token_entry.get("filename")
    if not filename:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该令牌还未关联任何文件。")

    try:
        abs_path = CloudDriveStorage.absolute_path(filename)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在或已被删除。")

    download_name = token_entry.get("original_filename") or os.path.basename(filename)
    Logger.info(f"令牌 {token_entry['token']} 触发文件下载: {filename}")
    return FileResponse(abs_path, media_type="application/octet-stream", filename=download_name)


@CLOUD_DRIVE_ROUTER.post("/token/delete")
async def api_delete_drive_token(
    request: DeleteTokenRequest,
    user: dict = Depends(AuthorizedHandler.get_current_user),
):
    """
    管理员删除指定令牌。
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    username = user.get("username")
    if not AuthorizedHandler.check_admin(username):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator privileges required.")

    token_value = request.token.strip()
    if not token_value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="口令不能为空。")

    deleted = CloudDriveTokenHandler.delete_token(token_value)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="令牌不存在或已过期。")

    Logger.info(f"管理员 {username} 删除云盘令牌: {token_value}")
    return {"data": True}
