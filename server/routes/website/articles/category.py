from pydantic import BaseModel
from typing import List
from scripts.mongodb.website import ArticleHandler
from .util import build_all_article_format


# =========================================================================

class T_Category_Articles_Response(BaseModel):
    data: List[dict]


async def get_articles_by_category(category_name: str):
    """
    根据分类获取文章列表
    Args:
        category_name (str): 分类名称
    Returns:
        list: 该分类下的所有文章列表
    """
    articles = ArticleHandler.get_articles_by_category(category_name)
    data = [build_all_article_format(art) for art in articles]
    return T_Category_Articles_Response(data=data)


# =========================================================================
async def new_category(req):
    pass
