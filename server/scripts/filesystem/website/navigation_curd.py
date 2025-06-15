import json
import typing
from core import Logger, ProjectConfig


class NavItem(typing.TypedDict):
    """
    Web header 的 Navigation 的单个配置项
    title: 标题
    url: 链接
    new: 是不是显示new的标志
    """
    title: str
    url: str
    new: bool


class NavInfoHandler:
    """
    加载 Navigation 配置
    """

    def __init__(self) -> None:
        config_file = ProjectConfig.get_navigation_path()
        # 读取这个路径的json文件
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                self.codespace_config = json.load(file)
        except FileNotFoundError:
            Logger.error(f"Navigation 配置文件未找到: {config_file}")
            self.codespace_config = {}
        except json.JSONDecodeError:
            Logger.error(f"Navigation 配置文件格式错误: {config_file}")
            self.codespace_config = {}
        except Exception as e:
            Logger.error(f"加载 Navigation 配置时发生错误: {e}")
            self.codespace_config = {}

    def get_navigation_items(self) -> typing.List[NavItem]:
        """
        获取 Navigation 配置中的所有项目
        """
        items = []
        for item in self.codespace_config.get('data', []):
            try:
                items.append(NavItem(
                    title=item['title'],
                    url=item['url'],
                    new=item['new'],
                ))
            except KeyError as e:
                Logger.error(f"Navigation 配置项缺少必要字段: {e}")
                continue
        return items
