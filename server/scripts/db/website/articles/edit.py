import os
from typing import List

from core import Logger, ProjectConfig
from scripts.db.connection import _lock, _read_json, _write_json, get_articles_db_path

ARTICLES_DIR = ProjectConfig.get_articles_path()


def _get_file_doc(path: str):
    from scripts.filesystem import ArticleCrudHandler
    return ArticleCrudHandler.get_file_doc(os.path.join(ARTICLES_DIR, path))


def _save_file(path: str, meta: dict, content: str) -> bool:
    from scripts.filesystem import ArticleCrudHandler
    return ArticleCrudHandler.save_file(path, meta, content)


def set_article_content_by_id(article_id: str, content: str) -> bool:
    """直接将新正文写入 .md 文件，watchdog 自动更新索引"""
    with _lock:
        data = _read_json(get_articles_db_path())
    article = data.get(article_id)
    if not article:
        Logger.warning(f"没有找到或未修改文章 ID: {article_id}")
        return False
    file_doc = _get_file_doc(article['path'])
    if not file_doc:
        return False
    return _save_file(article['path'], file_doc['meta'], content)


def set_article_meta_by_id(
        id: str, title: str, category: str, serialNo: int, tags: List[str],
        date: str, thumbnail: str, summary: str, csdn: str, juejin: str, github: str, gitee: str) -> bool:
    """更新 JSON 索引中的 meta，并同步写回 .md 文件"""
    db = get_articles_db_path()
    with _lock:
        data = _read_json(db)
        if id not in data:
            Logger.warning(f"没有找到或未修改文章标题: {title}")
            return False
        data[id]['meta'].update({
            'title': title,
            'category': category,
            'serialNo': serialNo,
            'tags': tags,
            'date': date,
            'thumbnail': thumbnail,
            'summary': summary,
            'csdn': csdn,
            'juejin': juejin,
            'github': github,
            'gitee': gitee,
        })
        updated_meta = dict(data[id]['meta'])
        path = data[id]['path']
        _write_json(db, data)

    file_doc = _get_file_doc(path)
    content = file_doc['content'] if file_doc else ''
    _save_file(path, updated_meta, content)
    return True


def set_article_serial_no(article_id: str, serial_no: int) -> bool:
    db = get_articles_db_path()
    with _lock:
        data = _read_json(db)
        if article_id not in data:
            return False
        data[article_id]['meta']['serialNo'] = serial_no
        _write_json(db, data)
    return True


def set_article_title(article_id: str, title: str) -> bool:
    db = get_articles_db_path()
    with _lock:
        data = _read_json(db)
        if article_id not in data:
            Logger.warning(f"没有找到或未修改文章 ID: {article_id}")
            return False
        data[article_id]['meta']['title'] = title
        _write_json(db, data)
    return True
