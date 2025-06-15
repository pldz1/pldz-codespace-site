from fastapi.routing import APIRouter
from scripts.filesystem import AdBannerHandler

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
