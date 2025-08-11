import fastapi
from scripts.mongodb import AuthorizedHandler
from .articles.all import all_articles, all_categories, all_tags
from .articles.article import T_Article_Exist_Request, get_articles_by_id, article_exist
from .articles.tag import get_articles_by_tag
from .articles.category import get_articles_by_category
from .articles.git import T_GitSync_Request, git_sync, git_pull
from .articles.file import \
    T_Add_Article_Request, \
    T_Article_File_Request, \
    T_Set_Article_Filename_Request, \
    T_Add_Category_Request, \
    add_article, \
    delete_article, \
    save_article_to_cache, \
    get_article_text, \
    sync_all_articles, \
    set_article_filename, \
    add_category
from .articles.edit import \
    T_Articl_Edit_Request, \
    T_Article_MetaEdit_Request, \
    T_Article_SerialNoEdit_Request, \
    T_Article_TitleEdit_Request, \
    edit_article_content, \
    edit_article_meta, \
    edit_article_serialno, \
    edit_article_title

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


@ARTICLES_ROUTE.post("/edit/content")
async def api_edit_article(article_edit: T_Articl_Edit_Request, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    return await edit_article_content(article_edit, user)


@ARTICLES_ROUTE.post("/edit/meta")
async def api_edit_article_meta(article_meta: T_Article_MetaEdit_Request, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    return await edit_article_meta(article_meta, user)


@ARTICLES_ROUTE.post("/edit/exist")
async def api_article_exist(article_data: T_Article_Exist_Request, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    return await article_exist(article_data, user)


@ARTICLES_ROUTE.post("/edit/serialNo")
async def api_edit_article_serialno(article_data: T_Article_SerialNoEdit_Request, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    return await edit_article_serialno(article_data, user)


@ARTICLES_ROUTE.post("/edit/title")
async def api_edit_article_title(article_data: T_Article_TitleEdit_Request, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    return await edit_article_title(article_data, user)


@ARTICLES_ROUTE.post("/file/new")
async def api_add_article(article_data: T_Add_Article_Request, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    return await add_article(article_data, user)


@ARTICLES_ROUTE.post("/file/delete")
async def api_delete_article(article: T_Article_File_Request, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    return await delete_article(article, user)


@ARTICLES_ROUTE.post("/file/sync")
async def api_save_article_to_cache(article: T_Article_File_Request, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    return await save_article_to_cache(article, user)


@ARTICLES_ROUTE.post("/file/text")
async def api_get_article_text(article: T_Article_File_Request, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    return await get_article_text(article, user)


@ARTICLES_ROUTE.post("/file/syncall")
async def api_sync_all_articles(user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    return await sync_all_articles(user)


@ARTICLES_ROUTE.post("/file/rename")
async def api_set_article_filename(article: T_Set_Article_Filename_Request, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    return await set_article_filename(article, user)


@ARTICLES_ROUTE.post("/file/addcategory")
async def api_add_category(category_data: T_Add_Category_Request, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    return await add_category(category_data, user)


@ARTICLES_ROUTE.post("/plugin/gitsync")
async def api_git_sync(git_data: T_GitSync_Request, user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    return await git_sync(git_data, user)


@ARTICLES_ROUTE.post("/plugin/gitpull")
async def api_git_pull(user: dict = fastapi.Depends(AuthorizedHandler.get_current_user)):
    return await git_pull(user)
