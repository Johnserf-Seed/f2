# path: f2/utils/_singleton.py

import threading


class Singleton(type):
    _instances = {}  # 存储实例的字典
    _lock: threading.Lock = threading.Lock()  # 线程锁

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        """
        重写默认的类实例化方法。当尝试创建类的一个新实例时，此方法将被调用。
        如果已经有一个与参数匹配的实例存在，则返回该实例；否则创建一个新实例。
        """
        key = (cls, args, frozenset(kwargs.items()))
        with cls._lock:
            if key not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[key] = instance
        return cls._instances[key]

    @classmethod
    def reset_instance(cls, *args, **kwargs):
        """
        重置指定参数的实例。这只是从 _instances 字典中删除实例的引用，
        并不真正删除该实例。如果其他地方仍引用该实例，它仍然存在且可用。
        """
        key = (cls, args, frozenset(kwargs.items()))
        with cls._lock:
            if key in cls._instances:
                del cls._instances[key]
