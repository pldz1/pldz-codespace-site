import os
import sys
import dotenv


class ProjectConfig:
    '''
    整个项目的配置文件
    '''
    # 当前文件相对于项目main.py的层级
    DIR_LOOP = 2

    PROJECT_ROOT = ''

    @classmethod
    def load_env(cls) -> None:
        """
        加载环境变量文件 .env
        """

        # 确定项目根目录
        cls.PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
        for _ in range(ProjectConfig.DIR_LOOP):
            cls.PROJECT_ROOT = os.path.dirname(cls.PROJECT_ROOT)

        # 判断环境文件是否存在
        env_file_path = cls.get_abs_path('', '.env')
        if not os.path.exists(env_file_path):
            print(f"环境变量文件 .env 未找到: {env_file_path}")
            sys.exit(1)

        # 加载环境变量
        dotenv.load_dotenv(env_file_path, override=False)

    @classmethod
    def get_abs_path(cls, folder: str = None, fileName: str = None) -> str:
        '''
        获取任何项目文件的绝对路径
        '''
        folder = folder if folder is not None else ''
        fileName = fileName if fileName is not None else ''
        path = os.path.normpath(os.path.join(cls.PROJECT_ROOT, folder, fileName))
        return path

    @classmethod
    def get_statics_path(cls) -> str:
        '''
        获得静态资源的绝对路径
        '''
        return cls.get_abs_path('server/statics')

    @classmethod
    def get_resource_path(cls) -> str:
        '''
        获得资源文件的绝对路径
        '''
        RESOURCES_PATH = os.environ.get('RESOURCES_PATH', "data/resources")
        return cls.get_abs_path(RESOURCES_PATH)

    @classmethod
    def get_images_path(cls) -> str:
        '''
        获得存储图像的绝对路径
        '''
        IMAGE_PATH = os.environ.get('IMAGES_PATH', "data/images")
        return cls.get_abs_path(IMAGE_PATH)

    @classmethod
    def get_articles_path(cls) -> str:
        '''
        获得存储文章的绝对路径
        '''
        ARTICLES_PATH = os.environ.get('ARTICLES_PATH', "data/articles")
        return cls.get_abs_path(ARTICLES_PATH)

    @classmethod
    def get_adbanner_config_path(cls) -> dict:
        """
        获取AdBanner配置的json文件
        """
        resource_path = cls.get_resource_path()
        return os.path.join(resource_path, 'website/adbanner.json')

    @classmethod
    def get_navigation_path(cls) -> str:
        """
        获取导航配置的json文件
        """
        resource_path = cls.get_resource_path()
        return os.path.join(resource_path, 'website/navigation.json')

    @classmethod
    def get_git_repo_path(cls) -> str:
        """
        获取Git仓库的路径
        """
        git_repo_path = os.environ.get('GIT_REPO_PATH', './git-repo')
        return cls.get_abs_path(git_repo_path)

    @classmethod
    def get_cache_path(cls) -> str:
        """
        获取缓存目录的路径
        """
        cache_path = os.environ.get('CACHE_PATH', 'data/cache')
        return cls.get_abs_path(cache_path)

    @classmethod
    def get_templates_path(cls) -> str:
        '''
        获得模板文件的绝对路径
        '''
        TEMPLATES_PATH = os.environ.get('TEMPLATES_PATH', "data/templates")
        return cls.get_abs_path(TEMPLATES_PATH)

    @classmethod
    def get_codespace_config_path(cls) -> str:
        """
        获取CodeSpace配置的json文件
        """
        resource_path = cls.get_resource_path()
        return os.path.join(resource_path, 'website/codespace.json')
