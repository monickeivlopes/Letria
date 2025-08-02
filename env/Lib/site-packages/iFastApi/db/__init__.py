# Author: IFCZT
# Email: ifczt@qq.com
import re
import time
from threading import local

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from starlette.requests import Request

from sqlalchemy import Column, Integer, SmallInteger, text, and_, event
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from ..api.RoureManager import RouteManager
from ..utils.toolfuns import path_to_key, with_condition
from ..utils.iResponse import Error
from .BaseQuery import BaseQuery
from ..utils.singleton import Singleton
from ..utils.time import time as t


def ping_listener(dbapi_con, con_record, con_proxy):
    """
    监听连接的事件，在每次会话开始时执行ping操作以确保连接的有效性
    """
    try:
        dbapi_con.ping(reconnect=True, attempts=3, delay=0.5)
    except Exception as e:
        # 处理ping异常，例如记录日志
        pass


@Singleton
class DBManager:
    base = declarative_base()

    def __init__(self):
        self._local = None
        self._engine = None
        self._session_factory = None
        self._async_engine = None
        self._async_session_factory = None
        self.roure_manager = RouteManager()

    def setup(self, config):
        if not hasattr(config, 'SQLALCHEMY_DATABASE_URI'):
            raise Exception('数据库连接地址未配置')

        self._engine = create_engine(config.SQLALCHEMY_DATABASE_URI, pool_recycle=3600, pool_pre_ping=True)
        self._async_engine = create_async_engine(config.ASYNC_SQLALCHEMY_DATABASE_URI, pool_recycle=3600, pool_pre_ping=True)
        self._session_factory = sessionmaker(bind=None, autocommit=False, autoflush=False, query_cls=BaseQuery)
        self._async_session_factory = sessionmaker(bind=self._async_engine, class_=AsyncSession, expire_on_commit=False)
        event.listen(self._session_factory, 'after_begin', ping_listener)

    def auto(self, request: Request):
        """
        自动生成会话对象 自动生成、关闭会话对象
        """

        path = path_to_key(request.url.path)
        if not self.roure_manager.is_use_db_route(path):
            yield
        else:
            try:
                yield self.get_session()
            finally:
                self.close_session()

    # region 同步引擎
    @property
    def engine(self):
        if not self._engine:
            raise Exception('数据库未连接')
        return self._engine

    @engine.setter
    def engine(self, database_uri):
        self._engine = create_engine(database_uri)

    def execute(self, sql, execute_type='read'):
        """执行sql语句"""
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            if execute_type == 'read':
                return result
            elif execute_type == 'write':
                conn.commit()
                return result.lastrowid

    # endregion

    # region 异步引擎
    @property
    def async_engine(self):
        if not self._async_engine:
            raise Exception('数据库未连接')
        return self._async_engine

    @async_engine.setter
    def async_engine(self, database_uri):
        self._async_engine = create_async_engine(database_uri)

    async def async_execute(self, sql, execute_type='read'):
        async with self._async_session_factory() as session:
            result = await session.execute(text(sql))
            if execute_type == 'read':
                result = result.fetchall()
                return result
            elif execute_type == 'write':
                await session.commit()
                return result.lastrowid

    # endregion

    def get_session(self):
        """
        获取当前线程的会话对象
        """
        if not self._local:
            self._local = local()
        if not hasattr(self._local, "session"):
            self._session_factory.configure(bind=self.engine)
            self._local.session = scoped_session(self._session_factory, scopefunc=lambda: id(self._local))
        # ping

        return self._local.session()

    @property
    def session(self):
        return self.get_session()

    def close_session(self):
        """
        关闭当前线程的会话对象
        """
        if hasattr(self._local, "session"):
            try:
                self._local.session.commit()
            except Exception as e:
                self._local.session.rollback()

            self._local.session.close()
            self._local.session.remove()
            del self._local.session

    async def shutdown(self):
        self.close_session()


class BaseDB(DBManager.base):
    __abstract__ = True
    __table_args__ = {"extend_existing": True}

    create_time = Column(Integer, comment='生成时间')
    status = Column(SmallInteger, default=1, comment='是否软删除 0 / 1')
    fileds = []
    protect_fileds = ['id', 'create_time']

    def __init__(self, *args, **kwargs):
        self.set_attrs(kwargs)
        self.create_time = t.int_time(modes="s")

    '''输出dict 相关方法'''

    def __getitem__(self, item):
        return getattr(self, item)

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    def keys(self):
        return self.fileds

    def hide(self, *keys):
        for key in keys:
            self.fileds.remove(key)
        return self

    def append(self, *keys):
        for key in keys:
            self.fileds.append(key)
        return self

    '''输出dict 相关方法'''

    @property
    def create_datetime(self):
        # 将时间戳转换为时间
        if self.create_time:
            return t.format_time(self.create_time)
        else:
            return None

    @classmethod
    @property
    def db(cls):
        return DBManager().session

    @classmethod
    @property
    def query(cls):
        return cls.db.query(cls)

    def dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}

    @classmethod
    def get_id(cls, ident, result_dict=None):
        result = cls.query.get(ident)
        result.fileds = result_dict or result.fileds
        return dict(result or {})

    @classmethod
    def get_list(cls, page=1, size=20, query_dict=None, order_by=None):
        """
        获取列表
        :param page: 页码
        :param size: 每页数量
        :param query_dict: 查询条件
        :param order_by: 排序 id^ = id desc id = id asc
        """
        condition = cls.build_query_condition(query_dict)
        total = cls.query.filter(condition).count()
        sql = cls.query.filter(condition)
        if order_by:
            order_by = re.sub(r'(\w+)\^', r'\1 desc', order_by)
            sql = sql.order_by(text(order_by))
        result = sql.limit(size).offset((page - 1) * size).all()
        return [dict(row) for row in result], total

    @classmethod
    def insert(cls, insert_dict):
        """
        插入
        :param insert_dict: 插入内容
        """
        try:
            obj = cls(**insert_dict)
            cls.db.add(obj)
            cls.db.commit()
            return obj
        except Exception as e:
            cls.db.rollback()
            raise e
        return obj

    @classmethod
    @with_condition
    def remove(cls, condition):
        """
        删除
        :param condition: 查询条件
        """

        cls.query.filter(condition).update({cls.status: 0})
        cls.db.commit()

    @classmethod
    @with_condition
    def delete(cls, condition):
        """
        删除
        :param condition: 查询条件
        """

        cls.query.filter(condition).delete()
        cls.db.commit()

    @classmethod
    def filter_update_dict(cls, update_dict):
        # 过滤掉不允许更新的字段
        for key in cls.protect_fileds:
            update_dict.pop(key, None)
        # 不在表中的字段
        for key in list(update_dict.keys()):
            if key not in cls.__table__.columns.keys():
                update_dict.pop(key, None)
        return update_dict

    @classmethod
    @with_condition
    def update(cls, update_dict, condition):
        """
        更新
        :param update_dict: 更新内容
        :param condition: 查询条件
        """
        if condition is None:
            raise Error(message='查询条件不能为空')
        update_dict = cls.filter_update_dict(update_dict)
        if not update_dict:
            raise Error(message='无更新内容')
        cls.query.filter(condition).update(update_dict)
        cls.db.commit()

    @classmethod
    def build_query_condition(cls, query_dict=None):
        if not query_dict:
            query_dict = {}
        if 'eq:status' not in query_dict:
            condition = and_(cls.status == 1)
        else:
            condition = and_()
        if not query_dict:
            return condition
        for key, value in query_dict.items():

            if key.startswith('eq:'):
                condition = and_(condition, getattr(cls, key[3:]) == value)
            elif key.startswith('ne:'):
                condition = and_(condition, getattr(cls, key[3:]) != value)
            elif key.startswith('gt:'):
                condition = and_(condition, getattr(cls, key[3:]) > value)
            elif key.startswith('ge:'):
                condition = and_(condition, getattr(cls, key[3:]) >= value)
            elif key.startswith('lt:'):
                condition = and_(condition, getattr(cls, key[3:]) < value)
            elif key.startswith('le:'):
                condition = and_(condition, getattr(cls, key[3:]) <= value)
            elif key.startswith('in:'):
                condition = and_(condition, getattr(cls, key[3:]).in_(value))
            elif key.startswith('like:'):
                condition = and_(condition, getattr(cls, key[5:]).like('%' + value + '%'))
            elif key.startswith('ilike:'):
                condition = and_(condition, getattr(cls, key[6:]).ilike(value))
            elif key.startswith('is:'):
                condition = and_(condition, getattr(cls, key[3:]) == value)
            elif key.startswith('isnot:'):
                condition = and_(condition, getattr(cls, key[6:]) != value)
            elif key.startswith('isnull:'):
                condition = and_(condition, getattr(cls, key[6:]) is None)
            elif key.startswith('isnotnull:'):
                condition = and_(condition, getattr(cls, key[9:]) is not None)
            elif key.startswith('between:'):
                if isinstance(value, str):
                    value = [value + ' 00:00:00', value + ' 23:59:59']
                condition = and_(condition, getattr(cls, key[8:]).between(value[0], value[1]))
        return condition
