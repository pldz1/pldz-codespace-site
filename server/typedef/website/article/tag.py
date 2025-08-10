from typing import TypedDict


class T_TagCount(TypedDict):
    """
    标签计数结构
    - text: 标签文本
    - size: 标签出现次数
    """
    text: str
    size: int
