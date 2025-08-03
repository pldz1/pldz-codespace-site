import os
import uuid
import jwt
from jwt import PyJWTError
from pymongo.errors import PyMongoError
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from passlib.context import CryptContext
from typing import TypedDict

from core import Logger
from scripts.mongodb import get_user_mongo_collection


ALGORITHM = "HS256"

SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin@pldz1.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "123")

ACCESS_EXPIRE = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
REFRESH_EXPIRE = timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)))

# 密码
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserItem(TypedDict):
    """
    用户信息的字典类型
    username: 用户名
    password: 哈希后的密码
    raw_password: 明文密码
    nickname: 昵称
    avatar: 头像URL
    role: 角色
    isadmin: 是否为管理员
    token: JWT令牌
    blacklisted: 是否在黑名单中
    """
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
        """ 
        初始化管理员账号
        """
        cls.add_user(ADMIN_USERNAME, ADMIN_PASSWORD, "爬楼的猪", "/api/v1/website/image/avatar/admin@pldz1_com_00000001.jpg")
        Logger.info(f"✔ 初始化管理员账号: {ADMIN_USERNAME}")

    @classmethod
    def create_token(cls, username: str, expires: timedelta, token_type: str):
        """
        创建JWT令牌
        :param username: 用户名
        :param expires: 过期时间
        :param token_type: 令牌类型(access或refresh)
        :return: JWT令牌字符串
        """
        payload = {"sub": username, "type": token_type, "exp": datetime.now() + expires}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        哈希密码
        :param password: 明文密码
        :return: 哈希后的密码
        """
        return pwd_context.hash(password)

    @classmethod
    def verify_password(cls, password: str, hashed: str) -> bool:
        """
        验证密码是否正确
        :param password: 明文密码
        :param hashed: 哈希后的密码
        :return: 验证结果
        """
        return pwd_context.verify(password, hashed)

    @classmethod
    def get_current_user(cls, request: Request):
        """
        获取当前用户
        :param request: FastAPI Request 对象
        :return: 当前用户的用户名
        """
        token = request.cookies.get('access_token')
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if data.get('type') != 'access':
                raise HTTPException(
                    status_code=401, detail="Invalid token type")
            username = data.get('sub')
            user = cls.get_user_by_username(username)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except PyJWTError as e:
            Logger.error(f"✖ JWT 错误: {e}")
            raise HTTPException(
                status_code=401, detail="Invalid or expired token")

    @classmethod
    def check_admin(cls, username: str):
        """
        检查当前用户是否为管理员
        :param username: 用户名
        :return: 如果是管理员返回 True, 否则返回 False
        """
        return username == ADMIN_USERNAME

    @classmethod
    def create_access_token(cls, user):
        """
        创建访问令牌
        :param user: 用户名
        :return: JWT访问令牌字符串
        """
        return cls.create_token(user, ACCESS_EXPIRE, 'access')

    @classmethod
    def create_refresh_token(cls, user):
        """
        创建刷新令牌
        :param user: 用户名
        :return: JWT刷新令牌字符串
        """
        tok = cls.create_token(user, REFRESH_EXPIRE, 'refresh')
        cls.update_user_token(user, tok)
        return tok

    @classmethod
    def blacklist_token(cls, token: str) -> bool:
        """
        将令牌加入黑名单
        Args:
            token (str): 要加入黑名单的令牌
        Returns:
            bool: 黑名单操作成功返回 True, 失败返回 False
        """
        coll = get_user_mongo_collection()
        try:
            result = coll.update_one(
                {'token': token},
                {'$set': {'blacklisted': True}},
                upsert=True
            )
            return result.modified_count > 0 or result.upserted_id is not None
        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return False

    @classmethod
    def is_token_blacklisted(cls, token: str) -> bool:
        """
        检查令牌是否在黑名单中
        Args:
            token (str): 要检查的令牌
        Returns:
            bool: 如果令牌在黑名单中返回 True, 否则返回 False
        """
        coll = get_user_mongo_collection()
        user = coll.find_one({'token': token, 'blacklisted': True})
        return user is not None

    @classmethod
    def add_user(cls, username: str, password: str, nickname: str, avatar: str = "/api/v1/website/image/avatar/default.jpg") -> bool:
        """
        添加新用户到数据库, 如果存在就更新, 如果不存在就创建
        Args:
            username (str): 用户名
            password (str): 密码
            nickname (str): 昵称
            avatar (str): 头像URL
        Returns:
            bool: 添加成功返回 True, 失败返回 False
        """
        coll = get_user_mongo_collection()
        isadmin = cls.check_admin(username)
        try:
            # 使用 upsert 更新或插入用户
            hash_password = cls.hash_password(ADMIN_PASSWORD)
            result = coll.update_one({'username': username},
                                     {'$set': {'password': hash_password,
                                               'raw_password': password,
                                               'nickname': nickname,
                                               'avatar': avatar,
                                               'isadmin': isadmin,
                                               'blacklisted': False
                                               },
                                      '$setOnInsert': {'id': str(uuid.uuid4())}
                                      }, upsert=True)
            return result.upserted_id is not None or result.modified_count > 0
        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return False

    @classmethod
    def verify_password_by_username(cls, username: str, password: str) -> bool:
        """
        验证用户密码
        Args:
            username (str): 用户名
            password (str): 密码
        Returns:
            bool: 验证成功返回 True, 失败返回 False
        """
        coll = get_user_mongo_collection()
        user = coll.find_one({'username': username})
        if not user:
            return False
        return cls.verify_password(password, user['password'])

    @classmethod
    def update_user_token(cls, username: str, token: str) -> bool:
        """
        更新用户的令牌
        Args:
            username (str): 用户名
            token (str): 新的令牌
        Returns:
            bool: 更新成功返回 True, 失败返回 False
        """
        coll = get_user_mongo_collection()
        try:
            result = coll.update_one(
                {'username': username},
                {'$set': {'token': token, 'blacklisted': False}}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return False

    @classmethod
    def get_user_by_username(cls, username: str) -> dict:
        """
        根据用户名获取用户信息
        Args:
            username (str): 用户名
        Returns:
            dict: 用户信息字典，如果用户不存在则返回 None
        """
        coll = get_user_mongo_collection()
        user = coll.find_one({'username': username})
        if not user:
            return None
        # 去掉_id 字段和其他隐私数据
        user.pop('_id', None)
        user.pop('password', None)
        user.pop('token', None)
        user.pop('blacklisted', None)
        return user

    @classmethod
    def get_user_password(cls, username: str) -> str:
        """
        获取用户密码
        Args:
            username (str): 用户名
        Returns:
            str: 用户密码哈希，如果用户不存在则返回 None
        """
        coll = get_user_mongo_collection()
        user = coll.find_one({'username': username})
        if not user:
            return None
        return user.get('password', None)

    @classmethod
    def update_user_avatar(cls, username: str, avatar: str) -> bool:
        """
        更新用户头像
        Args:
            username (str): 用户名
            avatar (str): 新的头像URL
        Returns:
            bool: 更新成功返回 True, 失败返回 False
        """
        coll = get_user_mongo_collection()
        try:
            result = coll.update_one(
                {'username': username},
                {'$set': {'avatar': avatar}}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return False

    @classmethod
    def get_all_users(cls) -> list:
        """
        获取所有用户信息
        Returns:
            list: 用户信息列表
        """
        coll = get_user_mongo_collection()
        users = coll.find({})
        user_list = []
        for user in users:
            user.pop('_id', None)
            user.pop('password', None)
            user.pop('token', None)
            user.pop('blacklisted', None)
            user_list.append(user)
        return user_list

    @classmethod
    def delete_user(cls, username: str) -> bool:
        """
        删除用户
        Args:
            username (str): 用户名
        Returns:
            bool: 删除成功返回 True, 失败返回 False
        """
        coll = get_user_mongo_collection()
        try:
            result = coll.delete_one({'username': username})
            return result.deleted_count > 0
        except PyMongoError as e:
            Logger.error(f"✖ MongoDB 错误: {e}")
            return False
