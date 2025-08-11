from typing import List
from pymongo.errors import PyMongoError
from core import Logger
from scripts.mongodb.connection import get_article_mongo_collection


def set_article_content_by_id(article_id: str, content: str) -> bool:
    """
    根据文章的ID编辑文章
    Args:
        article_id (str): 文章ID
        content (str): 文章内容
    Returns:
        bool: 编辑后的文章数据
    """
    coll = get_article_mongo_collection()
    try:
        # 更新文章内容
        result = coll.update_one(
            {'id': article_id},
            {'$set': {'content': content}}
        )
        if result.modified_count > 0:
            return True
        else:
            Logger.warning(f"没有找到或未修改文章 ID: {article_id}")
            return False
    except PyMongoError as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return False


def set_article_meta_by_id(id: str, title: str, category: str, serialNo: int, tags: List[str], date: str, thumbnail: str, summary: str) -> bool:
    """
    根据文章的ID编辑文章元数据
    Args:
        id (str): 文章ID
        title (str): 文章标题
        category (str): 文章分类
        serialNo (int): 文章序号
        tags (List[str]): 文章标签
        date (str): 文章日期
        thumbnail (str): 缩略图链接
        summary (str): 文章摘要
    Returns:
        bool: 编辑后的文章数据
    """
    coll = get_article_mongo_collection()
    try:
        # 更新文章元数据
        result = coll.update_one(
            {'id': id},
            {
                '$set': {
                    'meta.title': title,
                    'meta.category': category,
                    'meta.serialNo': serialNo,
                    'meta.tags': tags,
                    'meta.date': date,
                    'meta.thumbnail': thumbnail,
                    'meta.summary': summary
                }
            }
        )
        if result.modified_count > 0:
            return True
        else:
            Logger.warning(f"没有找到或未修改文章标题: {title}")
            return False
    except PyMongoError as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return False


def set_article_serial_no(article_id: str, serial_no: int) -> bool:
    """
    设置文章的序号
    Args:
        article_id (str): 文章ID
        serial_no (int): 文章序号
    Returns:
        bool: 如果设置成功则返回True，否则返回False
    """
    coll = get_article_mongo_collection()
    try:
        # 更新文章序号
        result = coll.update_one(
            {'id': article_id},
            {'$set': {'meta.serialNo': serial_no}}
        )
        return result.modified_count > 0
    except PyMongoError as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return False


def set_article_title(article_id: str, title: str) -> bool:
    """
    根据文章的ID编辑文章标题
    Args:
        article_id (str): 文章ID
        title (str): 文章标题
    Returns:
        bool: 编辑后的文章数据
    """
    coll = get_article_mongo_collection()
    try:
        # 更新文章标题
        result = coll.update_one(
            {'id': article_id},
            {'$set': {'meta.title': title}}
        )
        if result.modified_count > 0:
            return True
        else:
            Logger.warning(f"没有找到或未修改文章 ID: {article_id}")
            return False
    except PyMongoError as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return False
