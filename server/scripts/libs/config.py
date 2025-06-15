import os
import configparser
from dotenv import load_dotenv


class CaseSensitiveConfigParser(configparser.ConfigParser):
    '''
    严格区分大小写的configparser
    '''

    def optionxform(self, optionstr):
        return optionstr  # 保持原样，不转换为小写


class ProjectConfig:
    '''
    整个项目的配置文件
    '''
    # 当前文件相对于项目main.py的层级
    DIR_LOOP = 3

    # 项目用到的文件夹结构和实例对象的属性是一样的命名
    PROJECTNESSDIR = {'_articles_path', '_images_path',  '_cache_path', '_statics_path'}

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ProjectConfig, cls).__new__(
                cls, *args, **kwargs)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self) -> None:
        # 确保是单例
        if self.__initialized:
            return

        self.__initialized = False

        # 项目的一些路径信息
        self._images_path: str = 'images'                # 存储图像的文件夹路径
        self._articles_path: str = 'articles'            # 存储文章资源的文件夹路径
        self._cache_path: str = 'server/.cache'          # 缓存文件夹路径
        self._statics_path: str = 'server/statics'       # 静态资源相对项目的路径

        # 从外部依赖文件导入配置, 先加入用户的设置(这个优先级更高), 然后再加载模型的设置
        self.check_necessary_path()

        # 加载环境变量
        load_dotenv(self.get_abs_path('.env'))

        print(os.environ)

    def _abs_path(self):
        '''
        根据当前的脚本的位置, 获得项目的入口脚本文件夹的绝对路径
        '''
        project_root = os.path.abspath(os.path.dirname(__file__))
        for _ in range(ProjectConfig.DIR_LOOP):
            project_root = os.path.dirname(project_root)

        return project_root

    def get_abs_path(self, path: str = None, fileName: str = None) -> str:
        '''
        获取任何项目文件的绝对路径
        '''
        projectPath = self._abs_path()
        path = path if path is not None else ''
        fileName = fileName if fileName is not None else ''
        return os.path.normpath(os.path.join(projectPath, path, fileName))

    def check_necessary_path(self):
        '''
        判断项目必要的文件目录是不是存在
        '''
        for key in ProjectConfig.PROJECTNESSDIR:
            nessDirPath = self.get_abs_path(self.__dict__[key])
            if not os.path.exists(nessDirPath):
                os.mkdir(nessDirPath)

    def get_statics_path(self):
        '''
        获得静态资源的绝对路径
        '''
        return self.get_abs_path(self._statics_path)

    def get_cache_path(self):
        '''
        获得缓存的绝对路径
        '''
        return self.get_abs_path(self._cache_path)

    def get_images_path(self):
        '''
        获得静态资源的绝对路径
        '''
        return self.get_abs_path(self._images_path)
