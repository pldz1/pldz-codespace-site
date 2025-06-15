import json
import typing
from core import Logger, ProjectConfig


class AdBannerItem(typing.TypedDict):
    """
    Web site的 adbanner 的单个配置项
    title: 标题
    folder: 文件夹名称
    url: 访问链接
    thumbnail: 缩略图链接
    previewgif: 预览GIF链接
    sourcelink: 源代码链接
    date: 发布日期
    description: 描述信息
    """
    title: str
    folder: str
    url: str
    thumbnail: str
    previewgif: str
    sourcelink: str
    date: str
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
                    folder=item['folder'],
                    url=item['url'],
                    thumbnail=item['thumbnail'],
                    previewgif=item['previewgif'],
                    sourcelink=item['sourcelink'],
                    date=item['date'],
                    description=item.get('description', '')
                ))
            except KeyError as e:
                Logger.error(f"adbanner.json 配置项缺少必要字段: {e}")
        return items
