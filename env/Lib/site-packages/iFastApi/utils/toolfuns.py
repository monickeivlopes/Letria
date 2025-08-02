import hashlib
import re
from random import random
import inspect
from sqlalchemy import and_


# 多个装饰器合并
# 列如 @icompose(classmethod, idb)
def icompose(*funs):
    def deco(f):
        for fun in reversed(funs):
            f = fun(f)
        return f

    return deco


def path_to_key(path):
    return re.sub(r'/', ':', path.strip('/'))


# 生成密码
def encryption_md5(value: [str, bool]):
    return hashlib.md5(value.encode(encoding='UTF-8')).hexdigest()


def with_condition(func):
    """
        将ident 和 query_dict 两种方式的查询条件统一为 condition
    """

    def wrapper(*args, **kwargs):
        func_params = inspect.signature(func).parameters
        condition = kwargs.get('condition', None)
        ident = kwargs.get('ident')
        query_dict = kwargs.get('query_dict')
        cls = args[0]

        if not condition:
            if ident:
                condition = and_(cls.id == ident)
            elif query_dict:
                condition = cls.build_query_condition(query_dict)

        kwargs['condition'] = condition

        # 找出kwargs中与func参数匹配的键值对
        matched_kwargs = {param: kwargs[param] for param in func_params if param in kwargs}
        if len(condition.__str__()) > 0:
            return func(*args, **matched_kwargs)

    return wrapper
