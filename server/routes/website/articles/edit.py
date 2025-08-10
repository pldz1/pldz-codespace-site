from pydantic import BaseModel
from scripts.mongodb.website import ArticleHandler
from .util import check_user_permission

# =========================================================================


class T_Articl_Edit_Request(BaseModel):
    article_id: str
    content: str


class T_Articl_Edit_Response(BaseModel):
    data: bool


async def edit_article_content(article: T_Articl_Edit_Request, user: dict):
    """
    编辑文章
    Args:
        article (T_Articl_Edit_Request): 文章编辑数据
    Returns:
        bool: 编辑后的文章数据的结果
    """
    check_user_permission(user)
    res = ArticleHandler.edit_article_content_by_id(article.article_id, article.content)
    return T_Articl_Edit_Response(data=res)


# =========================================================================

class T_Article_MetaEdit_Request(BaseModel):
    article_id: str
    title: str = ""
    category: str = ""
    serialNo: int = 0
    tags: list = []
    date: str = ""
    thumbnail: str = ""
    summary: str = ""


async def edit_article_meta(article_meta: T_Article_MetaEdit_Request, user: dict):
    """
    编辑文章元数据
    Args:
        article_meta (T_Article_MetaEdit_Request): 文章编辑数据
    Returns:
        bool: 编辑后的文章元数据的结果
    """
    check_user_permission(user)
    res = ArticleHandler.edit_article_meta_by_id(
        article_meta.article_id,
        article_meta.title,
        article_meta.category,
        article_meta.serialNo,
        article_meta.tags,
        article_meta.date,
        article_meta.thumbnail,
        article_meta.summary
    )
    return T_Articl_Edit_Response(data=res)


# =========================================================================

class T_Article_SerialNoEdit_Request(BaseModel):
    id: str
    serialNo: int


async def edit_article_serialno(article_data: T_Article_SerialNoEdit_Request, user: dict):
    """
    编辑文章序号
    Args:
        article_data (T_Article_SerialNoEdit_Request): 文章序号编辑数据
    Returns:
        dict: 编辑后的文章序号数据
    """
    check_user_permission(user)
    res = ArticleHandler.edit_article_serial_no(article_data.id, article_data.serialNo)
    return T_Articl_Edit_Response(data=res)
