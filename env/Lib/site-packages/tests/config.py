# Author: IFCZT
# Email: ifczt@qq.com
from datetime import timedelta


class Config:
    ORIGINS = ["*"]

    SERVER_CONFIG = {
        "app": "main:IFastAPI.app",
        "host": "localhost",
        "port": 5000,
        "reload": True,
        # "workers": 3,
    }
    DB_CONFIG = {
        "dialect": 'mysql',
        "driver": 'pymysql',
        "async_driver": 'aiomysql',
        "username": 'root',
        "password": 'ifczt#IFCZT',
        "host": '127.0.0.1',
        "port": '3306',
        "database": 'ez.db'
    }
    SQLALCHEMY_DATABASE_URI = "{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4".format(**DB_CONFIG)
    ASYNC_SQLALCHEMY_DATABASE_URI = "{dialect}+{async_driver}://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4".format(**DB_CONFIG)
    ACCESS_TOKEN_EXPIRES = timedelta(minutes=60*10)
    PARAM_TRANSLATE = {
        "account": "账号",
        "password": "密码",
        "name": "姓名",
        "phone": "手机号",
        "email": "邮箱",
        "code": "验证码",
        "id": "编码"
    }
