from typing import TypedDict, List


class T_ArticleInfo(TypedDict):
    """
    文章展示信息结构（前端使用的精简版）
    - id: 文章唯一标识符
    - title: 文章标题
    - category: 文章分类
    - summary: 文章摘要
    - serialNo: 文章序号
    - thumbnail: 缩略图链接
    - tags: 文章标签列表
    - views: 文章浏览量
    - date: 文章发布日期
    """
    id: str
    title: str
    category: str
    summary: str
    serialNo: int
    thumbnail: str
    tags: List[str]
    views: int
    date: str
