from typing import Any, Dict, List
from pymongo import DESCENDING
from pymongo.errors import PyMongoError
from core import Logger
from scripts.mongodb.connection import get_article_mongo_collection
from typedef import T_TagCount, T_ArticleData


def find_all_tag_and_counts() -> List[T_TagCount]:
    """
    获取所有文章的标签及其对应的文章数量
    Returns:
        List[T_TagCount]: 包含所有标签及其对应文章数量的结构化数据
    """
    coll = get_article_mongo_collection()
    try:
        # 获取所有文章的标签
        tags: List[str] = coll.distinct('meta.tags')
        tag_counts: List[T_TagCount] = []
        for tag in tags:
            count: int = coll.count_documents({'meta.tags': tag})
            tag_counts.append(T_TagCount(text=tag, size=count))
        return tag_counts
    except PyMongoError as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return []


def find_articles_by_tag(tag: str) -> List[T_ArticleData]:
    """
    根据标签获取文章列表
    Args:
        tag (str): 文章标签
    Returns:
        List[T_ArticleData]: 包含该标签下所有文章的列表
    """
    coll = get_article_mongo_collection()
    try:
        # 查询指定标签的文章
        query: Dict[str, Any] = {'meta.tags': tag, 'meta.serialNo': {'$ne': 0}}
        cursor = coll.find(query).sort('meta.date', DESCENDING)
        docs: List[T_ArticleData] = list(cursor)
        return docs
    except PyMongoError as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return []
