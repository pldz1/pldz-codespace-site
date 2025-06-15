import fastapi
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from scripts.mongodb import ArticleHandler, AuthorizedHandler
from plugins.git import GitHandler


# 这里的 ARTICLES_ROUTE 是一个 FastAPI 的路由对象，用于定义与文章相关的 API 路径
ARTICLES_ROUTE = fastapi.APIRouter(prefix="/website/article", tags=["website-article"])


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


class NewArticle(BaseModel):
    title: str = ""
    category: str = ""


@ARTICLES_ROUTE.post("/edit/exist")
async def api_edit_article_exist(article_data: NewArticle, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    """
    编辑已存在文章
    Args:
        article_data (NewArticle): 文章数据
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

    res = ArticleHandler.is_article_exists(article_data.category, article_data.title)
    return {"data": res}


class ArticleSerialNoEdit(BaseModel):
    id: str
    serialNo: int


@ARTICLES_ROUTE.post("/edit/serialNo")
async def api_edit_article_serialno(article_data: ArticleSerialNoEdit, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    """
    编辑文章序号
    Args:
        article_data (ArticleSerialNoEdit): 文章序号编辑数据
    Returns:
        dict: 编辑后的文章序号数据
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

    res = ArticleHandler.set_article_serial_no(article_data.id, article_data.serialNo)
    return {"data": res}


@ARTICLES_ROUTE.post("/file/new")
async def api_edit_article_meta(article_data: NewArticle, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    """
    创建新文章
    Args:
        article_data (NewArticle): 文章数据
    Returns:
        dict: 创建的新文章数据
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

    res = ArticleHandler.add_article_by_title_and_category(article_data.category, article_data.title, username)

    return {"data": res}


class ArticleID(BaseModel):
    id: str


@ARTICLES_ROUTE.post("/file/delete")
async def api_delete_article(article: ArticleID, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    """
    删除文章
    Args:
        article (ArticleID): 文章对象，包含 id
    Returns:
        dict: 删除操作的结果
    """
    if not user:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to delete articles."
        )

    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete articles."
        )

    res = ArticleHandler.delete_article_by_id(article.id)
    return {"data": res}


@ARTICLES_ROUTE.post("/file/sync")
async def api_save_article_to_cache(article: ArticleID, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    """
    将文章保存到缓存
    Args:
        article (ArticleID): 文章对象，包含 id
    Returns:
        dict: 保存操作的结果
    """
    if not user:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to save articles to cache."
        )

    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to save articles to cache."
        )

    res = ArticleHandler.sync_article_file(article.id)
    return {"data": res}


@ARTICLES_ROUTE.post("/file/text")
async def api_get_article_text(article: ArticleID, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    """
    获取文章文件内容
    Args:
        article (ArticleID): 文章对象，包含 id
    Returns:
        dict: 文章文件内容
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

    res = ArticleHandler.get_article_text(article.id)
    return {"data": res}


@ARTICLES_ROUTE.post("/file/syncall")
async def api_sync_all_articles(user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    """
    同步所有文章
    Args:
        user (dict): 当前用户信息
    Returns:
        dict: 同步结果
    """
    if not user:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to sync articles."
        )

    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to sync articles."
        )

    return StreamingResponse(ArticleHandler.sync_all_article(), media_type="text/event-stream")


class GitSyncData(BaseModel):
    """
    Git同步数据模型
    """
    commit: str = ""


@ARTICLES_ROUTE.post("/plugin/gitsync")
async def api_git_sync(git_data: GitSyncData, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    """
    同步所有文章到Git仓库
    通过GitHandler处理Git同步
    需要用户登录并且是管理员权限
    Args:
        git_data (GitSyncData): Git同步数据 其中 commit 字段是可选的提交信息
        user (dict): 当前用户信息
    Returns:
        dict: 同步结果
    """
    if not user:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to sync articles."
        )

    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to sync articles."
        )

    commit_message = git_data.commit if git_data.commit else "✨ Sync articles"
    return StreamingResponse(GitHandler.git_sync(commit_message), media_type="text/event-stream")


@ARTICLES_ROUTE.post("/plugin/gitpull")
async def api_git_pull(user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    """
    从Git仓库拉取最新代码
    通过GitHandler处理Git拉取
    """
    if not user:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to sync articles."
        )

    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to sync articles."
        )

    return StreamingResponse(GitHandler.get_pull_async(), media_type="text/event-stream")
