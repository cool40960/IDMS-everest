"""T9: Redis 驱动（设计稿 §6.1）。

重点：RedisFailover CRD 没有 status 字段，就绪判定要查 operator 建的工作负载——
StatefulSet rfr-<name>（redis 主从）+ Deployment rfs-<name>（sentinel）的 readyReplicas。
"""
from unittest.mock import MagicMock

import pytest
from kubernetes.client import ApiException

from app.core import errors, status
from app.models.connection import RedisConn
from app.models.specs import RedisSpec
from app.drivers import redis as redis_mod
from app.drivers.redis import RedisDriver


def _spec(**kw):
    base = dict(name="redis-01", engine_type="redis", cpu="1", memory="2Gi", storage="20Gi")
    base.update(kw)
    return RedisSpec(**base)


def _workload(ready, desired):
    w = MagicMock()
    w.status.ready_replicas = ready
    w.spec.replicas = desired
    return w


def test_build_body_sentinel_fixed_3():
    d = RedisDriver()
    body = d.build_body(_spec())
    assert body["kind"] == "RedisFailover"
    assert body["spec"]["sentinel"]["replicas"] == 3  # 隐藏参数写死


def test_build_body_redis_replicas():
    d = RedisDriver()
    body = d.build_body(_spec(replicas=2))
    assert body["spec"]["redis"]["replicas"] == 2


@pytest.fixture
def mock_apps(monkeypatch):
    apps = MagicMock()
    monkeypatch.setattr(redis_mod, "get_apps_api", lambda: apps)
    # CRD 存在性检查也要 mock（get() 会先确认 CRD 还在）
    custom = MagicMock()
    custom.get_namespaced_custom_object.return_value = {"metadata": {"name": "redis-01"}}
    monkeypatch.setattr(redis_mod, "get_custom_api", lambda: custom)
    return apps


def test_get_ready_when_both_workloads_ready(mock_apps):
    mock_apps.read_namespaced_stateful_set.return_value = _workload(1, 1)
    mock_apps.read_namespaced_deployment.return_value = _workload(3, 3)
    d = RedisDriver()
    result = d.get("redis-01")
    assert result["status"] == status.READY
    assert result["name"] == "redis-01"


def test_get_initializing_when_redis_not_ready(mock_apps):
    mock_apps.read_namespaced_stateful_set.return_value = _workload(0, 1)
    mock_apps.read_namespaced_deployment.return_value = _workload(3, 3)
    d = RedisDriver()
    assert d.get("redis-01")["status"] == status.INITIALIZING


def test_get_creating_when_workloads_absent(mock_apps):
    mock_apps.read_namespaced_stateful_set.side_effect = ApiException(status=404)
    d = RedisDriver()
    assert d.get("redis-01")["status"] == status.CREATING


def test_parse_connection():
    d = RedisDriver()
    c = d.parse_connection("redis-01")
    assert isinstance(c, RedisConn)
    assert c.port == 6379
