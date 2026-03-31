import typing

from scripts.db.connection import _lock, _read_json, _write_json, get_comments_db_path


class CommentItem(typing.TypedDict):
    id: str
    created: str
    username: str
    content: str
    avatar: str
    replies: list
    replyToUsername: str


class CommentHandler:
    def __init__(self):
        pass

    @classmethod
    def get_all_comments_by_id(cls, article_id: str) -> typing.List[CommentItem]:
        if not article_id:
            return []
        db = get_comments_db_path()
        with _lock:
            data = _read_json(db)
            if article_id not in data:
                data[article_id] = []
                _write_json(db, data)
            return data[article_id]

    @classmethod
    def add_comment(cls, article_id: str, comment: CommentItem, parent_id: str) -> bool:
        if not article_id or not comment:
            return False
        required = CommentItem.__required_keys__
        missing = required - comment.keys()
        if missing:
            return False
        db = get_comments_db_path()
        with _lock:
            data = _read_json(db)
            if article_id not in data:
                data[article_id] = []
            comments = data[article_id]
            if parent_id:
                for item in comments:
                    if item['id'] == parent_id:
                        item.setdefault('replies', []).append(comment)
                        break
                else:
                    comments.append(comment)
            else:
                comments.append(comment)
            data[article_id] = comments
            _write_json(db, data)
        return True

    @classmethod
    def delete_comment(cls, article_id: str, comment_id: str) -> bool:
        if not article_id or not comment_id:
            return False
        db = get_comments_db_path()
        with _lock:
            data = _read_json(db)
            if article_id not in data:
                return False

            def _remove_comments(lst: typing.List[CommentItem]):
                new_list = []
                deleted = False
                for item in lst:
                    if item['id'] == comment_id:
                        deleted = True
                        continue
                    if isinstance(item.get('replies'), list) and item['replies']:
                        updated_replies, sub_deleted = _remove_comments(item['replies'])
                        if sub_deleted:
                            deleted = True
                            item['replies'] = updated_replies
                    new_list.append(item)
                return new_list, deleted

            updated_data, deleted = _remove_comments(data[article_id])
            if not deleted:
                return False
            data[article_id] = updated_data
            _write_json(db, data)
        return True
