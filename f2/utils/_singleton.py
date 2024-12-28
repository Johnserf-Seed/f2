# path: f2/utils/_singleton.py

import threading


class Singleton(type):
    """
    单例元类 (Singleton Metaclass)

    该元类用于实现单例模式，确保每个类在程序中只会创建一个实例。它通过重写 `__call__` 方法来控制实例化过程，确保在相同参数下返回相同实例。

    类属性:
    - _instances (dict): 存储每个类实例化对象的字典，键为 (类, 参数) 元组，值为实例对象。
    - _lock (threading.Lock): 用于保证线程安全的锁，防止多线程环境中出现多个实例。

    类方法:
    - __init__: 初始化方法，调用父类的构造方法。
    - __call__: 重写类实例化方法，当创建类实例时判断是否已经存在相同参数的实例，若存在则返回该实例，否则创建新实例。
    - reset_instance: 重置指定参数的实例，删除 `cls._instances` 中的实例引用，但不会删除实际实例。

    使用示例:
    ```python
        class MyClass(metaclass=Singleton):
            pass

        # 第一次创建实例
        instance1 = MyClass()

        # 再次创建实例，返回相同实例
        instance2 = MyClass()

        assert instance1 is instance2  # 返回 True，确保是相同实例
    ```

    备注:
    - 单例模式确保类只有一个实例，并且所有使用该类的代码共享同一个实例。
    - 通过重写 `__call__` 方法，可以灵活地管理实例创建，支持通过不同参数创建唯一实例。
    - 线程锁 (`_lock`) 确保在多线程环境下创建实例时的线程安全。

    异常处理:
    - 无显式异常处理，异常由类外部的代码或实例化过程中的错误触发。
    """

    _instances = {}  # 存储实例的字典
    _lock: threading.Lock = threading.Lock()  # 线程锁

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        """
        重写默认的类实例化方法。

        Args:
            *args: 位置参数
            **kwargs: 关键字参数

        Note:
            当尝试创建类的一个新实例时，此方法将被调用。
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
        重置指定参数的实例。

        Args:
            *args: 位置参数
            **kwargs: 关键字参数

        Note:
            这只是从 _instances 字典中删除实例的引用，
            并不真正删除该实例。如果其他地方仍引用该实例，它仍然存在且可用。
        """
        key = (cls, args, frozenset(kwargs.items()))
        with cls._lock:
            if key in cls._instances:
                del cls._instances[key]
