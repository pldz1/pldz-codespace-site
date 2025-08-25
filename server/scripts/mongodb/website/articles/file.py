import asyncio
import json
import os
import textwrap
from datetime import datetime
from typing import Any, AsyncGenerator, List, Optional
import uuid
from pymongo.errors import PyMongoError
from core import Logger, ProjectConfig
from scripts.mongodb.connection import get_article_mongo_collection
from typedef.mongodb.article import T_ArticleData, T_ArticleMeta

# 定义文章和图像目录路径
ARTICLES_DIR = ProjectConfig.get_articles_path()
IMAGES_DIR = ProjectConfig.get_images_path()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin@pldz1.com")


def get_article_id_by_path(path: str) -> Optional[str]:
    """
    根据文章路径获取文章ID
    Args:
        path (str): 文章路径
    Returns:
        Optional[str]: 如果找到文章则返回文章ID，否则返回None
    """
    rel: str = os.path.relpath(path, ARTICLES_DIR)
    pid: str = uuid.uuid5(uuid.NAMESPACE_URL, rel).hex[:16]
    return pid


def rename_article_file(article_id: str, filename: str) -> str:
    """
    重命名文章文件
    Args:
        article_id (str): 文章ID
        filename (str): 新的文件名（不包含扩展名）
    Returns:
        str: 如果重命名成功则返回新的文章ID，否则返回空字符串
    """
    coll = get_article_mongo_collection()
    try:
        # 查找文章路径
        doc = coll.find_one({'id': article_id}, {'_id': 0, 'path': 1})
        if not doc:
            Logger.warning(f"没有找到文章 ID: {article_id}")
            return ""

        path = doc['path']
        base_path = os.path.dirname(path)
        base_name = os.path.basename(path)
        # 获取原文件扩展名
        _, ext = os.path.splitext(base_name)
        old_path = os.path.join(ARTICLES_DIR, path)
        new_path = os.path.join(ARTICLES_DIR, base_path, filename + ext)
        os.rename(old_path, new_path)
        Logger.info(f"文件重命名成功")
        pid = get_article_id_by_path(new_path)
        return pid
    except Exception as e:
        Logger.error(f"重命名文件失败: {e}")
        return ""


def create_category(category_name: str) -> bool:
    """
    创建新的文章分类目录
    Args:
        category_name (str): 分类名称
    Returns:
        bool: 如果创建成功则返回True，否则返回False
    """
    try:
        new_category_path = os.path.join(ARTICLES_DIR, category_name)
        new_image_path = os.path.join(IMAGES_DIR, category_name)
        # 创建分类目录
        os.makedirs(new_category_path, exist_ok=True)
        os.makedirs(new_image_path, exist_ok=True)

        Logger.info(f"创建新的分类目录: {new_category_path}")
        Logger.info(f"创建新的图像目录: {new_image_path}")

        # 创建一个 ABOUT.md 文件
        about_file_path = os.path.join(new_category_path, 'ABOUT.md')
        datestr = datetime.now().strftime('%Y-%m-%d')
        md = f"""
        ---
        author: {ADMIN_USERNAME}
        category: {category_name}
        date: '{datestr}'
        serialNo: 0
        status: publish
        summary: {category_name}的随笔
        tags: []
        thumbnail:
        title: ABOUT
        ---

        # 🎉 前言

        创建 {category_name} 专栏
        """
        md = textwrap.dedent(md).lstrip("\n")
        with open(about_file_path, 'w', encoding='utf-8') as f:
            f.write(md)
        return True
    except Exception as e:
        Logger.error(f"创建分类目录失败: {e}")
        return False


def create_article_file(category: str, filename: str, username: str) -> str:
    """
    创建新的文章文件
    Args:
        category (str): 分类名称
        filename (str): 文件名（不包含扩展名）
        username (str): 创建者用户名
    Returns:
        str: 如果创建成功则返回文章ID，否则返回空字符串
    """
    try:
        new_file_path: str = os.path.join(ARTICLES_DIR, category, f"{filename}.md")
        datestr = datetime.now().strftime('%Y-%m-%d')
        md = f"""
        ---
        author: {username}
        category: {category}
        date: {datestr}
        serialNo: 99999
        status: publish
        summary:
        tags: []
        thumbnail:
        title: {filename}
        ---

        # {filename} !
        """
        md = textwrap.dedent(md).lstrip("\n")
        with open(new_file_path, 'w', encoding='utf-8') as f:
            f.write(md)
        Logger.info(f"文件创建成功: {new_file_path}")
        pid: str = get_article_id_by_path(new_file_path)
        return pid
    except Exception as e:
        Logger.error(f"创建文件失败: {e}")
        return ""


def write_article_to_file(article_id: str) -> bool:
    """
    保存文章的元数据和内容
    Args:
        article_id (str): 文章ID
    Returns:
        bool: 如果保存成功则返回True，否则返回False
    """
    coll = get_article_mongo_collection()
    try:
        # 打破循环导入
        from scripts.filesystem import ArticleCrudHandler
        # 根据文章ID查找文章
        article: Optional[T_ArticleData] = coll.find_one({'id': article_id})
        if not article:
            Logger.warning(f"没有找到文章 ID: {article_id}")
            return False

        path: str = article['path']
        meta: T_ArticleMeta = article['meta']
        content: str = article['content']
        # 保存到缓存文件
        return ArticleCrudHandler.save_file(path, meta, content)

    except Exception as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        return False


async def write_all_article() -> AsyncGenerator[str, Any]:
    """
    保存所有文章的元数据和内容
    Returns:
        AsyncGenerator[str, Any]: 生成器，返回同步状态
    """
    coll = get_article_mongo_collection()

    try:
        # 一次性拉取所有文档
        articles: List[T_ArticleData] = list(coll.find({}, {'id': 1, 'meta.title': 1}))
        if not articles:
            yield f"data: {json.dumps({'status': 'error', 'message': '没有找到文章'})}\n\n"
            return

        for idx, art in enumerate(articles, start=1):
            aid: str = art['id']
            title: str = art.get('meta', {}).get('title', '')

            try:
                write_article_to_file(aid)
                log: str = 'synced'
            except Exception as e:
                log = str(e)

            payload: str = f"index: {idx}, 'title': {title},  {log}."
            await asyncio.sleep(0.1)
            yield f"data: {json.dumps({'status': 'in_process', 'message': payload})}\n\n"

        yield f"data: {json.dumps({'status': 'in_process', 'message': '全部文章同步完成.'})}\n\n"
        return
    except PyMongoError as e:
        Logger.error(f"✖ MongoDB 错误: {e}")
        yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
        return
