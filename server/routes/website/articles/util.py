from fastapi import HTTPException, status
from scripts.mongodb import AuthorizedHandler
from typedef import T_ArticleData, T_ArticleInfo


def build_all_article_format(art: T_ArticleData) -> T_ArticleInfo:
    """
    将文章数据转换为统一格式
    Args:
        art (T_ArticleData): 文章数据
    Returns:
        T_ArticleInfo: 转换后的文章信息
    """
    meta = art.get('meta', {})
    return T_ArticleInfo(
        id=art.get('id', ''),
        title=meta.get('title', ''),
        category=meta.get('category', ''),
        summary=meta.get('summary', ''),
        serialNo=meta.get('serialNo', 0),
        thumbnail=meta.get('thumbnail', ''),
        tags=meta.get('tags', []),
        views=art.get('views', 0),
        date=meta.get('date', ''),
        path=art.get('path', ''),
        csdn=meta.get('csdn', ''),
        juejin=meta.get('juejin', ''),
        github=meta.get('github', ''),
        gitee=meta.get('gitee', '')
    )


def check_user_permission(user: dict):
    """
    检查用户是否有权限编辑文章
    Args:
        user (dict): 用户信息
    Raises:
        HTTPException: 如果用户未登录或没有权限
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to handle articles."
        )

    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to handle articles."
        )
