from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from scripts.filesystem import NavInfoHandler
from scripts.mongodb import AuthorizedHandler

NAV_ROUTER = APIRouter(prefix="/website/navs", tags=["website-navs"])

# 实例化 AdBanner 处理器
NAV_HANDLE = NavInfoHandler()


@NAV_ROUTER.get("/all")
async def api_get_navs():
    """
    获取导航信息
    :return: 导航信息列表
    """
    data = NAV_HANDLE.get_navigation_items()
    return {'data': data}


class SetNavsRequest(BaseModel):
    """
    设置导航信息的请求体
    """
    # 每个字典代表一个导航项，包含 title, url, new 等字段
    navs: list = []


@NAV_ROUTER.post("/set")
async def api_set_navs(request: SetNavsRequest, user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    设置导航信息
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
    flag = NAV_HANDLE.set_navigation_items(request.navs)
    return {"data": flag}
