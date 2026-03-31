import os
from typing import List, Optional

from core import Logger, ProjectConfig
from scripts.db.connection import _lock, _read_json, _write_json, get_articles_db_path
from typedef.db.article import T_ArticleData

ARTICLES_DIR = ProjectConfig.get_articles_path()


def _read_content(path: str) -> str:
    """从 .md 文件读取正文内容（不含 frontmatter）"""
    from scripts.filesystem import ArticleCrudHandler
    full_path = os.path.join(ARTICLES_DIR, path)
    file_doc = ArticleCrudHandler.get_file_doc(full_path)
    return file_doc['content'] if file_doc else ''


def find_all_articles() -> List[T_ArticleData]:
    with _lock:
        data = _read_json(get_articles_db_path())
    docs = [d for d in data.values() if d.get('meta', {}).get('serialNo', 0) != 0]
    docs.sort(key=lambda d: d.get('meta', {}).get('date', ''), reverse=True)
    return docs


def find_article_by_id(id: str) -> Optional[T_ArticleData]:
    db = get_articles_db_path()
    with _lock:
        data = _read_json(db)
        doc = data.get(id)
        if not doc:
            return None
        doc['views'] = doc.get('views', 0) + 1
        data[id] = doc
        _write_json(db, data)

    result = dict(doc)
    result['content'] = _read_content(doc['path'])
    return result


def delete_article_by_id(article_id: str) -> bool:
    db = get_articles_db_path()
    with _lock:
        data = _read_json(db)
        article = data.get(article_id)
        if not article:
            Logger.warning(f"没有找到文章 ID: {article_id}")
            return False
        del data[article_id]
        _write_json(db, data)

    path = article.get('path', '')
    full_path = os.path.join(ARTICLES_DIR, path)
    if os.path.exists(full_path):
        os.remove(full_path)
        Logger.info(f"✔ 已删除文章文件: {full_path}")
    else:
        Logger.warning(f"没有找到文章文件: {full_path}")
    return True


def get_article_text_by_id(article_id: str) -> str:
    with _lock:
        data = _read_json(get_articles_db_path())
    article = data.get(article_id)
    if not article:
        Logger.warning(f"没有找到文章 ID: {article_id}")
        return "没有找到文章"
    try:
        from scripts.filesystem import ArticleCrudHandler
        full_path = os.path.join(ARTICLES_DIR, article['path'])
        file_doc = ArticleCrudHandler.get_file_doc(full_path)
        if not file_doc:
            return "没有找到文章"
        return ArticleCrudHandler.get_md_file(file_doc['meta'], file_doc['content'], True)
    except Exception as e:
        Logger.error(f"✖ 获取文章内容失败: {e}")
        return "获取文章内容失败"
