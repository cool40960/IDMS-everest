"""T2: 自定义异常（设计稿 §八）。

各驱动只抛这里的异常，FastAPI 异常处理器按 http_status 集中翻成 {"error": ...}。
"""
import pytest

from app.core import errors


def test_base_class_holds_message():
    e = errors.IDMSError("出错了")
    assert str(e) == "出错了"
    assert e.message == "出错了"


def test_subclasses_inherit_base():
    for cls in (errors.AlreadyExistsError, errors.NotFoundError, errors.UpstreamError):
        assert issubclass(cls, errors.IDMSError)


@pytest.mark.parametrize(
    "cls,code",
    [
        (errors.AlreadyExistsError, 409),
        (errors.NotFoundError, 404),
        (errors.UpstreamError, 502),
    ],
)
def test_http_status_codes(cls, code):
    assert cls.http_status == code
    # 实例也能拿到（处理器统一读类属性）
    assert cls("x").http_status == code


def test_raisable():
    with pytest.raises(errors.NotFoundError):
        raise errors.NotFoundError("实例 foo 不存在")
