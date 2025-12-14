import datetime
import secrets
import string
import typing


TOKEN_VALID_DAYS = 7


class CloudDriveToken(typing.TypedDict, total=False):
    """
    云盘令牌结构
    created: 创建时间 (ISO)
    expires_at: 过期时间 (ISO)
    token: 令牌字符串
    allow_upload: 是否允许上传
    allow_download: 是否允许下载
    filename: 存储在服务器上的文件名
    original_filename: 用户看到的原始文件名
    description: 令牌备注
    size: 文件大小
    last_updated: 最后更新时间 (ISO)
    """

    created: str
    expires_at: str
    token: str
    allow_upload: bool
    allow_download: bool
    filename: typing.Optional[str]
    original_filename: typing.Optional[str]
    description: typing.Optional[str]
    size: int
    last_updated: str


class CloudDriveTokenHandler:
    _tokens: typing.List[CloudDriveToken] = []

    @classmethod
    def _now(cls) -> datetime.datetime:
        return datetime.datetime.now()

    @classmethod
    def _expiry(cls) -> datetime.datetime:
        return cls._now() + datetime.timedelta(days=TOKEN_VALID_DAYS)

    @classmethod
    def _prune_expired(cls) -> None:
        current = cls._now()
        cls._tokens = [
            item for item in cls._tokens
            if datetime.datetime.fromisoformat(item["expires_at"]) > current
        ]

    @classmethod
    def _generate_token(cls) -> str:
        alphabet = string.ascii_uppercase + string.digits
        while True:
            candidate = "".join(secrets.choice(alphabet) for _ in range(4))
            if all(item["token"] != candidate for item in cls._tokens):
                return candidate

    @classmethod
    def _clone(cls, item: CloudDriveToken) -> CloudDriveToken:
        return typing.cast(CloudDriveToken, {**item})

    @classmethod
    def generate_token(
        cls,
        *,
        allow_upload: bool,
        allow_download: bool,
        filename: typing.Optional[str] = None,
        original_filename: typing.Optional[str] = None,
        description: typing.Optional[str] = None,
        size: int = 0,
    ) -> CloudDriveToken:
        cls._prune_expired()

        if not allow_upload and not allow_download:
            raise ValueError("Token must allow upload or download.")

        now = cls._now()
        token_entry: CloudDriveToken = {
            "token": cls._generate_token(),
            "allow_upload": bool(allow_upload),
            "allow_download": bool(allow_download),
            "created": now.isoformat(),
            "expires_at": cls._expiry().isoformat(),
            "filename": filename or None,
            "original_filename": original_filename or filename or None,
            "description": description or None,
            "size": int(size) if size else 0,
            "last_updated": now.isoformat(),
        }
        cls._tokens.append(token_entry)
        return cls._clone(token_entry)

    @classmethod
    def get_token(cls, token: str) -> typing.Optional[CloudDriveToken]:
        cls._prune_expired()
        for item in cls._tokens:
            if item["token"] == token:
                return cls._clone(item)
        return None

    @classmethod
    def list_tokens(cls) -> typing.List[CloudDriveToken]:
        cls._prune_expired()
        return [
            cls._clone(item)
            for item in sorted(cls._tokens, key=lambda x: x.get("created", ""), reverse=True)
        ]

    @classmethod
    def delete_token(cls, token: str) -> bool:
        cls._prune_expired()
        original_len = len(cls._tokens)
        cls._tokens = [item for item in cls._tokens if item["token"] != token]
        return len(cls._tokens) < original_len

    @classmethod
    def update_file_info(
        cls,
        token: str,
        *,
        filename: str,
        original_filename: typing.Optional[str],
        size: int,
    ) -> typing.Optional[CloudDriveToken]:
        cls._prune_expired()
        for item in cls._tokens:
            if item["token"] != token:
                continue
            item["filename"] = filename
            item["original_filename"] = original_filename or filename
            item["size"] = int(size)
            item["last_updated"] = cls._now().isoformat()
            return cls._clone(item)
        return None

    @classmethod
    def touch(cls, token: str) -> typing.Optional[CloudDriveToken]:
        """
        更新令牌的 last_updated 时间，但不修改其他字段。
        """
        cls._prune_expired()
        for item in cls._tokens:
            if item["token"] == token:
                item["last_updated"] = cls._now().isoformat()
                return cls._clone(item)
        return None
