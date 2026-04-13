import fastapi
from .articles.all import all_articles, all_categories, all_tags
from .articles.article import get_articles_by_id
from .articles.tag import get_articles_by_tag
from .articles.category import get_articles_by_category

ARTICLES_ROUTE = fastapi.APIRouter(prefix="/website/article", tags=["website-article"])


@ARTICLES_ROUTE.get("/all/category")
async def api_all_categories():
    return await all_categories()


@ARTICLES_ROUTE.get("/all/article")
async def api_all_articles():
    return await all_articles()


@ARTICLES_ROUTE.get("/all/tag")
async def api_all_tags():
    return await all_tags()


@ARTICLES_ROUTE.get("/id/{article_id}")
async def api_articles_by_id(article_id: str):
    return await get_articles_by_id(article_id)


@ARTICLES_ROUTE.get("/tag/{tag_name}")
async def api_articles_by_tag(tag_name: str):
    return await get_articles_by_tag(tag_name)


@ARTICLES_ROUTE.get("/category/{category_name}")
async def api_articles_by_category(category_name: str):
    return await get_articles_by_category(category_name)
