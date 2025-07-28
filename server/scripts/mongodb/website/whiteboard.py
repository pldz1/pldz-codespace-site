
import typing
import datetime
import random


INVALID_TIME = 60*60*24  # 一天


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
    def random_key(cls, username: str, length: int = 4) -> str:
        """
        生成指定长度的随机字符串
        :param username: 用户名
        :param length: 字符串长度
        :return: 随机字符串"""
        # 可选字符：大写、小写、数字
        name = username.split('@')[0]
        rnum = random.randint(100, 999)
        return f"{name}-{rnum}"

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
                # 如果创建时间超过 INVALID_TIME 返回空字符串
                if (item['created'] and
                        (datetime.datetime.now() - datetime.datetime.fromisoformat(item['created'])).total_seconds() > INVALID_TIME):

                    # 如果new_key与现有的key重复，重新生成
                    new_key = cls.random_key(username)
                    while any(existing_item['key'] == new_key for existing_item in cls.white_board_list):
                        new_key = cls.random_key(username)

                    # 返回新的白板项
                    cls.white_board_list.remove(item)
                    new_item = {
                        'created': datetime.datetime.now().isoformat(),
                        'key': new_key,
                        'content': "",
                        'username': username,
                    }
                    cls.white_board_list.append(new_item)
                    # 返回新的白板项
                    return new_item
                # 返回白板内容
                return item
        # 如果没有找到或用户名为空，返回空内容但是新的item
        new_item = {
            'created': datetime.datetime.now().isoformat(),
            'key': cls.random_key(username),
            'content': "",
            'username': username,
        }
        cls.white_board_list.append(new_item)
        return new_item

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
                # 如果创建时间超过 INVALID_TIME 分钟返回空字符串
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
        if not key:
            return ""
        # 检查是否已存在该键的白板项
        for item in cls.white_board_list:
            if item['key'] == key:
                item['content'] = content
                item['created'] = datetime.datetime.now().isoformat()
                return item['created']
        # 如果不存在, 返回空
        return ""
