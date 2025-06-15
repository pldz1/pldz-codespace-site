from fastapi.routing import APIRouter
from scripts.filesystem import NavInfoHandler

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
