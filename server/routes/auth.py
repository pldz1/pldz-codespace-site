import os
import jwt
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time
import random

from scripts.mongodb import AuthorizedHandler, SECRET_KEY, ALGORITHM

AUTH_ROUTER = APIRouter()


@AUTH_ROUTER.get("/api/v1/auth/privacy")
async def api_privacy_get():
    """
    处理隐私政策的请求
    """
    icp = os.environ.get('APP_ICP', 'ICP信息未设置')
    copyright = os.environ.get('APP_COPYRIGHT', 'Copyright信息未设置')
    ps = os.environ.get('APP_PS', 'PS信息未设置')

    return {'data': {'icp': icp, 'copyright': copyright, 'ps': ps}}


class LoginData(BaseModel):
    username: str
    password: str


@AUTH_ROUTER.post('/api/v1/auth/login')
async def login(data: LoginData):
    """
    处理登录请求
    :param username: 用户名
    :param password: 密码
    """
    user = AuthorizedHandler.get_user_by_username(data.username)
    if not user or not AuthorizedHandler.verify_password(data.password, user['password']):
        return {'data': {"flag": False, 'log': '用户名或密码错误'}}

    # 生成访问令牌和刷新令牌
    access = AuthorizedHandler.create_access_token(data.username)
    refresh = AuthorizedHandler.create_refresh_token(data.username)

    # 设置响应头和Cookie
    is_admin = AuthorizedHandler.check_admin(data.username)
    resp = JSONResponse(
        {'data': {"flag": True, "isAdmin": is_admin, 'log': '登录成功'}})
    # 设置Cookie，httponly和samesite属性
    resp.set_cookie('access_token', access, httponly=True, samesite='lax')
    resp.set_cookie('refresh_token', refresh, httponly=True, samesite='lax')
    return resp


@AUTH_ROUTER.post('/api/v1/auth/register')
async def register(data: LoginData):
    """
    处理注册请求
    :param username: 用户名
    :param password: 密码
    """
    if AuthorizedHandler.get_user_by_username(data.username):
        time.sleep(random.uniform(0.1, 0.3))
        return {'data': {'flag': False, 'log': '用户名已存在'}}
    # 存储新用户
    AuthorizedHandler.add_user(
        data.username, AuthorizedHandler.hash_password(data.password))
    access = AuthorizedHandler.create_access_token(data.username)
    refresh = AuthorizedHandler.create_refresh_token(data.username)
    resp = JSONResponse({'data': {'flag': True, 'log': '注册成功'}})
    # 设置Cookie，httponly和samesite属性
    resp.set_cookie('access_token', access, httponly=True, samesite='lax')
    resp.set_cookie('refresh_token', refresh, httponly=True, samesite='lax')
    time.sleep(random.uniform(0.1, 0.3))
    return resp


@AUTH_ROUTER.get('/api/v1/auth/logout')
async def logout(request: Request):
    """ 
    处理登出请求
    :param request: FastAPI Request 对象
    """
    token = request.cookies.get('refresh_token')
    if token:
        # 将刷新令牌加入黑名单
        AuthorizedHandler.blacklist_token(token)
    resp = JSONResponse({'data': True})
    resp.delete_cookie('access_token')
    resp.delete_cookie('refresh_token')
    return resp


@AUTH_ROUTER.post('/api/v1/auth/refresh')
async def refresh(request: Request):
    """
    刷新访问令牌
    :param request: FastAPI Request 对象
    """
    token = request.cookies.get('refresh_token')
    if not token or AuthorizedHandler.is_token_blacklisted(token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('type') != 'refresh' or not payload.get('sub'):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    new_access = AuthorizedHandler.create_access_token(payload['sub'])
    username = AuthorizedHandler.get_current_user(request)
    is_admin = AuthorizedHandler.check_admin(username)
    resp = JSONResponse(
        {'data': {'flag': True, 'username': username, 'isAdmin': is_admin, 'log': '刷新成功'}})
    resp.set_cookie('access_token', new_access, httponly=True, samesite='lax')
    return resp
