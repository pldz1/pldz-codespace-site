from typing import List

from scripts.db.connection import _lock, _read_json, get_articles_db_path
from typedef import T_ArticleData
from .article import _is_published


def find_all_categories() -> List[str]:
    with _lock:
        data = _read_json(get_articles_db_path())
    categories = list({
        d['meta']['category']
        for d in data.values()
        if _is_published(d) and 'category' in d.get('meta', {})
    })
    return categories


def find_articles_by_category(category: str) -> List[T_ArticleData]:
    with _lock:
        data = _read_json(get_articles_db_path())
    docs = [
        d for d in data.values()
        if _is_published(d)
        and d.get('meta', {}).get('category') == category
        and d.get('meta', {}).get('serialNo', 0) != 0
    ]
    docs.sort(key=lambda d: d.get('meta', {}).get('serialNo', 0))
    return docs
