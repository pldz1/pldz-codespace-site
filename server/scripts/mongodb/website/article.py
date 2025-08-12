from typing import AsyncGenerator, Any, Dict, List, Optional
from typedef import T_ArticleData, T_TagCount

from .articles.category import find_all_categories, find_articles_by_category, find_latest_serial_no, find_article_in_category
from .articles.article import find_all_articles, find_article_by_id, delete_article_by_id, get_article_text_by_id
from .articles.tag import find_all_tag_and_counts, find_articles_by_tag
from .articles.edit import set_article_content_by_id, set_article_meta_by_id, set_article_serial_no, set_article_title
from .articles.file import write_article_to_file, write_all_article, rename_article_file, create_category, create_article_file


class ArticleHandler:

    def __init__(self) -> None:
        pass

    @classmethod
    def get_all_categories(cls) -> List[str]:
        return find_all_categories()

    @classmethod
    def get_all_articles(cls) -> List[T_ArticleData]:
        return find_all_articles()

    @classmethod
    def get_article_by_id(cls, article_id: str) -> Optional[T_ArticleData]:
        return find_article_by_id(article_id)

    @classmethod
    def get_all_tag_and_counts(cls) -> List[T_TagCount]:
        return find_all_tag_and_counts()

    @classmethod
    def get_articles_by_category(cls, category: str) -> List[T_ArticleData]:
        return find_articles_by_category(category)

    @classmethod
    def get_articles_by_tag(cls, tag: str) -> List[T_ArticleData]:
        return find_articles_by_tag(tag)

    @classmethod
    def edit_article_content_by_id(cls, article_id: str, content: str) -> bool:
        return set_article_content_by_id(article_id, content)

    @classmethod
    def edit_article_meta_by_id(
            cls,
            id: str,
            title: str,
            category: str,
            serialNo: int,
            tags: List[str],
            date: str,
            thumbnail: str,
            summary: str
    ) -> bool:
        return set_article_meta_by_id(id, title, category, serialNo, tags, date, thumbnail, summary)

    @classmethod
    def get_latest_serial_no(cls, category: str) -> int:
        return find_latest_serial_no(category)

    @classmethod
    def edit_article_serial_no(cls, article_id: str, serial_no: int) -> bool:
        return set_article_serial_no(article_id, serial_no)

    @classmethod
    def edit_article_title(cls, article_id: str, title: str) -> bool:
        return set_article_title(article_id, title)

    @classmethod
    def is_article_exists(cls, category: str, title: str) -> bool:
        return find_article_in_category(category, title)

    @classmethod
    def add_article_by_title_and_category(cls, category: str, title: str, username: str) -> str:
        return create_article_file(category, title, username)

    @classmethod
    def delete_article(cls, article_id: str) -> bool:
        return delete_article_by_id(article_id)

    @classmethod
    def get_article_text(cls, article_id: str) -> str:
        return get_article_text_by_id(article_id)

    @classmethod
    def set_article_filename(cls, article_id: str, filename: str) -> str:
        return rename_article_file(article_id, filename)

    @classmethod
    def add_category(cls, category: str) -> bool:
        return create_category(category)

    @classmethod
    def sync_article_file(cls, article_id: str) -> bool:
        return write_article_to_file(article_id)

    @classmethod
    async def sync_all_article(cls) -> AsyncGenerator[str, Any]:
        yield await write_all_article()
