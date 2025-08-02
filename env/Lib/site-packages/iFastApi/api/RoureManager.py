import logging

from ..utils.singleton import Singleton


@Singleton
class RouteManager:
    def __init__(self):
        # 无需使用DB的路由集合
        self.use_db_route = set()
        # 权限验证集合
        self.auth = {}
        # 需要token验证的路由集合
        self.need_token = set()
        # 规则验证集合
        self.rules = {}

    def add_auth(self, route, power):
        if isinstance(power, bool) and power:
            self.need_token.add(route)
            return
        self.auth[route] = power

    def add_rule(self, route, rules: list):
        if rules:
            self.rules[route] = rules

    def check_rule(self, route, authority: list):
        if route not in self.rules:
            return True
        # 只要存在交集就返回True
        return len(set(self.rules[route]) & set(authority or [])) > 0

    def check_auth(self, route, power):
        if route not in self.auth:
            return True
        return power in self.auth[route]

    def path_need_token(self, path_key):
        return path_key in self.need_token or path_key in self.auth

    def add_use_db_route(self, route):
        self.use_db_route.add(route)

    def is_use_db_route(self, route):
        return route in self.use_db_route
