from pydantic import BaseModel
from scripts.mongodb.website import ArticleHandler
from .util import check_user_permission

# =========================================================================


class T_ArticleData_Response(BaseModel):
    data: dict


async def get_articles_by_id(article_id: str):
    """
    根据文章ID获取文章内容
    Args:
        article_id (str): 文章的唯一标识符
    """
    article = ArticleHandler.get_article_by_id(article_id)
    return T_ArticleData_Response(data=article)

# =========================================================================


class T_Article_Exist_Request(BaseModel):
    title: str = ""
    category: str = ""


class T_Articl_Exist_Response(BaseModel):
    data: bool


async def article_exist(article_data: T_Article_Exist_Request, user: dict):
    """
    编辑已存在文章
    Args:
        article_data (T_Article_Exist_Request): 文章数据
    Returns:
        dict: 编辑后的文章数据
    """
    check_user_permission(user)
    res = ArticleHandler.is_article_exists(article_data.category, article_data.title)
    return T_Articl_Exist_Response(data=res)
