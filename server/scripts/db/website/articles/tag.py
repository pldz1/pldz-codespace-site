from typing import List

from scripts.db.connection import _lock, _read_json, get_articles_db_path
from typedef import T_TagCount, T_ArticleData


def find_all_tag_and_counts() -> List[T_TagCount]:
    with _lock:
        data = _read_json(get_articles_db_path())
    tag_map = {}
    for doc in data.values():
        for tag in doc.get('meta', {}).get('tags', []):
            tag_map[tag] = tag_map.get(tag, 0) + 1
    return [T_TagCount(text=t, size=c) for t, c in tag_map.items()]


def find_articles_by_tag(tag: str) -> List[T_ArticleData]:
    with _lock:
        data = _read_json(get_articles_db_path())
    docs = [
        d for d in data.values()
        if tag in d.get('meta', {}).get('tags', [])
        and d.get('meta', {}).get('serialNo', 0) != 0
    ]
    docs.sort(key=lambda d: d.get('meta', {}).get('date', ''), reverse=True)
    return docs
