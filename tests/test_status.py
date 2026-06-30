"""T1: 统一状态词常量（设计稿 §六）。注意是 error 不是 failed。"""
from app.core import status


def test_status_constants():
    assert status.CREATING == "creating"
    assert status.INITIALIZING == "initializing"
    assert status.READY == "ready"
    assert status.ERROR == "error"
    assert status.DELETING == "deleting"


def test_error_not_failed():
    # 设计稿明确：对齐 OpenEverest 实测，是 error 不是 failed
    assert status.ERROR == "error"
    assert not hasattr(status, "FAILED")


def test_all_set():
    assert status.ALL == frozenset(
        {"creating", "initializing", "ready", "error", "deleting"}
    )
