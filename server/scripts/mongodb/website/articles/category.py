import os
import uuid
from datetime import date
from typing import Any, Dict, List, Optional, Union
from pymongo import DESCENDING
from pymongo.errors import PyMongoError
from core import Logger, ProjectConfig
from scripts.mongodb.connection import get_article_mongo_collection
from typedef import T_ArticleData, T_ArticleMeta


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


def create_article_by_title_and_category(category: str, title: str, username: str) -> Dict[str, Union[bool, str]]:
    """
    添加新文章
    Args:
        category (str): 文章分类
        title (str): 文章标题
        username (str): 创建文章的用户名
    Returns:
        Dict[str, Union[bool, str]]: 新添加的文章数据
    """
    coll = get_article_mongo_collection()
    try:
        # 检查文章是不是存在
        existing_article: Optional[T_ArticleData] = coll.find_one({'meta.title': title, 'meta.category': category})
        if existing_article:
            Logger.warning(f"文章 '{title}' 已存在于分类 '{category}' 中")
            return {}

        # 生成新的文章ID
        fp: str = os.path.join(ARTICLES_DIR, category, f"{title}.md")
        rel: str = os.path.relpath(fp, ARTICLES_DIR)
        pid: str = uuid.uuid5(uuid.NAMESPACE_URL, rel).hex[:16]

        # 日期
        today: str = date.today().strftime("%Y-%m-%d")
        # 序列
        serial_no: int = find_latest_serial_no(category) + 1

        new_article: T_ArticleData = T_ArticleData(
            id=pid,
            meta=T_ArticleMeta(
                title=title,
                author=username,
                category=category,
                serialNo=serial_no,
                status='publish',
                tags=[],
                date=today,
                thumbnail="",
                summary=""
            ),
            content="",
            path=rel,
            views=0
        )
        # 插入新文章
        result = coll.insert_one(new_article)
        if result.acknowledged:
            return {'flag': True, 'id': new_article['id']}
        else:
            Logger.error("插入新文章失败")
            return {'flag': False, 'log': "插入新文章失败"}
    except PyMongoError as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return {'flag': False, 'log': str(e)}


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
        # 检查文章是否存在
        existing_article: Optional[T_ArticleData] = coll.find_one({'meta.title': title, 'meta.category': category})
        return existing_article is not None
    except PyMongoError as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return False
