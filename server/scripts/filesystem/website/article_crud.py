import os
import sys
import uuid
import time
import datetime
import typing
import frontmatter


from core import Logger, ProjectConfig

ARTICLES_DIR = ProjectConfig.get_articles_path()


class ArticleDocument(typing.TypedDict):
    """
    文章文档的结构定义
    id: 文章唯一标识符
    path: 文章文件的相对路径
    meta: 文章的元数据
    content: 文章的内容
    views: 文章的浏览量
    """
    id: str
    path: str
    meta: dict
    content: str
    views: int


class ArticleCrudHandler:
    @classmethod
    def normalize_meta(cls, obj):
        """递归将 metadata 中的 date/datetime 转为 ISO，防止 BSON 序列化错误"""
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: cls.normalize_meta(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [cls.normalize_meta(v) for v in obj]
        return obj

    @classmethod
    def get_file_doc(cls, file_path) -> ArticleDocument:
        """将单个 Markdown 文件转换为 MongoDB 文档格式"""
        try:
            post = frontmatter.load(file_path)
        except Exception as e:
            Logger.info(f"❗ 无法读取 {file_path}: {e}")
            return None

        rel = os.path.relpath(file_path, ARTICLES_DIR)
        pid = uuid.uuid5(uuid.NAMESPACE_URL, rel).hex[:16]

        # 处理 metadata，确保日期格式正确
        meta = cls.normalize_meta(post.metadata)

        # 写入mongodb的文档格式
        # 这里的 id 是基于文件相对路径生成的 UUID，确保唯一性
        doc: ArticleDocument = {'id': pid, 'path': rel, 'meta': meta, 'content': post.content}
        return doc

    @classmethod
    def get_md_file(cls, meta: object, content: str, replace: bool = False) -> str:
        """
        将文章的元数据和内容转换为 Markdown 格式的字符串
        Args:
            meta (object): 文章的元数据，通常是字典类型
            content: 文章内容
            replace (bool): 是否替换已有的元数据，默认为 False
        Returns:
            str: Markdown 格式的字符串
        """
        try:
            post = frontmatter.Post(content, **meta)
            text = frontmatter.dumps(post)
            if replace:
                # 对text全部的图像的数据进行字符串替换
                text = text.replace('/api/v1/image/', 'https://pldz1.com/api/v1/image/')
            return text
        except Exception as e:
            Logger.error(f"❗ 无法转换为 Markdown 格式: {e}")
            return ""

    @classmethod
    def save_file(cls, path: str,  meta: object, content: str) -> bool:
        """
        将文章的元数据和内容保存到缓存文件中
        Args:
            path (str): 文章的相对路径
            meta (object): 文章的元数据，通常是字典类型
            content: 文章内容
        Returns:
            bool: 是否保存成功
        """

        cache_file = os.path.join(ARTICLES_DIR, path)

        # 构建缓存文件的路径
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        text = cls.get_md_file(meta, content)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(text)
            Logger.info(f"✔ 缓存文件已保存: {cache_file}")
            return True
        except Exception as e:
            Logger.info(f"❗ 保存缓存文件失败: {e}")
            return False
