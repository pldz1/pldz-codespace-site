from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from plugins.git import GitHandler
from .util import check_user_permission

# =========================================================================


class T_GitSync_Request(BaseModel):
    """
    Git同步数据模型
    """
    commit: str = ""


async def git_sync(req: T_GitSync_Request, user: dict):
    """
    同步所有文章到Git仓库
    通过GitHandler处理Git同步
    需要用户登录并且是管理员权限
    Args:
        req (T_GitSync_Request): Git同步数据 其中 commit 字段是可选的提交信息
        user (dict): 当前用户信息
    Returns:
        dict: 同步结果
    """
    check_user_permission(user)
    commit_message = req.commit if req.commit else "✨ Sync articles"
    return StreamingResponse(GitHandler.git_sync(commit_message), media_type="text/event-stream")


# =========================================================================
async def git_pull(user: dict):
    """
    从Git仓库拉取最新代码
    通过GitHandler处理Git拉取
    """
    check_user_permission(user)
    return StreamingResponse(GitHandler.get_pull_async(), media_type="text/event-stream")
