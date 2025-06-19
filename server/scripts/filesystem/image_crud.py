import os
from pathlib import Path
from uuid import uuid4
from fastapi import HTTPException

from core import Logger, ProjectConfig


class ImageCrudHandler:
    @staticmethod
    def get_image_path(category: str, filename: str) -> str:
        """
        获取指定分类下的图片绝对路径
        :param category: 图片分类
        :param filename: 图片文件名
        """
        base_dir = ProjectConfig.get_images_path()
        full_path = os.path.join(base_dir, category, filename)
        abs_path = os.path.abspath(full_path)

        if not abs_path.startswith(os.path.abspath(base_dir) + os.sep):
            Logger.error(f"非法路径访问: {abs_path}")
            raise HTTPException(status_code=400, detail="非法的图片路径")
        if not os.path.isfile(abs_path):
            Logger.error(f"图片未找到: {abs_path}")
            raise HTTPException(status_code=404, detail="图片未找到")
        return abs_path

    @staticmethod
    def save_avatar(bytes_data: bytes, original_name: str, username: str) -> str:
        """
        保存用户头像到指定目录，并生成唯一文件名
        :param bytes_data: 头像的二进制数据
        :param original_name: 原始文件名
        :param username: 用户名，用于生成唯一文件名
        """
        suffix = Path(original_name).suffix or ""
        avatar_dir = Path(ProjectConfig.get_images_path()) / "avatar"
        avatar_dir.mkdir(parents=True, exist_ok=True)

        safe_stem = username.strip().replace(".", "_")
        unique_name = f"{safe_stem}_{uuid4().hex[:8]}{suffix}"
        target = avatar_dir / unique_name

        try:
            target.write_bytes(bytes_data)
        except Exception as e:
            Logger.error(f"保存 avatar 失败: {e}")
            # 给出错误信息
            raise HTTPException(status_code=500, detail=f"保存头像失败: {e}")
        return unique_name

    @staticmethod
    def save_article_image(bytes_data: bytes, category: str, name: str, original_name: str) -> str:
        """
        保存文章图片到指定分类目录，并生成唯一文件名
        :param bytes_data: 图片的二进制数据
        :param category: 图片分类
        :param name: 文件名（不含扩展名）
        :param original_name: 原始文件名
        """
        suffix = Path(original_name).suffix or ""
        category_dir = Path(ProjectConfig.get_images_path()) / category
        category_dir.mkdir(parents=True, exist_ok=True)

        target_name = f"{name}{suffix}"
        target = category_dir / target_name
        try:
            target.write_bytes(bytes_data)
        except Exception as e:
            Logger.error(f"保存文章图片失败: {e}")
            raise HTTPException(status_code=500, detail=f"保存文章图片失败: {e}")
        return target_name

    @staticmethod
    def check_exists(category: str, stem: str) -> bool:
        """
        检查指定分类下是否已存在同名图片
        :param category: 图片分类
        :param stem: 图片文件名（不含扩展名）
        """
        category_dir = Path(ProjectConfig.get_images_path()) / category
        category_dir.mkdir(parents=True, exist_ok=True)
        existing = {p.stem for p in category_dir.iterdir() if p.is_file()}
        return stem in existing
