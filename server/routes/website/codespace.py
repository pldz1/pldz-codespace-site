from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from scripts.filesystem import CodeSpaceHandler
from scripts.mongodb import AuthorizedHandler

CODESPACE_ROUTER = APIRouter(prefix="/website/codespace", tags=["website-codespace"])

# 实例化 CodeSpace 处理器
CODESPACE_HANDLE = CodeSpaceHandler()


@CODESPACE_ROUTER.get("/all")
async def api_get_all_codespace_items():
    """
    获取所有 CodeSpace 项目
    """
    items = CODESPACE_HANDLE.get_codespace_items()
    return {"data": items}


class SetCodespaceRequest(BaseModel):
    """
    设置 CodeSpace 信息的请求体
    """
    # 每个字典代表一个 CodeSpace 项，包含 title, url, new 等字段
    codespaces: list = []


@CODESPACE_ROUTER.post("/set")
async def api_set_codespace(request: SetCodespaceRequest, user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    设置 CodeSpace 信息
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
    flag = CODESPACE_HANDLE.set_codespace_items(request.codespaces)
    return {"data": flag}
