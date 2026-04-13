from typing import List, Optional
from typedef import T_ArticleData, T_TagCount

from .articles.category import find_all_categories, find_articles_by_category
from .articles.article import find_all_articles, find_article_by_id
from .articles.tag import find_all_tag_and_counts, find_articles_by_tag


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
