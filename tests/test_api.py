"""T14: API 层 + 异常处理（设计稿 §四/§八）。"""
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core import errors, status
from app.main import app
from app.models.connection import ClickHouseConn


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_driver(monkeypatch):
    driver = MagicMock()
    monkeypatch.setattr("app.api.databases.get_driver", lambda et: driver)
    return driver


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200


def test_database_engines(client):
    r = client.get("/database-engines")
    assert r.status_code == 200
    body = r.json()
    # 7 种引擎都列出
    names = {e["engine_type"] for e in body["engines"]}
    assert names == {"mysql", "postgresql", "mongodb", "clickhouse", "redis", "elasticsearch", "kafka"}


def test_create_returns_202(client, mock_driver):
    mock_driver.create.return_value = {"name": "ck-01", "engine_type": "clickhouse", "status": "creating"}
    r = client.post("/databases", json={
        "name": "ck-01", "engine_type": "clickhouse",
        "cpu": "1", "memory": "2Gi", "storage": "50Gi", "shards": 1,
    })
    assert r.status_code == 202
    assert r.json()["status"] == "creating"


def test_create_invalid_param_400(client, mock_driver):
    r = client.post("/databases", json={
        "name": "BAD_NAME", "engine_type": "clickhouse",
        "cpu": "1", "memory": "2Gi", "storage": "50Gi",
    })
    assert r.status_code == 400
    assert "error" in r.json()


def test_create_duplicate_409(client, mock_driver):
    mock_driver.create.side_effect = errors.AlreadyExistsError("实例 ck-01 已存在")
    r = client.post("/databases", json={
        "name": "ck-01", "engine_type": "clickhouse",
        "cpu": "1", "memory": "2Gi", "storage": "50Gi",
    })
    assert r.status_code == 409
    assert r.json() == {"error": "实例 ck-01 已存在"}


def test_get_status_200(client, mock_driver):
    mock_driver.get.return_value = {"name": "ck-01", "engine_type": "clickhouse", "status": "ready", "message": "", "raw": {}}
    r = client.get("/databases/clickhouse/ck-01")
    assert r.status_code == 200
    assert r.json()["status"] == "ready"


def test_get_not_found_404(client, mock_driver):
    mock_driver.get.side_effect = errors.NotFoundError("实例 x 不存在")
    r = client.get("/databases/clickhouse/x")
    assert r.status_code == 404
    assert "error" in r.json()


def test_list_200(client, mock_driver):
    mock_driver.list.return_value = [{"name": "ck-01", "engine_type": "clickhouse", "status": "ready"}]
    r = client.get("/databases/clickhouse")
    assert r.status_code == 200
    assert r.json()["items"][0]["name"] == "ck-01"


def test_delete_returns_202(client, mock_driver):
    mock_driver.delete.return_value = None
    r = client.delete("/databases/clickhouse/ck-01")
    assert r.status_code == 202
    assert r.json()["status"] == "deleting"


def test_connection_200(client, mock_driver):
    mock_driver.connection.return_value = ClickHouseConn(
        host="clickhouse-ck-01.clickhouse.svc", port=9000, username="idms", password="x"
    )
    r = client.get("/databases/clickhouse/ck-01/connection")
    assert r.status_code == 200
    assert r.json()["type"] == "clickhouse"
    assert r.json()["http_port"] == 8123


def test_upstream_error_502(client, mock_driver):
    mock_driver.get.side_effect = errors.UpstreamError("K8s 故障")
    r = client.get("/databases/clickhouse/ck-01")
    assert r.status_code == 502
    assert "error" in r.json()


def test_unknown_engine_in_path_404(client):
    # 未 mock，真实 registry 会对 oracle 抛 NotFound
    r = client.get("/databases/oracle/x")
    assert r.status_code == 404
