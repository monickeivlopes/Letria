from .singleton import Singleton


@Singleton
class Globals:
    def __init__(self):
        self.u_id = None
        self.config = None
        self.identity = None


g = Globals()
