from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from scripts.filesystem import LiveDemoHandler
from scripts.db import AuthorizedHandler

LIVEDEMO_ROUTER = APIRouter(prefix="/website/livedemo", tags=["website-livedemo"])

# 实例化 Live Demo 处理器
LIVEDEMO_HANDLE = LiveDemoHandler()


@LIVEDEMO_ROUTER.get("/all")
async def api_get_all_livedemo_items():
    """
    获取所有 live demo 项目
    """
    items = LIVEDEMO_HANDLE.get_livedemo_items()
    return {"data": items}


class SetLiveDemoRequest(BaseModel):
    """
    设置 livedemo 信息的请求体
    """
    # 每个字典代表一个 livedemo 项，包含 title, url, new 等字段
    data: list = []


@LIVEDEMO_ROUTER.post("/set")
async def api_set_livedemo(request: SetLiveDemoRequest, user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    设置 livedemo 信息
    """
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
    flag = LIVEDEMO_HANDLE.set_livedemo_items(request.data)
    return {"data": flag}
