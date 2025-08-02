# Author: IFCZT
# Email: ifczt@qq.com
from typing import Tuple, Any

from sqlalchemy import orm, func
from ..utils.iResponse import Error, HTTPStatus
import pandas as pd


class BaseQuery(orm.Query):
    def _all_selected_columns(self):
        # 获取当前查询对象中所有被选择的列
        selected_columns = set()
        for entity in self._entities:
            if isinstance(entity, orm.attributes.QueryableAttribute):
                selected_columns.add(entity)
        return selected_columns

    def _copy_internals(self, omit_attrs=(), **kw):
        # 复制当前查询对象的内部状态
        instance = self.__class__.__new__(self.__class__)
        instance.__dict__.update(self.__dict__)
        for attr in omit_attrs:
            delattr(instance, attr)
        instance.__dict__.update(kw)
        return instance

    def filter_by(self, **kwargs):
        kwargs['status'] = kwargs.get('status', 1)
        result = super(BaseQuery, self).filter_by(**kwargs)
        return result

    def first_or_404(self, message='资源不存在'):
        rv = self.first()
        if not rv:
            raise Error(message=message, status_code=HTTPStatus.NOT_FOUND)
        return rv

    def no_one(self, message='资源已存在'):
        rv = self.first()
        if rv:
            raise Error(message=message, status_code=HTTPStatus.BAD_REQUEST)
        return rv

    def count(self):
        """
        执行查询并返回结果的数量。
        :return: 结果数量
        """
        return self.with_entities(func.count()).scalar()

    def sum(self, column):
        """
        对指定列进行求和操作。
        :param column: 列名
        :return: 求和结果
        """
        return self.with_entities(func.sum(column)).scalar()

    def avg(self, column):
        """
        对指定列进行平均值计算。
        :param column: 列名
        :return: 平均值结果
        """
        return self.with_entities(func.avg(column)).scalar()

    def max(self, column):
        """
        获取指定列的最大值。
        :param column: 列名
        :return: 最大值
        """
        return self.with_entities(func.max(column)).scalar()

    def min(self, column):
        """
        获取指定列的最小值。
        :param column: 列名
        :return: 最小值
        """
        return self.with_entities(func.min(column)).scalar()

    def export_to_csv(self, filename):
        results = self.all()
        df = pd.read_sql(self.statement, self.session.bind)
        df.to_csv(filename, index=False)
