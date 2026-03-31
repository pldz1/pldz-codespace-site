import os
import json
import threading

from core import ProjectConfig

# 全局读写锁，单进程内保证并发安全
_lock = threading.Lock()


def _get_db_dir() -> str:
    return ProjectConfig.get_db_path()


def _read_json(filepath: str) -> dict:
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _write_json(filepath: str, data: dict) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_articles_db_path() -> str:
    return os.path.join(_get_db_dir(), 'articles.json')


def get_users_db_path() -> str:
    return os.path.join(_get_db_dir(), 'users.json')


def get_comments_db_path() -> str:
    return os.path.join(_get_db_dir(), 'comments.json')


# 以下别名保持 __init__.py 导出的兼容性
def get_article_mongo_collection():
    return get_articles_db_path()


def get_user_mongo_collection():
    return get_users_db_path()


def get_comments_mongo_collection():
    return get_comments_db_path()
