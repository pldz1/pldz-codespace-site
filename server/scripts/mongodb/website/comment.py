
import typing
from pymongo import ReturnDocument
from scripts.mongodb import get_comments_mongo_collection


class CommentItem(typing.TypedDict):
    """
    Web site的评论项配置
    id: 评论ID
    created: 创建时间
    username: 用户名
    content: 评论内容
    avatar: 用户头像链接
    replies: 回复列表，每个回复也是一个CommentItem
    例如:
    {
        "id": "12345",
        "created": "2023-10-01T12:00:00Z",
        "username": "user123",
        "content": "这是一个评论",
        "avatar": "https://example.com/avatar.jpg",
        "replies": [
            {
                "id": "12346",
                "created": "2023-10-01T12:05:00Z",
                "username": "user456",
                "content": "这是一个回复",
                "avatar": "https://example.com/avatar2.jpg",
                "replies": [],
                "replyToUsername": "user123",
            }
        ],
        "replyToUsername": "",
    }
    """
    id: str
    created: str
    username: str
    content: str
    avatar: str
    replies: list
    replyToUsername: str


class MongoCommentItem(typing.TypedDict):
    """
    MongoDB存储的评论项配置
    article_id: 文章的唯一id
    data: 评论列表, 每个评论也是一个CommentItem
    """
    article_id: str
    # 使用 CommentItem 类型来表示回复列表
    data: typing.List[CommentItem]


class CommentHandler:
    def __init__(self):
        pass

    @classmethod
    def get_all_comments_by_id(cls, article_id: str) -> typing.List[CommentItem]:
        """
        获取指定ID的评论
        :param article_id: 文章的唯一ID
        :return: 评论列表
        """
        if not article_id:
            return []

        coll = get_comments_mongo_collection()
        # 不存在就插入 {id, data: []}，并返回插入或更新后的文档
        doc = coll.find_one_and_update(
            {"id": article_id},
            {"$setOnInsert": {"data": []}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return doc.get("data", [])

    @classmethod
    def add_comment(cls, article_id: str, comment: CommentItem, parent_id: str) -> bool:
        """
        添加评论
        :param article_id: 文章的唯一ID
        :param comment: 要添加的评论
        :param parent_id: 父评论的ID,如果是顶级评论则为 None
        :return: 是否添加成功
        """
        if not article_id or not comment:
            return False

        coll = get_comments_mongo_collection()

        # 确保评论有必要的字段
        required = CommentItem.__required_keys__
        missing = required - comment.keys()
        if missing:
            return False

        # 查找对应的文章评论数据
        mongo_item = coll.find_one({"id": article_id})

        if not mongo_item:
            # 如果没有找到，插入一个新的文档
            mongo_item = {"id": article_id, "data": []}
            coll.insert_one(mongo_item)

        # 添加评论到数据中
        if parent_id:
            # 如果有父评论，找到父评论并添加到其回复列表中
            for item in mongo_item["data"]:
                if item["id"] == parent_id:
                    item.setdefault("replies", []).append(comment)
                    break
            else:
                # 如果没有找到父评论，则直接添加为顶级评论
                mongo_item["data"].append(comment)
        else:
            # 如果没有父评论，直接添加为顶级评论
            mongo_item["data"].append(comment)

        # 更新数据库中的文档
        coll.update_one({"id": article_id}, {"$set": {"data": mongo_item["data"]}})

        return True

    @classmethod
    def delete_comment(cls, article_id: str, comment_id: str) -> bool:
        """
        删除评论（支持任意深度的回复）
        :param article_id: 文章唯一ID
        :param comment_id: 要删除的评论ID
        :return: True=删除成功，False=没找到或参数无效
        """
        if not article_id or not comment_id:
            return False

        coll = get_comments_mongo_collection()
        doc = coll.find_one({"id": article_id})
        if not doc:
            return False

        def _remove_comments(data: typing.List[CommentItem]):
            new_list = []
            deleted = False
            for item in data:
                if item["id"] == comment_id:
                    # 当前这条被删
                    deleted = True
                    continue
                # 向下递归处理 replies
                if isinstance(item.get("replies"), list) and item["replies"]:
                    updated_replies, sub_deleted = _remove_comments(item["replies"])
                    if sub_deleted:
                        deleted = True
                        item["replies"] = updated_replies
                new_list.append(item)
            return new_list, deleted

        original_data = doc.get("data", [])
        updated_data, deleted = _remove_comments(original_data)

        if not deleted:
            # 顶层和所有嵌套里都没找到要删的ID
            return False

        # 确实删除了，写回数据库
        coll.update_one(
            {"id": article_id},
            {"$set": {"data": updated_data}}
        )
        return True
