from typing import TypedDict, List


class T_ArticleMeta(TypedDict):
    """
    文章完整元数据结构(MongoDB 数据库存储)
    - title: 文章标题
    - author: 文章作者
    - category: 文章分类
    - serialNo: 文章序号
    - status: 文章状态（如：草稿、已发布）
    - tags: 文章标签列表
    - date: 文章发布日期
    - thumbnail: 缩略图链接
    - summary: 文章摘要
    """
    title: str
    author: str
    category: str
    serialNo: int
    status: str
    tags: List[str]
    date: str
    thumbnail: str
    summary: str


class T_ArticleData(TypedDict):
    """
    完整文章数据结构(数据库存储)
    - id: 文章唯一标识符
    - meta: 文章元数据
    - content: 文章内容
    - path: 文章路径
    - views: 文章浏览量
    """
    id: str
    meta: T_ArticleMeta
    content: str
    path: str
    views: int
