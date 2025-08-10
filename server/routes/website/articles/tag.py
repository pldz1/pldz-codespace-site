from typing import List
from pydantic import BaseModel
from scripts.mongodb.website import ArticleHandler
from .util import build_all_article_format

# =========================================================================


class T_Tag_Articles_Response(BaseModel):
    data: List[dict]


async def get_articles_by_tag(tag_name: str):
    """
    根据标签获取文章列表
    Args:
        tag_name (str): 标签名称
    Returns:
        list: 相关文章列表
    """
    articles = ArticleHandler.get_articles_by_tag(tag_name)
    data = [build_all_article_format(art) for art in articles]
    return T_Tag_Articles_Response(data=data)
