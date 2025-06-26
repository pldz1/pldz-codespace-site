import os
from core import Logger, ProjectConfig


CACHE_PATH = ProjectConfig.get_cache_path()


class CacheCurdHandle:
    """
    缓存文件的增删改查处理类"""

    @classmethod
    def get_all_cache_files(cls) -> list:
        """
        获取所有缓存文件的列表
        """
        try:
            files = os.listdir(CACHE_PATH)
            # 只返回文件名和后缀名
            return [f for f in files if os.path.isfile(os.path.join(CACHE_PATH, f))]
        except Exception as e:
            Logger.error(f"获取缓存文件列表失败: {e}")
            return []

    @classmethod
    def get_cache_file(cls, filename: str) -> str:
        """
        获取指定缓存文件的绝对路径
        """
        file_path = os.path.join(CACHE_PATH, filename)
        if os.path.isfile(file_path):
            return file_path
        else:
            Logger.error(f"缓存文件 {filename} 不存在")
            return ""

    @classmethod
    def delete_cache_file(cls, filename: str) -> bool:
        """
        删除指定的缓存文件
        """
        file_path = os.path.join(CACHE_PATH, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                Logger.info(f"成功删除缓存文件: {filename}")
                return True
            except Exception as e:
                Logger.error(f"删除缓存文件失败: {e}")
                return False
        else:
            Logger.error(f"缓存文件 {filename} 不存在")
            return False

    @classmethod
    def save_cache_file(cls, filename: str, data: bytes) -> bool:
        """
        保存缓存文件
        :param filename: 文件名
        :param data: 文件内容
        :return: 是否保存成功
        """
        file_path = os.path.join(CACHE_PATH, filename)
        try:
            with open(file_path, 'wb') as f:
                f.write(data)
            Logger.info(f"成功保存缓存文件: {filename}")
            return True
        except Exception as e:
            Logger.error(f"保存缓存文件失败: {e}")
            return False
