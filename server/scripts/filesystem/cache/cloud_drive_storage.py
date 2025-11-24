import datetime
import os
import typing

from core import Logger, ProjectConfig


class CloudDriveStorage:
    """
    云盘文件存储助手，所有文件均存放于 data/cache 目录下。
    """

    ROOT = ProjectConfig.get_cache_path()
    SUBDIR = "cloud_drive"

    @classmethod
    def _ensure_root(cls) -> None:
        if not os.path.exists(cls.ROOT):
            Logger.info(f"缓存目录不存在, 创建目录: {cls.ROOT}")
            os.makedirs(cls.ROOT, exist_ok=True)

    @classmethod
    def _ensure_parent(cls, relative_path: str) -> str:
        abs_path = cls.resolve_path(relative_path)
        parent = os.path.dirname(abs_path)
        if not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)
        return abs_path

    @classmethod
    def sanitize_filename(cls, name: typing.Optional[str]) -> str:
        if not name:
            return "file.bin"
        name = os.path.basename(name)
        # 替换非法字符
        allowed = "-_.() "
        sanitized = "".join(
            ch if ch.isalnum() or ch in allowed else "_"
            for ch in name
        ).strip(" .")
        if not sanitized or sanitized in {".", ".."}:
            sanitized = "file.bin"
        if sanitized.startswith("."):
            sanitized = sanitized.lstrip(".")
        return sanitized or "file.bin"

    @classmethod
    def build_token_relative_path(cls, token: str, original_name: str) -> str:
        sanitized = cls.sanitize_filename(original_name)
        base, ext = os.path.splitext(sanitized)
        if not base:
            base = "file"
        directory = os.path.join(cls.SUBDIR, token.lower())
        candidate = os.path.join(directory, f"{base}{ext}")
        counter = 1
        while cls.file_exists(candidate):
            candidate = os.path.join(directory, f"{base}_{counter}{ext}")
            counter += 1
        return candidate

    @classmethod
    def resolve_path(cls, relative_path: str) -> str:
        cls._ensure_root()
        relative_path = (relative_path or "").lstrip("/\\")
        norm_relative = os.path.normpath(relative_path)
        abs_path = os.path.normpath(os.path.join(cls.ROOT, norm_relative))
        if not abs_path.startswith(cls.ROOT):
            raise ValueError("Invalid path outside cache directory.")
        return abs_path

    @classmethod
    def save_bytes(cls, relative_path: str, data: bytes) -> None:
        abs_path = cls._ensure_parent(relative_path)
        with open(abs_path, "wb") as handler:
            handler.write(data)
        Logger.info(f"成功保存云盘文件: {abs_path}")

    @classmethod
    def file_exists(cls, relative_path: str) -> bool:
        try:
            abs_path = cls.resolve_path(relative_path)
        except ValueError:
            return False
        return os.path.isfile(abs_path)

    @classmethod
    def file_info(cls, relative_path: str) -> typing.Optional[dict]:
        if not cls.file_exists(relative_path):
            return None
        abs_path = cls.resolve_path(relative_path)
        stat = os.stat(abs_path)
        return {
            "size": stat.st_size,
            "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

    @classmethod
    def absolute_path(cls, relative_path: str) -> str:
        abs_path = cls.resolve_path(relative_path)
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(abs_path)
        return abs_path
