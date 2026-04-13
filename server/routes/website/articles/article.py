from scripts.db.website import ArticleHandler
from pydantic import BaseModel


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
