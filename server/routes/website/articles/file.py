from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from scripts.mongodb.website import ArticleHandler
from .util import check_user_permission

# =========================================================================


class T_Add_Article_Request(BaseModel):
    title: str = ""
    category: str = ""


class T_New_Article_Response(BaseModel):
    data: dict


async def add_article(req: T_Add_Article_Request, user: dict):
    """
    创建新文章
    Args:
        req (T_Add_Article_Request): 文章数据
    Returns:
        dict: 创建的新文章数据
    """
    check_user_permission(user)
    username = user.get('username')
    res = ArticleHandler.add_article_by_title_and_category(req.category, req.title, username)
    return T_New_Article_Response(data=res)


# =========================================================================

class T_Article_File_Request(BaseModel):
    id: str


class T_Article_File_Response(BaseModel):
    data: bool


# =========================================================================

async def delete_article(req: T_Article_File_Request, user: dict):
    """
    删除文章
    Args:
        req (T_Article_File_Request): 文章对象，包含 id
    Returns:
        bool: 删除操作的结果
    """
    check_user_permission(user)
    res = ArticleHandler.delete_article(req.id)
    return T_Article_File_Response(data=res)


# =========================================================================

async def save_article_to_cache(req: T_Article_File_Request, user: dict):
    """
    将文章保存到缓存
    Args:
        req (T_Article_File_Request): 文章对象，包含 id
    Returns:
        dict: 保存操作的结果
    """
    check_user_permission(user)
    res = ArticleHandler.sync_article_file(req.id)
    return T_Article_File_Response(data=res)


# =========================================================================

async def get_article_text(req: T_Article_File_Request, user: dict):
    """
    获取文章文件内容
    Args:
        req (T_Article_File_Request): 文章对象，包含 id
    Returns:
        dict: 文章文件内容
    """
    check_user_permission(user)
    res = ArticleHandler.get_article_text(req.id)
    return {"data": res}

# =========================================================================


async def sync_all_articles(user: dict):
    """
    同步所有文章
    Args:
        user (dict): 当前用户信息
    Returns:
        dict: 同步结果
    """
    check_user_permission(user)
    return StreamingResponse(ArticleHandler.sync_all_article(), media_type="text/event-stream")
