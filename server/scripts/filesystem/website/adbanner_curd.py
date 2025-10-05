import json
import typing
from core import Logger, ProjectConfig


class AdBannerItem(typing.TypedDict):
    """
    Web site的 adbanner 的单个配置项
    title: 标题
    url: 访问链接
    description: 描述信息
    """
    title: str
    url: str
    description: str


class AdBannerHandler:
    """
    加载AdBanner配置
    """

    def __init__(self) -> None:
        config_file = ProjectConfig.get_adbanner_config_path()
        # 读取这个路径的json文件
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                self.adbanner_config = json.load(file)
        except FileNotFoundError:
            Logger.error(f"AdBanner配置文件未找到: {config_file}")
            self.adbanner_config = {}
        except json.JSONDecodeError:
            Logger.error(f"AdBanner配置文件格式错误: {config_file}")
            self.adbanner_config = {}
        except Exception as e:
            Logger.error(f"加载AdBanner配置时发生错误: {e}")
            self.adbanner_config = {}

    def get_adbanner_items(self) -> typing.List[AdBannerItem]:
        """
        获取AdBanner配置中的所有项目
        """
        items = []
        for item in self.adbanner_config.get('data', []):
            try:
                items.append(AdBannerItem(
                    title=item['title'],
                    url=item['url'],
                    description=item.get('description', '')
                ))
            except KeyError as e:
                Logger.error(f"adbanner.json 配置项缺少必要字段: {e}")
        return items

    def set_adbanner_items(self, items: typing.List[AdBannerItem]) -> None:
        """
        设置AdBanner配置中的所有项目
        """
        self.adbanner_config['data'] = items
        config_file = ProjectConfig.get_adbanner_config_path()
        try:
            with open(config_file, 'w', encoding='utf-8') as file:
                json.dump(self.adbanner_config, file, ensure_ascii=False, indent=4)
            Logger.info(f"AdBanner配置已更新: {config_file}")
            self.get_adbanner_items()
            return True
        except Exception as e:
            Logger.error(f"保存AdBanner配置时发生错误: {e}")
            return False
