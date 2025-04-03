# path: tests/test_singleton.py

from f2.utils.core.singleton import Singleton


class Database(metaclass=Singleton):
    def __init__(self, db_name):
        print(f"初始化数据库：{db_name}")
        self.db_name = db_name

    def query(self, query_str):
        return f"查询 {self.db_name} 数据库：{query_str}"


# 测试单例模式
db1 = Database("db1")
print(db1.query("SELECT * FROM users"))

db2 = Database("db2")
print(db2.query("SELECT * FROM aweme"))

# 尝试销毁 db1 实例。注意这不是真的删除实例，只是从 _instances 字典中删除它的引用。
Database.reset_instance("db1")

# 由于我们仍然持有原始 db1 对象的引用，因此它仍然是可访问的。
print(db1.query("SELECT * FROM apps"))

# 创建一个名为 "db1" 的新实例。这将是一个全新的实例，但在当前实现中，__init__ 方法不会被再次调用。
db1_new = Database("db1")
print(db1_new.query("SELECT name FROM users"))
