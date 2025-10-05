import json
import typing
from core import Logger, ProjectConfig


class CodeSpaceItem(typing.TypedDict):
    """
    Web site的 codespace 的单个配置项
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


class CodeSpaceHandler:
    """
    加载CodeSpace配置
    """

    def __init__(self) -> None:
        config_file = ProjectConfig.get_codespace_config_path()
        # 读取这个路径的json文件
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                self.codespace_config = json.load(file)
        except FileNotFoundError:
            Logger.error(f"CodeSpace配置文件未找到: {config_file}")
            self.codespace_config = {}
        except json.JSONDecodeError:
            Logger.error(f"CodeSpace配置文件格式错误: {config_file}")
            self.codespace_config = {}
        except Exception as e:
            Logger.error(f"加载CodeSpace配置时发生错误: {e}")
            self.codespace_config = {}

    def get_codespace_items(self) -> typing.List[CodeSpaceItem]:
        """
        获取CodeSpace配置中的所有项目
        """
        items = []
        for item in self.codespace_config.get('data', []):
            try:
                items.append(CodeSpaceItem(
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
                Logger.error(f"codespace.json 配置项缺少必要字段: {e}")
        return items

    def set_codespace_items(self, items: typing.List[CodeSpaceItem]) -> None:
        """
        设置CodeSpace配置中的所有项目
        """
        self.codespace_config['data'] = items
        config_file = ProjectConfig.get_codespace_config_path()
        try:
            with open(config_file, 'w', encoding='utf-8') as file:
                json.dump(self.codespace_config, file, ensure_ascii=False, indent=4)
            Logger.info(f"CodeSpace配置已更新: {config_file}")
            self.get_codespace_items()
            return True
        except Exception as e:
            Logger.error(f"保存CodeSpace配置时发生错误: {e}")
            return False
