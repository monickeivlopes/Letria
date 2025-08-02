# Author: IFCZT
# Email: ifczt@qq.com
from urllib.request import Request

from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteException
from starlette.middleware.cors import CORSMiddleware

from .api.BaseRoute import BaseRoute
from .db import DBManager
from .utils.globals import g
from .utils.iResponse import HTTPStatus, Error, JSONResponse
from .utils.jwtToken import JWTBearer


class IFastAPI:
    """
    config: 配置文件
        - ORIGINS: 允许跨域的域名 默认为'*'
    """
    config = None
    app = FastAPI(dependencies=[Depends(DBManager().auto), Depends(JWTBearer())])

    def setup(self):
        self.setup_config()
        self.setup_db()
        self.setup_route()

    def setup_config(self):
        """配置config"""
        origins = self.config.ORIGINS  # 允许跨域的域名
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=origins,
            allow_headers=origins,
        )

    def setup_db(self):
        """配置数据库"""
        _db = DBManager()
        _db.setup(self.config)
        _db.base.metadata.create_all(bind=_db.engine)

    def setup_route(self):
        """配置路由"""
        BaseRoute.init_router(self.app)

    def run(self, config):
        self.config = IFastAPI.config = config
        g.config = config

        self.setup()

    # 增加依赖
    def add_depend(self, depend):
        print(self.app.dependency_overrides)
        self.app.dependency_overrides[depend] = Depends(depend)
        print(self.app.dependency_overrides)
    @staticmethod
    @app.exception_handler(Error)
    async def unicorn_exception_handler(request: Request, exc: Error):
        content = {
            "success": False,
            "status_code": exc.status_code,
            "message": exc.message,
        }
        content.update(exc.data)
        return JSONResponse(
            status_code=exc.status_code,
            content=content
        )

    @staticmethod
    @app.exception_handler(StarletteException)  # 自定义HttpRequest 请求异常
    async def http_exception_handle(request, exc):
        match exc.status_code:
            case HTTPStatus.METHOD_NOT_ALLOWED:
                message = '未定义该接口'
            case HTTPStatus.NOT_FOUND:
                message = '访问接口不存在'
            case _:
                message = exc.detail
        return JSONResponse(message=message, status_code=exc.status_code)

    @staticmethod
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message="服务器内部错误"
        )

    @staticmethod
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        D = IFastAPI.config.PARAM_TRANSLATE
        errors = exc.errors()
        locs = []
        for i in errors:
            if i.get('loc'):
                locs.extend(list(i.get('loc')))
        locs = list(set(locs))
        locs = [D.get(i, i) for i in locs]
        if 'body' in locs:
            locs.remove('body')

        message = f"参数[{','.join(locs) if isinstance(locs, list) else locs}]未通过验证" if locs else '未接受到任何有效参数'
        return JSONResponse(message=message, status_code=HTTPStatus.UNPROCESSABLE_ENTITY)


