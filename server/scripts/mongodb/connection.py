import os
import sys
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

from core import Logger

# MongoDB 配置
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DB = os.environ.get('MONGODB_DB', 'blog-server')
MONGODB_ARTICLE_COLL = os.environ.get('MONGODB_ARTICLE_COLL', 'articles')
MONGODB_USER_COLL = os.environ.get('MONGODB_USER_COLL', 'users')
MONGODB_COMMENT_COLL = os.environ.get('MONGODB_COMMENT_COLL', 'comments')
CONNECT_TIMEOUT_MS = int(os.environ.get('MONGODB_CONNECT_TIMEOUT_MS', 10000))
SOCKET_TIMEOUT_MS = int(os.environ.get('MONGODB_SOCKET_TIMEOUT_MS', 10000))


# 唯一的链接
_client = None


def get_article_mongo_collection():
    """初始化并返回 MongoDB 的 article 的collection"""
    global _client
    if _client is None:
        try:
            _client = MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=CONNECT_TIMEOUT_MS,
                socketTimeoutMS=SOCKET_TIMEOUT_MS
            )
            _client.admin.command('ping')
        except ServerSelectionTimeoutError as e:
            Logger.info(f"✖ 无法连接到 MongoDB: {e}")
            sys.exit(1)
        except PyMongoError as e:
            Logger.info(f"✖ MongoDB 错误: {e}")
            sys.exit(1)

    db = _client[MONGODB_DB]
    coll = db[MONGODB_ARTICLE_COLL]
    coll.create_index('id', unique=True)
    return coll


def get_user_mongo_collection():
    """初始化并返回 MongoDB 的 user 的collection"""
    global _client
    if _client is None:
        try:
            _client = MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=CONNECT_TIMEOUT_MS,
                socketTimeoutMS=SOCKET_TIMEOUT_MS
            )
            _client.admin.command('ping')
        except ServerSelectionTimeoutError as e:
            Logger.info(f"✖ 无法连接到 MongoDB: {e}")
            sys.exit(1)
        except PyMongoError as e:
            Logger.info(f"✖ MongoDB 错误: {e}")
            sys.exit(1)

    db = _client[MONGODB_DB]
    coll = db[MONGODB_USER_COLL]
    coll.create_index('id', unique=True)
    return coll


def get_comments_mongo_collection():
    """初始化并返回 MongoDB 的 comments 的collection"""
    global _client
    if _client is None:
        try:
            _client = MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=CONNECT_TIMEOUT_MS,
                socketTimeoutMS=SOCKET_TIMEOUT_MS
            )
            _client.admin.command('ping')
        except ServerSelectionTimeoutError as e:
            Logger.info(f"✖ 无法连接到 MongoDB: {e}")
            sys.exit(1)
        except PyMongoError as e:
            Logger.info(f"✖ MongoDB 错误: {e}")
            sys.exit(1)

    db = _client[MONGODB_DB]
    coll = db[MONGODB_COMMENT_COLL]
    coll.create_index('id', unique=True)
    return coll
