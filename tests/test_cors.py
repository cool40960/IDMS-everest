"""T1(前端轮): 验证后端开启了 CORS（前端跨域访问需要）。"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_cors_header_present_on_simple_request():
    # 带 Origin 的请求，响应应回 Access-Control-Allow-Origin
    r = client.get("/healthz", headers={"Origin": "http://localhost:5173"})
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "*"


def test_cors_preflight_allows_methods():
    # 预检请求（OPTIONS）应被允许，且回显允许的方法
    r = client.options(
        "/databases",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert r.status_code in (200, 204)
    assert r.headers.get("access-control-allow-origin") == "*"
