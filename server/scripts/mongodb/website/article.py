import os
import json
import uuid
import asyncio
from datetime import date
from pymongo import DESCENDING
from pymongo.errors import PyMongoError
from typing import AsyncGenerator, Any, Dict, List, Optional, Union, TypedDict
from core import Logger, ProjectConfig
from scripts.mongodb import get_article_mongo_collection
from typedef import T_ArticleMeta, T_ArticleData, T_ArticleInfo, T_TagCount

# 定义文章目录路径
ARTICLES_DIR = ProjectConfig.get_articles_path()


class ArticleHandler:

    def __init__(self) -> None:
        pass

    @classmethod
    def get_all_categories(cls) -> List[str]:
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

    @classmethod
    def get_article_info(cls, art: T_ArticleData) -> T_ArticleInfo:
        """
        从完整文章数据中提取前端展示所需的信息
        Args:
            art (T_ArticleData): 完整文章数据
        Returns:
            T_ArticleInfo: 前端展示用的精简文章信息
        """
        meta = art['meta']
        return T_ArticleInfo(
            id=art['id'],
            title=meta['title'],
            category=meta['category'],
            summary=meta['summary'],
            serialNo=meta['serialNo'],
            thumbnail=meta['thumbnail'],
            tags=meta['tags'],
            views=art['views'],
            date=meta['date'],
        )

    @classmethod
    def get_all_articles(cls) -> List[T_ArticleInfo]:
        coll = get_article_mongo_collection()
        try:
            # 过滤 serialNo != 0，再按 meta.date 降序排列
            query: Dict[str, Any] = {'meta.serialNo': {'$ne': 0}}
            cursor = coll.find(query).sort('meta.date', DESCENDING)
            docs: List[T_ArticleData] = list(cursor)
            arts: List[T_ArticleInfo] = []
            for art in docs:
                item: T_ArticleInfo = cls.get_article_info(art)
                arts.append(item)
            return arts

        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return []

    @classmethod
    def get_article_by_id(cls, article_id: str) -> Optional[T_ArticleData]:
        coll = get_article_mongo_collection()
        try:
            # 根据 'id' 字段查找
            doc: Optional[T_ArticleData] = coll.find_one({'id': article_id})
            if doc:
                # 对views的数字加1
                coll.update_one({'id': article_id}, {'$inc': {'views': 1}})
                # 去除mongodb的原生键 不然不好json序列号
                doc.pop("_id", None)
            return doc
        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return None

    @classmethod
    def get_all_tag_and_counts(cls) -> List[T_TagCount]:
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

    @classmethod
    def get_articles_by_category(cls, category: str) -> List[T_ArticleInfo]:
        """
        根据分类获取文章列表
        Args:
            category (str): 文章分类
        Returns:
            List[T_ArticleInfo]: 包含该分类下所有文章的列表
        """
        coll = get_article_mongo_collection()
        try:
            # 查询指定分类的文章
            query: Dict[str, Any] = {'meta.category': category, 'meta.serialNo': {'$ne': 0}}
            cursor = coll.find(query).sort('meta.date', DESCENDING)
            docs: List[T_ArticleData] = list(cursor)
            arts: List[T_ArticleInfo] = []
            for art in docs:
                item: T_ArticleInfo = cls.get_article_info(art)
                arts.append(item)
            return arts
        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return []

    @classmethod
    def get_articles_by_tag(cls, tag: str) -> List[T_ArticleInfo]:
        """
        根据标签获取文章列表
        Args:
            tag (str): 文章标签
        Returns:
            List[T_ArticleInfo]: 包含该标签下所有文章的列表
        """
        coll = get_article_mongo_collection()
        try:
            # 查询指定标签的文章
            query: Dict[str, Any] = {'meta.tags': tag, 'meta.serialNo': {'$ne': 0}}
            cursor = coll.find(query).sort('meta.date', DESCENDING)
            docs: List[T_ArticleData] = list(cursor)
            arts: List[T_ArticleInfo] = []
            for art in docs:
                item: T_ArticleInfo = cls.get_article_info(art)
                arts.append(item)
            return arts
        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return []

    @classmethod
    def edit_article_content_by_id(cls, article_id: str, content: str) -> bool:
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

    @classmethod
    def edit_article_meta_by_id(
            cls, id: str, title: str, category: str, serialNo: int, tags: List[str], date: str, thumbnail: str, summary: str) -> bool:
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

    @classmethod
    def get_latest_serial_no(cls, category: str) -> int:
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

    @classmethod
    def set_article_serial_no(cls, article_id: str, serial_no: int) -> bool:
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

    @classmethod
    def is_article_exists(cls, category: str, title: str) -> bool:
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

    @classmethod
    def add_article_by_title_and_category(cls, category: str, title: str, username: str) -> Dict[str, Union[bool, str]]:
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
            serial_no: int = cls.get_latest_serial_no(category) + 1

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

    @classmethod
    def delete_article_by_id(cls, article_id: str) -> bool:
        """
        根据文章ID删除文章
        Args:
            article_id (str): 文章ID
        Returns:
            bool: 如果删除成功则返回True，否则返回False
        """
        coll = get_article_mongo_collection()
        try:
            # 删除文章
            result = coll.delete_one({'id': article_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return False

    @classmethod
    def get_article_text(cls, article_id: str) -> Union[str, bool]:
        """
        根据文章ID获取文章数据
        Args:
            article_id (str): 文章ID
        Returns:
            Union[str, bool]: 文章数据，如果未找到则返回False
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

            meta: T_ArticleMeta = article['meta']
            content: str = article['content']
            # 保存到缓存文件
            text: str = ArticleCrudHandler.get_md_file(meta, content, True)
            return text

        except Exception as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return False

    @classmethod
    def sync_article_file(cls, article_id: str) -> bool:
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
    async def sync_all_article(cls) -> AsyncGenerator[str, Any]:
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
                    cls.sync_article_file(aid)
                    log: str = 'synced'
                except Exception as e:
                    log = str(e)

                payload: str = f"index: {idx}, 'title': {title},  {log}."
                await asyncio.sleep(0.5)
                yield f"data: {json.dumps({'status': 'in_process', 'message': payload})}\n\n"

            yield f"data: {json.dumps({'status': 'in_process', 'message': '全部文章同步完成.'})}\n\n"
            return
        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
            return
