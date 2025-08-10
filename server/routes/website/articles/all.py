from pydantic import BaseModel
from typing import List

from scripts.mongodb.website import ArticleHandler
from .util import build_all_article_format


# =========================================================================


class T_All_Article_Response(BaseModel):
    data: List[dict]


async def all_articles():
    """
    获取所有文章的列表
    Returns:
        : 包含所有文章的列表
    """
    data = ArticleHandler.get_all_articles()
    format_data = [build_all_article_format(art) for art in data]
    res = T_All_Article_Response(data=format_data)
    return res


# =========================================================================

class T_All_Categories_Response(BaseModel):
    data: List[str]


async def all_categories():
    """
    获取所有文章的分类列表
    Returns:
        list: 包含所有分类的列表
    """

    categories = ArticleHandler.get_all_categories()
    res = T_All_Categories_Response(data=categories)
    return res


# =========================================================================


class T_All_Tags_Response(BaseModel):
    data: List[dict]


async def all_tags():
    """
    获取所有文章的标签及其对应的文章数量
    Returns:
        list: 包含所有标签及其文章数量的列表
    """
    tag_counts = ArticleHandler.get_all_tag_and_counts()
    res = T_All_Tags_Response(data=tag_counts)
    return res
