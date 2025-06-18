import fastapi
from pydantic import BaseModel

from scripts.mongodb import ArticleHandler, AuthorizedHandler


# 这里的 ARTICLES_ROUTE 是一个 FastAPI 的路由对象，用于定义与文章相关的 API 路径
ARTICLES_ROUTE = fastapi.APIRouter(prefix="/api/v1/article", tags=["article"])


@ARTICLES_ROUTE.get("/all/category")
async def api_all_categories():
    """
    获取所有文章的分类列表
    Returns:
        list: 包含所有分类的列表
    """

    categories = ArticleHandler.get_all_categories()
    return {"data": categories}


@ARTICLES_ROUTE.get("/all/article")
async def api_all_articles():
    """
    获取所有文章的列表
    Returns:
        list: 包含所有文章的列表
    """
    all_articles = ArticleHandler.get_all_articles()
    return {"data": all_articles}


@ARTICLES_ROUTE.get("/id/{article_id}")
async def api_articles_by_id(article_id: str):
    """
    根据文章ID获取文章内容
    Args:
        article_id (str): 文章的唯一标识符
    """
    article = ArticleHandler.get_article_by_id(article_id)
    return {"data": article}


@ARTICLES_ROUTE.get("/all/tag")
async def api_all_tags():
    """
    获取所有文章的标签及其对应的文章数量
    Returns:
        list: 包含所有标签及其文章数量的列表
    """
    tag_counts = ArticleHandler.get_all_tag_and_counts()
    return {"data": tag_counts}


@ARTICLES_ROUTE.get("/tag/{tag_name}")
async def api_articles_by_tag(tag_name: str):
    """
    根据标签获取文章列表
    Args:
        tag_name (str): 标签名称
    Returns:
        list: 相关文章列表
    """
    articles = ArticleHandler.get_articles_by_tag(tag_name)
    return {"data": articles}


@ARTICLES_ROUTE.get("/category/{category_name}")
async def api_articles_by_category(category_name: str):
    """
    根据分类获取文章列表
    Args:
        category_name (str): 分类名称
    Returns:
        list: 该分类下的所有文章列表
    """
    articles = ArticleHandler.get_articles_by_category(category_name)
    return {"data": articles}


class ArticleEdit(BaseModel):
    article_id: str
    content: str


@ARTICLES_ROUTE.post("/edit/content")
async def api_edit_article(article_edit: ArticleEdit, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    """
    编辑文章
    Args:
        article_edit (ArticleEdit): 文章编辑数据
    Returns:
        dict: 编辑后的文章数据
    """
    if not user:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to edit articles."
        )
    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit articles."
        )

    res = ArticleHandler.edit_article_content_by_id(
        article_edit.article_id, article_edit.content)
    return {"data": res}


class ArticleMetaEdit(BaseModel):
    article_id: str
    title: str = ""
    category: str = ""
    serialNo: int = 0
    tags: list = []
    date: str = ""
    thumbnail: str = ""
    summary: str = ""


@ARTICLES_ROUTE.post("/edit/meta")
async def api_edit_article_meta(article_meta_edit: ArticleMetaEdit, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    """
    编辑文章元数据
    Args:
        article_meta_edit (ArticleMetaEdit): 文章编辑数据
    Returns:
        dict: 编辑后的文章元数据
    """
    if not user:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to edit articles."
        )

    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit articles."
        )

    res = ArticleHandler.edit_article_meta_by_id(
        article_meta_edit.article_id,
        article_meta_edit.title,
        article_meta_edit.category,
        article_meta_edit.serialNo,
        article_meta_edit.tags,
        article_meta_edit.date,
        article_meta_edit.thumbnail,
        article_meta_edit.summary
    )
    return {"data": res}
