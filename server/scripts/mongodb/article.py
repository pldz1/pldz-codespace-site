from pymongo import DESCENDING
from pymongo.errors import PyMongoError

from core import Logger
from scripts.mongodb import get_article_mongo_collection


class ArticleHandler:

    def __init__(self) -> None:
        pass

    @classmethod
    def get_all_categories(cls) -> list:
        """
        获取所有文章的分类列表
        Returns:
            list: 包含所有分类的列表
        """
        coll = get_article_mongo_collection()
        try:
            # 获取所有文章的分类
            categories = coll.distinct('meta.category')
            return categories
        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return []

    @classmethod
    def get_article_info(cls, art) -> dict:
        """
        获取文章的基本信息
        Args:
            art (dict): 文章数据
        Returns:
            dict: 包含文章基本信息的字典
        """
        return {
            'id': art['id'],
            'title': art['meta'].get('title', 'null'),
            'category': art['meta'].get('category', 'null'),
            'summary': art['meta'].get('summary', 'null'),
            'serialNo': art['meta'].get('serialNo', 0),
            'thumbnail': art['meta'].get('thumbnail', 'null'),
            'tags': art['meta'].get('tags', []),
            'views': art['views'] if 'views' in art else 0,
            'date': art['meta'].get('date', "null"),
        }

    @classmethod
    def get_all_articles(cls) -> list:
        coll = get_article_mongo_collection()
        try:
            # 过滤 serialNo != 0，再按 meta.date 降序排列
            query = {'meta.serialNo': {'$ne': 0}}
            cursor = coll.find(query).sort('meta.date', DESCENDING)
            docs = list(cursor)
            arts = []
            for art in docs:
                item = cls.get_article_info(art)
                arts.append(item)
            return arts

        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return []

    @classmethod
    def get_article_by_id(cls, article_id):
        coll = get_article_mongo_collection()
        try:
            # 根据 'id' 字段查找
            doc = coll.find_one({'id': article_id})
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
    def get_all_categories(cls):
        """
        获取所有文章的分类列表
        """
        coll = get_article_mongo_collection()
        try:
            # 获取所有文章的分类
            categories = coll.distinct('meta.category')
            return categories
        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return []

    @classmethod
    def get_all_tag_and_counts(cls) -> list:
        """
        获取所有文章的标签及其对应的文章数量
        Returns:
            list: 包含所有标签及其对应文章数量的字典
        """
        coll = get_article_mongo_collection()
        try:
            # 获取所有文章的标签
            tags = coll.distinct('meta.tags')
            tag_counts = []
            for tag in tags:
                count = coll.count_documents({'meta.tags': tag})
                tag_counts.append({'text': tag, 'size': count})
            return tag_counts
        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return []

    @classmethod
    def get_articles_by_category(cls, category: str) -> list:
        """
        根据分类获取文章列表
        Args:
            category (str): 文章分类
        Returns:
            list: 包含该分类下所有文章的列表
        """
        coll = get_article_mongo_collection()
        try:
            # 查询指定分类的文章
            query = {'meta.category': category, 'meta.serialNo': {'$ne': 0}}
            cursor = coll.find(query).sort('meta.date', DESCENDING)
            docs = list(cursor)
            arts = []
            for art in docs:
                item = cls.get_article_info(art)
                arts.append(item)
            return arts
        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return []

    @classmethod
    def get_articles_by_tag(cls, tag: str) -> list:
        """
        根据标签获取文章列表
        Args:
            tag (str): 文章标签
        Returns:
            list: 包含该标签下所有文章的列表
        """
        coll = get_article_mongo_collection()
        try:
            # 查询指定标签的文章
            query = {'meta.tags': tag, 'meta.serialNo': {'$ne': 0}}
            cursor = coll.find(query).sort('meta.date', DESCENDING)
            docs = list(cursor)
            arts = []
            for art in docs:
                item = cls.get_article_info(art)
                arts.append(item)
            return arts
        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return []

    @classmethod
    def edit_article_content_by_id(cls, article_id: str, content: str):
        """
        根据文章的ID编辑文章
        Args:
            article_id (str): 文章ID
            content (str): 文章内容
        Returns:
            dict: 编辑后的文章数据
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
            cls, id: str, title: str, category: str, serialNo: int, tags: list, date: str, thumbnail: str, summary: str) -> list:
        """
        根据文章的ID编辑文章元数据
        Args:
            id (str): 文章ID
            title (str): 文章标题
            category (str): 文章分类
            serialNo (int): 文章序号
            tags (list): 文章标签
            date (str): 文章日期
            thumbnail (str): 缩略图链接
            summary (str): 文章摘要
        Returns:
            list: 编辑后的文章数据
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
