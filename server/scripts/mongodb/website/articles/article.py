import os
from typing import Any, Dict, List, Optional
from pymongo import DESCENDING
from pymongo.errors import PyMongoError
from core import Logger, ProjectConfig
from scripts.mongodb.connection import get_article_mongo_collection
from typedef.mongodb.article import T_ArticleData, T_ArticleMeta


# 定义文章目录路径
ARTICLES_DIR = ProjectConfig.get_articles_path()


def find_all_articles() -> List[T_ArticleData]:
    """
    获取所有文章数据
    Returns:
        List[T_ArticleData]: 包含所有文章数据的列表
    """
    coll = get_article_mongo_collection()
    try:
        # 过滤 serialNo != 0，再按 meta.date 降序排列
        query: Dict[str, Any] = {'meta.serialNo': {'$ne': 0}}
        cursor = coll.find(query).sort('meta.date', DESCENDING)
        docs: List[T_ArticleData] = list(cursor)
        return docs

    except PyMongoError as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return []


def find_article_by_id(id: str) -> Optional[T_ArticleData]:
    """
    根据文章ID获取文章数据，并将浏览量加1
    Args:
        article_id (str): 文章ID
    Returns:
        Optional[T_ArticleData]: 文章数据，如果未找到则返回None
    """
    coll = get_article_mongo_collection()
    try:
        # 根据 'id' 字段查找
        doc: Optional[T_ArticleData] = coll.find_one({'id': id})
        if doc:
            # 对views的数字加1
            coll.update_one({'id': id}, {'$inc': {'views': 1}})
            # 去除mongodb的原生键 不然不好json序列号
            doc.pop("_id", None)
        return doc
    except PyMongoError as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return None


def delete_article_by_id(article_id: str) -> bool:
    """
    根据文章ID删除文章
    Args:
        article_id (str): 文章ID
    Returns:
        bool: 如果删除成功则返回True，否则返回False
    """
    coll = get_article_mongo_collection()
    try:
        # 获得文章的path属性
        article: Optional[T_ArticleData] = coll.find_one({'id': article_id})
        if not article:
            Logger.warning(f"没有找到文章 ID: {article_id}")
            return False
        # 1. 删除文章的mongodb记录
        result = coll.delete_one({'id': article_id})
        if result.deleted_count == 0:
            Logger.warning(f"没有删除任何文章 ID: {article_id}")
            return False

        # 2. 删除文章的缓存文件
        path = article.get('path', '')
        full_path = os.path.join(ARTICLES_DIR, path)
        if os.path.exists(full_path):
            os.remove(full_path)
            Logger.info(f"✔ 已删除文章缓存文件: {full_path}")
        else:
            Logger.warning(f"没有找到文章缓存文件: {full_path}")
        return True
    except PyMongoError as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return False


def get_article_text_by_id(article_id: str) -> str:
    """
    根据文章ID获取文章数据
    Args:
        article_id (str): 文章ID
    Returns:
        str: 文章数据，如果未找到则返回错误的文本
    """
    coll = get_article_mongo_collection()
    try:
        # 打破循环导入
        from scripts.filesystem import ArticleCrudHandler
        # 根据文章ID查找文章
        article: Optional[T_ArticleData] = coll.find_one({'id': article_id})
        if not article:
            Logger.warning(f"没有找到文章 ID: {article_id}")
            return "没有找到文章"

        meta: T_ArticleMeta = article['meta']
        content: str = article['content']
        # 保存到缓存文件
        text: str = ArticleCrudHandler.get_md_file(meta, content, True)
        return text

    except Exception as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return "获取文章内容失败"
