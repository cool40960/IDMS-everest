"""T6: DatabaseDriver 抽象基类（设计稿 §3.1）。"""
import pytest

from app.drivers.base import DatabaseDriver


def test_cannot_instantiate_abstract():
    with pytest.raises(TypeError):
        DatabaseDriver()


def test_partial_impl_still_abstract():
    class Partial(DatabaseDriver):
        def create(self, spec):
            return "x"
        # 故意不实现其余方法

    with pytest.raises(TypeError):
        Partial()


def test_full_impl_instantiable():
    class Full(DatabaseDriver):
        def create(self, spec): return "x"
        def get(self, name): return {}
        def delete(self, name): return None
        def list(self): return []
        def connection(self, name): return {}

    d = Full()
    assert d.create(None) == "x"


def test_has_five_abstract_methods():
    expected = {"create", "get", "delete", "list", "connection"}
    assert expected <= DatabaseDriver.__abstractmethods__
