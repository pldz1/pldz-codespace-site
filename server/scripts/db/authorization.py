import os
import uuid
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from passlib.context import CryptContext
from typing import TypedDict

from core import Logger
from scripts.db.connection import _lock, _read_json, _write_json, get_users_db_path


ALGORITHM = "HS256"

SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin@pldz1.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "123")

ACCESS_EXPIRE = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
REFRESH_EXPIRE = timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserItem(TypedDict):
    username: str
    password: str
    raw_password: str
    nickname: str
    avatar: str
    isadmin: bool
    role: str
    token: str
    blacklisted: bool


class AuthorizedHandler:

    def __init__(self) -> None:
        pass

    @classmethod
    def init_admin(cls):
        cls.add_user(ADMIN_USERNAME, ADMIN_PASSWORD, "爬楼的猪", "/api/v1/website/image/avatar/admin@pldz1_com_00000001.jpg")
        Logger.info(f"✔ 初始化管理员账号: {ADMIN_USERNAME}")

    @classmethod
    def create_token(cls, username: str, expires: timedelta, token_type: str):
        payload = {"sub": username, "type": token_type, "exp": datetime.now() + expires}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return pwd_context.hash(password)

    @classmethod
    def verify_password(cls, password: str, hashed: str) -> bool:
        return pwd_context.verify(password, hashed)

    @classmethod
    def get_current_user(cls, request: Request):
        token = request.cookies.get('access_token')
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if data.get('type') != 'access':
                raise HTTPException(status_code=401, detail="Invalid token type")
            username = data.get('sub')
            user = cls.get_user_by_username(username)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except PyJWTError as e:
            Logger.error(f"✖ JWT 错误: {e}")
            raise HTTPException(status_code=401, detail="Invalid or expired token")

    @classmethod
    def check_admin(cls, username: str):
        return username == ADMIN_USERNAME

    @classmethod
    def create_access_token(cls, user):
        return cls.create_token(user, ACCESS_EXPIRE, 'access')

    @classmethod
    def create_refresh_token(cls, user):
        tok = cls.create_token(user, REFRESH_EXPIRE, 'refresh')
        cls.update_user_token(user, tok)
        return tok

    @classmethod
    def blacklist_token(cls, token: str) -> bool:
        db = get_users_db_path()
        with _lock:
            data = _read_json(db)
            for user in data.values():
                if user.get('token') == token:
                    user['blacklisted'] = True
                    _write_json(db, data)
                    return True
        return False

    @classmethod
    def is_token_blacklisted(cls, token: str) -> bool:
        with _lock:
            data = _read_json(get_users_db_path())
        for user in data.values():
            if user.get('token') == token and user.get('blacklisted'):
                return True
        return False

    @classmethod
    def add_user(cls, username: str, password: str, nickname: str, avatar: str = "/api/v1/website/image/avatar/default.jpg") -> bool:
        db = get_users_db_path()
        isadmin = cls.check_admin(username)
        hash_password = cls.hash_password(ADMIN_PASSWORD)
        with _lock:
            data = _read_json(db)
            if username in data:
                data[username].update({
                    'password': hash_password,
                    'raw_password': password,
                    'nickname': nickname,
                    'avatar': avatar,
                    'isadmin': isadmin,
                    'blacklisted': False,
                })
            else:
                data[username] = {
                    'id': str(uuid.uuid4()),
                    'username': username,
                    'password': hash_password,
                    'raw_password': password,
                    'nickname': nickname,
                    'avatar': avatar,
                    'isadmin': isadmin,
                    'blacklisted': False,
                    'token': '',
                }
            _write_json(db, data)
        return True

    @classmethod
    def verify_password_by_username(cls, username: str, password: str) -> bool:
        with _lock:
            data = _read_json(get_users_db_path())
        user = data.get(username)
        if not user:
            return False
        return cls.verify_password(password, user['password'])

    @classmethod
    def update_user_token(cls, username: str, token: str) -> bool:
        db = get_users_db_path()
        with _lock:
            data = _read_json(db)
            if username not in data:
                return False
            data[username]['token'] = token
            data[username]['blacklisted'] = False
            _write_json(db, data)
        return True

    @classmethod
    def get_user_by_username(cls, username: str) -> dict:
        with _lock:
            data = _read_json(get_users_db_path())
        user = data.get(username)
        if not user:
            return None
        result = dict(user)
        result.pop('password', None)
        result.pop('token', None)
        result.pop('blacklisted', None)
        return result

    @classmethod
    def get_user_password(cls, username: str) -> str:
        with _lock:
            data = _read_json(get_users_db_path())
        user = data.get(username)
        if not user:
            return None
        return user.get('password', None)

    @classmethod
    def update_user_avatar(cls, username: str, avatar: str) -> bool:
        db = get_users_db_path()
        with _lock:
            data = _read_json(db)
            if username not in data:
                return False
            data[username]['avatar'] = avatar
            _write_json(db, data)
        return True

    @classmethod
    def get_all_users(cls) -> list:
        with _lock:
            data = _read_json(get_users_db_path())
        result = []
        for user in data.values():
            u = dict(user)
            u.pop('password', None)
            u.pop('token', None)
            u.pop('blacklisted', None)
            result.append(u)
        return result

    @classmethod
    def delete_user(cls, username: str) -> bool:
        db = get_users_db_path()
        with _lock:
            data = _read_json(db)
            if username not in data:
                return False
            del data[username]
            _write_json(db, data)
        return True
