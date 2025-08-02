import json
import typing

from fastapi import HTTPException
from starlette.responses import JSONResponse as _JSONResponse

from .functionPipe import CustomEncoder


class HTTPStatus:
    OK = 200  # 请求成功
    CREATED = 201  # 请求成功，并且服务器创建了新的资源
    NO_CONTENT = 204  # 请求成功，但是响应报文中没有实体的主体部分
    BAD_REQUEST = 400  # 请求报文存在语法错误或者参数错误，服务器无法理解
    UNAUTHORIZED = 401  # 请求需要用户验证
    FORBIDDEN = 403  # 请求被服务器拒绝，一般是权限不足
    INVALID_TOKEN = 431  # 无效TOKEN
    NOT_FOUND = 404  # 请求的资源不存在
    METHOD_NOT_ALLOWED = 405  # 请求方法不被允许
    NOT_ACCEPTABLE = 406  # 请求格式不可得
    REQUEST_TIMEOUT = 408  # 请求超时
    UNPROCESSABLE_ENTITY = 422  # 请求格式正确，但是由于语义错误无法响应
    INTERNAL_SERVER_ERROR = 500  # 服务器内部错误
    BAD_GATEWAY = 502  # 服务器作为网关或者代理，从上游服务器接收到了一个无效的响应
    SERVICE_UNAVAILABLE = 503  # 请求的服务不可用
    GATEWAY_TIMEOUT = 504  # 作为网关或代理的服务器在等待上游服务器响应时超时


class JSONResponse(_JSONResponse):

    def __init__(self, content=None, message=None, status_code=HTTPStatus.OK, headers=None, media_type=None, background=None):
        from ..db import BaseDB
        if content is None:
            content = {}
        content = dict(filter(lambda item: item[1] is not None and item[1] != '', content.items()))
        if isinstance(content.get('data', None), BaseDB):
            content['data'] = dict(content['data'])
        if message:
            content['message'] = message
        super().__init__(content=content, status_code=status_code, headers=headers, media_type=media_type, background=background)

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=CustomEncoder
        ).encode("utf-8")


class Error(Exception):
    def __init__(self, status_code: int = HTTPStatus.BAD_REQUEST, message: str = '未知错误', data=None):
        if data is None:
            data = {}

        self.message = message
        self.status_code = status_code
        self.data = data


class iResponse(JSONResponse):
    def __init__(self, data=None, message=None, status_code=HTTPStatus.OK, **kwargs):
        body = {"success": status_code < 300, "message": message, "data": data}
        if kwargs:
            body.update(kwargs)
        super().__init__(content=body, status_code=status_code)


class Success(iResponse):
    pass
