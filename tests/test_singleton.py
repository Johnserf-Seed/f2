import pytest

from f2.utils._singleton import Singleton

class Database(metaclass=Singleton):
    def __init__(self, name):
        self.name = name

    def query(self, sql):
        return f"query {self.name}: {sql}"

def test_singleton_basic():
    db1 = Database("main")
    db2 = Database("main")
    assert db1 is db2
    assert db1.query("SELECT 1") == "query main: SELECT 1"


def test_singleton_reset():
    db1 = Database("temp")
    Database.reset_instance("temp")
    db2 = Database("temp")
    assert db1 is not db2
    assert db2.query("SELECT 2") == "query temp: SELECT 2"
