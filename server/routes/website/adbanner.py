from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from scripts.filesystem import AdBannerHandler
from scripts.mongodb import AuthorizedHandler

AD_BANNER_ROUTER = APIRouter(prefix="/website/adbanner", tags=["website-adbanner"])

# 实例化 AdBanner 处理器
AD_BANNER_HANDLE = AdBannerHandler()


@AD_BANNER_ROUTER.get("/all")
async def api_get_all_adbanner_items():
    """
    获取所有 AdBanner 项目
    """
    items = AD_BANNER_HANDLE.get_adbanner_items()
    return {"data": items}


class SetAdsRequest(BaseModel):
    """
    设置广告信息的请求体
    """
    # 每个字典代表一个广告项，包含 title, url, new 等字段
    ads: list = []


@AD_BANNER_ROUTER.post("/set")
async def api_set_ads(request: SetAdsRequest, user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    设置广告信息
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
    flag = AD_BANNER_HANDLE.set_adbanner_items(request.ads)
    return {"data": flag}
