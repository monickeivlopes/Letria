import binascii
import os
from datetime import datetime

import jwt
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .iResponse import Error, HTTPStatus
from .globals import g
from .toolfuns import path_to_key
from ..api.RoureManager import RouteManager

SECRET_KEY = "4105177d86fa16a2747212a7101dafda5c4027a4e4f64054"  # 密钥
ALGORITHM = "HS256"  # 算法


class JWTBearer(HTTPBearer):
    def __init__(self, rules=None, auto_error: bool = False):
        self.rules = rules
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.roure_manager = RouteManager()

    @staticmethod
    def token(data: dict, expires_time=None):
        if expires_time is None:
            expires_time = g.config.ACCESS_TOKEN_EXPIRES
            if expires_time is None:
                raise Error(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, message="未设置ACCESS_TOKEN_EXPIRES")
        exp = datetime.utcnow() + expires_time  # expire 令牌到期时间
        data.update({"exp": exp})
        __token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        return __token

    async def __call__(self, request: Request):
        if not self.roure_manager.path_need_token(path_to_key(request.url.path)):
            return True
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise Error(status_code=HTTPStatus.INVALID_TOKEN, message="无效的身份验证方案。")
            account_info = JWTBearer.verify_jwt(credentials.credentials)
            identity = account_info.get(g.config.POWER_KEY)
            if not account_info:
                raise Error(status_code=HTTPStatus.INVALID_TOKEN, message="无效令牌或过期令牌。")
            if not self.roure_manager.check_auth(path_to_key(request.url.path), identity):
                raise Error(status_code=HTTPStatus.FORBIDDEN, message="权限不足，拒绝继续访问")
            if g.config.GOD_IDENTITY and g.config.GOD_IDENTITY != identity:
                if not self.roure_manager.check_rule(path_to_key(request.url.path), account_info.get('authority')):
                    raise Error(status_code=HTTPStatus.FORBIDDEN, message="没有访问该接口的权限")
            g.u_id = account_info.get('u_id', account_info.get('id'))
            g.identity = account_info.get('identity')
            return account_info
        else:
            raise Error(status_code=HTTPStatus.FORBIDDEN, message="无效的授权代码。")

    # 验证token
    @staticmethod
    def verify_jwt(jwtoken: str) -> dict:
        # noinspection PyBroadException
        try:
            jwtoken = jwtoken.strip()
            load_data = jwt.decode(jwtoken, SECRET_KEY, algorithms=[ALGORITHM])
        except Exception:
            load_data = {}
        return load_data

    # 验证用户权限
    @staticmethod
    def verify_type(rules, account_info):
        _type = account_info.get('type')
        if _type not in rules:
            raise Error(status_code=HTTPStatus.FORBIDDEN, message="权限不足，拒绝继续访问")
