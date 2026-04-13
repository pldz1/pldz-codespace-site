from fastapi import HTTPException, status
from scripts.db import AuthorizedHandler
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
