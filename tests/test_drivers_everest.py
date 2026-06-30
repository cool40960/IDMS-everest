"""T12: Everest 驱动（设计稿 §九）。

重点：① JWT 登录（原代码完全没有）；② engine.type 映射 mysql→pxc/mongodb→psmdb
（原代码直接透传，建不出库）；③ 账密从环境变量读，不硬编码。
"""
from unittest.mock import MagicMock

import pytest

from app.core import errors, status
from app.models.connection import MySQLConn
from app.models.specs import MySQLSpec
from app.drivers import everest as everest_mod
from app.drivers.everest import EverestDriver


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("EVEREST_USER", "admin")
    monkeypatch.setenv("EVEREST_PASSWORD", "admin123")


@pytest.fixture
def mock_session(monkeypatch):
    """mock requests：登录返回 token，其余按需配置。"""
    sess = MagicMock()
    login_resp = MagicMock()
    login_resp.status_code = 200
    login_resp.json.return_value = {"token": "JWT-TOKEN"}
    sess.post.return_value = login_resp
    monkeypatch.setattr(everest_mod.requests, "request", sess.request)
    monkeypatch.setattr(everest_mod.requests, "post", sess.post)
    return sess


def _spec(name="mysql-01", engine_type="mysql"):
    return MySQLSpec(name=name, engine_type=engine_type, cpu="1", memory="2Gi", storage="20Gi")


def test_type_mapping():
    assert EverestDriver("mysql")._everest_type() == "pxc"
    assert EverestDriver("mongodb")._everest_type() == "psmdb"
    assert EverestDriver("postgresql")._everest_type() == "postgresql"


def test_credentials_from_env_required(monkeypatch):
    monkeypatch.delenv("EVEREST_USER", raising=False)
    monkeypatch.delenv("EVEREST_PASSWORD", raising=False)
    d = EverestDriver("mysql")
    with pytest.raises(errors.UpstreamError):
        d._login()


def test_login_returns_bearer(env, mock_session):
    d = EverestDriver("mysql")
    token = d._login()
    assert token == "JWT-TOKEN"
    headers = d._auth_headers()
    assert headers["Authorization"] == "Bearer JWT-TOKEN"


def test_create_maps_type_in_body(env, mock_session):
    resp = MagicMock(status_code=200)
    resp.json.return_value = {"metadata": {"name": "mysql-01"}}
    mock_session.request.return_value = resp
    d = EverestDriver("mysql")
    d.create(_spec())
    # 找到建库那次 request 调用，验证 body 里 engine.type 已映射成 pxc
    body = None
    for c in mock_session.request.call_args_list:
        if c.kwargs.get("json", {}).get("kind") == "DatabaseCluster":
            body = c.kwargs["json"]
    assert body["spec"]["engine"]["type"] == "pxc"


def test_parse_status():
    d = EverestDriver("mysql")
    assert d.parse_status({"status": "ready"}) == status.READY
    assert d.parse_status({"status": "error"}) == status.ERROR
    assert d.parse_status({"status": "initializing"}) == status.INITIALIZING


def test_relogin_on_401(env, mock_session):
    calls = {"n": 0}

    def request_side(method, url, **kwargs):
        if "session" in url:  # 登录
            r = MagicMock(status_code=200)
            r.json.return_value = {"token": "T2"}
            return r
        calls["n"] += 1
        r = MagicMock()
        r.status_code = 401 if calls["n"] == 1 else 200
        # 真实 Everest 结构：status 是嵌套对象
        r.json.return_value = {"status": {"status": "ready"}}
        return r

    mock_session.request.side_effect = request_side
    d = EverestDriver("mysql")
    result = d.get("mysql-01")
    # 第一次 401 触发重登 + 重试，最终拿到 ready
    assert result["status"] == status.READY
    assert calls["n"] == 2
