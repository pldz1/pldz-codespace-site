
import typing
import datetime
import hashlib


INVALID_TIME = 60*10  # 10分钟的秒数


class WhiteBoardItem(typing.TypedDict):
    """
    白板项配置
    created: 创建时间
    key: 白板项的键
    content: 白板项的内容
    username: 创建者的用户名
    """
    created: str
    key: str
    content: str
    username: str


class WhiteBoardHandler:
    white_board_list: typing.List[WhiteBoardItem] = []

    def __init__(self):
        pass

    @classmethod
    def hash_username(cls, username: str) -> str:
        """
        哈希用户名
        :param username: 用户名
        :return: 哈希后的用户名
        """
        if not username:
            return ""
        h = hashlib.new('sha256')
        h.update(username.encode('utf-8'))
        return h.hexdigest()

    @classmethod
    def get_item_by_username(cls, username) -> typing.Optional[WhiteBoardItem]:
        """
        获取指定用户名的白板内容
        :param username: 用户名
        :return: 白板元素
        """
        if not username:
            return None
        for item in cls.white_board_list:
            if item['username'] == username:
                # 如果创建时间超过10分钟返回空字符串
                if (item['created'] and
                        (datetime.datetime.now() - datetime.datetime.fromisoformat(item['created'])).total_seconds() > INVALID_TIME):
                    return {
                        'created': datetime.datetime.now().isoformat(),
                        'key': cls.hash_username(username),
                        'content': "",
                        'username': username,
                    }
                # 返回白板内容
                return item
        # 如果没有找到或用户名为空，返回空内容但是新的item
        return {
            'created': datetime.datetime.now().isoformat(),
            'key': cls.hash_username(username),
            'content': "",
            'username': username,
        }

    @classmethod
    def get_item_by_key(cls, key: str) -> typing.Optional[WhiteBoardItem]:
        """
        获取指定键的白板内容
        :param key: 白板项的键
        :return: 白板元素
        """
        if not key:
            return None
        for item in cls.white_board_list:
            if item['key'] == key:
                # 如果创建时间超过10分钟返回空字符串
                if (item['created'] and
                        (datetime.datetime.now() - datetime.datetime.fromisoformat(item['created'])).total_seconds() > INVALID_TIME):
                    return {
                        'created': datetime.datetime.now().isoformat(),
                        'key': key,
                        'content': "",
                        'username': item['username'],
                    }
                # 返回白板内容
                return item
        # 如果没有找到或键为空，返回空
        return None

    @classmethod
    def set_content_by_key(cls, key: str, content: str) -> str:
        """
        设置指定键的白板内容
        :param key: 白板项的键
        :param content: 白板内容
        """
        if not key or not content:
            return ""
        # 检查是否已存在该键的白板项
        for item in cls.white_board_list:
            if item['key'] == key:
                item['content'] = content
                item['created'] = datetime.datetime.now().isoformat()
                return item['created']
        # 如果不存在, 返回空
        return ""
