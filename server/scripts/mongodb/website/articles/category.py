import os
import uuid
from datetime import date
from typing import Any, Dict, List, Optional, Union
from pymongo import DESCENDING
from pymongo.errors import PyMongoError
from core import Logger, ProjectConfig
from scripts.mongodb.connection import get_article_mongo_collection
from typedef import T_ArticleData


# 定义文章目录路径
ARTICLES_DIR = ProjectConfig.get_articles_path()


def find_all_categories() -> List[str]:
    """
    获取所有文章的分类列表
    Returns:
        List[str]: 包含所有分类的列表
    """
    coll = get_article_mongo_collection()
    try:
        # 获取所有文章的分类
        categories: List[str] = coll.distinct('meta.category')
        return categories
    except PyMongoError as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return []


def find_articles_by_category(category: str) -> List[T_ArticleData]:
    """
    根据分类获取文章列表
    Args:
        category (str): 文章分类
    Returns:
        List[T_ArticleData]: 包含该分类下所有文章的列表
    """
    coll = get_article_mongo_collection()
    try:
        # 查询指定分类的文章
        query: Dict[str, Any] = {'meta.category': category, 'meta.serialNo': {'$ne': 0}}
        cursor = coll.find(query).sort('meta.date', DESCENDING)
        docs: List[T_ArticleData] = list(cursor)
        return docs
    except PyMongoError as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return []


def find_latest_serial_no(category: str) -> int:
    """
    获取指定分类下的最新文章序号
    Args:
        category (str): 文章分类
    Returns:
        int: 最新的文章序号, 如果没有文章则返回1
    """
    coll = get_article_mongo_collection()
    try:
        # 查询指定分类的最新文章序号
        query: Dict[str, Any] = {'meta.category': category, 'meta.serialNo': {'$ne': 0}}
        latest_article: Optional[T_ArticleData] = coll.find_one(query, sort=[('meta.serialNo', DESCENDING)])
        if latest_article and 'meta' in latest_article:
            return latest_article['meta'].get('serialNo', 1)
        return 1
    except PyMongoError as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return 1


def find_article_in_category(category: str, title: str) -> bool:
    """
    检查文章是否存在
    Args:
        category (str): 文章分类
        title (str): 文章标题
    Returns:
        bool: 如果文章存在则返回True，否则返回False
    """
    coll = get_article_mongo_collection()
    try:
        # 检查文章是否存在, 找出 category 下的所有文章
        all_docs: List[T_ArticleData] = coll.find({'meta.category': category})
        all_paths: List[str] = [doc['path'] for doc in all_docs]
        all_filename = [os.path.basename(path) for path in all_paths]

        if title + '.md' in all_filename:
            return True
        else:
            return False
    except PyMongoError as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return False
