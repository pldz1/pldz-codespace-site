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
        dotenv.load_dotenv(env_file_path)

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
    def get_images_path(self) -> str:
        '''
        获得存储图像的绝对路径
        '''
        IMAGE_PATH = os.environ.get('IMAGES_PATH', "images")
        return self.get_abs_path(IMAGE_PATH)

    @classmethod
    def get_articles_path(self) -> str:
        '''
        获得存储文章的绝对路径
        '''
        ARTICLES_PATH = os.environ.get('ARTICLES_PATH', "articles")
        return self.get_abs_path(ARTICLES_PATH)
