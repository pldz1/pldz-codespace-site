import asyncio
import json
from typing import Any, AsyncGenerator, List, Optional
from pymongo.errors import PyMongoError
from core import Logger
from scripts.mongodb.connection import get_article_mongo_collection
from typedef.mongodb.article import T_ArticleData, T_ArticleMeta


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


@classmethod
async def write_all_article(cls) -> AsyncGenerator[str, Any]:
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
