"""占位测试：确认 pytest 能跑、pythonpath 配好、app 包可导入。"""
import app  # noqa: F401


def test_pytest_works():
    assert True
