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
        finally:
            if not isinstance(self.codespace_config, dict):
                Logger.warning("Navigation 配置文件根节点格式错误，已初始化为空对象")
                self.codespace_config = {}
            data = self.codespace_config.get('data', [])
            if not isinstance(data, list):
                Logger.warning("Navigation 配置 data 字段格式错误，已重置为空列表")
                self.codespace_config['data'] = []
            else:
                self.codespace_config.setdefault('data', [])

    def get_navigation_items(self) -> typing.List[NavItem]:
        """
        获取 Navigation 配置中的所有项目
        """
        items = []
        data = self.codespace_config.get('data', [])
        if not isinstance(data, list):
            Logger.warning("Navigation 配置 data 字段不是列表，无法解析导航项")
            return items

        for index, item in enumerate(data):
            if not isinstance(item, dict):
                Logger.warning(f"Navigation 配置项类型错误，索引 {index} 已跳过")
                continue

            title = item.get('title')
            url = item.get('url')
            if not title:
                Logger.warning(f"Navigation 配置项缺少必要字段 title，索引 {index} 已跳过")
                continue
            if not url:
                Logger.warning(f"Navigation 配置项缺少必要字段 url，索引 {index} 已跳过")
                continue

            nav_item: NavItem = {
                'title': str(title),
                'url': str(url),
                'new': bool(item.get('new', False)),
            }
            items.append(nav_item)
        return items

    def set_navigation_items(self, items: typing.List[NavItem]) -> None:
        """
        设置 Navigation 配置中的所有项目
        :param items: 导航项列表
        """
        self.codespace_config['data'] = items
        config_file = ProjectConfig.get_navigation_path()
        try:
            with open(config_file, 'w', encoding='utf-8') as file:
                json.dump(self.codespace_config, file, ensure_ascii=False, indent=4)
            Logger.info(f"Navigation 配置已更新: {config_file}")
            return True
        except Exception as e:
            Logger.error(f"保存 Navigation 配置时发生错误: {e}")
            return False
